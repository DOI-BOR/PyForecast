import pandas as pd
import numpy as np
import subprocess
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
from matplotlib import gridspec
from statsmodels.tsa.stattools import adfuller
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, QtCore

class matrixCanvas(FigureCanvas):

    # Initialize a graph
    def __init__(self, parent=None, dpi=100):
        self.fig = plt.figure()
        self.fig.patch.set_facecolor("#e8e8e8")
        self.gs = gridspec.GridSpec(1,1)
        self.ax0 = plt.subplot(self.gs[0])
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotMatrix(self, data, exitMenu):
        df = data.copy()
        dataIndex = []
        colCounter = 1
        for ithCol in data:
            dataIndex.append('Var-' + str(colCounter))
            exitAction = QtWidgets.QAction('Var-' + str(colCounter) + ': ' + ithCol.replace('\n', ', ').replace('\r', ''), self)
            exitMenu.addAction(exitAction)
            colCounter = colCounter + 1
        df.columns = dataIndex
        scatter_matrix(df, alpha=0.2, diagonal='kde', ax=self.ax0)
        #plt.savefig("Resources/tempFiles/MatrixPlot{0}.png".format(int(1000*np.random.random(1))))
        self.draw()

class analysisDialog(QtWidgets.QDialog):

    def __init__(self, data):
        super(analysisDialog, self).__init__()
        data = data.dropna()
        data = data.apply(pd.to_numeric)
        self.data = data
        self.setStyleSheet("background-color:white; color:black;")
        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)
        self.setWindowTitle('Data Analysis')
        # Build menu bar
        self.myQMenuBar = QtWidgets.QMenuBar(self)
        self.statsMenu = self.myQMenuBar.addMenu('Data Analysis Options')
        self.statsAction = QtWidgets.QAction('Generate Summary Stats', self)
        self.statsMenu.addAction(self.statsAction)
        self.stationarityAction = QtWidgets.QAction('Run Stationarity Test', self)
        self.statsMenu.addAction(self.stationarityAction)
        self.exitMenu = self.myQMenuBar.addMenu('Variable Descriptions')
        mainLayout.addWidget(self.myQMenuBar)
        # Build scatter-plot
        self.plot = matrixCanvas(self)
        mainLayout.addWidget(self.plot)
        self.plot.plotMatrix(data, self.exitMenu)
        # Add menu actions
        self.statsAction.triggered.connect(self.runSummaryStats)
        self.stationarityAction.triggered.connect(self.runStationarityTest)
        self.exec_()


    def openFile(self, filename):
        try:
            try:
                subprocess.check_call(['cmd','/c','start',filename])
            except Exception as e:
                print(e)
                subprocess.check_call(['open',filename])
        except:
            pass


    def writeDFrame(self, dataFrame, file):
        colHeader = ','
        for ithCol in dataFrame.columns:
            colHeader = colHeader + ithCol.replace('\n', '').replace('\r', '').replace(',','') + ','
        print(colHeader[:-1], file=file)
        for index, row in dataFrame.iterrows():
            rowStr = row.to_csv(header=False, index=False, sep=',').replace('\n', ',').replace('\r', '')
            idxStr = index.replace('\n', '').replace('\r', '').replace(',','') + ','
            print(idxStr + rowStr, file=file)


    def runSummaryStats(self):
        print('Calculating summary stats...')
        filename = "Resources/tempFiles/tmp{0}.csv".format(datetime.now().timestamp())
        file = open(filename, "w")
        # summary stats
        print('', file=file)
        print('SUMMARY STATISTICS', file=file)
        df = self.data.describe()
        self.writeDFrame(df, file)
        # correlation
        print('', file=file)
        print('CORRELATION MATRIX', file=file)
        df = self.data.corr()
        self.writeDFrame(df, file)
        file.close()
        self.openFile(filename)


    def runStationarityTest(self):
        print('Running stationarity test...')
        df = self.data.copy()

        filename = "Resources/tempFiles/tmp{0}.csv".format(datetime.now().timestamp())
        file = open(filename, "w")
        file.write('Dataset,ADF-Statistic,P-Value,nLags,nObservations,Critical-Value-1%,Critical-Value-5%,Critical-Value-10%,Stationarity@1%,Stationarity@5%,Stationarity@10%,\n')

        # Perform Augmented-Dickey-Fuller (ADF) TEST
        # https://machinelearningmastery.com/time-series-data-stationary-python/
        for ithCol in df:
            dSetName = ithCol.replace('\n', '; ').replace('\r', '').replace(',','')
            series = df.loc[:,ithCol]
            # Clean-up data
            X = series.values
            X = X[~np.isnan(X)]#remove nans
            if X.min() <= 0:#shift data for log transform
                X = X + (X.min() * -1) + 0.1
            X = np.log(X) #log-transform data
            result = adfuller(X)
            critVals = ''
            stationarityVals = ''
            for key, value in result[4].items():
                critVals = critVals + '%s: %.5f' % (key, value) + ','
                if result[0] < value:
                    stationarityVals = stationarityVals + 'Stationary at ' + '%s' % (key) + ','
                else:
                    stationarityVals = stationarityVals + 'Non-Stationary at ' + '%s' % (key) + ','
            file.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(
                dSetName,
                '%.5f' % (result[0]),
                result[1],
                result[2],
                result[3],
                critVals[:-1],
                stationarityVals[:-1]
            ))
        file.close()
        self.openFile(filename)
