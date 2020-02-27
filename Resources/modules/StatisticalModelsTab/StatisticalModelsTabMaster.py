from datetime import datetime, timedelta

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
                period = 'R/{0}/P1D/F1Y'.format(datetime.strftime(forecastIssueDay - timedelta(days=1), '%Y-%m-%d')

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