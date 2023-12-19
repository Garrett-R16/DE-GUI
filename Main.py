from PyQt6 import QtWidgets, uic, QtCore, QtGui
import threading
import math
import datetime
import time
import enum
import cv2
import sys

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

    self.Worker1 = Worker1()
    self.Worker1.start()
    self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
  
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
        Pic = ConvertToQtFormat.scaled(800, 700, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.ImageUpdate.emit(Pic)

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