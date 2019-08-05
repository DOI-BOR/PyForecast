import pandas as pd
import numpy as np
import subprocess
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
from matplotlib import gridspec
from statsmodels.tsa.stattools import adfuller
import statsmodels.imputation.mice as mice
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

    def plotMatrix(self, data, exitMenu = False):
        self.fig.suptitle("Data Correlation Matrix")
        df = data.copy()
        dataIndex = []
        colCounter = 1
        for ithCol in data:
            dataIndex.append('Var-' + str(colCounter))
            exitAction = QtWidgets.QAction('Var-' + str(colCounter) + ': ' + ithCol.replace('\n', ', ').replace('\r', ''), self)
            if exitMenu:
                exitMenu.addAction(exitAction)
            colCounter = colCounter + 1
        df.columns = dataIndex
        scatter_matrix(df, alpha=0.2, diagonal='kde', ax=self.ax0)
        #plt.savefig("Resources/tempFiles/MatrixPlot{0}.png".format(int(1000*np.random.random(1))))
        self.draw()


class missingCanvas(FigureCanvas):

    # Initialize a graph
    def __init__(self, parent=None, dpi=100):
        self.fig = plt.figure(figsize=(14, 12))
        self.fig.patch.set_facecolor("#e8e8e8")
        self.gs = gridspec.GridSpec(1, 1)
        self.ax0 = plt.subplot(self.gs[0])
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotMissing(self, data, exitMenu = False):
        self.fig.suptitle("Missing Data Visualization")
        color = (0.04, 0.52, 0.80)
        z = data.notnull().values
        g = np.zeros((data.shape[0], data.shape[1], 3))
        g[z < 0.5] = [1, 1, 1]
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
        dataIndex = []
        colCounter = 1
        for ithCol in data:
            dataIndex.append('Var-' + str(colCounter))
            exitAction = QtWidgets.QAction('Var-' + str(colCounter) + ': ' + ithCol.replace('\n', ', ').replace('\r', ''), self)
            if exitMenu:
                exitMenu.addAction(exitAction)
            colCounter = colCounter + 1
        fontsize = 10
        self.ax0.set_xticklabels(dataIndex, wrap=True, ha=ha, fontsize=fontsize)
        if data.shape[0] > 7000:
            freq = '12MS'
        else:
            freq = '6MS'

        in_between = [x + 0.5 for x in range(0, data.shape[1] - 1)]
        for point in in_between:
            self.ax0.axvline(point, linestyle='-', color='white')
        ts_array = pd.date_range(data.index.date[0], data.index.date[-1], freq=freq).values
        ts_ticks = pd.date_range(data.index.date[0], data.index.date[-1], freq=freq).map(
            lambda t: t.strftime('%Y-%m-%d'))
        ts_list = []
        try:
            for value in ts_array:
                ts_list.append(data.index.get_loc(value))
        except:
            print('erorr...')
        self.ax0.set_yticks(ts_list)
        self.ax0.set_yticklabels(ts_ticks, fontsize=9, rotation=0)
        plt.tight_layout(rect=[0, 0, 1, 0.9])
        self.draw()


class imputationCanvas(FigureCanvas):

    # Initialize a graph
    def __init__(self, parent=None, dpi=100):
        self.fig = plt.figure()
        self.fig.patch.set_facecolor("#e8e8e8")
        self.gs = gridspec.GridSpec(2,2)
        self.ax0 = plt.subplot(self.gs[0])
        self.ax0.title.set_text('Time-Series Graph')
        self.ax1 = plt.subplot(self.gs[1])
        self.ax1.title.set_text('Distribution Difference')
        self.ax2 = plt.subplot(self.gs[2])
        self.ax2.title.set_text('Density Difference')
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotResult(self, rawData, filledData):
        filledPoints = filledData[rawData.isnull()]
        self.fig.suptitle("Data Imputation Results")
        # time-series lineplot
        rawData.plot(ax=self.ax0, color='dodgerblue', label='Raw Dataset')
        filledPoints.plot(ax=self.ax0, linestyle = 'None', color='tomato', markerfacecolor='none', marker='o', label='Imputed Data-Points')
        self.ax0.legend(loc='best')
        # distribution boxplots
        df = pd.concat([rawData, filledPoints, filledData], axis=1)
        df.columns = ['Raw Dataset', 'Imputed Data-Points','Filled Dataset']
        bplot = df.boxplot(ax=self.ax1, patch_artist=True, return_type=None, notch=True)#, color=color)
        bplot.findobj(matplotlib.patches.Patch)[0].set_facecolor("dodgerblue")
        bplot.findobj(matplotlib.patches.Patch)[1].set_facecolor("tomato")
        bplot.findobj(matplotlib.patches.Patch)[2].set_facecolor("gray")
        # distribution density plots
        rawData.plot(ax=self.ax2, kind='density', color='dodgerblue', label='Raw Dataset')
        filledPoints.plot(ax=self.ax2, kind='density', color='tomato', label='Imputed Data-Points')
        filledData.plot(ax=self.ax2, kind='density', color='gray', label='Filled Dataset')
        self.ax2.legend(loc='best')



        self.draw()


class analysisDialog(QtWidgets.QDialog):

    def __init__(self, data):
        super(analysisDialog, self).__init__()
        data = data.apply(pd.to_numeric)
        self.rawdata = data
        #data = data.replace([np.inf, -np.inf], np.nan).dropna()
        #self.data = data
        self.setStyleSheet("background-color:white; color:black;")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinMaxButtonsHint)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle('Data Analysis')
        # Build menu bar
        self.myQMenuBar = QtWidgets.QMenuBar(self)
        self.statsMenu = self.myQMenuBar.addMenu('Data Analysis Options')
        self.corrMatrixAction = QtWidgets.QAction('Show Correlation Matrix', self)
        self.statsMenu.addAction(self.corrMatrixAction)
        self.missingAction = QtWidgets.QAction('Show Missing', self)
        self.statsMenu.addAction(self.missingAction)
        self.statsAction = QtWidgets.QAction('Generate Summary Stats', self)
        self.statsMenu.addAction(self.statsAction)
        self.stationarityAction = QtWidgets.QAction('Run Stationarity Test', self)
        self.statsMenu.addAction(self.stationarityAction)
        self.imputationAction = QtWidgets.QAction('Fill Missing Data', self)
        self.statsMenu.addAction(self.imputationAction)
        self.exitMenu = self.myQMenuBar.addMenu('Variable Descriptions')
        self.mainLayout.addWidget(self.myQMenuBar)
        # Build scatter-plot
        self.plot = missingCanvas(self)
        self.mainLayout.addWidget(self.plot)
        self.plot.plotMissing(self.rawdata, self.exitMenu)
        self.setWindowTitle('Data Analysis - Missing Data Plot')
        # Add menu actions
        self.statsAction.triggered.connect(self.runSummaryStats)
        self.stationarityAction.triggered.connect(self.runStationarityTest)
        self.missingAction.triggered.connect(self.showMissingData)
        self.corrMatrixAction.triggered.connect(self.showCorrMatrix)
        self.imputationAction.triggered.connect(self.runDataImputation)
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


    def showCorrMatrix(self):
        self.setWindowTitle('Data Analysis - Rendering Correlation Matrix...')
        self.mainLayout.removeWidget(self.plot)
        self.plot = matrixCanvas(self)
        self.mainLayout.addWidget(self.plot)
        self.plot.plotMatrix(self.rawdata)
        self.setWindowTitle('Data Analysis - Correlation Matrix')


    def showMissingData(self):
        self.setWindowTitle('Data Analysis - Rendering Missing Data Plot...')
        self.mainLayout.removeWidget(self.plot)
        self.plot = missingCanvas(self)
        self.mainLayout.addWidget(self.plot)
        self.plot.plotMissing(self.rawdata)
        self.setWindowTitle('Data Analysis - Missing Data Plot')


    def showImputationResult(self, imputationCol):
        self.setWindowTitle('Data Analysis - Rendering Imputation Results...')
        filled = self.imputedData[imputationCol]
        raw = self.imputeeData[imputationCol]

        # TODO: Visualize/QA/QC/Accept/Reject imputation results
        self.mainLayout.removeWidget(self.plot)
        self.plot = imputationCanvas(self)
        self.mainLayout.addWidget(self.plot)
        self.plot.plotResult(raw, filled)
        self.setWindowTitle('Data Analysis - Imputation Results - ' + imputationCol)

        a = 1


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
        df = self.rawdata.describe()
        self.writeDFrame(df, file)
        # correlation
        print('', file=file)
        print('CORRELATION MATRIX', file=file)
        df = self.rawdata.corr()
        self.writeDFrame(df, file)
        file.close()
        self.openFile(filename)


    def runStationarityTest(self):
        print('Running stationarity test...')
        df = self.rawdata.copy()

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


    def runDataImputation(self):
        df = self.rawdata.copy()
        df = df.apply(pd.to_numeric)

        # Rename column index statsmodels imputation does not like wierd column names
        impIndex = []
        origIndex = []
        colCounter = 1
        for ithCol in df:
            impIndex.append('Var' + str(colCounter))
            origIndex.append(ithCol.replace('\n', ', ').replace('\r', ''))
            colCounter = colCounter + 1
        df.columns = impIndex

        # Get columns with nans
        naSums = df.isnull().sum()
        naCols = naSums[naSums > 0]
        if len(naCols) < 1: #don't run imputation if there are no missing data
            QtWidgets.QMessageBox.question(self, 'Info', 'There are no missing data points to fill in...', QtWidgets.QMessageBox.Ok)
            return
        datetimeIdx = df.index
        self.imputeeData = df[naCols.index]

        # Run imputation
        imp = mice.MICEData(df)
        #print(df.isna().sum())
        imp.update_all()
        #print(imp.data.isna().sum())

        # Get columns with filled-in nans
        self.imputedData = imp.data[naCols.index]
        self.imputedData.set_index(datetimeIdx, inplace=True)

        # Append results to menu-bar
        if hasattr(self, 'imputationMenu'):
            self.imputationMenu.clear()
        else:
            self.imputationMenu = self.myQMenuBar.addMenu('Data Imputation Results')
        for ithCol in self.imputedData:
            ithImputationAction = QtWidgets.QAction(ithCol, self)
            ithImputationAction.triggered.connect(lambda checked, item=ithCol: self.showImputationResult(item))
            self.imputationMenu.addAction(ithImputationAction)

        df.columns = origIndex
