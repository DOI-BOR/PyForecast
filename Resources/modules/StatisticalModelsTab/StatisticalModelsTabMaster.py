from datetime import datetime, timedelta
import numpy as np
from resources.modules.Miscellaneous import loggingAndErrors
from PyQt5 import QtCore, QtGui
import pandas as pd

class statisticalModelsTab(object):
    """
    STATISTICAL MODELS TAB
    The Statistical Models Tab contains tools for creating
    new statistical models (i.e. forecast equations). 
    """

    def initializeStatisticalModelsTab(self):
        """
        Initialize the Tab
        """
        self.connectEventsStatisticalModelsTab()

        return


    def connectEventsStatisticalModelsTab(self):
        """
        Connects all the signal/slot events for the dataset tab
        """

        self.modelTab.targetWidgetButton.changeTabSignal.connect(self.changedTabsStatisticalModelsPage)
        self.modelTab.predictorWidgetButton.changeTabSignal.connect(self.changedTabsStatisticalModelsPage)
        self.modelTab.optionsWidgetButton.changeTabSignal.connect(self.changedTabsStatisticalModelsPage)
        self.modelTab.summaryWidgetButton.changeTabSignal.connect(self.changedTabsStatisticalModelsPage)

        self.modelTab.datasetList.itemPressed.connect(lambda x: self.modelTab.targetSelect.setCurrentIndex(self.modelTab.datasetList.row(x)))
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.targetSelect.hidePopup())
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.plotTarget() if x >= 0 else None)
        self.modelTab.periodStart.dateChanged.connect(lambda x: self.plotTarget())
        self.modelTab.periodEnd.dateChanged.connect(lambda x: self.plotTarget())
        self.modelTab.methodCombo.currentIndexChanged.connect(lambda x: self.plotTarget())
        self.modelTab.customMethodSpecEdit.editingFinished.connect(self.plotTarget)
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.selectedItemDisplay.setDatasetTable(self.datasetTable.loc[self.modelTab.datasetList.item(x).data(QtCore.Qt.UserRole).name])  if x >= 0 else None)
        self.modelTab.methodCombo.currentIndexChanged.connect(lambda x: self.modelTab.customMethodSpecEdit.show() if self.modelTab.methodCombo.itemData(x) == 'custom' else self.modelTab.customMethodSpecEdit.hide())
        
        return


    def changedTabsStatisticalModelsPage(self, index):
        """
        Handles changing the stacked widget when a user clicks one of the hover 
        labels on the left side.
        """

        for i in range(4):
            if i != index:
                self.modelTab.buttons[i].onDeselect()

        return


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
        start = self.modelTab.periodStart.date().toString("1900-MM-dd")
        start_dt = pd.to_datetime(start)
        end = self.modelTab.periodEnd.date().toString("1900-MM-dd")
        end_dt = pd.to_datetime(end)
        length = (end_dt - start_dt).days
        period = 'R/{0}/P{1}D/F12M'.format(start, length)

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
                    [pd.date_range(start=start_dt, periods=10000), 10000*[12013]],
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

        # Handle the actual plotting
        self.modelTab.dataPlot.plot.getAxis('left').setLabel(units)
        self.modelTab.dataPlot.displayDatasets(datasetID, period, method, function)

        # Set a title for the plot
        self.modelTab.dataPlot.plot.setTitle('<strong style="font-family: Open Sans, Arial;">{4} {0} - {1} {2} {3}</strong>'.format(start_dt.strftime("%b %d"), end_dt.strftime("%b %d"), methodText.title(), dataset['DatasetParameter'], dataset['DatasetName'] ))

        return


    def autoGeneratePredictors(self):
        """
        Generates default predictors based on the input to the
        previous sections.
        """

        # First verify that all the previous sections have been filled in correctly
        # PLACEHOLDERS
        target = None # DatasetID 
        targetPeriodStart = None # Month-Day combo, e.g.April 1st
        targetPeriodEnd = None # Month-Day combo e.g. July 31st
        forecastIssueDay = None # Month-day combo e.g. Feb 01
        
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
                wyStart = datetime(forecastIssueDay.year if forecastIssueDay.month > 10 else forecastIssueDay.year - 1, 10, 1)
                period = 'R/{0}/P{1}D/F1Y'.format(datetime.strftime(wyStart, '%Y-%m-%d'), (forecastIssueDay - wyStart).days - 1)
            
            elif  any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['FLOW'])): 
                wyStart = datetime(forecastIssueDay.year if forecastIssueDay.month > 10 else forecastIssueDay.year - 1, 10, 1)
                period = 'R/{0}/P1M/F1Y'.format(datetime.strftime(wyStart, '%Y-%m-%d'))

            suggestedPredictors.append((dataset.name, method, period)) 

        # Add the predictors to the GUI
        

        return


    def createModelRunEntry(self):
        """
        Parses the left hand model specification pane and creates 
        a new entry to the modelRunsTable. 
        """

        return


    def beginModelGeneration(self):
        """
        Initializes the Model Generation Worker to begin finding
        suitable models using the latest entry in the modelRunsTable.
        """

        return
        

    def processModelResults(self):
        """
        Processes the model results from the Model Generation Worker. 
        Resulting models are checked for similarity, the results are 
        compiled into an analysis table, and the results are entered 
        into the model results table.
        """

        return