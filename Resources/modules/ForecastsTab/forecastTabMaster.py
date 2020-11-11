from datetime import datetime, timedelta
from resources.modules.Miscellaneous import loggingAndErrors
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd
from scipy import stats
import numpy as np
import datetime
from itertools import compress
from dateutil import parser
from statsmodels.tsa.stattools import ccf

from resources.modules.Miscellaneous.generateModel import Model
from resources.GUI.CustomWidgets.SpreadSheet import GenericTableModel
from resources.GUI.CustomWidgets.forecastList_FormattedHTML import forecastList_HTML

class forecastsTab(object):
    """
    FORECAST TAB
    The Forecast Tab contains tools for generating forecasts and hindcasts using saved models
    from the model creation tab.
    """

    def initializeForecastsTab(self):
        """
        Initializes the Tab
        """
        self.connectEventsForecastsTab()

        return

    def resetForecastsTab(self):
        self.forecastsTab.savedModelsTable.clearTable()
        self.forecastsTab.savedModelsTable.loadDataIntoModel(self.savedForecastEquationsTable)
        self.forecastsTab.savedForecastsPane.clearForecasts()
        self.forecastsTab.savedForecastsPane.setForecastTable()


        return


    def connectEventsForecastsTab(self):
        """
        Connects all the signal/slot events for the forecasting tab
        """

        # Create an update method for when the tab widget gets changed to refresh elements
        self.forecastsTab.workflowWidget.currentChanged.connect(self.selectedForecastTabChanged)

        # Connect saved model table actions
        self.savedEquationSelectionModel = self.forecastsTab.savedModelsTable.view.selectionModel()
        self.savedEquationSelectionModel.selectionChanged.connect(self.generateSavedModel)
        self.forecastsTab.savedModelsTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.forecastsTab.savedModelsTable.customContextMenuRequested.connect(self.savedModelTableRightClick)

        # Connect model data year and forecasting actions
        self.forecastsTab.modelYearSpin.valueChanged.connect(self.updateForecastYearData)
        self.forecastsTab.runModelButton.clicked.connect(self.generateModelPrediction)
        self.forecastsTab.saveModelButton.clicked.connect(self.saveModelPrediction)

        # Connect forecast comparison actions
        self.savedForecastSelectionModel = self.forecastsTab.savedForecastsPane.selectionModel()
        self.savedForecastSelectionModel.selectionChanged.connect(self.generateSavedForecast)

        return


    # ====================================================================================================================
    # FORECAST DETAIL TAB FUNCTIONS
    # <editor-fold desc="Expand Forecast Detail tab functions...">
    def generateSavedModel(self, selected, deselected):
        # todo: doc string

        # Get model info
        tableIdx = self.forecastsTab.savedModelsTable.view.selectionModel().currentIndex()
        modelIdx = tableIdx.siblingAtColumn(0).data()
        try:
            forecastEquationTableEntry = self.forecastsTab.parent.savedForecastEquationsTable.loc[int(modelIdx)]
        except:
            return

        # Rebuild model
        self.updateStatusMessage('Regenerating model...')
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.forecastsTab.selectedModel = Model(self.forecastsTab.parent, forecastEquationTableEntry)
        self.forecastsTab.selectedModel.equationID = modelIdx
        self.forecastsTab.selectedModel.generate()
        QtWidgets.QApplication.restoreOverrideCursor()

        # Update UI with selected model metadata
        self.forecastsTab.selectedModel.report(modelIdx, self.forecastsTab.resultSelectedList)

        # Update Plots
        self.forecastsTab.resultsObservedForecstPlot.updateScatterPlot(self.forecastsTab.selectedModel.regressionData)

        # Update model run year and table
        self.forecastsTab.modelYearSpin.setRange(self.forecastsTab.selectedModel.years[0], self.forecastsTab.selectedModel.years[-1])
        self.forecastsTab.modelYearSpin.setValue(self.forecastsTab.selectedModel.years[-1])
        self.updateForecastYearData()
        self.forecastsTab.runModelButton.setEnabled(True)
        self.forecastsTab.saveModelButton.setEnabled(False)
        self.updateStatusMessage('')


    def updateForecastYearData(self):
        lookupYear = self.forecastsTab.modelYearSpin.value()
        try:
            lookupData = self.forecastsTab.selectedModel.predictorData.loc[int(lookupYear)]
        except:
            return
        remainingData = self.forecastsTab.selectedModel.predictorData.drop(index=lookupYear)
        remainingAvg = remainingData.mean()
        lookupAvg = 100.0 * lookupData / remainingAvg
        remainingPctls = remainingData.quantile([0,.1,.25,.5,.75,.9,1])
        predNames = []
        predIdxs = []
        for i in range(len(self.forecastsTab.selectedModel.xIDs)):
            predNames.append('X' + str(i+1) + ': ' + str(self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.xIDs[i]].DatasetName) + \
                      ' - ' + str(self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.xIDs[i]].DatasetParameter))
            predIdxs.append(self.forecastsTab.selectedModel.xIDs[i])
        preds = pd.Series(predNames, index=predIdxs)
        lookupDataTable = pd.concat([pd.DataFrame(data=[preds, lookupData,lookupAvg,remainingAvg]),remainingPctls])
        lookupDataTable.index = ['Predictor', str(lookupYear) + ' Value', str(lookupYear) + ' Pct-Average','Average','Min', 'P10', 'P25', 'Median', 'P75', 'P90', 'Max']
        self.forecastsTab.selectedModelDataTable.loadDataIntoModel(lookupDataTable, rowHeaders=list(lookupDataTable.columns), columnHeaders=list(lookupDataTable.index))


    def savedModelTableRightClick(self, pos):
        if self.forecastsTab.savedModelsTable.view.selectionModel().selection().indexes():
            for i in self.forecastsTab.savedModelsTable.view.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QtGui.QMenu()
            deleteAction = menu.addAction("Delete Model")
            action = menu.exec_(self.forecastsTab.savedModelsTable.view.mapToGlobal(pos))
            if action ==deleteAction:
                self.deleteSavedModelAction(row, column)


    def deleteSavedModelAction(self, row, column):
        # Get model info
        tableIdx = self.forecastsTab.savedModelsTable.view.selectionModel().currentIndex()
        modelIdx = tableIdx.siblingAtColumn(0).data()
        try:
            # Delete row from  self.forecastsTab.parent.savedForecastEquationsTable
            self.forecastsTab.parent.savedForecastEquationsTable.drop([int(modelIdx)], inplace=True)
            self.resetForecastsTab()
        except:
            return


    def generateModelPrediction(self):
        self.updateStatusMessage('Generating prediction...')
        self.forecastsTab.runModelButton.setChecked(False)
        lookupYear = self.forecastsTab.modelYearSpin.value()
        self.forecastsTab.selectedModel.predictionYear = lookupYear
        # Get data from the displayed table
        xData = pd.Series()
        for i in range(len(self.forecastsTab.selectedModelDataTable.dataTable.columns)):
            xData.loc[i] = float(self.forecastsTab.selectedModelDataTable.model.item(1, i).text())
        xData.index = self.forecastsTab.selectedModelDataTable.dataTable.columns
        self.forecastsTab.selectedModel.predict(xData=xData)
        # Get data based on the toggled year
        #self.forecastsTab.selectedModel.predict(year=str(lookupYear))
        self.forecastsTab.resultsObservedForecstPlot.appendForecast(self.forecastsTab.selectedModel.prediction,
                                                                    self.forecastsTab.selectedModel.predictionRange.loc[[10,25,75,90]])
        self.forecastsTab.saveModelButton.setEnabled(True)
        self.updateStatusMessage('')


    def saveModelPrediction(self):
        print('Saving prediction. Prediction=' + ('%0.0f' % self.forecastsTab.selectedModel.prediction) +
              ' - Bootstrapped Prediction Range: [10%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[10]) +
              ', 25%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[25]) +
              ', 50%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[50]) +
              ', 75%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[75]) +
              ', 90%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[90]) + ']')
        eqID = int(self.forecastsTab.selectedModel.equationID)
        fcastYear = self.forecastsTab.selectedModel.predictionYear
        fcastExc  = 0.5
        fcastIdx = [(eqID, fcastYear, fcastExc)]
        if self.forecastsTable.index.isin(fcastIdx).any():
            self.forecastsTable.drop(fcastIdx, inplace=True)
        self.forecastsTab.selectedModel.predictionRange.loc[-1] = self.forecastsTab.selectedModel.prediction
        self.forecastsTable.loc[eqID,fcastYear,fcastExc]=[self.forecastsTab.selectedModel.predictionRange]
    # </editor-fold>


    # ====================================================================================================================
    # COMPARE FORECASTS TAB FUNCTIONS
    # <editor-fold desc="Expand Compare Forecasts tab functions...">
    def generateSavedForecast(self):

        self.forecastsTab.savedForecastsCharts.clearPlot()
        selectedSavedForecasts = self.forecastsTab.savedForecastsPane.selectedItems()
        try:
            # Remove non-forecast card items
            nonFcastIdxs = []
            for i in range(len(selectedSavedForecasts)):
                if not hasattr(selectedSavedForecasts[i],'modelID'):
                    nonFcastIdxs.append(i)
            selectedSavedForecasts = [i for j, i in enumerate(selectedSavedForecasts) if j not in nonFcastIdxs]
            boxPlotData = []
            fcastCounter = 10
            for fcast in selectedSavedForecasts:
                # boxPlotData = [  ## fields are (xVal, P50, P25, P75, P10, P90, fcast).
                #     (10, 11, 10, 13, 5, 15, 12),
                #     (20, 15, 13, 17, 9, 20, 14),
                #     ...
                # ]
                boxPlotData.append((int(fcastCounter), fcast.forecastValues.loc[50].values[0],
                                    fcast.forecastValues.loc[25].values[0], fcast.forecastValues.loc[75].values[0],
                                    fcast.forecastValues.loc[10].values[0], fcast.forecastValues.loc[90].values[0],
                                    fcast.forecastValues.loc[-1].values[0]))
                fcastCounter = fcastCounter + 10

            #self.forecastsTab.savedForecastsCharts.appendSavedForecast(fcast.forecastValues, fcast.modelID)
            self.forecastsTab.savedForecastsCharts.appendSavedForecast(boxPlotData)
        except:
            return
    # </editor-fold>


    # ====================================================================================================================
    # TAB CHANGE FUNCTIONS


    def selectedForecastTabChanged(self, tabIndex):
        # todo: doc string
        ### Get the current index the widget has been changed to ###
        #currentIndex = self.workflowWidget.currentIndex()
        #print(tabIndex)

        if tabIndex == 0:
            self.forecastsTab.savedModelsTable.clearTable()
            self.forecastsTab.savedModelsTable.loadDataIntoModel(self.savedForecastEquationsTable)

        if tabIndex == 1:
            self.forecastsTab.savedForecastsPane.clearForecasts()
            self.forecastsTab.savedForecastsPane.setForecastTable()

