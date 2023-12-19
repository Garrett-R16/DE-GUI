from PyQt6 import QtWidgets, uic, QtCore, QtGui
import cv2
import sys

# creating the main window

class MainWindow(QtWidgets.QMainWindow):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)

    # loading the qtdesigner GUI I made

    uic.loadUi('draftGUI.ui', self)

    # mapping the buttons to a function--probably a better way of doing this but ¯\_(ツ)_/¯ for the mmt

    self.x_pos.clicked.connect(self.ButtonClicked)
    self.x_neg.clicked.connect(self.ButtonClicked)
    self.y_pos.clicked.connect(self.ButtonClicked)
    self.y_neg.clicked.connect(self.ButtonClicked)
    self.z_pos.clicked.connect(self.ButtonClicked)
    self.z_neg.clicked.connect(self.ButtonClicked)
    self.grip_pos.clicked.connect(self.ButtonClicked)
    self.grip_neg.clicked.connect(self.ButtonClicked)
    self.grip_state.clicked.connect(self.ButtonClicked)

    # Starting a second thread to run the camera video

    self.Worker1 = Worker1()
    self.Worker1.start()
    self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
  
  def ImageUpdateSlot(self, Image):
    self.labelFeed.setPixmap(QtGui.QPixmap.fromImage(Image))
    
  # basic button function

  def ButtonClicked(self):
    print("click")

class Worker1(QtCore.QThread):

  # essentially retrieving the video from the camera using OpenCV and then putting it in a format PyQt can read

  ImageUpdate = QtCore.pyqtSignal(QtGui.QImage)
  print("worker initialized")
  camera = cv2.VideoCapture(0)

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
        Pic = ConvertToQtFormat.scaled(1500, 1000, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.ImageUpdate.emit(Pic)

def main():
    app=QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
  
if __name__=='__main__':
    main()