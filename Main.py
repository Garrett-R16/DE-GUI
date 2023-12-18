from PyQt6 import QtWidgets, uic, QtCore, QtGui
import cv2
import sys

import imagecodecs


class MainWindow(QtWidgets.QMainWindow):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)

    uic.loadUi('draftGUI.ui', self)
    self.x_pos.clicked.connect(self.xButtonClicked)

    self.Worker1 = Worker1()
    self.Worker1.start()
    self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
  
  def ImageUpdateSlot(self, Image):
    self.labelFeed.setPixmap(QtGui.QPixmap.fromImage(Image))
    
  def xButtonClicked(self):
    print("click")

class Worker1(QtCore.QThread):
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