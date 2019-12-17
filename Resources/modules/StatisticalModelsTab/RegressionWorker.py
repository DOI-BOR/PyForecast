"""
Script Name:    RegressionWorker.py

Description:    RegressionWorker
"""
import pandas as pd
from tqdm import tqdm
import numpy as np

import os
import sys
sys.path.append(os.getcwd())

from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
import multiprocessing as mp
import importlib
import bitarray as ba



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
        self.xTraining = []
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
            
            self.xTraining.append(list(data.loc[self.trainingDates[0]: self.trainingDates[1]])) # Training Data
            self.x.append(list(data)) # All Data

        # Compute the target data
        self.y = resampleDataSet(
            self.parent.dataTable.loc[(slice(None), self.modelRunTableEntry['Predictand']), 'Value'],
            self.modelRunTableEntry['PredictandPeriod'],
            self.modelRunTableEntry['PredictandMethod']
        )
        self.yTraining = list(self.y.loc[self.trainingDates[0]: self.trainingDates[1]]) # Training Data
        self.y = list(self.y) # All Data

        # Set the forced predictors
        self.forcedPredictors = ba.bitarray(self.modelRunTableEntry['PredictorForceFlag'])

        # Add any missing data for the current water year to the arrays
        maxListLength = max([len(i) for i in self.x])
        [i.append(np.nan) for i in self.x if len(i) < maxListLength]

        # Convert data lists to numpy arrays
        self.x = np.array(self.x).T
        self.xTraining = np.array(self.xTraining).T
        self.y = np.array(self.y)
        self.yTraining = np.array(self.yTraining)

        # Compute the total number of model combinations that are possible
        self.numPossibleModels = int('1'*self.x.shape[1], 2)

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

            # Iteration tracker
            i = 0

            # Compute at least 10,000 models
            while len(self.computedModels) < (self.numPossibleModels if self.numPossibleModels < 10000 else 10000):

                print(len(self.computedModels))
                
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

                # Iterate tracker
                i += 1


        return

    

# DEBUGGING
if __name__ == '__main__':

    from sklearn.datasets import make_regression, load_boston
    from resources.modules.StatisticalModelsTab import PredictionIntervalBootstrap
    from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
    import time
    import warnings
    warnings.filterwarnings("ignore")

    
    # Load some toy data
    df = pd.read_csv('test_blr.csv', index_col=0, parse_dates=True)
    
    datasets = list(df.columns)
    num_predictors = len(datasets)
    df = df.stack(0)
    df.name = 'Value'
    df = pd.DataFrame(df)
    df.index.names = ['Datetime','DatasetID']
    print(df)

    # Initialize a model run
    dm = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ModelRunID'),
            columns = [
                "ModelTrainingPeriod",      # E.g. 1978-10-01/2019-09-30 (model trained on  WY1979-WY2019 data)
                "Predictand",               # E.g. 100302 (datasetInternalID)
                "PredictandPeriod",         # E.g. R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",         # E.g. Accumulation, Average, Max, etc
                "PredictorPool",            # E.g. [100204, 100101, ...]
                "PredictorForceFlag",       # E.g. [False, False, True, ...]
                "PredictorPeriods",         # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, ...]
                "PredictorMethods",         # E.g. ['Accumulation', 'First', 'Last', ...]
                "RegressionTypes",          # E.g. ['Regr_MultipleLinearRegression', 'Regr_ZScoreRegression']
                "CrossValidationType",      # E.g. K-Fold (10 folds)
                "FeatureSelectionTypes",    # E.g. ['FeatSel_SequentialFloatingSelection', 'FeatSel_GeneticAlgorithm']
                "ScoringParameters"         # E.g. ['ADJ_R2', 'MSE']
            ]
        )
    
    # Set up predictors from toy dataset
    predictors = ['HucPrecip'] + ['Nino3.4']*3 + datasets[2:]
    print(predictors)
    periodList = ["R/1990-02-01/P2M/F1Y","R/1990-02-01/P1M/F1Y","R/1990-01-01/P1M/F1Y","R/1990-03-01/P1M/F1Y",'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-03-01/P1M/F1Y', 'R/1989-10-01/P6M/F1Y', 'R/1990-03-01/P1M/F1Y']
    methodList = ["accumulation","average","average","average",'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'average', 'accumulation', 'average']
    print(len(periodList), len(predictors), len(methodList))
    # Create a model run entry
    dm.loc[1] = [   
                    '1989-10-01/2017-09-30', 
                    datasets[0],
                    'R/1990-04-01/P4M/F1Y', 
                    'accumulation', 
                    predictors,
                    [False]*(len(predictors)), 
                    periodList,
                    methodList,
                    ['Regr_GammaGLM'], 
                    'KFOLD_5', 
                    ['FeatSel_SequentialForwardFloating'], 
                    ['AIC']
                ]

    # Fake Parent Object
    class p(object):
        dataTable = df

    p_ = p()

    # Initialize regressor
    rg = RegressionWorker(parent = p_, modelRunTableEntry=dm.loc[1])
    rg.setData()
    print('yrange is {0} - {1}'.format(min(rg.y), max(rg.y)))

    # Run RegressionWorker
    print('There are {0} possible combinations'.format(int('1'*(len(predictors)-1),2)+1))
    a = time.time()
    rg.run()
    b = time.time()

    print('analyzed {0} combinations'.format(len(rg.computedModels.keys())))
    print('ran in {0} sec'.format(b-a))

    # Sort Results by score
    d = pd.DataFrame().from_dict(rg.computedModels, orient='index')
    d.sort_values(by=['AIC'], inplace=True, ascending=False)
    d.index.name = 'model'
    
    print(d)

    # # Retrieve the top model
    # topModel = ba.bitarray(d.index[0])

    # # Assemble the training data
    # x = rg.xTraining[:, list(topModel)]
    # y = rg.yTraining[~np.isnan(x).any(axis=1)]
    # x = x[~np.isnan(x).any(axis=1)]

    # # Get the latest X Data
    # xNew = rg.x[:, list(topModel)][-1]

    # # Get the regressor
    # regressionName = rg.regressionSchemes[0]
    # module = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(regressionName))
    # regressionClass = getattr(module, 'Regressor')
    # regression = regressionClass(crossValidation = "KFOLD_5", scoringParameters = "ADJ_R2")

    # # Define a dummy preprocessor
    # class preprocessor(object):

    #     def __init__(self, data):

    #         self.data = data

    #     def getTransformedX(self):

    #         return self.data[:, :-1]

    #     def getTransformedY(self):

    #         return self.data[:,-1]
            
    #     def transform(self, data):

    #         return data

    #     def inverseTransform(self, data):

    #         return data
    
    # pre = preprocessor(x)
