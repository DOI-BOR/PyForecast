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
import bitarray as ba
from resources.modules.StatisticalModelsTab.ModelScoring import sortScores
from operator import itemgetter
from itertools import repeat
from sklearn.cluster import KMeans
REGRESSION_STOP_ITERATIONS = {
    "Regr_MultipleLinearRegressor": 20000,
    "Regr_PCARegressor": 10000,
    "Regr_ZScore":20000,
    "Regr_SVM_RBF":4000,
    "Regr_MLPerceptron":500,
    "Regr_GammaGLM":2000
}

class RegressionWorkerSignals(QtCore.QObject):
    """
    supported signals are:

    finished
        No data

    currentModel
        model true/false list, e.g. [True, False, False, True, ...]
    """

    finished = QtCore.pyqtSignal()
    currentModel = QtCore.pyqtSignal(object)


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

        # Initialize the regression schemes, feature selectors, cross validators, and preprocessors
        self.regressionSchemes = modelRunTableEntry['RegressionTypes']
        self.featureSelectionSchemes = [self.parent.featureSelectors[featSel]['module'] for featSel in modelRunTableEntry['FeatureSelectionTypes']]
        self.crossValidationScheme = modelRunTableEntry['CrossValidationType']
        self.scoringParameters = modelRunTableEntry['ScoringParameters']
        self.preprocessors = [self.parent.preProcessors[preproc]['module'] for preproc in modelRunTableEntry['Preprocessors']]
        
        return

    
    def setData(self):
        """
        Initializes the regression worker dataset with an entry from
        the application's modelRunsTable. 
        """
        
        # Create X, Y arrays
        self.xTraining = []
        self.excludeYears = []

        # Set the start and end dates for the model training period
        modelTrainingStrings = self.modelRunTableEntry['ModelTrainingPeriod'].split('/') 
        self.trainingDates = list(map(int, modelTrainingStrings[:2]))
        if len(modelTrainingStrings) > 2:
            self.excludeYears = list(map(int, modelTrainingStrings[2].split(',')))

        popindex = []
        # Iterate over predictor datasets and append to arrays
        for i in range(len(self.modelRunTableEntry['PredictorPool'])):

            data = resampleDataSet(
                self.parent.dataTable.loc[(slice(None), self.modelRunTableEntry['PredictorPool'][i]), 'Value'],
                self.modelRunTableEntry['PredictorPeriods'][i],
                self.modelRunTableEntry['PredictorMethods'][i]
                )

            data.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in data.index], axis = 0, inplace = True)
            data = data.loc[self.trainingDates[0]: self.trainingDates[1]]
            if data.apply(lambda x: x == 0 or np.isnan(x)).all():
                print('all zero variable detected at position:', i)
                popindex.append(i) 
                continue
            if np.isnan(data.loc[self.excludeYears[0]]):
                print('missing exclude year at: ', i)
                popindex.append(i)
                continue
            #print(data)
            idx = list(filter(lambda date: date not in self.excludeYears, data.index))
            self.xTraining.append(list(data.loc[idx])) # Training Data
        self.modelRunTableEntry['PredictorPool'] = list(np.delete(self.modelRunTableEntry['PredictorPool'], popindex))
        self.modelRunTableEntry['PredictorPeriods'] = list(np.delete(self.modelRunTableEntry['PredictorPeriods'], popindex))
        self.modelRunTableEntry['PredictorMethods'] = list(np.delete(self.modelRunTableEntry['PredictorMethods'], popindex))
        self.modelRunTableEntry['PredictorForceFlag'] = list(np.delete(self.modelRunTableEntry['PredictorForceFlag'], popindex))

            

        # Compute the target data
        self.y = resampleDataSet(
            self.parent.dataTable.loc[(slice(None), self.modelRunTableEntry['Predictand']), 'Value'],
            self.modelRunTableEntry['PredictandPeriod'],
            self.modelRunTableEntry['PredictandMethod']
        )
        self.y.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in self.y.index], axis = 0, inplace = True)
        data = self.y.loc[self.trainingDates[0]: self.trainingDates[1]]
        idx = list(filter(lambda date: date not in self.excludeYears, data.index))
        self.yTraining = self.y.loc[idx].values # Training Data
        

        # Set the forced predictors
        print("force flag", self.modelRunTableEntry['PredictorForceFlag'])
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

            print("Using Preprocessor: ", preprocessor)

            # Initialize the preprocesser
            self.preprocessor = preprocessor(np.concatenate([self.xTraining, self.yTraining], axis=1))

            # Compute the preprocessed dataset
            self.proc_xTraining = self.preprocessor.getTransformedX()
            self.proc_yTraining = self.preprocessor.getTransformedY()
        
            # Iterate over the regression methods
            for regression in self.regressionSchemes:
                
                print("Using Regression: ", regression)

                # Create a model list to store already computed models (Used for feature seleciton 
                # algorithms to keep track of model scores)
                self.computedModels = {}

                # Iteration tracker
                i = 0

                # Compute models
                while len(self.computedModels) < (self.numPossibleModels if self.numPossibleModels <  REGRESSION_STOP_ITERATIONS[regression] else REGRESSION_STOP_ITERATIONS[regression]):

                    # Iterate over the feature selection methods
                    for featSel in self.featureSelectionSchemes:

                        # In our first run of the feature selection scheme, 
                        # use the scheme's default initial model. In the 
                        # case of brute force scheme, the scheme will
                        # see all models from this initialization
                        if i == 0:
                            
                            # Initialize the feature selection scheme with the scheme's default model
                            f = featSel(    
                                        parent = self, 
                                        regression = regression, 
                                        crossValidation = self.crossValidationScheme, 
                                        scoringParameters = self.scoringParameters)
                                    

                        # Otherwise, generate a random model.
                        else:

                            # Generate a random model
                            model = ba.bitarray(list(np.random.randint(0, 2, self.xTraining.shape[1])))

                            # Initialize the feature selection scheme with the random model
                            f = featSel(    
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

    # Import modules
    import pickle
    import time
    import warnings
    import importlib
    import inspect
    import sys
    from resources.modules.StatisticalModelsTab import PredictionIntervalBootstrap2 as PredictionIntervalBootstrap

    import random
    warnings.filterwarnings("ignore")
    from PyQt5 import QtWidgets,QtCore
    import signal
    import atexit
    from colorama import init, Style
    init()


    # Load data
    with open('../GIBR_NEXTFLOW3.fcst', 'rb') as readfile:
            datasetTable = pickle.load(readfile)
            dataTable = pickle.load(readfile)

    # Create a model initialization table
    modelInitTable = pd.DataFrame(
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
    for year in range(1990,2020):
        for i, date in enumerate(pd.date_range("2020-04-01", "2020-04-05", freq="MS")):
            if date.month == 4:
                if date.day != 1:
                    period = "R/{0}/P{1}D/F12M".format(date.strftime("1970-%m-%d"), (pd.to_datetime("2020-7-31") - date).days)
                else:
                    period = "R/{0}/P{1}D/F12M".format("1970-04-01", (pd.to_datetime("2020-7-31") - pd.to_datetime("2020-04-01")).days)
            elif date.month > 4:
                period = "R/{0}/P{1}D/F12M".format(date.strftime("1970-%m-%d"), (pd.to_datetime("2020-7-31") - date).days)
            else:
                period = "R/{0}/P{1}D/F12M".format("1970-04-01", (pd.to_datetime("2020-7-31") - pd.to_datetime("2020-04-01")).days)
            MonthAverage_1 = "R/1968-{0}/P1M/F12M".format((date - pd.DateOffset(months=1)).strftime("%m-%d"))
            MonthAverage_2 = "R/1968-{0}/P15D/F12M".format((date - pd.DateOffset(days=15)).strftime("%m-%d"))
            ytdAccum = "R/1968-11-01/P{0}D/F12M".format((date - pd.to_datetime("2019-11-01")).days)
            dayOfSample = "R/1968-{0}/P1D/F12M".format(date.strftime("%m-%d"))

            predP = [
                
                102123,
                100432,
                100431,
                101371,
                101364,
                102052,
                101318,
                100560,
                100059,
                101481,
                101388,
                100607,
                10889,
                11889,
                11889,
                14001,
                14002,
                18038,
                14043,
                106187,
                106187
            ]
            methods = [
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "first",
                "average",
                "accumulation",
                "average",
                "average",
                "average",
                "average",
                "average",
                "accumulation",
                "average"
            ]
            times = [
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                dayOfSample,
                MonthAverage_1,
                ytdAccum,
                MonthAverage_1,
                MonthAverage_1,
                MonthAverage_1,
                MonthAverage_1,
                MonthAverage_1,
                ytdAccum,
                MonthAverage_1



            ]

            #predP = [102123,102052,101318,100560,100059,101481,100432,100431,10889,11889,11889,14043,14001,18038,106187,106187,998876,998877,998878,998879]
            #methods = ["first","first","first","first","first","first","first","first","average","accumulation","accumulation","average","average","average","average","average","first","first","first","first"]
            #times = [dayOfSample,dayOfSample,dayOfSample,dayOfSample,dayOfSample,dayOfSample,dayOfSample,dayOfSample,MonthAverage_1,MonthAverage_1,ytdAccum,MonthAverage_1,MonthAverage_1,MonthAverage_1,MonthAverage_1,MonthAverage_2,dayOfSample,dayOfSample,dayOfSample,dayOfSample]

            modelInitTable.loc[len(modelInitTable)] = [
                "1970/2019/{0}".format(year),
                date.strftime("%B %d"),
                106187,
                period,
                'accumulation_cfs_kaf',
                [],
                [],
                predP,
                [False]*len(predP),
                times,
                methods,
                ['Regr_MultipleLinearRegressor'],
                'KFOLD_5',
                ['FeatSel_SequentialForwardFloating',],
                ['MSE'],
                ['PreProc_YAware']
            ]
    print(modelInitTable.iloc[0])
    # Fake Parent Object
    class p(object):
        def __init__(self, dataTable=None, modelInit = None, datasetTable=None):
            #QtWidgets.QWidget.__init__(self)
            #self.thread = QtCore.QThreadPool()
            # Load the modules
            self.preProcessors = {}
            self.regressors = {}
            self.featureSelectors = {}
            self.crossValidators = {}
            self.scorers = {}
            for file_ in os.listdir("resources/modules/StatisticalModelsTab/RegressionAlgorithms"):
                if '.py' in file_:
                    scriptName = file_[:file_.index(".py")]
                    mod = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(scriptName))
                    self.regressors[scriptName] = {}
                    self.regressors[scriptName]["module"] = getattr(mod, "Regressor")
                    self.regressors[scriptName]["name"] = self.regressors[scriptName]["module"].NAME
                    self.regressors[scriptName]['website'] = self.regressors[scriptName]["module"].WEBSITE
                    self.regressors[scriptName]['description'] = self.regressors[scriptName]["module"].DESCRIPTION

            for file_ in os.listdir("resources/modules/StatisticalModelsTab/PreProcessingAlgorithms"):
                if '.py' in file_:
                    scriptName = file_[:file_.index(".py")]
                    mod = importlib.import_module("resources.modules.StatisticalModelsTab.PreProcessingAlgorithms.{0}".format(scriptName))
                    self.preProcessors[scriptName] = {}
                    self.preProcessors[scriptName]["module"] = getattr(mod, "preprocessor")
                    self.preProcessors[scriptName]["name"] = self.preProcessors[scriptName]["module"].NAME
                    self.preProcessors[scriptName]["description"] = self.preProcessors[scriptName]["module"].DESCRIPTION
            
            for file_ in os.listdir("resources/modules/StatisticalModelsTab/FeatureSelectionAlgorithms"):
                if '.py' in file_:
                    scriptName = file_[:file_.index(".py")]
                    mod = importlib.import_module("resources.modules.StatisticalModelsTab.FeatureSelectionAlgorithms.{0}".format(scriptName))
                    self.featureSelectors[scriptName] = {}
                    self.featureSelectors[scriptName]["module"] = getattr(mod, "FeatureSelector")
                    self.featureSelectors[scriptName]["name"] = self.featureSelectors[scriptName]["module"].NAME
                    self.featureSelectors[scriptName]["description"] = self.featureSelectors[scriptName]["module"].DESCRIPTION
            
            mod = importlib.import_module("resources.modules.StatisticalModelsTab.CrossValidationAlgorithms")
            for cv, class_ in inspect.getmembers(mod, inspect.isclass):
                self.crossValidators[cv] = {}
                self.crossValidators[cv]["module"] = class_
                self.crossValidators[cv]["name"] = class_.NAME
            
            mod = importlib.import_module("resources.modules.StatisticalModelsTab.ModelScoring")
            self.scorers["class"] = getattr(mod, "Scorers")
            self.scorers['info'] = self.scorers["class"].INFO
            self.scorers["module"] = mod
            for scorer, scorerFunc in inspect.getmembers(self.scorers['class'], inspect.isfunction):
                self.scorers[scorer] = scorerFunc
            
            self.dataTable = dataTable
            self.modelInit = modelInit
            self.datasetTable = datasetTable
    
            #
        def runDate(self, i):
            self.rg = RegressionWorker(self, modelRunTableEntry=self.modelInit.iloc[i])
            self.rg.setData()
            self.rg.run()
    
    p_ = p(dataTable, modelInitTable, datasetTable)

    
    # Create an output dataframe
    percentiles = list(range(2,100,2))
    cols = ['_{0}'.format(pct) for pct in range(2, 100, 2)] + ['actual']
    dfOut = pd.DataFrame(index = pd.DatetimeIndex([]), columns=cols)

    def saveFile(*args):
        print("Exiting Safely")
        dfOut.to_csv("exited_hindcasts8.csv")
        sys.exit()
        
    atexit.register(saveFile)
    signal.signal(signal.SIGTERM, saveFile)
    signal.signal(signal.SIGINT, saveFile)

    # Run the dates
    for i, row in p_.modelInit.iterrows():
        date = row['ModelTrainingPeriod'].split('/')[2] + ' ' + row["ForecastIssueDate"]
        print("Processing date: ", date)
        
        # Get the best models
        #try:
        p_.runDate(i)
        #except Exception as E:
        #    print("  ! Couldn't run date: {0}".format(date))
        #    print(E)
        #    continue
        # Create X, Y arrays
        xTraining = []
        xTest = []
        excludeYears = []

        # Set the start and end dates for the model training period
        modelTrainingStrings = row['ModelTrainingPeriod'].split('/') 
        trainingDates = list(map(int, modelTrainingStrings[:2]))
        if len(modelTrainingStrings) > 2:
            excludeYears = list(map(int, modelTrainingStrings[2].split(',')))

        # Iterate over predictor datasets and append to arrays
        for j in range(len(row['PredictorPool'])):

            data = resampleDataSet(
                p_.dataTable.loc[(slice(None), row['PredictorPool'][j]), 'Value'],
                row['PredictorPeriods'][j],
                row['PredictorMethods'][j]
                )

            data.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in data.index], axis = 0, inplace = True)
            data = data.loc[trainingDates[0]: trainingDates[1]]
            #print(data)
            idx = list(filter(lambda date: date not in excludeYears, data.index))
            xTraining.append(list(data.loc[idx])) # Training Data
            xTest.append(list(data.loc[excludeYears]))

        # Compute the target data
        y = resampleDataSet(
            p_.dataTable.loc[(slice(None), row['Predictand']), 'Value'],
            row['PredictandPeriod'],
            row['PredictandMethod']
        )
        y.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in y.index], axis = 0, inplace = True)
        data = y.loc[trainingDates[0]: trainingDates[1]]
        actual = float(y.loc[excludeYears[0]])
        idx = list(filter(lambda date: date not in excludeYears, data.index))
        yTraining = y.loc[idx].values # Training Data
        

        # Add any missing data for the current water year to the arrays
        maxListLength = max([len(i) for i in xTraining])
        [i.append(np.nan) for i in xTraining if len(i) < maxListLength]

        # Convert data lists to numpy arrays
        xTraining = np.array(xTraining).T
        xTest = np.array(xTest).T
        yTraining = np.array(yTraining).reshape(-1,1)
        XY = np.hstack([xTraining, yTraining])
        XY = np.vstack([XY, np.append(xTest, np.nan).reshape(1,-1)])

        # Use K-means clustering to choose the best model from 20 separate clusters
        #modelList = np.array([model['Model'] for model in p_.rg.resultsList])
        modelList = p_.rg.resultsList
        #est = KMeans(n_clusters=50)
        #est.fit(modelList)
        #idx = np.unique(est.labels_, return_index=True)[1]
        #modelList = [p_.rg.resultsList[idx_] for idx_ in idx]
        #sortScores(modelList)
        #modelList.reverse()
        print('\n')
        for t, model in enumerate(modelList[:1]):
            m = model['Model']
            m = ''.join(['1' if tt else '0' for tt in m])
            m = m.replace("0", Style.DIM + "0" + Style.RESET_ALL)
            m = m.replace("1", Style.BRIGHT + "1" + Style.RESET_ALL)
            
            print("{0:<2}: {1} {2} {3}".format(t,m,model['Score'],model['Method']))
        print()

        # Iterate over a random sample of the 50 best models, including the best one 
        #idx = np.array(np.append([1], np.random.permutation(np.arange(2,50))[:25]))

        results = np.array([])

        for model in modelList[:1]:

            # Get the filtered model data onyl
            XY_ = XY[:, model['Model']+[True]]


            # Run a bootstrap on the datasets
            method = model['Method'].split('/')
            preprocessor = p_.preProcessors[method[1]]['module']
            regressor = p_.regressors[method[2]]['module']
            crossValidator = method[3]
            try:
                results = np.append(results,PredictionIntervalBootstrap.computePredictionInterval(p_.rg, XY_, preprocessor, regressor, crossValidator, ['ADJ_R2', 'MSE']))
            except Exception as E:
                print(E)
                continue
        # '_90', '_70', '_50', '_30', '_10', 'actual'
        results = np.sort(results)
        pct_ = list(np.percentile(results, percentiles))
        dfOut.loc[pd.to_datetime(date)] = pct_ + [actual]
        print(' - '.join(list(map(lambda x: str(round(x, 1)), [pct_[4],pct_[14],pct_[24],pct_[34],pct_[44]]))), 'ACTUAL:', actual)
        print('\n')
        if i%15 == 0:
            dfOut.to_csv("results_hindcasts8.csv")
            
    
    # from resources.modules.StatisticalModelsTab import PredictionIntervalBootstrap
    # import time
    # import warnings
    # import random
    # warnings.filterwarnings("ignore")
    
    # import matplotlib.pyplot as plt
    # #plt.ion()
    # import sys
    # from scipy.stats import iqr
    # from sklearn.neighbors import KernelDensity
    # import matplotlib.colors as mc
    # COLORS = list(mc.CSS4_COLORS.keys())
    # random.shuffle(COLORS)

    # from PyQt5 import QtWidgets,QtCore
    # from workspace_2 import PredictorGrid

    # app = QtWidgets.QApplication(sys.argv)
    
    # # Load some toy data
    # datasetTable = pd.read_pickle("toyDatasets.pkl")
    # dataTable = pd.read_pickle("toyData.pkl")
    # modelInit = pd.read_pickle("toyModelInit.pkl")

    # modelInit.loc[100]['FeatureSelectionTypes'] = ['FeatSel_BruteForce']
    
    
    # # Fake Parent Object
    # class p(object):
    #     def __init__(self, dataTable=None, modelInit = None, datasetTable=None):
    #         #QtWidgets.QWidget.__init__(self)
    #         #self.thread = QtCore.QThreadPool()
            
    #         self.dataTable = dataTable
    #         self.modelInit = modelInit
    #         self.datasetTable = datasetTable
    
    #         self.rg = RegressionWorker(self, modelRunTableEntry=self.modelInit.iloc[0])
            
    #         self.forecastIssueDate = pd.to_datetime('2019-04-01')
    
    # p_ = p(dataTable, modelInit, datasetTable)

    # # Initialize regression worker
    # p_.rg.setData()
    
    # # Run the regression worker
    # a = time.time()
    # p_.rg.run()
    # b = time.time()

    # # Print results
    # [print(f) for f in p_.rg.resultsList[:30]]

    # # Do a prediction with the best equation
    # best_equation = p_.rg.resultsList[0]
    # preproc = best_equation['Method'].split("/")[1]
    # regr = best_equation['Method'].split("/")[2]
    # cval = best_equation['Method'].split("/")[3]
    # xt, yt = p_.rg.xTraining, p_.rg.yTraining

    # # put the observations in the right format
    # XY = np.hstack((xt, yt))
    # lastRow = np.full((1, XY.shape[1]), np.nan)

    # for i in range(xt.shape[1]):

    #     data = resampleDataSet(
    #         dataTable.loc[(slice(None), modelInit.iloc[0]['PredictorPool'][i]), 'Value'],
    #         modelInit.iloc[0]['PredictorPeriods'][i],
    #         modelInit.iloc[0]['PredictorMethods'][i]
    #     )
    #     data = data.loc[data.index.year == p_.forecastIssueDate.year]
    #     lastRow[0][i] = data
    
    # #lastRow = lastRow.flatten()
    # XY = np.vstack((XY, lastRow))

    # def plot_forecast(equation, XY, i):
    #     preproc = equation['Method'].split('/')[1]
    #     regr = equation['Method'].split("/")[2]
    #     cval = equation['Method'].split("/")[3]
    #     model = [True if i == '1' else False for i in equation['Model']] + [True]
    #     XY_ = XY[:, model]
    #     preproc_ = importlib.import_module("resources.modules.StatisticalModelsTab.PreProcessingAlgorithms.{0}".format(preproc))
    #     regressor_ = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(regr))
    #     results = PredictionIntervalBootstrap.computePredictionInterval(XY_, preproc_.preprocessor, regressor_.Regressor, cval)

    #     # Histogram up that prediction!
    #     total_number = len(results)
    #     p90 = results[int(total_number/10)]
    #     p50 = results[int(total_number/2)]
    #     p10 = results[total_number - int(total_number/10)]

    #     iqr_ = iqr(results)
    #     std_ = np.std(results)
    #     h = 0.9*(min(iqr_, std_))*pow(total_number, -1/5)

    #     # Compute KDE
    #     kde = KernelDensity(bandwidth=h).fit(results.reshape(-1,1))
    #     xs = np.linspace(p10 - 800, p90 + 800, 1000)
    #     log_dens = kde.score_samples(xs.reshape(-1,1))

    #     idx = int(equation['Model'], 2)

    #     plt.hist(results, bins=int(len(results)/30), normed=True, facecolor = COLORS[i], alpha = 0.6)
    #     plt.plot(xs, np.exp(log_dens), color=COLORS[i])
    
    # for i, mod in enumerate(p_.rg.resultsList[0:100:10]):
    #     print(mod['Model'])
    #     plot_forecast(mod, XY, i)

    # plt.xlim((0, 1500))

    # plt.show()
