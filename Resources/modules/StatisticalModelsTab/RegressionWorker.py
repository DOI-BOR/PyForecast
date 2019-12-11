"""
Basic Workflow
Predictor Pool

    ||
    ||
    \/

FOR REGR IN REGR METHODS
    FOR I IN NUM MODELS
        FEAT_SEL_METHOD = FEAT_SEL_LIST [i%LEN LIST]
        DO FEAT_SEL_METHOD TO COMPLETION 
            -> Check if model in models (If it is either go forward or backward a set)
        ADD MODEL TO MODEL OUTPUT

    ||
    ||
    \/

ANALYZE MODEL LIST FOR DUPLICATES, SIMILAR MODELS
RETURN MODEL LIST
"""
import pandas as pd
import numpy as np
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
import multiprocessing as mp
import importlib
import bitarray as ba


# Not super sure how this stucture will be set up yet.
class RegressionWorker(object):

    def __init__(self, parent = None, modelRunTableEntry = None, *args, **kwargs):

        # Create References to the parent and the regression model run entry
        self.parent = parent
        self.modelRunTableEntry = modelRunTableEntry

        # Initialize lists of regression schemes, etc.
        self.regressionSchemes = modelRunTableEntry['RegressionTypes']
        self.featureSelectionSchemes = [importlib.import_module("resources.modules.StatisticalModelsTab.FeatureSelectionAlgorithms.{0}".format(f)) for f in modelRunTableEntry['FeatureSelectionTypes']]
        self.crossValidationScheme = modelRunTableEntry['CrossValidationType']
        self.scoringParameters = modelRunTableEntry['ScoringParameters']

        return
    
    def setData(self):
        """
        Initializes the regression worker dataset with an entry from
        the application's modelRunsTable. 
        """
        
        # Create X, Y arrays
        self.x = []
        self.y = []

        # Set the start and end dates for the model training period
        self.trainingDates = list(map(pd.to_datetime, self.modelRunTableEntry['ModelTrainingPeriod'].split('/')))

        # Iterate over predictor datasets and append to arrays
        for i in range(len(self.modelRunTableEntry['PredictorPool'])):

            data = resampleDataSet(
                self.parent.dataTable.loc[(slice(None), self.modelRunTableEntry['PredictorPool'][i]), 'Value'],
                self.modelRunTableEntry['PredictorPeriods'][i],
                self.modelRunTableEntry['PredictorMethods'][i]
                )
            
            self.x.append(list(data.loc[self.trainingDates[0]: self.trainingDates[1]]))

        # Compute the target data
        self.y = resampleDataSet(
            self.parent.dataTable.loc[(slice(None), self.modelRunTableEntry['Predictand']), 'Value'],
            self.modelRunTableEntry['PredictandPeriod'],
            self.modelRunTableEntry['PredictandMethod']
        )
        self.y = list(self.y.loc[self.trainingDates[0]: self.trainingDates[1]])

        # Convert data lists to numpy arrays
        self.x = np.array(self.x).T
        self.y = np.array(self.y)

        return

    def run(self):
        """
        Iterates over the regression types provided and performs 
        feature selection on each one. 
        """
        
        # Iterate over the regression methods
        for regression in self.regressionSchemes:

            # Create a model list to store already computed models
            self.computedModels = {}

            # Iterate a few times over each regression method
            for i in range(4):

                # Iterate over the feature selection methods
                for featSel in self.featureSelectionSchemes:

                    if i != 0:

                        # Generate a random model
                        model = ba.bitarray(list(np.random.randint(0, 2, self.x.shape[1])))

                        # Initialize the feature selection scheme with the random model
                        f = featSel.FeatureSelector(    
                                    parent = self, 
                                    regression = regression, 
                                    crossValidation = self.crossValidationScheme, 
                                    scoringParameters = self.scoringParameters,
                                    initialModel = model)

                    else:

                        # Initialize the feature selection scheme with the scheme's default model
                        f = featSel.FeatureSelector(    
                                    parent = self, 
                                    regression = regression, 
                                    crossValidation = self.crossValidationScheme, 
                                    scoringParameters = self.scoringParameters)

                    # Run the feature selection algorithm
                    f.iterate()

        return

    

# DEBUGGING
if __name__ == '__main__':

    from sklearn.datasets import make_regression
    
    # Make some regression data
    
    dates = pd.date_range('2000-10-01', '2018-10-01')
    datasets = [10,20,30,40,50,60,70]
    arrays = [(date, i) for date in dates for i in datasets]

    x, y = make_regression(n_samples=len(dates), n_features=len(datasets)-1, n_informative=3, bias=10, noise=10, effective_rank=1, tail_strength=0.88)
    XY = np.concatenate((x, y.reshape(-1,1)), axis=1)

    # Initialize a dataset
    df = pd.DataFrame(
        XY.T.flatten(),
        columns = ['Value'],
        index = pd.MultiIndex.from_tuples(
            arrays,
            names=('Datetime', 'DatasetID')   
        )
    )

    # Initialize a model run
    dm = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ModelRunID'),
            columns = [
                "ModelTrainingPeriod",  # E.g. 1978-10-01/2019-09-30 (model trained on  WY1979-WY2019 data)
                "Predictand",           # E.g. 100302 (datasetInternalID)
                "PredictandPeriod",     # E.g. R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",     # E.g. Accumulation, Average, Max, etc
                "PredictorPool",        # E.g. [100204, 100101, ...]
                "PredictorForceFlag",   # E.g. [False, False, True, ...]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, ...]
                "PredictorMethods",     # E.g. ['Accumulation', 'First', 'Last', ...]
                "RegressionTypes",      # E.g. ['Regr_MultipleLinearRegression', 'Regr_ZScoreRegression']
                "CrossValidationType",  # E.g. K-Fold (10 folds)
                "FeatureSelectionTypes",# E.g. ['FeatSel_SequentialFloatingSelection', 'FeatSel_GeneticAlgorithm']
                "ScoringParameters"     # E.g. ['ADJ_R2', 'MSE']
            ]
        )

    dm.loc[1] = [   
                    '2000-10-01/2017-09-30', 
                    50,
                    'R/2001-04-01/P4M/F1Y', 
                    'accumulation', 
                    [10,20,30,40,60,70],
                    [False, False, False, False, False, False], 
                    ['R/2001-02-01/P1M/F12M', 'R/2001-02-01/P1M/F12M', 'R/2001-02-01/P1M/F12M', 'R/2001-02-01/P1M/F12M','R/2001-02-01/P1M/F12M', 'R/2001-02-01/P1M/F12M'],
                    ['average', 'average', 'accumulation', 'average', 'accumulation', 'average'],
                    ['Regr_MultipleLinearRegressor'], 
                    'KFOLD_5', 
                    ['FeatSel_BruteForce'], 
                    ['ADJ_R2','MSE']
                ]

    class p(object):
        dataTable = df

    p_ = p()


    rg = RegressionWorker(parent = p_, modelRunTableEntry=dm.loc[1])
    rg.setData()
    print('')
    print('')