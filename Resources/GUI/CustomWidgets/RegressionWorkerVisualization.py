"""
Script Name:    RegressionWorkerVisualization.py

Description:    Adds a visualization for whats going on while the
                regression worker is building models

"""

from PyQt5 import QtWidgets, QtCore, QtGui
import bitarray as ba

class RegressionWorkerVisualization(QtWidgets.QWidget):

    def __init__(self, parent):

        QtWidgets.QWidget.__init__(self, parent)

        # INITIALIZATION
        self.array = None
        self.paused = True
        self.started = False
        self.mode = 0           # 0 == Real-time, 1 == Accumulation

        return

    def paintEvent(self, QtGui.QPaintEvent):

        return

    def updateVisulation(self, bit_array):

        self.array = bit_array
        self.update()

        return

    def startVisualization(self):

        return

    def endVisualization(self):

        return

    def pauseVisualization(self):

        return

    def resumeVisualization(self):

        return

    def hoverEvent(self):

        return