import os
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import textwrap
from PyQt5 import QtWidgets, QtCore

class missingCanvas(FigureCanvas):

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
    
    def plotMissing(self, data, color = (0.04,0.52,0.80)):
        z = data.notnull().values
        g = np.zeros((data.shape[0], data.shape[1], 3))
        g[z < 0.5] = [1,1,1]
        g[z > 0.5] = color
        self.ax0.imshow(g, interpolation='none')
        self.ax0.set_aspect('auto')
        self.ax0.grid(b=False)
        self.ax0.xaxis.tick_top()
        self.ax0.xaxis.set_ticks_position('none')
        self.ax0.yaxis.set_ticks_position('none')
        self.ax0.spines['top'].set_visible(False)
        self.ax0.spines['right'].set_visible(False)
        self.ax0.spines['bottom'].set_visible(False)
        self.ax0.spines['left'].set_visible(False)
        ha = 'center'
        self.ax0.set_xticks(list(range(0, data.shape[1])))
        labels = [textwrap.fill(text, 15) for text in list(data.columns)]
        fontsize = 10
        self.ax0.set_xticklabels(labels, wrap = True, ha=ha, fontsize=fontsize)
        if data.shape[0] > 7000:
            freq = '12MS'
        else:
            freq = '6MS'

        in_between = [x + 0.5 for x in range(0, data.shape[1] - 1)]
        for point in in_between:
            self.ax0.axvline(point, linestyle='-', color='white')
        ts_array = pd.date_range(data.index.date[0], data.index.date[-1], freq=freq).values
        ts_ticks = pd.date_range(data.index.date[0], data.index.date[-1], freq=freq).map(lambda t: t.strftime('%Y-%m-%d'))
        ts_list = []
        try:
            for value in ts_array:
                ts_list.append(data.index.get_loc(value))
        except:
            print('erorr...')
        self.ax0.set_yticks(ts_list)
        self.ax0.set_yticklabels(ts_ticks, fontsize = 9, rotation = 0)
        plt.tight_layout(rect=[0,0,1,0.9])
        self.draw()

class missingDialog(QtWidgets.QDialog):

    def __init__(self, data):
        super(missingDialog, self).__init__()
        self.setStyleSheet("background-color:white; color:black;")
        mainLayout = QtWidgets.QVBoxLayout()
        self.plot = missingCanvas(self)
        mainLayout.addWidget(self.plot)
        self.setLayout(mainLayout)
        self.setWindowTitle('Missing Data Visualization')
        self.plot.plotMissing(data)
        self.exec_()