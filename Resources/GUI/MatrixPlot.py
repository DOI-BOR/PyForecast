import os
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
from matplotlib import gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import textwrap
from PyQt5 import QtWidgets, QtCore

class matrixCanvas(FigureCanvas):

    # Initialize a graph
    def __init__(self, parent=None, dpi=100):
        self.fig = plt.figure(figsize = (14,12))
        self.fig.patch.set_facecolor("#e8e8e8")
        self.gs = gridspec.GridSpec(1,1)
        self.ax0 = plt.subplot(self.gs[0])
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotMatrix(self, data, color = (0.04,0.52,0.80)):
        df2 = data.dropna()
        df2 = df2.apply(pd.to_numeric)
        scatter_matrix(df2, alpha=0.2, diagonal='kde', ax=self.ax0)
        #plt.savefig("Resources/tempFiles/MatrixPlot{0}.png".format(int(1000*np.random.random(1))))
        self.draw()

class matrixDialog(QtWidgets.QDialog):

    def __init__(self, data):
        super(matrixDialog, self).__init__()
        self.setStyleSheet("background-color:white; color:black;")
        mainLayout = QtWidgets.QVBoxLayout()
        self.plot = matrixCanvas(self, data)
        mainLayout.addWidget(self.plot)
        self.setLayout(mainLayout)
        self.setWindowTitle('Data Correlation Visualization')
        self.plot.plotMatrix(data)
        self.exec_()