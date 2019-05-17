from PyQt5 import QtCore, QtWidgets, QtGui
import os

class hoverLabel(QtWidgets.QLabel):
    def __init__(self, pathToNormalIcon, pathToHoverIcon, hoverText):
        QtWidgets.QLabel.__init__(self)
        self.p1 = pathToNormalIcon
        self.p2 = pathToHoverIcon
        self.setPixmap(QtGui.QPixmap(os.path.abspath(self.p1)).scaled(15,15, QtCore.Qt.KeepAspectRatio))
    def enterEvent(self, ev):
        self.setPixmap(QtGui.QPixmap(os.path.abspath(self.p2)).scaled(15,15, QtCore.Qt.KeepAspectRatio))
    def leaveEvent(self, ev):
        self.setPixmap(QtGui.QPixmap(os.path.abspath(self.p1)).scaled(15,15, QtCore.Qt.KeepAspectRatio))

class hoverButton(QtWidgets.QLabel):
    triggered = QtCore.pyqtSignal(bool)
    def __init__(self, pathToNormalIcon, pathToHoverIcon):
        QtWidgets.QLabel.__init__(self)
        self.p1 = pathToNormalIcon
        self.p2 = pathToHoverIcon
        self.setPixmap(QtGui.QPixmap(os.path.abspath(self.p1)).scaled(15,15, QtCore.Qt.KeepAspectRatio))
    def enterEvent(self, ev):
        self.setPixmap(QtGui.QPixmap(os.path.abspath(self.p2)).scaled(15,15, QtCore.Qt.KeepAspectRatio))
    def leaveEvent(self, ev):
        self.setPixmap(QtGui.QPixmap(os.path.abspath(self.p1)).scaled(15,15, QtCore.Qt.KeepAspectRatio))
    def mousePressEvent(self, ev):
        self.triggered.emit(True)