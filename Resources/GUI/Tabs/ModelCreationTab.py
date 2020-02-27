"""
Script Name:        ModelCreationTab.py

Description:        'ModelCreationTab.py' is a PyQt5 GUI for the NextFlow application. 
                    The GUI includes all the visual aspects of the Model Creation Tab (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

"""
NOTES ---------------------

-predictor significance tests
-predictor importance in overall model result table

"""

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
import  sys
import time
import  os
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import patches
import matplotlib.pyplot as plt

class PredictorCurrentGraph(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = fig.add_subplot(211)
        self.axes1.grid(which='major', lw=2, color='k')
        self.axes1.tick_params(labelbottom=False, direction='in', labelleft=False)
        self.axes1.set_title("Current Model", loc='left', fontsize=9, fontfamily='consolas')
        self.axes2 = fig.add_subplot(212)
        self.axes2.grid(which='major', lw=2, color='k')
        self.axes2.tick_params(labelbottom=False, direction='in', labelleft=False)
        self.axes2.set_title("All Models", loc='left', fontsize=9, fontfamily='consolas')

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.draw()

        return

    def setPredictorGrid(self, modelRunTableEntry = None, datasetTable = None):
        """
        Creates the predictor grid using the model run table
        entry provided, and also sets up references to the 
        predictor information / model chromosome / and forced
        data.
        """
        
        # Get Predictor Metadata for all the predictors in this model initialization
        self.predictorPool = modelRunTableEntry['PredictorPool']
        self.predictorPeriods = modelRunTableEntry['PredictorPeriods']
        self.predictorMethods = modelRunTableEntry['PredictorMethods']
        self.predictorForceFlags = modelRunTableEntry['PredictorForceFlag']
        #self.predictorNames = [datasetTable.loc[predictorID]['DatasetName'] for predictorID in self.predictorPool]
        #self.predictorParameters = [datasetTable.loc[predictorID]['DatasetParameter'] for predictorID in self.predictorPool]
        
        # Figure out how many ros and columns we'll need for the plot
        square = np.sqrt(len(self.predictorPool))
        square = int(square) if square%1 == 0 else int(square) + 1
        self.numRows, self.numCols = [square, square]

        # Figure out which pixels correspond to which predictors
        self.pixelsToPredictors = np.full((self.numRows, self.numCols), np.nan)
        for i, predictor in enumerate(self.predictorPool):
            self.pixelsToPredictors[int(i/square), i%square] = predictor

        # Set the initial on/off status of the predictorGrid
        self.currentStatus = np.full(self.pixelsToPredictors.shape, 0, dtype='float32')

        # Set the initial predictor count for each predictor
        self.currentCount = np.full(self.currentStatus.shape, 0, dtype='float32')
    
        # Plot hatched areas over the non-used pixels
        for i in range(len(self.predictorPool), square**2):
            self.currentStatus[int(i/square), i%square] = np.nan
            self.currentCount[int(i/square), i%square] = np.nan
            self.axes1.add_patch(patches.Rectangle(((i%square)-0.5,int(i/square)-0.5), 1, 1, hatch='////', fill=False, snap=False))
            self.axes2.add_patch(patches.Rectangle(((i%square)-0.5,int(i/square)-0.5), 1, 1, hatch='////', fill=False, snap=False))

        # Don't count forced predictors in the currentCount array and plot hatched areas over them in graph 2
        for i, forceFlag in enumerate(self.predictorForceFlags):
            if forceFlag:
                self.axes1.text(i%square-0.4, int(i/square)+0.4, 'F', fontweight='bold', horizontalalignment='left', verticalalignment='bottom', fontfamily='consolas', color='w')
                self.currentCount[int(i/square), i%square] = np.nan
                self.axes2.add_patch(patches.Rectangle(((i%square)-0.5,int(i/square)-0.5), 1, 1, hatch='**', fill=True, snap=False, facecolor='g'))
                
                self.axes2.text(i%square-0.4, int(i/square)+0.4, 'F', fontweight='bold', horizontalalignment='left', verticalalignment='bottom', fontfamily='consolas', color='k')
                self.axes2.text(i%square-0.42, int(i/square)+0.42, 'F', fontweight='bold', horizontalalignment='left', verticalalignment='bottom', fontfamily='consolas', color='r')
                self.axes2.text(i%square-0.44, int(i/square)+0.44, 'F', fontweight='bold', horizontalalignment='left', verticalalignment='bottom', fontfamily='consolas', color='w')


        # Plot the current status
        self.pixels1 = self.axes1.imshow(self.currentStatus, interpolation='nearest', cmap='binary', vmax=1)
        self.pixels2 = self.axes2.imshow(self.currentCount, interpolation='nearest', cmap='binary', vmax=1)

        # Set the major grid
        self.axes1.xaxis.set_ticks(np.arange(-0.5, self.numRows+0.5, 1))
        self.axes1.yaxis.set_ticks(np.arange(-0.5, self.numCols+0.5, 1))
        self.axes2.xaxis.set_ticks(np.arange(-0.5, self.numRows+0.5, 1))
        self.axes2.yaxis.set_ticks(np.arange(-0.5, self.numCols+0.5, 1))

        # Draw the plot
        self.draw()

        return

    def updateGrid(self, currentModel = None):
        """
        """

        for i, p in enumerate(currentModel):
            if self.predictorForceFlags[i] == True:
                self.currentStatus[int(i/self.numRows), i%self.numCols] = 0.5
            elif p==1:
                self.currentStatus[int(i/self.numRows), i%self.numCols] = 1
                self.currentCount[int(i/self.numRows), i%self.numCols] += 1
            else:
                self.currentStatus[int(i/self.numRows), i%self.numCols] = 0
        
        self.pixels1.set_data(self.currentStatus)
        self.pixels2.set_clim(vmax = np.nanmax(self.currentCount), vmin = np.nanmin(self.currentCount))
        self.pixels2.set_data(self.currentCount)

        self.draw()

        return


class ModelCreationTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self)

        self.grid = PredictorCurrentGraph(parent=self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.grid)
        self.button = QtWidgets.QPushButton("Run")
        self.button.pressed.connect(self.run1)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.qtimer = QtCore.QTimer()
        self.qtimer.setInterval(5)
        self.qtimer.timeout.connect(self.run1)
        self.qtimer.start()
        self.show()        
        
        return

    def run1(self, dummy=None):

        c = np.random.randint(0,2,len(self.grid.predictorPool))
        self.grid.updateGrid(c)
            
    
if __name__ == '__main__':
    import sys
    import os
    import pandas as pd

    app = QtWidgets.QApplication(sys.argv)


    modelRunsTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ModelRunID'),
            columns = [
                "ModelTrainingPeriod",  # E.g. 1978-10-01/2019-09-30 (model trained on  WY1979-WY2019 data)
                "ForecastIssueDate",    # E.g. January 13th
                "Predictand",           # E.g. 100302 (datasetInternalID)
                "PredictandPeriod",     # E.g. R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",     # E.g. Accumulation, Average, Max, etc
                "PredictorGroups",      # E.g. ["SNOTEL SITES", "CLIMATE INDICES", ...]
                "PredictorGroupMapping",# E.g. [0, 0, 0, 1, 4, 2, 1, 3, ...] maps each predictor in the pool to a predictor group
                "PredictorPool",        # E.g. [100204, 100101, ...]
                "PredictorForceFlag",   # E.g. [False, False, True, ...]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, ...]
                "PredictorMethods",     # E.g. ['Accumulation', 'First', 'Last', ...]
                "RegressionTypes",      # E.g. ['Regr_MultipleLinearRegression', 'Regr_ZScoreRegression']
                "CrossValidationType",  # E.g. K-Fold (10 folds)
                "FeatureSelectionTypes",# E.g. ['FeatSel_SequentialFloatingSelection', 'FeatSel_GeneticAlgorithm']
                "ScoringParameters",    # E.g. ['ADJ_R2', 'MSE']
                "Preprocessors"         # E.g. ['PreProc_Logarithmic', 'PreProc_YAware']
            ]
        )
    
    numPredictors = 13

    modelRunsTable.loc[0] = [
        "",
        "",
        1,
        "",
        "",
        [],
        [],
        [int(10000*np.random.random()) for i in range(numPredictors)],
        [[True, False][1 if np.random.randint(0,11)<9 else 0] for i in range(numPredictors)],
        ["" for i in range(numPredictors)],
        ["" for i in range(numPredictors)],
        [],
        "",
        [],
        [],
        []
    ]

    widg = ModelCreationTab()
    widg.grid.setPredictorGrid(modelRunsTable.loc[0], None)

    sys.exit(app.exec_())