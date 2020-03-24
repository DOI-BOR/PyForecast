"""
Script Name:        ModelCreationTab.py

Description:        'ModelCreationTab.py' is a PyQt5 GUI for the PyForecast application. 
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
from matplotlib.colors import ListedColormap
matplotlib.use('Qt5Agg')
from matplotlib import patches
import matplotlib.pyplot as plt
plt.ion()


class PredictorCurrentGraph(FigureCanvas):
    
    def __init__(self, parent=None, width=8, height=8, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = self.fig.add_subplot(211)
        self.axes1.grid(which='major', lw=2, color='k')
        self.axes1.tick_params(labelbottom=False, direction='in', labelleft=False)
        self.axes1.set_title("Current Model", loc='left', fontsize=9, fontfamily='consolas')
        self.axes2 = self.fig.add_subplot(212)
        self.axes2.grid(which='major', lw=2, color='k')
        self.axes2.tick_params(labelbottom=False, direction='in', labelleft=False)
        self.axes2.set_title("All Models", loc='left', fontsize=9, fontfamily='consolas')

        # Colormaps
        self.axes1_colormap = ListedColormap(["white", "black"])

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.draw()

        # Create legend elements
        self.legendElements1 = [patches.Patch(edgecolor='k', facecolor='k', label="On"),patches.Patch(edgecolor='k', facecolor='w', label="Off"), patches.Patch(hatch="**", edgecolor='k', facecolor='grey', label="Forced On")]
        self.legendElements2 = [patches.Patch(edgecolor='k', facecolor='w', label="Unused"),patches.Patch(edgecolor='k', facecolor='k', label="Very used"), patches.Patch(hatch="**", edgecolor='k', facecolor='grey', label="Forced On")]
        self.axes1.legend(handles=self.legendElements1, handlelength=1, handleheight=1, fancybox=False, loc="upper left", bbox_to_anchor=(1,1), frameon=False)
        self.axes2.legend(handles=self.legendElements2, handlelength=1, handleheight=1, fancybox=False, loc="upper left", bbox_to_anchor=(1,1), frameon=False)

        # Create an annotation to display predictor properties
        self.annot = self.axes1.annotate("", xy=(1,0), xycoords='axes fraction')
        self.annot2 = self.axes2.annotate("", xy=(1,0), xycoords='axes fraction')

        # Create a hover box
        self.hoverBox = patches.Rectangle((0,0), 1, 1, linewidth=4, edgecolor='r', fill=False, zorder=1000)
        self.hoverBox.set_alpha(0)
        self.axes1.add_patch(self.hoverBox)

        self.hoverBox2 = patches.Rectangle((0,0), 1, 1, linewidth=4, edgecolor='r', fill=False, zorder=1000)
        self.hoverBox2.set_alpha(0)
        self.axes2.add_patch(self.hoverBox2)

        self.mpl_connect("motion_notify_event", self.hover)
        self.frameBuffer = 0

        return


    def hover(self, event):

        if event.inaxes == self.axes1:

            #row = event.ydata
            #col = event.xdata

            row, col = list(map(lambda x: int(round(x)), [event.ydata, event.xdata]))

            predictor = self.pixelsToPredictors[row, col]

            if np.isnan(predictor):
                self.annot.set_text('')
                self.hoverBox.set_alpha(0)

                return

            predictorIdx = self.predictorPool.index(predictor)
            period = self.predictorPeriods[predictorIdx]

            self.annot.set_text(""" Predictor: {0}\n Period: {1}\n Method: {2}""".format(int(predictor), "4-Month", "Average"))
            self.hoverBox.set_alpha(1)
            self.hoverBox.set_xy((col-0.5, row-0.5))

            predictorIdx = self.predictorPool.index(predictor)
            period = self.predictorPeriods[predictorIdx]
            count = self.currentCount[row, col] 

            self.annot2.set_text(""" Predictor: {0}\n Count: {1}""".format(int(predictor), int(count) if not np.isnan(count) else "Forced"))
            self.hoverBox2.set_alpha(1)
            self.hoverBox2.set_xy((col-0.5, row-0.5))


        elif event.inaxes == self.axes2:

            row, col = list(map(lambda x: int(round(x)), [event.ydata, event.xdata]))

            predictor = self.pixelsToPredictors[row, col]

            if np.isnan(predictor):
                self.annot2.set_text('')
                self.hoverBox2.set_alpha(0)

                return

            predictorIdx = self.predictorPool.index(predictor)
            period = self.predictorPeriods[predictorIdx]
            count = self.currentCount[row, col]

            self.annot2.set_text(""" Predictor: {0}\n Count: {1}""".format(int(predictor), int(count) if not np.isnan(count) else "Forced"))
            self.hoverBox2.set_alpha(1)
            self.hoverBox2.set_xy((col-0.5, row-0.5))

            predictorIdx = self.predictorPool.index(predictor)
            period = self.predictorPeriods[predictorIdx]

            self.annot.set_text(""" Predictor: {0}\n Period: {1}\n Method: {2}""".format(int(predictor), "4-Month", "Average"))
            self.hoverBox.set_alpha(1)
            self.hoverBox.set_xy((col-0.5, row-0.5))


            pass
            
        self.draw()
        #self.parent().repaint()

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

                # Hatched areas and text for plot 1
                self.axes1.text(i%square-0.4, int(i/square)+0.4, 'F', fontweight='bold', horizontalalignment='left', verticalalignment='bottom', fontfamily='consolas', color='w')
                self.axes1.add_patch(patches.Rectangle(((i%square)-0.5,int(i/square)-0.5), 1, 1, hatch='**', fill=True, snap=False, facecolor='grey'))

                # Hatched areas and text for plot 2
                self.currentCount[int(i/square), i%square] = np.nan
                self.axes2.add_patch(patches.Rectangle(((i%square)-0.5,int(i/square)-0.5), 1, 1, hatch='**', fill=True, snap=False, facecolor='grey'))
                self.axes2.text(i%square-0.44, int(i/square)+0.44, 'F', fontweight='bold', horizontalalignment='left', verticalalignment='bottom', fontfamily='consolas', color='w')

        # Plot the current status
        self.pixels1 = self.axes1.imshow(self.currentStatus, interpolation='nearest', cmap=self.axes1_colormap, vmax=1)
        self.pixels2 = self.axes2.imshow(self.currentCount, interpolation='nearest', cmap='Greys', vmax=1)

        # Set the major grid
        self.axes1.xaxis.set_ticks(np.arange(-0.5, self.numRows+0.5, 1))
        self.axes1.yaxis.set_ticks(np.arange(-0.5, self.numCols+0.5, 1))
        self.axes2.xaxis.set_ticks(np.arange(-0.5, self.numRows+0.5, 1))
        self.axes2.yaxis.set_ticks(np.arange(-0.5, self.numCols+0.5, 1))

        # Draw the plot
        self.draw()
        #self.parent().repaint()

        return

    def updateGrid(self, currentModel = None, lastStatus=None):
        """
        """
        if self.frameBuffer != 100 and not lastStatus:
            self.frameBuffer += 1
            return
        else:
            self.frameBuffer = 0

        for i, p in enumerate(currentModel):
            if self.predictorForceFlags[i] == True:
                self.currentStatus[int(i/self.numRows), i%self.numCols] = 0
            elif p==1:
                self.currentStatus[int(i/self.numRows), i%self.numCols] = 1
                self.currentCount[int(i/self.numRows), i%self.numCols] += 1
            else:
                self.currentStatus[int(i/self.numRows), i%self.numCols] = 0
        
        self.pixels1.set_data(self.currentStatus)
        self.pixels2.set_clim(vmax = np.nanmax(self.currentCount), vmin = np.nanmin(self.currentCount))
        self.pixels2.set_data(self.currentCount)
        
        self.draw()
        self.parent().repaint()

        return

class ModelCreationTab_(QtWidgets.QWidget):
    """
    This class defines the GUI layout of the Model Creation Tab
    """

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)

        # Create a few layouts that we'll end up using
        self.overallLayout = QtWidgets.QHBoxLayout()
        self.leftPaneLayout = QtWidgets.QVBoxLayout()
        self.rightPaneLayout = QtWidgets.QVBoxLayout()
        self.genStatusLayout = QtWidgets.QHBoxLayout()

        # Build the Left Pane Layout
        title = QtWidgets.QLabel('<b style="font-size: 17px">Generate Models</b>')
        title.setTextFormat(QtCore.Qt.RichText)

        # Settings Radio selection
        self.settingsLoadPreviousRadio = QtWidgets.QRadioButton("Load previous settings", self)
        self.settingsLoadPreviousDropDown = QtWidgets.QComboBox()
        self.settingsNewSettingsRadio = QtWidgets.QRadioButton("Specify new settings", self)
        
        # Separator
        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)

        # Settings Specification
        fcstTargetLabel = QtWidgets.QLabel("Forecast Target")
        self.fcstTargetDropDown = QtWidgets.QComboBox()
        fcstPeriodLabel = QtWidgets.QLabel("Forecast Period")
        self.fcstPeriodStart = QtWidgets.QDateTimeEdit()
        self.fcstPeriodStart.setCalendarPopup(True)
        self.fcstPeriodStart.setDisplayFormat("MMMM d")
        currentDate = QtCore.QDate.currentDate()
        self.fcstPeriodStart.setMinimumDate(QtCore.QDate(currentDate.year(), 1, 1))
        self.fcstPeriodStart.setMaximumDate(QtCore.QDate(currentDate.year(), 12, 31))
        self.fcstPeriodEnd = QtWidgets.QDateTimeEdit()
        self.fcstPeriodEnd.setCalendarPopup(True)
        self.fcstPeriodEnd.setDisplayFormat("MMMM d")
        self.fcstPeriodEnd.setMinimumDate(QtCore.QDate(currentDate.year(), 1, 1))
        self.fcstPeriodEnd.setMaximumDate(QtCore.QDate(currentDate.year(), 12, 31))
        fcstMethodLabel = QtWidgets.QLabel("Resampling Method")
        self.fcstResampleMethod = QtWidgets.QComboBox()
        predictorsLabel = QtWidgets.QLabel("Predictors")
        self.predictorSpecButton = QtWidgets.QPushButton("Specify Predictors")
        preprocessorsLabel = QtWidgets.QLabel("Preprocessors")
        self.preprocGroup = QtWidgets.QButtonGroup()
        self.preprocGroup.setExclusive(False)
        self.NoPreProcButton = QtWidgets.QCheckBox("No Preprocessing")
        self.LogYButton = QtWidgets.QCheckBox("Logarithmic Y Preprocessing")
        self.LogXButton = QtWidgets.QCheckBox("Logarithmic X Preprocessing")
        self.MinMaxButton = QtWidgets.QCheckBox("Min / Max Preprocessing")
        self.YAwareButton = QtWidgets.QCheckBox("Y-Aware Preprocessing")
        self.preprocGroup.addButton(self.NoPreProcButton)
        self.preprocGroup.addButton(self.LogYButton)
        self.preprocGroup.addButton(self.LogXButton)
        self.preprocGroup.addButton(self.MinMaxButton)
        self.preprocGroup.addButton(self.YAwareButton)
        featureSelectionLabel = QtWidgets.QLabel("Feature Selection")
        self.featSelGroup = QtWidgets.QButtonGroup()
        self.featSelGroup.setExclusive(False)
        self.SFFSButton = QtWidgets.QCheckBox("Sequential Forward")
        self.SBFSButton = QtWidgets.QCheckBox("Sequential Backward")
        self.GeneticButton = QtWidgets.QCheckBox("Genetic Algorithm")
        self.BruteForceButton = QtWidgets.QCheckBox("Brute Force")
        self.featSelGroup.addButton(self.SFFSButton, 1)
        self.featSelGroup.addButton(self.SFFSButton, 2)
        self.featSelGroup.addButton(self.GeneticButton, 3)
        self.featSelGroup.addButton(self.BruteForceButton, 4)

        # Layout the left side pane
        self.leftPaneLayout.addWidget(title)
        self.leftPaneLayout.addWidget(self.settingsLoadPreviousRadio)
        self.leftPaneLayout.addWidget(self.settingsLoadPreviousDropDown)
        self.leftPaneLayout.addWidget(self.settingsNewSettingsRadio)
        self.leftPaneLayout.addWidget(hline)
        self.leftPaneLayout.addWidget(fcstTargetLabel)
        self.leftPaneLayout.addWidget(self.fcstTargetDropDown)
        self.leftPaneLayout.addWidget(fcstPeriodLabel)
        self.leftPaneLayout.addWidget(self.fcstPeriodStart)
        self.leftPaneLayout.addWidget(self.fcstPeriodEnd)
        self.leftPaneLayout.addWidget(fcstMethodLabel)
        self.leftPaneLayout.addWidget(self.fcstResampleMethod)
        self.leftPaneLayout.addWidget(predictorsLabel)
        self.leftPaneLayout.addWidget(self.predictorSpecButton)
        self.leftPaneLayout.addWidget(featureSelectionLabel)
        self.leftPaneLayout.addWidget(self.SFFSButton)
        self.leftPaneLayout.addWidget(self.SBFSButton)
        self.leftPaneLayout.addWidget(self.GeneticButton)
        self.leftPaneLayout.addWidget(self.BruteForceButton)
        self.leftPaneLayout.addWidget(preprocessorsLabel)
        self.leftPaneLayout.addWidget(self.NoPreProcButton)
        self.leftPaneLayout.addWidget(self.LogYButton)
        self.leftPaneLayout.addWidget(self.LogXButton)
        self.leftPaneLayout.addWidget(self.MinMaxButton)
        self.leftPaneLayout.addWidget(self.YAwareButton)

        # Set the widget layout
        self.setLayout(self.leftPaneLayout)

        self.show()

class ModelCreationTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self)

        self.grid = PredictorCurrentGraph(parent=self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.grid)
        self.button = QtWidgets.QPushButton("Run")
        
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.qtimer = QtCore.QTimer()
        self.qtimer.setInterval(5)
        self.qtimer.timeout.connect(self.run1)
        self.button.pressed.connect(self.qtimer.start)
        
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
    
    numPredictors = 32

    modelRunsTable.loc[0] = [
        "",
        "",
        1,
        "",
        "",
        [],
        [],
        [int(10000*np.random.random()) for i in range(numPredictors)],
        [[True, False][1 if np.random.randint(0,11)<10 else 0] for i in range(numPredictors)],
        ["SFEFSF" for i in range(numPredictors)],
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