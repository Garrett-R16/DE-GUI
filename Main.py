from PyQt6 import QtWidgets, uic, QtCore, QtGui
import threading
import math
import datetime
import time
import enum
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

# creating the main window

class MainWindow(QtWidgets.QMainWindow):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)

    # loading the qtdesigner GUI I made

    uic.loadUi('draftGUI.ui', self)

    # mapping the buttons to a function--probably a better way of doing this but ¯\_(ツ)_/¯ for the mmt

    self.list1 = ["x", "y", "z", "grip"]

    for i in self.list1:
      exec("self.{}_pos.{}.connect(self.ButtonClicked)".format(i, "clicked"))
      exec("self.{}_neg.{}.connect(self.ButtonClicked)".format(i, "clicked"))
      exec("self.{}_pos.{}.connect(self.ButtonReleased)".format(i, "released"))
      exec("self.{}_neg.{}.connect(self.ButtonReleased)".format(i, "released"))

    self.grip_state.clicked.connect(self.ButtonClicked)

    # Starting a second thread to run the camera video

    self.camera_tracker = camera_tracker()
    self.cameras_object = self.camera_tracker.get_camera_info()

    # adding the options to the QComboBox

    for i in self.cameras_object:
      camera_name = str(i.get('camera_index')) + " " + i.get('camera_name')
      self.comboCamera.addItem(camera_name)

    self.comboCamera.currentIndexChanged.connect(self.on_combo_box_changed)

    self.Worker1 = Worker1()
    self.Worker1.start()
    self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

  def on_combo_box_changed(self, selection):
    # splitting the selected text into an index of strings to access the first value, the camera index
    selection = self.comboCamera.currentText()
    selection.split()

    new_camera_index = int(selection[0])
    print(new_camera_index)
    self.Worker1.camera_changed(new_camera_index)

  def ImageUpdateSlot(self, Image):
    self.labelFeed.setPixmap(QtGui.QPixmap.fromImage(Image))

  # basic button function
  def ButtonClicked(self):
    print("click")

  def ButtonReleased(self):
    print("Released")

class Worker1(QtCore.QThread):

  # essentially retrieving the video from the camera using OpenCV and then putting it in a format PyQt can read

  ImageUpdate = QtCore.pyqtSignal(QtGui.QImage)
  print("Worker1 initialized")

  def __init__(self):
    super(Worker1, self).__init__()
    print("Worker1 initialized")
    self.camera = cv2.VideoCapture(0)

  def camera_changed(self, camera_index):
    self.camera.release()
    self.camera = cv2.VideoCapture(camera_index)

  def run(self):
    print("thread is running")
    self.ThreadActive = True
    print("thread is running")
    print("wow")
    
    while self.ThreadActive:
      # getting frame from webcam
      ret, frame = self.camera.read()
      if ret:
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FlippedImage = cv2.flip(Image, 1)
        ConvertToQtFormat = QtGui.QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QtGui.QImage.Format.Format_RGB888)
        Pic = ConvertToQtFormat.scaled(800, 700, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.ImageUpdate.emit(Pic)

VIDEO_DEVICES = 4

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

  # TODO add MacOS specific implementations
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

# The button and arm control sections of code are heavily inspired by the work Jonathan Hearn
# It relies on the use of the library he created for controlling the UFactory arm with xbox controls

#class Button(Control, Handler):

def main():
  app=QtWidgets.QApplication(sys.argv)
  main = MainWindow()
  main.show()
  sys.exit(app.exec())
  
if __name__=='__main__':
  main()