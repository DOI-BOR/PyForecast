"""
Script Name:    RegressionWorker.py

Description:    RegressionWorker Iterates over the product of the provided 
                preprocessing schemes, feature selection schemes, and 
                regression schemes.

                Computed models are kept track of at the preprocessing and
                regression level. 
"""
import pandas as pd
from tqdm import tqdm
import numpy as np
import os
import sys
from PyQt5 import QtWidgets, QtCore
sys.path.append(os.getcwd())
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
import multiprocessing as mp
import importlib
import bitarray as ba
from resources.modules.StatisticalModelsTab.ModelScoring import sortScores
from operator import itemgetter

class RegressionWorkerSignals(QtCore.QObject):
    """
    supported signals are:

    finished
        No data

    currentModel
        model true/false list, e.g. [True, False, False, True, ...]
    """

    finished = QtCore.pyqtSignal()
    currentModel = QtCore.pyqtSignal(list)


class RegressionWorker(QtCore.QRunnable):

    def __init__(self, parent = None, modelRunTableEntry = None, *args, **kwargs):
        """
        Initialize the RegressionWorker Object
        """
        QtCore.QRunnable.__init__(self)
        self.signals = RegressionWorkerSignals()

        # Create References to the parent and the regression model run entry
        self.parent = parent
        self.modelRunTableEntry = modelRunTableEntry

        # reference to run time
        self.currentDate = pd.Timestamp.today().strftime("%Y-%m-%d")

        # Initialize lists of regression schemes, etc.
        self.regressionSchemes = modelRunTableEntry['RegressionTypes']
        self.featureSelectionSchemes = [importlib.import_module("resources.modules.StatisticalModelsTab.FeatureSelectionAlgorithms.{0}".format(f)) for f in modelRunTableEntry['FeatureSelectionTypes']]
        self.crossValidationScheme = modelRunTableEntry['CrossValidationType']
        self.scoringParameters = modelRunTableEntry['ScoringParameters']
        self.preprocessors = [importlib.import_module("resources.modules.StatisticalModelsTab.PreProcessingAlgorithms.{0}".format(p)) for p in modelRunTableEntry['Preprocessors']]
        
        return

    
    def setData(self):
        """
        Initializes the regression worker dataset with an entry from
        the application's modelRunsTable. 
        """
        
        # Create X, Y arrays
        self.xTraining = []

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
            

        # Compute the target data
        self.y = resampleDataSet(
            self.parent.dataTable.loc[(slice(None), self.modelRunTableEntry['Predictand']), 'Value'],
            self.modelRunTableEntry['PredictandPeriod'],
            self.modelRunTableEntry['PredictandMethod']
        )
        self.yTraining = self.y.loc[self.trainingDates[0]: self.trainingDates[1]].values # Training Data
        

        # Set the forced predictors
        self.forcedPredictors = ba.bitarray(self.modelRunTableEntry['PredictorForceFlag'])

        # Add any missing data for the current water year to the arrays
        maxListLength = max([len(i) for i in self.xTraining])
        [i.append(np.nan) for i in self.xTraining if len(i) < maxListLength]

        # Convert data lists to numpy arrays
        self.xTraining = np.array(self.xTraining).T
        self.yTraining = np.array(self.yTraining).reshape(-1,1)

        # Compute the total number of model combinations that are possible
        self.numPossibleModels = int('1'*self.xTraining.shape[1], 2)

        # Create a table to store results
        self.resultsList = []

        return


    def updateViz(self, currentModel = None):
        """
        Updates the main threads vizualizations with the model
        """

        self.signals.currentModel.emit(currentModel)

        return

    @QtCore.pyqtSlot()
    def run(self):
        """
        Iterates over the regression types provided and performs 
        feature selection on each one. 
        """

        # Iterate over the preprocessing schemes
        for preprocessor in self.preprocessors:

            # Initialize the preprocesser
            self.preprocessor = preprocessor.preprocessor(np.concatenate([self.xTraining, self.yTraining], axis=1))

            # Compute the preprocessed dataset
            self.proc_xTraining = self.preprocessor.getTransformedX()
            self.proc_yTraining = self.preprocessor.getTransformedY()
        
            # Iterate over the regression methods
            for regression in self.regressionSchemes:

                # Create a model list to store already computed models (Used for feature seleciton 
                # algorithms to keep track of model scores)
                self.computedModels = {}

                # Iteration tracker
                i = 0

                # Compute at least 10,000 models
                while len(self.computedModels) < (self.numPossibleModels if self.numPossibleModels < 10000 else 10000):
                    print(len(self.computedModels))
                    # Iterate over the feature selection methods
                    for featSel in self.featureSelectionSchemes:

                        # In our first run of the feature selection scheme, 
                        # use the scheme's default initial model. In the 
                        # case of brute force scheme, the scheme will
                        # see all models from this initialization
                        if i == 0:
                            
                            print("i 0")

                            # Initialize the feature selection scheme with the scheme's default model
                            f = featSel.FeatureSelector(    
                                        parent = self, 
                                        regression = regression, 
                                        crossValidation = self.crossValidationScheme, 
                                        scoringParameters = self.scoringParameters)
                                    

                        # Otherwise, generate a random model.
                        else:
                            print('i 1')

                            # Generate a random model
                            model = ba.bitarray(list(np.random.randint(0, 2, self.xTraining.shape[1])))

                            # Initialize the feature selection scheme with the random model
                            f = featSel.FeatureSelector(    
                                        parent = self, 
                                        regression = regression, 
                                        crossValidation = self.crossValidationScheme, 
                                        scoringParameters = self.scoringParameters,
                                        initialModel = model)

                        # Run the feature selection algorithm
                        f.iterate()

                    # Iterate tracker
                    i += 1

        # Remove nans from the results List
        self.resultsList = list(filter(lambda x: not np.all([np.isnan(i[1]) for i in x['Score'].items()]), self.resultsList))

        # Sort the scores
        sortScores(self.resultsList)
        self.resultsList.reverse()

        return

    

# DEBUGGING
if __name__ == '__main__':

    from resources.modules.StatisticalModelsTab import PredictionIntervalBootstrap
    import time
    import warnings
    import random
    warnings.filterwarnings("ignore")
    
    import matplotlib.pyplot as plt
    #plt.ion()
    import sys
    from scipy.stats import iqr
    from sklearn.neighbors import KernelDensity
    import matplotlib.colors as mc
    COLORS = list(mc.CSS4_COLORS.keys())
    random.shuffle(COLORS)

    from PyQt5 import QtWidgets,QtCore
    
    # Load some toy data
    datasetTable = pd.read_pickle("toyDatasets.pkl")
    dataTable = pd.read_pickle("toyData.pkl")
    modelInit = pd.read_pickle("toyModelInit.pkl")

    modelInit.loc[100]['FeatureSelectionTypes'] = ['FeatSel_BruteForce']
    
    
    # Fake Parent Object
    class p(object):
        def __init__(self, dataTable=None, modelInit = None, datasetTable=None):
            #QtWidgets.QWidget.__init__(self)
            #self.thread = QtCore.QThreadPool()
            
            self.dataTable = dataTable
            self.modelInit = modelInit
            self.datasetTable = datasetTable
    
            self.rg = RegressionWorker(self, modelRunTableEntry=self.modelInit.iloc[0])
            
            self.forecastIssueDate = pd.to_datetime('2019-04-01')
     
    
    p_ = p(dataTable, modelInit, datasetTable)

    # Initialize regression worker
    p_.rg.setData()
    
    # Run the regression worker
    a = time.time()
    p_.rg.run()
    b = time.time()

    # Print results
    [print(f) for f in p_.rg.resultsList[:30]]

    # Do a prediction with the best equation
    best_equation = p_.rg.resultsList[0]
    preproc = best_equation['Method'].split("/")[1]
    regr = best_equation['Method'].split("/")[2]
    cval = best_equation['Method'].split("/")[3]
    xt, yt = p_.rg.xTraining, p_.rg.yTraining

    # put the observations in the right format
    XY = np.hstack((xt, yt))
    lastRow = np.full((1, XY.shape[1]), np.nan)

    for i in range(xt.shape[1]):

        data = resampleDataSet(
            dataTable.loc[(slice(None), modelInit.iloc[0]['PredictorPool'][i]), 'Value'],
            modelInit.iloc[0]['PredictorPeriods'][i],
            modelInit.iloc[0]['PredictorMethods'][i]
        )
        data = data.loc[data.index.year == p_.forecastIssueDate.year]
        lastRow[0][i] = data
    
    #lastRow = lastRow.flatten()
    XY = np.vstack((XY, lastRow))

    def plot_forecast(equation, XY, i):
        preproc = equation['Method'].split('/')[1]
        regr = equation['Method'].split("/")[2]
        cval = equation['Method'].split("/")[3]
        model = [True if i == '1' else False for i in equation['Model']] + [True]
        XY_ = XY[:, model]
        preproc_ = importlib.import_module("resources.modules.StatisticalModelsTab.PreProcessingAlgorithms.{0}".format(preproc))
        regressor_ = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(regr))
        results = PredictionIntervalBootstrap.computePredictionInterval(XY_, preproc_.preprocessor, regressor_.Regressor, cval)

        # Histogram up that prediction!
        total_number = len(results)
        p90 = results[int(total_number/10)]
        p50 = results[int(total_number/2)]
        p10 = results[total_number - int(total_number/10)]

        iqr_ = iqr(results)
        std_ = np.std(results)
        h = 0.9*(min(iqr_, std_))*pow(total_number, -1/5)

        # Compute KDE
        kde = KernelDensity(bandwidth=h).fit(results.reshape(-1,1))
        xs = np.linspace(p10 - 800, p90 + 800, 1000)
        log_dens = kde.score_samples(xs.reshape(-1,1))

        idx = int(equation['Model'], 2)

        plt.hist(results, bins=int(len(results)/30), normed=True, facecolor = COLORS[i], alpha = 0.6)
        plt.plot(xs, np.exp(log_dens), color=COLORS[i])
    
    for i, mod in enumerate(p_.rg.resultsList[0:1]):
        print(mod['Model'])
        plot_forecast(mod, XY, i)

    plt.xlim((0, 1500))

    plt.show()
