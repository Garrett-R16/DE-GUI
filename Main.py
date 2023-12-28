from PyQt6 import QtWidgets, uic, QtCore, QtGui
import time
import cv2
import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
import asyncio
import platform
import cv2


if platform.system() == 'Windows':
	import winrt.windows.devices.enumeration as windows_devices

import mediapipe as mp

# creating the main window

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)

		# loading the qtdesigner GUI I made

		uic.loadUi('draftGUI.ui', self)
		# mapping the buttons to a function--probably a better way of doing this but ¯\_(ツ)_/¯ for the mmt
		self.armDirections = ["x", "y", "z", "grip"]

		# starting button monitor qthread
		self.button_monitor = button_monitor()
		self.button_monitor.start()

		for button_direction in self.armDirections:
			button = getattr(self, f"{button_direction}_pos")  # Assuming buttons have names like x_pos, y_pos, etc.
			button.pressed.connect(lambda button_name=button_direction: self.Button_Action(button_name, "pressed"))
			button.released.connect(lambda button_name=button_direction: self.Button_Action(button_name, "released"))

			button = getattr(self, f"{button_direction}_neg")
			button.pressed.connect(lambda button_name=button_direction: self.Button_Action(button_name, "pressed"))
			button.released.connect(lambda button_name=button_direction: self.Button_Action(button_name, "released"))

		self.grip_state.clicked.connect(lambda: self.Button_Action("grip_state", "clicked"))

		# Starting a second thread to run the camera video

		self.camera_tracker = camera_tracker()
		self.cameras_object = self.camera_tracker.get_camera_info()

		# adding the options to the QComboBox

		for i in self.cameras_object:
			camera_name = str(i.get('camera_index')) + " " + i.get('camera_name')
			self.comboCamera.addItem(camera_name)

		self.comboCamera.currentIndexChanged.connect(self.on_combo_box_changed)

		self.imageMonitor = imageMonitor()
		self.imageMonitor.start()
		self.imageMonitor.ImageUpdate.connect(self.ImageUpdateSlot)

	def on_combo_box_changed(self, selection):
        # splitting the selected text into an index of strings to access the first value, the camera index
		selection = self.comboCamera.currentText().split()
		new_camera_index = int(selection[0])
		print(new_camera_index)
		self.imageMonitor.camera_changed(new_camera_index)

	def ImageUpdateSlot(self, Image):
		self.labelFeed.setPixmap(QtGui.QPixmap.fromImage(Image))

    # basic button function
	def Button_Action(self, button_name, action_type):
		print(f"Button {button_name} {action_type}")
		

		if action_type == "pressed":
			self.start_time = time.time()
			self.button_monitor.button_state(action_type, self.start_time, button_name)
			
		if action_type == "released":
			self.button_monitor.button_state(action_type, self.start_time, button_name)
			# self.button_monitor
			# elapsed_time = time.time() - self.start_time
			# if elapsed_time <= 0.5:
			# 	print("button was pressed")
			# if elapsed_time>0.5:
			# 	print(f"{button_name} held for {elapsed_time} seconds")
    
class button_monitor(QtCore.QThread):
    
	def __init__(self):
		super(button_monitor, self).__init__()
		print("button_monitor thread started")
		self.currentState = None
		self.buttonPushed = False
		self.start_time = 0
		self.mutex = QtCore.QMutex()

	def button_state(self, currentState, start_time, button_name):
		self.currentState=currentState

		if self.currentState=="pressed":
			self.buttonPushed = True
			self.start_time=start_time

		while self.buttonPushed:
			elapsed_time = time.time() - self.start_time
			if self.currentState == "released" and elapsed_time < 0.5:
				print("button pressed")
				self.buttonPushed=False
				break

			elif self.currentState != "released" and elapsed_time > 0.5:
				print("button is being held")

			elif self.currentState == "released" and elapsed_time > 0.5:
				print(f"Button {button_name} was held for {elapsed_time} seconds")
				break



# Thank you to SH for helping me learn how to embed a OpenCV video

class imageMonitor(QtCore.QThread):

	# essentially retrieving the video from the camera using OpenCV and then putting it in a format PyQt can read

	ImageUpdate = QtCore.pyqtSignal(QtGui.QImage)
	mpMesh = mp.solutions.face_mesh
	Mesh = mpMesh.FaceMesh()
	mpDraw = mp.solutions.drawing_utils
	
	# mouthpoints were found using https://raw.githubusercontent.com/google/mediapipe/a908d668c730da128dfa8d9f6bd25d519d006692/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
	# can also be found using https://github.com/tensorflow/tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts

	mouthPoints = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

	def __init__(self):
		super(imageMonitor, self).__init__()
		print("imageMonitor initialized")
		self.camera = cv2.VideoCapture(0)

	def camera_changed(self, camera_index):
		self.camera.release()
		self.camera = cv2.VideoCapture(camera_index)

	def run(self):
		print("imageMonitor is running")
		self.ThreadActive = True

		while self.ThreadActive:
			# getting frame from webcam
			ret, frame = self.camera.read()
			if ret:
				Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				Image = self.face_landmarks(Image)

				FlippedImage = cv2.flip(Image, 1)
				ConvertToQtFormat = QtGui.QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QtGui.QImage.Format.Format_RGB888)
				Pic = ConvertToQtFormat.scaled(800, 650, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
				self.ImageUpdate.emit(Pic)
    
	def face_landmarks(self, Image):
		results = self.Mesh.process(Image)

		if results.multi_face_landmarks:
			for face_landmarks in results.multi_face_landmarks:
				#mpDraw.draw_landmarks(img, face_landmarks, mpMesh.FACEMESH_TESSELATION)
				for id, lm in enumerate(face_landmarks.landmark):
					if id in self.mouthPoints:
						h, w, c = Image.shape
						cx, cy = int(lm.x*w), int(lm.y*h)
						cv2.circle(Image, (cx, cy), 4, (0, 255, 0), cv2.FILLED)
		return Image

VIDEO_DEVICES = 4

# Big thanks to https://stackoverflow.com/questions/52558617/enumerate-over-cameras-in-python for helping figuring out how to enumrate over cameras

class camera_tracker:

	def __init__(self):
		print("camera tracker initialized")
		self.cameras = []

	def get_camera_info(self) -> list:
		self.cameras = []

		camera_indexes = self.get_camera_indexes()

		if len(camera_indexes) == 0:
			return self.cameras

		self.cameras = self.add_camera_information(camera_indexes)

		return self.cameras

	def get_camera_indexes(self):
		index = 0
		camera_indexes = []
		max_numbers_of_cameras_to_check = 10
		while max_numbers_of_cameras_to_check > 0:
			capture = cv2.VideoCapture(index)
			if capture.read()[0]:
				camera_indexes.append(index)
				capture.release()
			index += 1
			max_numbers_of_cameras_to_check -= 1
		return camera_indexes

	def add_camera_information(self, camera_indexes: list) -> list:
		platform_name = platform.system()
		cameras = []

		if platform_name == 'Windows':
			cameras_info_windows = asyncio.run(self.get_camera_information_for_windows())

			for camera_index in camera_indexes:
				
				if camera_index < len(cameras_info_windows):
					camera_name = cameras_info_windows.get_at(camera_index).name.replace('\n', '')
					cameras.append({'camera_index': camera_index, 'camera_name': camera_name})

			return cameras
	
	async def get_camera_information_for_windows(self):
		return await windows_devices.DeviceInformation.find_all_async(VIDEO_DEVICES)

def main():
	app=QtWidgets.QApplication(sys.argv)
	main = MainWindow()
	main.show()
	sys.exit(app.exec())

if __name__=='__main__':
	main()