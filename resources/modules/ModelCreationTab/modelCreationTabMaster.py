from datetime import datetime, timedelta
from resources.modules.Miscellaneous import loggingAndErrors
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd
import numpy as np
import datetime
from itertools import compress
from dateutil import parser

from resources.modules.ModelCreationTab import RegressionWorker
from resources.modules.ModelCreationTab.Operations.Fill import fill_missing
from resources.modules.ModelCreationTab.Operations.Extend import extend
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
from resources.modules.Miscellaneous.generateModel import Model

from resources.GUI.CustomWidgets.PyQtGraphs import WindowTabPlots, ModelTabTargetPlot

class modelCreationTab(object):
    """
    STATISTICAL MODELS TAB
    The Statistical Models Tab contains tools for creating
    new statistical models (i.e. forecast equations). 
    """

    def initializeModelCreationTab(self):
        """
        Initialize the Tab
        """
        self.connectEventsModelCreationTab()
        self.modelTab.defButton.setChecked(True)

        return

    def resetModelCreationTab(self):
        self.modelTab.summaryListWidget.clearTable()
        self.modelTab.summaryListWidget.model().loadDataIntoModel(self.datasetTable, self.datasetOperationsTable)
        for idx, rows in self.datasetOperationsTable.iterrows():
            dsetRow = self.datasetTable.loc[idx[0]]
            self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.loc[(idx[0], idx[1]), list(self.datasetTable.columns)] = list(dsetRow)

        # Set the expert doublelist
        self.modelTab.layoutDataDoubleList.updateLinkedOperationsTables()

        # Update the simple double list
        self.modelTab.layoutSimpleDoubleList.listOutput.itemColors = [QtCore.Qt.white for x in self.datasetOperationsTable.iterrows()]
        for idx, rows in self.datasetOperationsTable.iterrows():
            if self.datasetOperationsTable.loc[idx]['AccumulationMethod'] == 'None' or \
               self.datasetOperationsTable.loc[idx]['AccumulationPeriod'] == 'None' or \
               self.datasetOperationsTable.loc[idx]['ForcingFlag'] == 'None':
                self.modelTab.layoutSimpleDoubleList.listOutput.itemColors[idx] = QtCore.Qt.darkGray

        self.modelTab.layoutSimpleDoubleList.listInput.refreshDatasetList()
        self.modelTab.layoutSimpleDoubleList.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.modelTab.layoutSimpleDoubleList.updatedLinkedList.emit(self.modelTab.layoutSimpleDoubleList.listInput, self.modelTab.layoutSimpleDoubleList.listOutput)
        self.modelTab.layoutSimpleDoubleList.updatedOutputList.emit()

        self.modelTab.resultsMetricTable.clearTable()
        self.modelTab.resultsMetricTable.loadDataIntoModel(self.forecastEquationsTable)

        # Set model-creation tab inputs only once on forecast-file load
        modelRunEntry = self.modelRunsTable
        if len(modelRunEntry.index) == 1 and not hasattr(self.modelTab,'initialized'):
            self.modelTab.initialized = True
            self.modelTab.expertButton.setChecked(True)
            runStartYr = modelRunEntry['ModelTrainingPeriod'][0].split('/')[0]
            runEndYr = modelRunEntry['ModelTrainingPeriod'][0].split('/')[1]
            runExcludeYr = modelRunEntry['ModelTrainingPeriod'][0].split('/')[2]
            runPredictand = modelRunEntry['Predictand'][0]
            runPredictandT1 = datetime.datetime.strptime(modelRunEntry['PredictandPeriod'][0].split('/')[1], '%Y-%m-%d')
            runPredictandT2Offset = modelRunEntry['PredictandPeriod'][0].split('/')[2][1:len(modelRunEntry['PredictandPeriod'][0].split('/')[2])-1]
            runPredictandT2 = runPredictandT1 + datetime.timedelta(days=int(runPredictandT2Offset))
            runPredictandMethod = modelRunEntry['PredictandMethod'][0]
            runCV = modelRunEntry['CrossValidationType'][0]
            runPreproc = modelRunEntry['Preprocessors'][0]
            runRegressions = modelRunEntry['RegressionTypes'][0]
            runFeatSel = modelRunEntry['FeatureSelectionTypes'][0]
            runScorer = modelRunEntry['ScoringParameters'][0]

            # Set predictand
            predIdx = 0
            for i in range(self.modelTab.targetSelect.count()):
                if runPredictand == self.modelTab.targetSelect.itemData(i).name:
                    predIdx = i
            self.modelTab.targetSelect.setCurrentIndex(predIdx)
            # Set aggregation scheme
            aggIdx = self.modelTab.methodCombo.findData(runPredictandMethod)
            self.modelTab.methodCombo.setCurrentIndex(aggIdx)
            # Set predictand dates
            self.modelTab.periodStart.setDateTime(
                QtCore.QDateTime(QtCore.QDate().currentDate().year(), runPredictandT1.month, runPredictandT1.day, 0, 0))
            self.modelTab.periodEnd.setDateTime(
                QtCore.QDateTime(QtCore.QDate().currentDate().year(), runPredictandT2.month, runPredictandT2.day, 0, 0))
            # Set training period
            self.modelTab.targetPeriodStartYear.setText(runStartYr)
            self.modelTab.targetPeriodEndYear.setText(runEndYr)
            if runExcludeYr != '1900':
                self.modelTab.targetPeriodExcludedYears.setText(runExcludeYr)
            # Set CV algos
            for j in range (len(self.modelTab.optionsCrossValidators)):
                jthReg = self.modelTab.optionsCrossValidators[j].objectName()
                if jthReg in [runCV]:
                    self.modelTab.optionsCrossValidators[j].setChecked(True)
                else:
                    self.modelTab.optionsCrossValidators[j].setChecked(False)
                self.modelTab.optionsCrossValidators[j].clicked_update()
            # Set Pre-Processing algos
            for j in range (len(self.modelTab.optionsPreprocessor)):
                jthReg = self.modelTab.optionsPreprocessor[j].objectName()
                if jthReg in runPreproc:
                    self.modelTab.optionsPreprocessor[j].setChecked(True)
                else:
                    self.modelTab.optionsPreprocessor[j].setChecked(False)
                self.modelTab.optionsPreprocessor[j].clicked_update()
            # Set regression algos
            for j in range (len(self.modelTab.optionsRegression)):
                jthReg = self.modelTab.optionsRegression[j].objectName()
                if jthReg in runRegressions:
                    self.modelTab.optionsRegression[j].setChecked(True)
                else:
                    self.modelTab.optionsRegression[j].setChecked(False)
                self.modelTab.optionsRegression[j].clicked_update()
            # Set Feature Selection algos
            for j in range (len(self.modelTab.optionsSelection)):
                jthReg = self.modelTab.optionsSelection[j].objectName()
                if jthReg in runFeatSel:
                    self.modelTab.optionsSelection[j].setChecked(True)
                else:
                    self.modelTab.optionsSelection[j].setChecked(False)
                self.modelTab.optionsRegression[j].clicked_update()
            # Set Scoring algos
            for j in range (len(self.modelTab.optionsScoring)):
                jthReg = self.modelTab.optionsScoring[j].objectName()
                if jthReg in runScorer:
                    self.modelTab.optionsScoring[j].setChecked(True)
                else:
                    self.modelTab.optionsScoring[j].setChecked(False)
                self.modelTab.optionsScoring[j].clicked_update()


        return


    def connectEventsModelCreationTab(self):
        """
        Connects all the signal/slot events for the model creation tab
        """

        ### Setup page level actions ##
        self.modelTab.datasetList.itemPressed.connect(lambda x: self.modelTab.targetSelect.setCurrentIndex(self.modelTab.datasetList.row(x)))
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.targetSelect.hidePopup())
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.plotTarget() if x >= 0 else None)
        self.modelTab.periodStart.dateChanged.connect(lambda x: self.plotTarget())
        self.modelTab.periodEnd.dateChanged.connect(lambda x: self.plotTarget())
        self.modelTab.methodCombo.currentIndexChanged.connect(lambda x: self.plotTarget())
        self.modelTab.customMethodSpecEdit.editingFinished.connect(self.plotTarget)
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.selectedItemDisplay.setDatasetTable(self.datasetTable.loc[self.modelTab.datasetList.item(x).data(QtCore.Qt.UserRole).name])  if x >= 0 else None)
        #self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.selectedItemDisplay.refreshList())
        self.modelTab.methodCombo.currentIndexChanged.connect(lambda x: self.modelTab.customMethodSpecEdit.show() if self.modelTab.methodCombo.itemData(x) == 'custom' else self.modelTab.customMethodSpecEdit.hide())
        self.modelTab.defButton.toggled.connect(lambda checked: self.updateModelSettings(checked))

        # Create an update method for when the tab widget gets changed to refresh elements
        self.modelTab.workflowWidget.currentChanged.connect(self.updateTabDependencies)

        ### Connect the simple predictor setup page ###
        # Link the doublelist to the output
        self.modelTab.layoutSimpleDoubleList.listOutput.itemSelectionChanged.connect(self.updateSimpleLayoutAggregationOptions)
        self.modelTab.layoutSimpleDoubleList.predictorAdded.connect(self.addPredictorToDatasetOperationTable)
        self.modelTab.layoutSimpleDoubleList.predictorRemoved.connect(self.removePredictorFromDatasetOperationTable)

        # Set the button actions
        self.modelTab.layoutSimplePlotButton.clicked.connect(self.showSimplePlots)
        self.modelTab.predictorPlotButton.clicked.connect(self.switchSimplePlots)
        self.modelTab.layoutSimpleClearButton.clicked.connect(self.applySimpleClear)
        self.modelTab.layoutSimpleApplyButton.clicked.connect(self.applySimpleOptions)

        # Setup the prediction button
        self.modelTab.targetSelect.currentIndexChanged.connect(self.updateTargetInfo)
        self.modelTab.predictandApplyButton.clicked.connect(self.applyPredictandAggregationOption)

        ### Connect the fill page ###
        # Connect the list widget to the right panel to adjust the display
        self.modelTab.fillList.currentRowChanged.connect(self.updateFillOptionsOnDataset)

        # Link the button to the clear function
        self.modelTab.layoutFillClearButton.clicked.connect(self.applyFillClearToDataset)
        self.modelTab.layoutFillClearButton.clicked.connect(self.updateFillSubtab)

        # Link the button to the apply function
        self.modelTab.layoutFillApplyButton.clicked.connect(self.applyFillOptionsToDataset)

        # Connect the stacked widget with the selection combo box
        self.modelTab.layoutFillMethodSelector.currentIndexChanged.connect(self.updateFillSubtab)

        ### Connect the extend page ###
        # Connect the list widget to the right panel to adjust the display
        self.modelTab.extendList.currentRowChanged.connect(self.updateExtendOptionsOnDataset)

        # Connect the methods selector with the update function
        self.modelTab.layoutExtendMethodSelector.currentIndexChanged.connect(self.updateExtendSubtab)

        # Link the button to the clear function
        self.modelTab.layoutExtendClearButton.clicked.connect(self.applyExtendClearToDataset)
        self.modelTab.layoutExtendClearButton.clicked.connect(self.updateExtendSubtab)

        # Connect the stacked widget with the selection combo box
        self.modelTab.layoutExtendMethodSelector.currentIndexChanged.connect(self.updateExtendSubtab)

        # Link the button to the apply function
        self.modelTab.layoutExtendApplyButton.clicked.connect(self.applyExtendOptionsToDataset)

        ### Connect the window page ###
        # Connect the list widget to the right panel to adjust the display
        self.modelTab.windowList.currentRowChanged.connect(self.updateWindowOptionsOnDataset)

        # Connect the plot widgets together with the plotting routines
        self.modelTab.periodStartWindow.dateChanged.connect(self.updateWindowPlot)
        self.modelTab.periodEndWindow.dateChanged.connect(self.updateWindowPlot)

        # Link the button to the clear function
        self.modelTab.layoutWindowClearButton.clicked.connect(self.applyWindowClearToDataset)

        # Link the button to the apply function
        self.modelTab.layoutWindowApplyButton.clicked.connect(self.applyWindowOptionsToDataset)

        # Link the plot group the the switch operation
        self.modelTab.layoutWindowPlottingOptionAggregated.clicked.connect(self.switchWindowStack)
        self.modelTab.layoutWindowPlottingOptionRawCrossCorrelation.clicked.connect(self.switchWindowStack)
        self.modelTab.layoutWindowPlottingOptionAggregatedCrossCorrelation.clicked.connect(self.switchWindowStack)

        ### Connect the summary page ###
        # Connect the clear button to its action function
        self.modelTab.summaryClearButton.clicked.connect(self.applySummaryClear)

        # Connect the start button to its action function
        self.modelTab.summaryStartButton.clicked.connect(self.applySummaryStart)

        ### Connect the results page ###
        self.selectionModel = self.modelTab.resultsMetricTable.view.selectionModel()
        self.selectionModel.selectionChanged.connect(self.generateSelectedModel)
        self.modelTab.resultsMetricTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.modelTab.resultsMetricTable.customContextMenuRequested.connect(self.modelTableRightClick)
        self.modelTab.exportResultModelsButton.clicked.connect(self.generateModelsAnalysis)

        return


    # def changedTabsModelCreationPage(self, index):
    #     """
    #     Handles changing the stacked widget when a user clicks one of the hover
    #     labels on the left side.
    #     """
    #
    #     for i in range(4):
    #         if i != index:
    #             self.modelTab.buttons[i].onDeselect()
    #
    #     return
    #
    #TODO: JR - implement this code into the pred-selection process
    def autoGeneratePredictors(self):
        """
        Generates default predictors based on the input to the
        previous sections.
        """

        # First verify that all the previous sections have been filled in correctly
        # PLACEHOLDERS
        target = None  # DatasetID
        targetPeriodStart = None  # Month-Day combo, e.g.April 1st
        targetPeriodEnd = None  # Month-Day combo e.g. July 31st
        forecastIssueDay = None  # Month-day combo e.g. Feb 01

        # Set up a list to store the suggestions
        suggestedPredictors = []

        # Iterate over the datasetlist and add each predictors default resampling
        # method for the prior period
        for i, dataset in self.datasetTable.iterrows():

            # Pull the default resampling method
            method = dataset['DatasetDefaultResampling']

            # Check dataset parameter, we'll use this to generate the resample period
            if any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['SWE', 'SNOW'])):
                period = 'R/{0}/P1D/F1Y'.format(datetime.strftime(forecastIssueDay - timedelta(days=1), '%Y-%m-%d'))

            elif any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['TEMP', 'INDEX'])):
                period = 'R/{0}/P28D/F1Y'.format(datetime.strftime(forecastIssueDay - timedelta(weeks=4), '%Y-%m-%d'))

            elif any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['PRECIP'])):
                wyStart = datetime(forecastIssueDay.year if forecastIssueDay.month > 10 else forecastIssueDay.year - 1,
                                   10, 1)
                period = 'R/{0}/P{1}D/F1Y'.format(datetime.strftime(wyStart, '%Y-%m-%d'),
                                                  (forecastIssueDay - wyStart).days - 1)

            elif any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['FLOW'])):
                wyStart = datetime(forecastIssueDay.year if forecastIssueDay.month > 10 else forecastIssueDay.year - 1,
                                   10, 1)
                period = 'R/{0}/P1M/F1Y'.format(datetime.strftime(wyStart, '%Y-%m-%d'))

            suggestedPredictors.append((dataset.name, method, period))

            # Add the predictors to the GUI
        return


    # ====================================================================================================================
    # FORECAST TARGET TAB FUNCTIONS
    # <editor-fold desc="Expand Forecast Target tab functions...">
    def updateTargetInfo(self):
        try:
            predictandData = self.modelTab.targetSelect.currentData()
            predID = predictandData.name
            # Get Min dataset date
            minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[0]))
            maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[-1]))
            selT = parser.parse(self.modelTab.periodStart.dateTime().toString("yyyy-MM-ddThh:mm:ss.zzz"))
            self.modelTab.targetPeriodStartYear.setText(str(minT.year))
            self.modelTab.targetPeriodEndYear.setText(str(maxT.year))
        except:
            pass


    def applyPredictandAggregationOption(self):
        # todo: doc string

        self.modelTab.predictandApplyButton.setChecked(False)

        # Ask user if sure
        if len(self.modelRunsTable) > 0:
            msgBox = self.clearAppTablesPrompt(modelRunsTable=True)
            result = msgBox.exec_()
            if result == QtWidgets.QMessageBox.Ok:
                self.clearAppTables(modelRunsTable=True)
            else:
                return

        predictandData = self.modelTab.targetSelect.currentData()
        predID = predictandData.name
        # Get Min dataset date
        minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[0]))
        maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[-1]))
        selT = parser.parse(self.modelTab.periodStart.dateTime().toString("yyyy-MM-ddThh:mm:ss.zzz"))
        if (parser.parse(str(minT.year) + '-'+str(selT.month)+ '-'+str(selT.day))<minT):
            startT = parser.parse(str(minT.year + 1) + '-' + str(selT.month) + '-' + str(selT.day))
        else:
            startT = parser.parse(str(minT.year) + '-' + str(selT.month) + '-' + str(selT.day))

        t1 = self.modelTab.periodStart.date()
        t2 = self.modelTab.periodEnd.date()
        if t1.month() > 9:
            t1 = parser.parse('1900-'+str(t1.month())+ '-'+str(t1.day()))
        else:
            t1 = parser.parse('1901-'+str(t1.month())+ '-'+str(t1.day()))
        t2 = parser.parse('1901-' + str(t2.month()) + '-' + str(t2.day()))
        nDays = (t2-t1).days
        periodString = "R/" + startT.strftime("%Y-%m-%d") + "/P" + str(nDays) + "D/F12M" #(e.g. R/1978-02-01/P1M/F1Y)
        if self.modelRunsTable.shape[0] < 1:
            self.modelRunsTable.loc[0] = [None] * self.modelRunsTable.columns.shape[0]

        #self.modelRunsTable.loc[0]['ModelTrainingPeriod'] = minT.strftime("%Y") + "/" + maxT.strftime("%Y") + "/1900"
        excludedYears = self.modelTab.targetPeriodExcludedYears.text()
        if excludedYears == '':
            excludedYears = '1900'
        startYear = self.modelTab.targetPeriodStartYear.text()
        if startYear == '':
            startYear = minT.strftime("%Y")
            self.modelTab.targetPeriodStartYear.setText(minT.strftime("%Y"))
        endYear = self.modelTab.targetPeriodEndYear.text()
        if endYear == '':
            endYear = maxT.strftime("%Y")
            self.modelTab.targetPeriodEndYear.setText(maxT.strftime("%Y"))
        self.modelRunsTable.loc[0]['ModelTrainingPeriod'] = startYear + "/" + endYear + "/" + excludedYears
        self.modelRunsTable.loc[0]['Predictand'] = predID
        self.modelRunsTable.loc[0]['PredictandPeriod'] = periodString
        self.modelRunsTable.loc[0]['PredictandMethod'] = self.modelTab.methodCombo.currentData()

        # Set the coloration to white
        # self.modelTab.layoutSimpleDoubleList.listOutput.itemColors[self.modelTab.layoutSimpleDoubleList.listOutput.currentIndex().row()] = QtCore.Qt.white


    def plotTarget(self):
        """
        Waits for any changes to the forecast target specification
        and updates the plot accordingly. See the connectEvents function
        to figure out when this function is called.
        """

        # Make sure that the forecast target is an actual dataset
        if self.modelTab.targetSelect.currentIndex() < 0:
            return

        # Get the forecast target's internal ID and dataset
        dataset = self.modelTab.datasetList.item(self.modelTab.targetSelect.currentIndex()).data(QtCore.Qt.UserRole)
        datasetID = dataset.name

        # Get the period string
        t1 = self.modelTab.periodStart.date()
        t2 = self.modelTab.periodEnd.date()
        if t1.month() > 9:
            t1 = parser.parse('1900-' + str(t1.month()) + '-' + str(t1.day()))
        else:
            t1 = parser.parse('1901-' + str(t1.month()) + '-' + str(t1.day()))
        t2 = parser.parse('1901-' + str(t2.month()) + '-' + str(t2.day()))
        nDays = (t2-t1).days
        period = "R/" + self.modelTab.periodStart.date().toString("1900-MM-dd") + "/P" + str(nDays) + "D/F12M"  # (e.g. R/1978-02-01/P1M/F1Y)

        # start = self.modelTab.periodStart.date().toString("1900-MM-dd")
        # start_dt = pd.to_datetime(start)
        # end = self.modelTab.periodEnd.date().toString("1900-MM-dd")
        # end_dt = pd.to_datetime(end)
        # length = (end_dt - start_dt).days
        # period = 'R/{0}/P{1}D/F12M'.format(start, length)

        # Get the forecast method. If the method is 'custom', get the custom method as well
        method = str(self.modelTab.methodCombo.currentData())
        methodText = str(self.modelTab.methodCombo.currentText()).split('(')[0]

        # Get the units
        units = 'KAF' if 'KAF' in method.upper() else dataset['DatasetUnits']

        if method == 'custom':

            # Get the custom function
            function = self.modelTab.customMethodSpecEdit.text()

            # Check if there is a unit
            if '|' in function:
                units = function.split('|')[1].strip()
                function = function.split('|')[0].strip()

            # Make sure the custom function can evaluate
            x = pd.DataFrame(
                np.random.random((10000,1)),
                index = pd.MultiIndex.from_arrays(
                    [pd.date_range(start=t1, periods=10000), 10000*[12013]],
                    names = ['Datetime', 'DatasetInternalID']
                ),
                columns = ['Value']
            )
            x = x.loc[(slice(None), 12013), 'Value']

            try:
                result = eval(function)

            except Exception as e:
                print(e)
                return
            if not isinstance(result, float) and not isinstance(result, int):
                print("result: ", result)
                loggingAndErrors.showErrorMessage(self, "Custom function must evaluate to a floating point number or NaN.")
                return
        else:
            function = None

        # DONT ALLOW EMPTY DATASETS TO BE PLOTTED
        #print(datasetID)
        #print(set(self.dataTable.index.get_level_values(1)))
        #print(datasetID in self.dataTable.index.get_level_values(1))
        if datasetID not in self.dataTable.index.get_level_values(1):
            self.modelTab.dataPlot.clearPlots()
            return

        # Handle the actual plotting
        self.modelTab.dataPlot.plot.getAxis('left').setLabel(units)

        resampledData = resampleDataSet(
            self.dataTable.loc[(slice(None), datasetID), 'Value'],
            period,
            method,
            function
        ).dropna()

        x = resampledData.index.get_level_values(0)
        y = resampledData.values

        self.modelTab.dataPlot.displayData(x, y, [units], [dataset['DatasetParameter'] + ': ' + dataset['DatasetName']])

        # Set a title for the plot
        self.modelTab.dataPlot.plot.setTitle('<strong style="font-family: Open Sans, Arial;">{4} {0} - {1} {2} {3}</strong>'.format(t1.strftime("%b %d"), t2.strftime("%b %d"), methodText.title(), dataset['DatasetParameter'], dataset['DatasetName'] ))

        return
    # </editor-fold>


    # ====================================================================================================================
    # PREDICTORS TAB FUNCTIONS
    # <editor-fold desc="Expand Predictors tab functions...">
    # <editor-fold desc="Expand Default subtab functions...">
    def addPredictorToDatasetOperationTable(self):
        for idx in self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index:
            if idx not in self.datasetOperationsTable.index:
                self.datasetOperationsTable.loc[idx, list(self.datasetOperationsTable.columns)] = [None] * len(
                    self.datasetOperationsTable.columns)


    def removePredictorFromDatasetOperationTable(self):
        for idx in self.datasetOperationsTable.index:
            if idx not in self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index:
                self.datasetOperationsTable.drop(idx, inplace=True)


    def updateSimpleLayoutAggregationOptions(self):
        #todo: doc string

        if len(self.modelTab.layoutSimpleDoubleList.listOutput.selectedIndexes()) > 0:
            # Get the current datasest index
            currentIndex = self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index[self.modelTab.layoutSimpleDoubleList.listOutput.selectedIndexes()[0].row()]
            try:
                indexExists = self.datasetOperationsTable.loc[currentIndex]
            except:
                return

            # Get the current dataset and operations settings
            datasetInfo = self.modelTab.fillList.datasetTable.loc[currentIndex]["DatasetName"] + " - " + \
                          self.modelTab.fillList.datasetTable.loc[currentIndex]["DatasetParameter"] + " " + \
                          str(self.modelTab.fillList.datasetTable.loc[currentIndex].name)
            accumMethod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])
            accumPeriod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'])
            predForcing = str(self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'])

            # Update the dataset list with the single display option
            if len(self.modelTab.layoutSimpleDoubleList.listOutput.selectedIndexes()) > 1:
                self.modelTab.layoutAggregationOptions.activeSelection.showMultipleItemsSelected()
            else:
                self.modelTab.layoutAggregationOptions.activeSelection.refreshDatasetListFromExtenal(self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.loc[currentIndex])

            # Set the list coloration
            selIdxs = self.modelTab.layoutSimpleDoubleList.listOutput.selectedIndexes()
            for selIdx in selIdxs:
                # selIdxRow = self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index[selIdx.row()]
                if accumMethod == 'None' or accumPeriod == 'None' or predForcing == 'None':
                    self.modelTab.layoutSimpleDoubleList.listOutput.itemColors[selIdx.row()] = QtCore.Qt.darkGray
                else:
                    self.modelTab.layoutSimpleDoubleList.listOutput.itemColors[selIdx.row()] = QtCore.Qt.white
            self.modelTab.layoutSimpleDoubleList.listOutput.updateColors()

            # Set date selector range
            minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[0]))
            maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))
            self.modelTab.layoutAggregationOptions.periodStart.setMinimumDateTime(minT)
            self.modelTab.layoutAggregationOptions.periodStart.setMaximumDateTime(maxT)
            self.modelTab.layoutAggregationOptions.periodStart.setDate(minT)

            # Set aggregation option on UI
            if accumMethod == 'None':
                # Get default resampling method
                defResampling = self.datasetTable.loc[self.datasetOperationsTable.loc[currentIndex].name[0]]['DatasetDefaultResampling']
                defIdx = self.modelTab.layoutAggregationOptions.predictorAggregationOptions.index(defResampling)
                self.modelTab.layoutAggregationOptions.radioButtons.button(defIdx).setChecked(True)
            else: #set defined aggregation scheme
                defIdx = self.modelTab.layoutAggregationOptions.predictorAggregationOptions.index(accumMethod)
                self.modelTab.layoutAggregationOptions.radioButtons.button(defIdx).setChecked(True)

            # Set aggregation period on UI
            if accumPeriod != 'None':
                predPeriodItems = accumPeriod.split("/") #R/1978-03-01/P1M/F12M/S1Y
                self.modelTab.layoutAggregationOptions.periodStart.setDate(parser.parse(predPeriodItems[1]))
                predPeriodPStep = str(predPeriodItems[2])[-1]
                a = self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodPStep)
                self.modelTab.layoutAggregationOptions.tStepChar.setCurrentIndex(self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodPStep))
                predPeriodPNum = ''.join(map(str,[int(s) for s in predPeriodItems[2] if s.isdigit()]))
                self.modelTab.layoutAggregationOptions.tStepInteger.setValue(int(predPeriodPNum))
                predPeriodFStep = str(predPeriodItems[3])[-1]
                self.modelTab.layoutAggregationOptions.freqChar.setCurrentIndex(self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodFStep))
                predPeriodFNum = ''.join(map(str,[int(s) for s in predPeriodItems[3] if s.isdigit()]))
                self.modelTab.layoutAggregationOptions.freqInteger.setValue(int(predPeriodFNum))
                if len(predPeriodItems) >= 5:
                    predPeriodSStep = str(predPeriodItems[4])[-1]
                    self.modelTab.layoutAggregationOptions.shiftChar.setCurrentIndex(self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodSStep))
                    predPeriodSNum = ''.join(map(str, [int(s) for s in predPeriodItems[4] if s.isdigit()]))
                    self.modelTab.layoutAggregationOptions.shiftInteger.setValue(int(predPeriodSNum))
                else:
                    self.modelTab.layoutAggregationOptions.shiftChar.setCurrentIndex(2)
                    self.modelTab.layoutAggregationOptions.shiftInteger.setValue(0)


            # Set forcing flag on UI
            if predForcing != 'None':
                self.modelTab.layoutAggregationOptions.predForceCheckBox.setChecked(predForcing == 'True')

            # Plot datasets
            # Resample predictor
            try:
                dataset = self.modelTab.fillList.datasetTable.loc[currentIndex]
                units = 'KAF' if 'KAF' in accumMethod.upper() else dataset['DatasetUnits']
                rawData = self.dataTable.loc[(slice(None), currentIndex[0]), 'Value']
                resampledData = resampleDataSet(rawData, accumPeriod, accumMethod).dropna()
                x = resampledData.index.get_level_values(0)
                y = resampledData.values
                self.modelTab.predictorPlot.clearPlots()
                self.modelTab.predictorPlot.displayData(x, y, [units], [dataset['DatasetParameter'] + ': ' + dataset['DatasetName']])
                self.modelTab.predictorPlot.plot.setTitle('<strong style="font-family: Open Sans, Arial;">Resampled {0} - {1}</strong>'.format(
                    dataset['DatasetName'], dataset['DatasetParameter']))
                xLabel = ('{0} - {1} ({2})').format(dataset['DatasetName'], dataset['DatasetParameter'], units)
            except:
                self.modelTab.predictorPlot.plot.updateText('<div style="color:#4e4e4e"><h1>Oops!</h1><br>Predictor not defined<br>Fully define the selected predictor to view resampled data plot...</div>')
            # Resample target
            try:
                targetID = self.modelRunsTable.loc[0].Predictand
                targetPeriod = self.modelRunsTable.loc[0].PredictandPeriod
                targetAccum = self.modelRunsTable.loc[0].PredictandMethod
                targetData = self.dataTable.loc[(slice(None), targetID), 'Value']
                dataset = self.datasetTable.loc[targetID]
                units = 'KAF' if 'KAF' in targetAccum.upper() else dataset['DatasetUnits']
                resampledTarget = resampleDataSet(targetData, targetPeriod, targetAccum).dropna()
                scatterDataFrame = pd.DataFrame(data=[x, y, resampledTarget.values, resampledTarget.values],index=['Years','Observed','Prediction','CV-Prediction']).T
                self.modelTab.predictorCorrelationPlot.clearPlot()
                self.modelTab.predictorCorrelationPlot.updateScatterPlot(scatterDataFrame, showCV=False, showLegend=False)
                yLabel = ('{0} - {1} ({2})').format(dataset['DatasetName'], dataset['DatasetParameter'],units)
                self.modelTab.predictorCorrelationPlot.setAxesLabels(xLabel,yLabel)
            except:
                self.modelTab.predictorCorrelationPlot.updateText('<div style="color:#4e4e4e"><h1>Oops!</h1><br>Looks like there is no target defined<br>Define a forecast target to view correlation...</div>')
        else:
            self.modelTab.layoutAggregationOptions.activeSelection.refreshDatasetListFromExtenal(None)

        self.modelTab.layoutAggregationOptions.resamplingUpdate()


    def applySimpleOptions(self):
        """
        Applies the attributes from the simple predictor page into the dataset operations table

        """

        # Clear the button click
        self.modelTab.layoutSimpleApplyButton.setChecked(False)

        # Get the current datasest indexes
        rowIdxs = self.modelTab.layoutSimpleDoubleList.listOutput.selectedIndexes()
        #rowIdx = self.modelTab.layoutSimpleDoubleList.listOutput.currentIndex().row()
        for rowIdx in rowIdxs:
            if rowIdx.row() >= 0:
                currentIndex = self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index[rowIdx.row()]
                # Apply selected options
                self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = self.modelTab.layoutAggregationOptions.selectedAggOption
                self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = self.modelTab.layoutAggregationOptions.periodStart.dateTime().toString("yyyy-MM-dd")
                self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = (parser.parse(str(np.sort(list(
                    set(self.dataTable.loc[(slice(None), currentIndex[0]), 'Value'].index.get_level_values(0).values)))[-1]))).strftime("%Y-%m-%d")
                self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = self.modelTab.layoutAggregationOptions.selectedAggPeriod
                self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = str(self.modelTab.layoutAggregationOptions.predForceCheckBox.checkState() == 2)

        self.updateSimpleLayoutAggregationOptions()


    def applySimpleClear(self):
        """
        Clears the fill attributes of a predictor

        """

        # Drop all rows in the dataset operations table
        self.datasetOperationsTable.drop(self.datasetOperationsTable.index, inplace=True)

        # Reset the output table
        self.modelTab.layoutSimpleDoubleList.resetOutputItems()

        # Clear the checkboxes
        self.modelTab.layoutSimpleExtendCheckBox.setChecked(False)
        self.modelTab.layoutSimpleFillCheckBox.setChecked(False)

        ### Reset the button state ###
        self.modelTab.layoutSimpleClearButton.setChecked(False)


    def showSimplePlots(self):
        self.modelTab.layoutSimplePlotButton.setChecked(False)
        if self.modelTab.predictorPlotWidget.isHidden():
            self.modelTab.predictorPlotWidget.show()
            self.modelTab.layoutSimplePlotButton.setText('<strong style="font-size: 16px; color:darkcyan">Hide Plot</strong>')
        else:
            self.modelTab.predictorPlotWidget.hide()
            self.modelTab.layoutSimplePlotButton.setText('<strong style="font-size: 16px; color:darkcyan">Show Plot</strong>')


    def switchSimplePlots(self):
        self.modelTab.predictorPlotButton.setChecked(False)
        if self.modelTab.predictorPlot.isHidden():
            self.modelTab.predictorPlot.show()
            self.modelTab.predictorCorrelationPlot.hide()
            self.modelTab.predictorPlotButton.setText('<strong style="font-size: 12px; color:darkcyan">Show resampled data correlation to target</strong>')
        else:
            self.modelTab.predictorPlot.hide()
            self.modelTab.predictorCorrelationPlot.show()
            self.modelTab.predictorPlotButton.setText('<strong style="font-size: 12px; color:darkcyan">Show resampled data time-series</strong>')
    # </editor-fold>


    # <editor-fold desc="Expand Expert subtab functions...">
    def updateFillSubtab(self):
        """
        Updates the state of the fill subtab methods pane based on the method selector

        """

        ### Update the widget pane ###
        # Switch the stacked widgets
        self.modelTab.stackedFillLayout.setCurrentIndex(self.modelTab.layoutFillMethodSelector.currentIndex())

        # Update the gap limit visibility
        if self.modelTab.layoutFillMethodSelector.currentIndex() > 0:
            self.modelTab.layoutFillGapLimitLabel.setVisible(True)
            self.modelTab.layoutFillGapLimit.setVisible(True)
        else:
            self.modelTab.layoutFillGapLimitLabel.setVisible(False)
            self.modelTab.layoutFillGapLimit.setVisible(False)

        if self.modelTab.layoutFillMethodSelector.currentIndex() >= 5:
            self.modelTab.layoutFillOrderLabel.setVisible(True)
            self.modelTab.layoutFillOrder.setVisible(True)
        else:
            self.modelTab.layoutFillOrderLabel.setVisible(False)
            self.modelTab.layoutFillOrder.setVisible(False)


    def updateFillOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Get the current datasest index
        currentIndex = self.modelTab.fillList.datasetTable.index[self.modelTab.fillList.currentIndex().row()]

        ### Update the widgets with dataset information ###
        # Get the options for the item
        fillMethod = self.datasetOperationsTable.loc[currentIndex]['FillMethod']
        fillGap = self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap']
        fillOrder = self.datasetOperationsTable.loc[currentIndex]['FillOrder']
        # If needed, can extract more information based on the fill method here

        # Get the options for the selector and stack
        fillOptionsIndex = [x for x in range(self.modelTab.layoutFillMethodSelector.count())
                            if self.modelTab.layoutFillMethodSelector.itemText(x) == fillMethod]
        if fillOptionsIndex:
            fillOptionsIndex = fillOptionsIndex[0]
        else:
            fillOptionsIndex = 0

        # Get the fill order index
        fillOrderIndex = [x for x in range(self.modelTab.layoutFillOrder.count())
                          if self.modelTab.layoutFillOrder.itemText(x) == str(fillOrder)]
        if fillOrderIndex:
            fillOrderIndex = fillOrderIndex[0]
        else:
            fillOrderIndex = 0

        # Set the values into the widgets
        self.modelTab.stackedFillLayout.setCurrentIndex(fillOptionsIndex)
        self.modelTab.layoutFillMethodSelector.setCurrentIndex(fillOptionsIndex)
        self.modelTab.layoutFillOrder.setCurrentIndex(fillOrderIndex)

        # Set the values into the widgets
        # Correct this issue
        self.modelTab.layoutFillGapLimit.setText(str(fillGap))

        ### Update the plot with the dataset and interpolation ###
        self.updateFillPlot(currentIndex, fillMethod, fillGap, fillOrder)


    def applyFillOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Extract the fill limit
        try:
            fillLimit = int(self.modelTab.layoutFillGapLimit.text())
        except:
            fillLimit = None

        # Get the method to be utilized
        fillMethod = self.modelTab.layoutFillMethodSelector.currentText()

        # Get the order
        fillOrder = int(self.modelTab.layoutFillOrder.currentText())

        # Get the current dataset
        currentIndex = self.modelTab.fillList.datasetTable.index[self.modelTab.fillList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['FillMethod'] = fillMethod
        self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = fillLimit
        self.datasetOperationsTable.loc[currentIndex]['FillOrder'] = fillOrder

        # Clear the button click
        self.modelTab.layoutFillApplyButton.setChecked(False)

        # Update the plot on the tab
        self.updateFillPlot(currentIndex, fillMethod, fillLimit, fillOrder)


    def applyFillClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.modelTab.fillList.datasetTable.index[self.modelTab.fillList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['FillMethod'] = None
        self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = None
        self.datasetOperationsTable.loc[currentIndex]['FillOrder'] = None

        # Clear the button click
        self.modelTab.layoutFillClearButton.setChecked(False)

        # Switch the stacked widgets
        self.modelTab.layoutFillMethodSelector.setCurrentIndex(0)
        self.updateFillSubtab()


    def updateFillPlot(self, currentIndex, fillMethod, fillLimit, fillOrder):
        """
        Updates the plot on the fill subtab

        Parameters
        ----------
        currentIndex: pandas index
            Index which specifies the active dataset
        fillMethod: str
            Fill method specified to fill the gaps
        fillLimit: int
            Maximum size of gap to fill via interpolation
        fillOrder: int
            Order of the fill method, if applicable

        """

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        sourceData = self.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        if fillMethod is not None and fillMethod != 'None':
            # Fill the data with the applied operation
            filledData = fill_missing(sourceData, fillMethod.lower(), fillLimit, order=fillOrder)

            # Promote and set the status of the filled data
            fillData = pd.DataFrame(filledData)
            fillData['Status'] = 'Filled'
            fillData.set_index(['Status'], append=True, inplace=True)

            # Promote and set the status of the source data
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'
            sourceData.set_index(['Status'], append=True, inplace=True)

            # Stack it together with the existing data
            sourceData = pd.concat([fillData, sourceData]).sort_index()

        else:
            # No filled data is present. Promote back to a dataframe and add the plotting label
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'

            # Convert to a multiinstance table
            sourceData.set_index(['Status'], append=True, inplace=True)

        ## Plot the source dataset ##
        self.modelTab.layoutFillPlot.updateData(sourceData, 'Status', sourceUnits)
        self.modelTab.layoutFillPlot.displayDatasets()


    def updateExtendSubtab(self):
        """
        Updates the state of the extend subtab methods pane based on the method selector

        """

        ### Switch the stacked widgets ###
        self.modelTab.stackedExtendLayout.setCurrentIndex(self.modelTab.layoutExtendMethodSelector.currentIndex())

        ### Set all options to false and reenable if active ###
        ## Linear widgets ##
        self.modelTab.layoutExtendLinearDurationLabel.setVisible(False)
        self.modelTab.layoutExtendLinearDurationLimit.setVisible(False)

        ## Fourier widgets ##
        self.modelTab.layoutExtendFourierDurationLabel.setVisible(False)
        self.modelTab.layoutExtendFourierDurationLimit.setVisible(False)
        self.modelTab.layoutExtendFourierFilterLabel.setVisible(False)
        self.modelTab.layoutExtendFourierFilter.setVisible(False)

        # Update the gap limit visibility
        if self.modelTab.layoutExtendMethodSelector.currentIndex() == 1:
            # Update visibility for the linear option
            self.modelTab.layoutExtendLinearDurationLabel.setVisible(True)
            self.modelTab.layoutExtendLinearDurationLimit.setVisible(True)

        elif self.modelTab.layoutExtendMethodSelector.currentIndex() == 2:
            # Update visibility for the fourier option
            self.modelTab.layoutExtendFourierDurationLabel.setVisible(True)
            self.modelTab.layoutExtendFourierDurationLimit.setVisible(True)
            self.modelTab.layoutExtendFourierFilterLabel.setVisible(True)
            self.modelTab.layoutExtendFourierFilter.setVisible(True)


    def updateExtendOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Get the current datasest index
        currentIndex = self.modelTab.extendList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Get the options for the item
        extendMethod = self.datasetOperationsTable.loc[currentIndex]['ExtendMethod']
        extendDuration = self.datasetOperationsTable.loc[currentIndex]['ExtendDuration']
        extendFilter = self.datasetOperationsTable.loc[currentIndex]['ExtendFilter']

        # Get the options for the selector and stack
        extendOptionsIndex = [x for x in range(self.modelTab.layoutExtendMethodSelector.count()) if self.modelTab.layoutExtendMethodSelector.itemText(x) == extendMethod]
        if extendOptionsIndex:
            extendOptionsIndex = extendOptionsIndex[0]
        else:
            extendOptionsIndex = 0

        # Toggle the stack to the correct display
        self.modelTab.stackedExtendLayout.setCurrentIndex(extendOptionsIndex)

        # Toggle the method selector to the correct display
        self.modelTab.layoutExtendMethodSelector.setCurrentIndex(extendOptionsIndex)

        # Set the options based on set option
        if extendOptionsIndex == 1:
            # Set the linear options
            self.modelTab.layoutExtendLinearDurationLimit.setText(str(extendDuration))

        elif extendOptionsIndex == 2:
            # Set the fourier options
            self.modelTab.layoutExtendFourierDurationLimit.setText(str(extendMethod))

            if extendFilter == 'Day':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(0)
            if extendFilter == 'Week':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(1)
            if extendFilter == 'Month':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(2)
            if extendFilter == 'Year':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(3)

        # Update the plot on the tab
        self.updateExtendPlot(currentIndex, extendMethod, extendDuration, extendFilter)


    def applyExtendOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        ### Extract the data from the GUI ###
        # Get the method to be utilized
        extendMethod = self.modelTab.layoutExtendMethodSelector.currentText()

        # Parse the output based on the method
        if extendMethod == 'None':
            extendMethod = None
            extendLimit = None
            extendFilter = None

        elif extendMethod == 'Linear':
            # Extract the information from the linear stack
            extendLimit = int(self.modelTab.layoutExtendLinearDurationLimit.text())
            extendFilter = None

        elif extendMethod == 'Fourier':
            # Extract the information from the fourier stack
            extendLimit = int(self.modelTab.layoutExtendFourierDurationLimit.text())
            extendFilter = self.modelTab.layoutExtendFourierFilter.currentText()

        # Get the current dataset
        currentIndex = self.modelTab.extendList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Set the fill values on the data
        self.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = extendMethod
        self.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = extendLimit
        self.datasetOperationsTable.loc[currentIndex]['ExtendFilter'] = extendLimit

        # Clear the button click
        self.modelTab.layoutExtendApplyButton.setChecked(False)

        # Update the plot on the tab
        self.updateExtendPlot(currentIndex, extendMethod, extendLimit, extendFilter)


    def applyExtendClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.modelTab.extendList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = None
        self.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = None
        self.datasetOperationsTable.loc[currentIndex]['ExtendFilter'] = None

        # Clear the button click
        self.modelTab.layoutFillClearButton.setChecked(False)

        # # Switch the stacked widgets
        self.modelTab.layoutExtendMethodSelector.setCurrentIndex(0)
        self.updateExtendSubtab()


    def updateExtendPlot(self, currentIndex, extendMethod, extendLimit, extendFilter):
        """
        Updates the plot on the extend subtab

        Parameters
        ----------
        currentIndex: pandas index
            Index which specifies the active dataset
        extendMethod: str
            Fill method specified to extend the series
        extendLimit: int
            Extension period

        """

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        sourceData = self.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        ### Extract the data from the fill chart ###
        fillMethod = self.datasetOperationsTable.loc[currentIndex]['FillMethod']
        fillDuration = self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap']
        fillOrder = self.datasetOperationsTable.loc[currentIndex]['FillOrder']

        if extendMethod is not None and extendMethod != 'None':
            # Fill the data with the applied operation
            extendedData, lostDensity = extend(sourceData, fillMethod.lower(), fillDuration, fillOrder,
                                               extendMethod.lower(), extendLimit, extendFilter)

            # Add missing source days into the extended data
            addIndices = [x for x in sourceData.index if x not in extendedData]
            extendedData = extendedData.append(pd.Series(np.ones(len(addIndices)) * np.NaN, index=addIndices, name='Value'))

            # Add the missing extend dats into the source data
            addIndices = [x for x in extendedData.index if x not in sourceData]
            sourceData = sourceData.append(pd.Series(np.ones(len(addIndices)) * np.NaN, index=addIndices, name='Value'))

            # Promote and set the status of the filled data
            extendedData = pd.DataFrame(extendedData)
            extendedData['Status'] = 'Extended'
            extendedData.set_index(['Status'], append=True, inplace=True)

            # Promote and set the status of the source data
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Extended'
            sourceData.set_index(['Status'], append=True, inplace=True)

            # Stack it together with the existing data
            sourceData = pd.concat([extendedData, sourceData]).sort_index()
            # sourceData = pd.concat([extendedData, sourceData])

        else:
            # No filled data is present. Promote back to a dataframe and add the plotting label
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Extended'

            # Convert to a multiinstance table
            sourceData.set_index(['Status'], append=True, inplace=True)

        ## Plot the source dataset ##
        self.modelTab.layoutExtendPlot.updateData(sourceData, 'Status', sourceUnits)
        self.modelTab.layoutExtendPlot.displayDatasets()


    def updateWindowOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the window pane

        """

        # Get the current datasest index
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.windowList.currentIndex().row()]

        # Get the current dataset and operations settings
        datasetInfo = self.modelTab.windowList.datasetTable.loc[currentIndex]["DatasetName"] + " - " + \
                      self.modelTab.windowList.datasetTable.loc[currentIndex]["DatasetParameter"] + " " + \
                      str(self.modelTab.windowList.datasetTable.loc[currentIndex].name)
        accumMethod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])
        accumPeriod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'])
        predForcing = str(self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'])

        # Set date selector range
        minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[0]))
        maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))
        self.modelTab.layoutWindowAggregationGroup.periodStart.minimumDate = minT
        self.modelTab.layoutWindowAggregationGroup.periodStart.maximumDate = maxT
        self.modelTab.layoutWindowAggregationGroup.periodStart.setDate(minT)

        # Set aggregation option on UI
        if accumMethod != 'None':
            defIdx = self.modelTab.layoutWindowAggregationGroup.predictorAggregationOptions.index(accumMethod)
            self.modelTab.layoutWindowAggregationGroup.radioButtons.button(defIdx).setChecked(True)

        # Set aggregation period on UI
        if accumPeriod != 'None':
            predPeriodItems = accumPeriod.split("/") #R/1978-03-01/P1M/F12M
            self.modelTab.layoutWindowAggregationGroup.periodStart.setDate(parser.parse(predPeriodItems[1]))
            predPeriodPStep = str(predPeriodItems[2])[-1]
            a = self.modelTab.layoutWindowAggregationGroup.predictorResamplingOptions.index(predPeriodPStep)
            self.modelTab.layoutWindowAggregationGroup.tStepChar.setCurrentIndex(self.modelTab.layoutWindowAggregationGroup.predictorResamplingOptions.index(predPeriodPStep))
            predPeriodPNum = ''.join(map(str,[int(s) for s in predPeriodItems[2] if s.isdigit()]))
            self.modelTab.layoutWindowAggregationGroup.tStepInteger.setValue(int(predPeriodPNum))
            predPeriodFStep = str(predPeriodItems[3])[-1]
            self.modelTab.layoutWindowAggregationGroup.freqChar.setCurrentIndex(self.modelTab.layoutWindowAggregationGroup.predictorResamplingOptions.index(predPeriodFStep))
            predPeriodFNum = ''.join(map(str,[int(s) for s in predPeriodItems[3] if s.isdigit()]))
            self.modelTab.layoutWindowAggregationGroup.freqInteger.setValue(int(predPeriodFNum))

        # Set forcing flag on UI
        if predForcing != 'None':
            self.modelTab.layoutWindowAggregationGroup.predForceCheckBox.setChecked(predForcing == 'True')

        self.modelTab.layoutWindowAggregationGroup.resamplingUpdate()

        # Update the plot
        self.updateWindowPlot()


    def applyWindowOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Get the current active index
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.windowList.currentIndex().row()]

        # Apply the attributes into the data table
        self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = \
            self.modelTab.layoutWindowAggregationGroup.selectedAggOption
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = \
            self.modelTab.layoutWindowAggregationGroup.periodStart.dateTime().toString("yyyy-MM-dd")
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = \
            (parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None), currentIndex[0]), 'Value'].index.get_level_values(0).values)))[-1]))).strftime("%Y-%m-%d")
        self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = \
            self.modelTab.layoutWindowAggregationGroup.selectedAggPeriod
        self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = \
            str(self.modelTab.layoutWindowAggregationGroup.predForceCheckBox.checkState() == 2)

        # Set the button to clear
        self.modelTab.layoutWindowApplyButton.setChecked(False)

        # Update the plot
        self.updateWindowPlot()

        
    def applyWindowClearToDataset(self):
        """
        Clears the window attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = None
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = None
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = None
        self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = None
        self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = None

        # Clear the button click
        self.modelTab.layouWindowClearButton.setChecked(False)


    def updateWindowPlot(self):
        """
        Updates the plot within the window subtab

        """

        # Get the index of the current selected dataset
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.windowList.currentIndex().row()]

        # Update the plot based on the user specified settings
        if self.modelTab.layoutWindowPlottingOptionAggregated.isChecked():

            # Toggle the widget stack to the current function
            self.modelTab.stackedWindowLayout.setCurrentIndex(0)

            # Resample predictor
            try:
                dataset = self.modelTab.windowList.datasetTable.loc[currentIndex]
                units = 'KAF' if 'KAF' in str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod']).upper() else dataset['DatasetUnits']
                rawData = self.dataTable.loc[(slice(None), currentIndex[0]), 'Value']
                resampledData = resampleDataSet(rawData, str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod']),
                                                str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])).dropna()
                x = resampledData.index.get_level_values(0)
                y = resampledData.values
                self.modelTab.layoutWindowPlotStandard.clearPlots()
                self.modelTab.layoutWindowPlotStandard.displayData(x, y, [units],
                                                        [dataset['DatasetParameter'] + ': ' + dataset['DatasetName']])
                self.modelTab.layoutWindowPlotStandard.plot.setTitle(
                    '<strong style="font-family: Open Sans, Arial;">Resampled {0} - {1}</strong>'.format(
                        dataset['DatasetName'], dataset['DatasetParameter']))
            except:
                self.modelTab.layoutWindowPlotStandard.plot.updateText(
                    '<div style="color:#4e4e4e"><h1>Oops!</h1><br>Predictor not defined<br>Fully define the selected predictor to view resampled data plot...</div>')

            # Update the window page correlation boxes
            self.updateWindowCorrelation()

        elif self.modelTab.layoutWindowPlottingOptionRawCrossCorrelation.isChecked():

            # Toggle the widget stack to the current function
            self.modelTab.stackedWindowLayout.setCurrentIndex(1)

            ### Get the data from the widgets ###
            startDate = self.modelTab.periodStartWindow.dateTime().toPyDateTime()
            endDate = self.modelTab.periodEndWindow.dateTime().toPyDateTime()

            ### Update the plot with the dataset and interpolation ###
            # Get the source and fill dataset. This copies it to avoid changing the source data
            sourceName = self.datasetTable.loc[currentIndex[0]]['DatasetName']
            sourceData = self.dataTable.loc[(slice(None), currentIndex), 'Value']
            sourceData = sourceData.droplevel('DatasetInternalID')
            sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']

            # Extract the target dataset
            targetData = self.dataTable.loc[(slice(None), self.modelTab.targetSelect.currentData().name), 'Value']
            targetName = self.datasetTable.loc[self.modelTab.targetSelect.currentData().name]['DatasetName']
            targetData = targetData.droplevel('DatasetInternalID')
            targetUnits = self.datasetTable.loc[self.modelTab.targetSelect.currentData().name]['DatasetUnits']

            # Window the data between the start and end dates
            sourceData = sourceData[startDate:endDate]
            targetData = targetData[startDate:endDate]

            # Calculate and plot the updated data
            self.modelTab.layoutWindowPlot.displayDatasets(sourceName, targetName, sourceData, targetData,
                                                           sourceUnits, targetUnits, '')

            # Update the window page correlation boxes
            self.updateWindowCorrelation()

        elif self.modelTab.layoutWindowPlottingOptionAggregatedCrossCorrelation.isChecked():

            # Toggle the widget stack to the current function
            self.modelTab.stackedWindowLayout.setCurrentIndex(1)

            # Resample predictor
            try:
                dataset = self.modelTab.windowList.datasetTable.loc[currentIndex]
                units = 'KAF' if 'KAF' in str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod']).upper() else dataset['DatasetUnits']
                rawData = self.dataTable.loc[(slice(None), currentIndex[0]), 'Value']
                resampledData = resampleDataSet(rawData, str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod']),
                                                str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])).dropna()
            except:
                resampledData = None

            # Resample the predictor
            try:
                targetID = self.modelRunsTable.loc[0].Predictand
                targetPeriod = self.modelRunsTable.loc[0].PredictandPeriod
                targetAccum = self.modelRunsTable.loc[0].PredictandMethod
                targetData = self.dataTable.loc[(slice(None), targetID), 'Value']
                resampledTarget = resampleDataSet(targetData, targetPeriod, targetAccum).dropna()
            except:
                resampledTarget = None

            # Setup the remaining items for the plot
            ### Get the data from the widgets ###
            startDate = self.modelTab.periodStartWindow.dateTime().toPyDateTime()
            endDate = self.modelTab.periodEndWindow.dateTime().toPyDateTime()

            ### Update the plot with the dataset and interpolation ###
            # Get the source and fill dataset. This copies it to avoid changing the source data
            sourceName = self.datasetTable.loc[currentIndex[0]]['DatasetName']
            sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']
            sourceData = resampledData

            # Extract the target dataset
            targetName = self.datasetTable.loc[self.modelTab.targetSelect.currentData().name]['DatasetName']
            targetUnits = self.datasetTable.loc[self.modelTab.targetSelect.currentData().name]['DatasetUnits']
            targetData = resampledTarget

            if sourceData is not None and targetData is not None:
                # Window the data between the start and end dates
                sourceData = sourceData[startDate:endDate]
                targetData = targetData[startDate:endDate]

                # Calculate and plot the updated data
                self.modelTab.layoutWindowPlot.displayDatasets(sourceName, targetName, sourceData, targetData,
                                                               sourceUnits, targetUnits, '')

            else:
                # Clear the existing plot
                self.modelTab.layoutWindowPlot.clearPlots()

            # Update the window page correlation boxes
            self.updateWindowCorrelation()

        else:
            raise NotImplementedError('Type of window plot is not understood')


    def updateWindowCorrelation(self):
        """

        """

        # Get the index of the current selected dataset
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.windowList.currentIndex().row()]

        # Resample predictor
        try:
            dataset = self.modelTab.windowList.datasetTable.loc[currentIndex]
            units = 'KAF' if 'KAF' in str(
                self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod']).upper() else dataset[
                'DatasetUnits']
            rawData = self.dataTable.loc[(slice(None), currentIndex[0]), 'Value']
            resampledData = resampleDataSet(rawData,
                                            str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod']),
                                            str(self.datasetOperationsTable.loc[currentIndex][
                                                    'AccumulationMethod'])).dropna()
        except:
            resampledData = None

        # Resample the predictor
        targetData = None
        try:
            targetID = self.modelRunsTable.loc[0].Predictand
            targetPeriod = self.modelRunsTable.loc[0].PredictandPeriod
            targetAccum = self.modelRunsTable.loc[0].PredictandMethod
            targetData = self.dataTable.loc[(slice(None), targetID), 'Value']
            resampledTarget = resampleDataSet(targetData, targetPeriod, targetAccum).dropna()
        except:
            resampledTarget = None

        # Stack the input data and calculate the correlation
        if targetData is not None:
            rawFrame = pd.concat([rawData, targetData], axis=1)
            rawCorrelate = rawFrame.corr('pearson').values[0, 1]
        else:
            rawCorrelate = np.NaN

        if resampledData is not None and targetData is not None:
            # Window the data between the start and end dates
            aggregatedFrame = pd.concat([resampledData, resampledTarget], axis=1)
            aggregatedCorrelate = aggregatedFrame.corr('pearson').values[0, 1]
        else:
            aggregatedCorrelate = np.NaN

        # Update the text boxes
        if np.any(np.isnan(rawCorrelate)):
            self.modelTab.rawCorrelation.setText('N/A')
        else:
            self.modelTab.rawCorrelation.setText(str(np.round(rawCorrelate, 3)))

        if np.any(np.isnan(aggregatedCorrelate)):
            self.modelTab.aggregatedCorrelation.setText('N/A')
        else:
            self.modelTab.aggregatedCorrelation.setText(str(np.round(aggregatedCorrelate, 3)))


    def switchWindowStack(self):
        """
        Controls the plotting stack within the window subtab

        """

        # Toggle to the correct plot display
        if self.modelTab.layoutWindowPlottingOptionAggregated.isChecked():
            # Toggle the widget stack to the current function
            self.modelTab.stackedWindowLayout.setCurrentIndex(0)

        else:
            self.modelTab.stackedWindowLayout.setCurrentIndex(1)

        # Update the plot
        self.updateWindowPlot()
    # </editor-fold>
    # </editor-fold>


    # ====================================================================================================================
    # SUMMARY TAB FUNCTIONS
    # <editor-fold desc="Expand Summary tab functions...">
    def updateModelSettings(self, defaultSettings):
        """
        This function is run when the user toggles the default model settings
        on the model settings sub-tab.
        """
        if defaultSettings:
            self.clickDefaults(self.modelTab.optionsCrossValidators, [2], False)
            self.clickDefaults(self.modelTab.optionsPreprocessor, [3], False)
            self.clickDefaults(self.modelTab.optionsRegression, [2, 3, 5], False)
            self.clickDefaults(self.modelTab.optionsSelection, [2], False)
            self.clickDefaults(self.modelTab.optionsScoring, [5], False)
        else:
            try:
                self.clickOption([self.modelRunsTable.loc[0]['CrossValidationType']], self.modelTab.optionsCrossValidators)
                self.clickOption(self.modelRunsTable.loc[0]['Preprocessors'], self.modelTab.optionsPreprocessor)
                self.clickOption(self.modelRunsTable.loc[0]['RegressionTypes'], self.modelTab.optionsRegression)
                self.clickOption(self.modelRunsTable.loc[0]['FeatureSelectionTypes'], self.modelTab.optionsSelection)
                self.clickOption(self.modelRunsTable.loc[0]['ScoringParameters'], self.modelTab.optionsScoring)
            except:
                print('INFO: No model run options defined in forecast file')
                self.clickDefaults(self.modelTab.optionsCrossValidators, [2], True)
                self.clickDefaults(self.modelTab.optionsPreprocessor, [3], True)
                self.clickDefaults(self.modelTab.optionsRegression, [2, 3, 5], True)
                self.clickDefaults(self.modelTab.optionsSelection, [2], True)
                self.clickDefaults(self.modelTab.optionsScoring, [5], True)
        return


    def clickOption(self, selectedOptions, optionList):
        for i in selectedOptions:
            for j in optionList:
                j.setEnabled(True)
                if i == j.objectName():
                    if not j.isChecked(): #click only if button isn't already clicked
                        j.click()
                else:
                    if j.isChecked():
                        j.click()
        return


    def clickDefaults(self, optionList, defaultIdx, enableButtons):
        counter = 0
        for j in optionList:
            if counter in defaultIdx:
                if not j.isChecked():  # click only if button isn't already clicked
                    j.click()
            else:
                if j.isChecked():
                    j.click()
            counter = counter + 1
            j.setEnabled(enableButtons)
        return

    # </editor-fold>


    # ====================================================================================================================
    # RUN TAB FUNCTIONS
    # <editor-fold desc="Expand Run tab functions...">
    def applySummaryClear(self):
        """
        Clear/reset all dataset and analysis options within the application

        """

        ### Reset the dataset operations table ###
        # Drop all rows in the tables
        self.modelRunsTable.drop(self.modelRunsTable.index, inplace=True)
        self.datasetOperationsTable.drop(self.datasetOperationsTable.index, inplace=True)

        # Update the table display elements
        self.modelTab.summaryListWidget.model().loadDataIntoModel(self.datasetTable, self.datasetOperationsTable)

        ### Reset all processing options ###
        # Reset the cross validation operations
        for x in self.modelTab.optionsCrossValidators:
            x.updateToUnchecked()

        # Reset the preprocessing operations
        for x in self.modelTab.optionsPreprocessor:
            x.updateToUnchecked()

        # Reset the regression options
        for x in self.modelTab.optionsRegression:
            x.updateToUnchecked()

        # Reset the selection options
        for x in self.modelTab.optionsSelection:
            x.updateToUnchecked()

        # Reset the scoring operations
        for x in self.modelTab.optionsScoring:
            x.updateToUnchecked()

        ### Reset the button state ###
        self.modelTab.summaryClearButton.setChecked(False)
        self.updateTabDependencies(3)

        ### Emit change to the doublelist object ###
        self.modelTab.layoutSimpleDoubleList.resetOutputItems()


    def applySummaryStart(self):
        """
        Start the regression analysis using the specified settings

        """
        
        ### Check and warn if defaults are set ###
        continueConfirmation = False
        if self.modelTab.defButton.isChecked():
            msgBox = self.startDefaultConfirmationPrompt()
            result = msgBox.exec_()

            if result == QtWidgets.QMessageBox.Ok:
                continueConfirmation = True
            else:
                continueConfirmation = False

        else:
            continueConfirmation = True

        ### Reset the button state ###
        self.modelTab.summaryStartButton.setChecked(False)
        errorString = 'Model Errors: '

        #### Continue only if valid valid options are present ####
        if continueConfirmation:

            ### Check if a predictand has been selected ###
            if self.modelRunsTable.shape[0] < 1:
                errorString += 'Select and define a valid predictand from the Forecast Target tab. '

            ### Get predictors ###
            predPool = []
            predPeriods = []
            predMethods = []
            predForced = []

            for index, row in self.datasetOperationsTable.iterrows():
                predPool.append(row.name[0])
                predPeriods.append(str(row['AccumulationPeriod']))
                predMethods.append(str(row['AccumulationMethod']))
                predForced.append(str(row['ForcingFlag']))

            if len(predPool) < 1:
                errorString += 'Select at least 1 predictor from the Predictors tab. '

            if predPeriods.count('None') > 0 or predMethods.count('None') > 0 or predForced.count('None') > 0:
                errorString += 'Fully define aggregation options for selected predictors on the Predictors tab. '

            ### Get base model run definitions ###

            # Cross validators
            crossVals = []
            for crossVal in self.modelTab.optionsCrossValidators:
                if crossVal.isChecked():
                    crossVals.append(crossVal.objectName())

            # Pre-processors
            preProcList = []
            for preProc in self.modelTab.optionsPreprocessor:
                if preProc.isChecked():
                    preProcList.append(preProc.objectName())

            # Regression algorithms
            regAlgs = []
            for regAlg in self.modelTab.optionsRegression:
                if regAlg.isChecked():
                    regAlgs.append(regAlg.objectName())

            # Feature selection algorithms
            selAlgs = []
            for selAlg in self.modelTab.optionsSelection:
                if selAlg.isChecked():
                    selAlgs.append(selAlg.objectName())

            # Scoring parameters
            scoreParams = []
            for scoreParam in self.modelTab.optionsScoring:
                if scoreParam.isChecked():
                    scoreParams.append(scoreParam.objectName())

            if len(crossVals) != 1:
                errorString += 'Select 1 Cross-Validation algorithm from the Options tab. '

            if len(preProcList) < 1 or len(regAlgs) < 1 or len(selAlgs) < 1 or len(scoreParams) < 1:
                errorString += 'Select at least 1 Preprocessor, Regressor, Feature Selector, and Model Scoring option from the Options tab. '

            ### Apply operations to datasets ###

            ### Final go no-go ###
            if len(errorString) > 20:
                self.modelTab.summaryLayoutErrorLabel.setText(errorString)
                self.modelTab.summaryLayoutErrorLabel.setStyleSheet("color : red")
                self.modelTab.summaryLayoutErrorLabel.setVisible(True)
                return
            else:
                # Populate self.modelRunsTable with validated entries
                self.modelRunsTable.loc[0]['PredictorPool'] = predPool
                self.modelRunsTable.loc[0]['PredictorForceFlag'] = predForced
                self.modelRunsTable.loc[0]['PredictorPeriods'] = predPeriods
                self.modelRunsTable.loc[0]['PredictorMethods'] = predMethods
                self.modelRunsTable.loc[0]['CrossValidationType'] = crossVals[0]
                self.modelRunsTable.loc[0]['Preprocessors'] = preProcList
                self.modelRunsTable.loc[0]['RegressionTypes'] = regAlgs
                self.modelRunsTable.loc[0]['FeatureSelectionTypes'] = selAlgs
                self.modelRunsTable.loc[0]['ScoringParameters'] = scoreParams

                # Ask user if sure
                #msgBox = self.clearAppTablesPrompt(forecastEquationsTable=True)
                #result = msgBox.exec_()
                #if result == QtWidgets.QMessageBox.Ok:
                #    self.clearAppTables(forecastEquationsTable=True)
                #else:
                #    return

                ### Kick off the analysis ###
                self.updateStatusMessage('Running regression calculations. Please wait...')
                print('INFO: ---- MODEL RUN TABLE ----')
                print(self.modelRunsTable.iloc[0])
                print('-------------------------')
                print('INFO: Beginning regression calculations...')
                self.rg = None
                self.rg = RegressionWorker.RegressionWorker(self.modelTab.parent, modelRunTableEntry=self.modelRunsTable.iloc[0])
                self.rg.setData()
                self.rg.run()

                ### Populate self.forecastEquationsTable ###
                print('INFO: Populating forecast equations table...')
                self.updateStatusMessage('Populating forecast equations table...')
                self.forecastEquationsTable.drop(self.forecastEquationsTable.index, inplace=True)
                df = pd.DataFrame(self.rg.resultsList)
                df[['PIPE', 'Pre-ProcessingMethod', 'RegressionMethod', 'CrossValidation']] = df['Method'].str.split('/', expand=True)
                df = df.groupby('RegressionMethod').head(200) #get top-100 models out of each regression method
                resultCounter = 0
                for result in df.iterrows():
                    self.forecastEquationsTable.loc[resultCounter] = [None] * self.forecastEquationsTable.columns.shape[0]
                    resultPredictors = result[1].Model
                    self.forecastEquationsTable.loc[resultCounter]['EquationSource'] = 'PyForecast'
                    self.forecastEquationsTable.loc[resultCounter]['ModelTrainingPeriod'] = self.modelRunsTable.loc[0]['ModelTrainingPeriod']
                    self.forecastEquationsTable.loc[resultCounter]['EquationPredictand'] = self.modelRunsTable.loc[0]['Predictand']
                    self.forecastEquationsTable.loc[resultCounter]['PredictandPeriod'] = self.modelRunsTable.loc[0]['PredictandPeriod']
                    self.forecastEquationsTable.loc[resultCounter]['PredictandMethod'] = self.modelRunsTable.loc[0]['PredictandMethod']
                    self.forecastEquationsTable.loc[resultCounter]['EquationCreatedOn'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # self.forecastEquationsTable.loc[resultCounter]['EquationIssueDate'] = ''
                    self.forecastEquationsTable.loc[resultCounter]['EquationMethod'] = result[1].Method
                    self.forecastEquationsTable.loc[resultCounter]['EquationSkill'] = result[1].Score
                    self.forecastEquationsTable.loc[resultCounter]['EquationPredictors'] = list(compress(predPool, resultPredictors))
                    self.forecastEquationsTable.loc[resultCounter]['PredictorPeriods'] = list(compress(predPeriods, resultPredictors))
                    self.forecastEquationsTable.loc[resultCounter]['PredictorMethods'] = list(compress(predMethods, resultPredictors))
                    # self.forecastEquationsTable.loc[resultCounter]['DirectEquation'] = ''
                    self.forecastEquationsTable.loc[resultCounter]['EquationComment'] = \
                        ["NegativeCoefficients:"+str(self.rg.resultsList[resultCounter]['NegativeCoefficients'])]
                    resultCounter += 1

                if len(self.rg.resultsList) >= 1:
                    self.modelTab.summaryLayoutErrorLabel.setText('Success! ' + str(len(self.rg.resultsList)) + ' models were evaluated...')
                    self.modelTab.summaryLayoutErrorLabel.setStyleSheet("color : green")
                    self.modelTab.summaryLayoutErrorLabel.setVisible(True)

                print('INFO: Model run complete!')
                self.updateStatusMessage('Model run complete! ' + str(len(self.rg.resultsList)) + ' models were evaluated.')
                self.modelTab.resultsMetricTable.clearTable()
                self.modelTab.resultsMetricTable.loadDataIntoModel(self.forecastEquationsTable)

    # </editor-fold>


    # ====================================================================================================================
    # RESULTS TAB FUNCTIONS
    # <editor-fold desc="Expand Results tab functions...">
    def generateModelsAnalysis(self):
        self.modelTab.exportResultModelsButton.setChecked(False)
        modelsTable = self.forecastEquationsTable
        self.buildModelAnalysisReport(modelsTable)
        return


    def generateSelectedModel(self, selected, deselected):
        # todo: doc string

        # Get model info
        tableIdx = self.modelTab.resultsMetricTable.view.selectionModel().currentIndex()
        modelIdx = tableIdx.siblingAtColumn(0).data()
        try:
            forecastEquationTableEntry = self.modelTab.parent.forecastEquationsTable.iloc[int(modelIdx)]
        except:
            return

        # Rebuild model
        self.updateStatusMessage('Regenerating model...')
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.modelTab.selectedModel = Model(self.modelTab.parent, forecastEquationTableEntry)
        self.modelTab.selectedModel.generate()
        QtWidgets.QApplication.restoreOverrideCursor()

        # Update UI with selected model metadata
        self.modelTab.selectedModel.report(self.modelTab.resultSelectedList)

        # Update Plots
        self.modelTab.resultsObservedForecstPlot.updateScatterPlot(self.modelTab.selectedModel.regressionData)
        self.modelTab.resultsInflowYearPlot.updateTimeSeriesPlot(self.modelTab.selectedModel.regressionData)
        self.modelTab.resultsResidualYearPlot.updateResidualPlot(self.modelTab.selectedModel.regressionData)
        self.updateStatusMessage('')


    def modelTableRightClick(self, pos):
        if self.modelTab.resultsMetricTable.view.selectionModel().selection().indexes():
            for i in self.modelTab.resultsMetricTable.view.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QtWidgets.QMenu()
            saveAction = menu.addAction("Save Model")
            action = menu.exec_(self.modelTab.resultsMetricTable.view.mapToGlobal(pos))
            if action ==saveAction:
                self.saveModelAction(row, column)


    def saveModelAction(self, row, column):
        # Get model info
        tableIdx = self.modelTab.resultsMetricTable.view.selectionModel().currentIndex()
        modelIdx = tableIdx.siblingAtColumn(0).data()
        try:
            # Get model definition row and write to self.modelTab.parent.savedForecastEquationsTable

            forecastEquationTableEntry = self.modelTab.parent.forecastEquationsTable.iloc[int(modelIdx)]

            tableLength = len(self.modelTab.parent.savedForecastEquationsTable)
            self.modelTab.parent.savedForecastEquationsTable.loc[tableLength] = forecastEquationTableEntry.values
            self.resetForecastsTab()
        except:
            return
    # </editor-fold>


    # ====================================================================================================================
    # TAB CHANGE FUNCTION
    def updateTabDependencies(self, tabIndex):
        # todo: doc string

        ### Get the current index the widget has been changed to ###
        #print(tabIndex)
        
        if tabIndex == 1:
            if self.modelTab.defaultPredictorButton.isChecked():
                self.modelTab.stackedPredictorWidget.setCurrentIndex(0)
                self.modelTab.layoutPredictorSimpleAnalysis.setVisible(True)
            elif self.modelTab.expertPredictorButton.isChecked():
                self.modelTab.stackedPredictorWidget.setCurrentIndex(1)
                self.modelTab.expertPredictorWidget.setVisible(True)

        if tabIndex == 3:
            # Update the summary boxes
            # Update predictand options
            self.modelTab.summaryLayoutErrorLabel.setVisible(False)
            if self.modelRunsTable.shape[0] < 1:
                self.modelTab.summaryLayoutLabel1.setText('     Period: None')
                self.modelTab.summaryLayoutLabel1.setStyleSheet("color : red")
                self.modelTab.summaryLayoutLabel2.setText('     Predictand: None')
                self.modelTab.summaryLayoutLabel2.setStyleSheet("color : red")
                self.modelTab.summaryLayoutLabel3.setText('     Predictand Period: None')
                self.modelTab.summaryLayoutLabel3.setStyleSheet("color : red")
                self.modelTab.summaryLayoutLabel4.setText('     Predictand Method: None')
                self.modelTab.summaryLayoutLabel4.setStyleSheet("color : red")
            else:
                selDataset = self.datasetTable.loc[self.modelRunsTable.loc[0]['Predictand']]
                selName = str(selDataset['DatasetName']) + ' (' + str(selDataset['DatasetAgency']) + ') ' + str(selDataset['DatasetParameter'])
                self.modelTab.summaryLayoutLabel1.setText('     Period: ' + str(self.modelRunsTable.loc[0]['ModelTrainingPeriod']))
                self.modelTab.summaryLayoutLabel1.setStyleSheet("color : green")
                self.modelTab.summaryLayoutLabel2.setText('     Predictand: ' + selName)
                self.modelTab.summaryLayoutLabel2.setStyleSheet("color : green")
                self.modelTab.summaryLayoutLabel3.setText('     Predictand Period: ' + str(self.modelRunsTable.loc[0]['PredictandPeriod']))
                self.modelTab.summaryLayoutLabel3.setStyleSheet("color : green")
                self.modelTab.summaryLayoutLabel4.setText('     Predictand Method: ' + str(self.modelRunsTable.loc[0]['PredictandMethod']))
                self.modelTab.summaryLayoutLabel4.setStyleSheet("color : green")

            # Load predictors table
            self.modelTab.summaryListWidget.model().loadDataIntoModel(self.datasetTable, self.datasetOperationsTable)

        elif tabIndex == 4:
            self.updateStatusMessage('Updating generated forecasts table...')
            # self.modelTab.resultsMetricTable.loadDataIntoModel(self.forecastEquationsTable)
            self.updateStatusMessage('')

    def startDefaultConfirmationPrompt(self):
        """
        Prompts the user regarding the user of default options prior to allowing a model run.

        """

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.setWindowTitle('Confirm default settings')
        msg.setText('Use of the default settings is intended to be a first order analysis that provides a high-level '
                    'overview of a basin. It may be inaccurate, subject to large uncertainties, and is not suitable '
                    'for all forecasts. \n\nPlease confirm the use of default settings prior to proceeding.')

        return msg

    def clearAppTablesPrompt(self, modelRunsTable):
        pass

