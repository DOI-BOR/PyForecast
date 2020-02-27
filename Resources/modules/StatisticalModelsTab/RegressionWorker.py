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
sys.path.append(os.getcwd())
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
import multiprocessing as mp
import importlib
import bitarray as ba
from resources.modules.StatisticalModelsTab.ModelScoring import sortScores
from operator import itemgetter

class RegressionWorker(object):

    def __init__(self, parent = None, modelRunTableEntry = None, *args, **kwargs):
        """
        Initialize the RegressionWorker Object
        """

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
                    
                    # Iterate over the feature selection methods
                    for featSel in self.featureSelectionSchemes:

                        # In our first run of the feature selection scheme, 
                        # use the scheme's default initial model. In the 
                        # case of brute force scheme, the scheme will
                        # see all models from this initialization
                        if i == 0:
                            
                            #print("i 0")

                            # Initialize the feature selection scheme with the scheme's default model
                            f = featSel.FeatureSelector(    
                                        parent = self, 
                                        regression = regression, 
                                        crossValidation = self.crossValidationScheme, 
                                        scoringParameters = self.scoringParameters)
                                    

                        # Otherwise, generate a random model.
                        else:
                            #print('i 1')

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
        #self.resultsList = [i for i in self.resultsList if np.all(np.isnan(j[1]) for j in list(i['Score'].items()))]

        # Sort the scores
        #func = itemgetter("Scores")
        #print(self.resultsList[0])
        sortScores(self.resultsList)
        self.resultsList.reverse()

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
    df = pd.read_csv('BOYR_SNODAS_TEST.csv', index_col=0, parse_dates=True)
    
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
                "Preprocessors",    
                "ScoringParameters"         # E.g. ['ADJ_R2', 'MSE']
            ]
        )

    #model results table
    de = pd.DataFrame(
        index = pd.Index([], dtype=int, name='ForecastEquationID'),
        columns = [
                "EquationSource",       # e.g. 'NextFlow','NRCS', 'CustomImport'
                "EquationComment",      # E.g. 'Equation Used for 2000-2010 Forecasts'
                "EquationPredictand",   # E.g. 103011
                "PredictandPeriod",     # R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",      # E.g. Accumulation, Average, Max, etc
                "EquationCreatedOn",    # E.g. 2019-10-04
                "EquationIssueDate",    # E.g. 2019-02-01
                "EquationMethod",       # E.g. Pipeline string (e.g. PIPE/PreProc_Logistic/Regr_Gamma/KFOLD_5)
                "EquationSkill",        # E.g. Score metric dictionary (e.g. {"AIC_C": 433, "ADJ_R2":0.32, ...})
                "EquationPredictors",   # E.g. [100204, 100101, 500232]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M]
                "PredictorMethods"      # E.g. ['Average', 'First', 'Max']
            ]
    )
    
    # Set up predictors from toy dataset
    #predictors = ['HucPrecip'] + ['Nino3.4']*3 + datasets[2:]
    predictors = datasets[1:]
    print(predictors)
    #periodList = ["R/1990-02-01/P2M/F1Y","R/1990-02-01/P1M/F1Y","R/1990-01-01/P1M/F1Y","R/1990-03-01/P1M/F1Y",'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-03-01/P1M/F1Y', 'R/1989-10-01/P6M/F1Y', 'R/1990-03-01/P1M/F1Y']
    #methodList = ["accumulation","average","average","average",'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'average', 'accumulation', 'average']
    for date in pd.date_range("2019-01-01", "2019-04-01", freq='D'):
        periodList = ["R/2004-{0:02}-{1:02}/P1D/F1Y".format(date.month, date.day)]*len(predictors)
        #periodList = ["R/2004-04-01/P1D/F1Y"]*len(predictors)
        methodList = ["first"]*len(predictors)
        #print(len(periodList), len(predictors), len(methodList))
        # Create a model run entry
        perf = ['ADJ_R2']
        cv = 'LOO'
        regressionName = "Regr_MultipleLinearRegressor"
        #regressionName = "Regr_GammaGLM"
        dm.loc[1] = [   
                        '2003-10-01/2018-09-30', 
                        datasets[0],
                        'R/1990-04-01/P4M/F1Y', 
                        'accumulation', 
                        predictors,
                        [False]*(len(predictors)), 
                        periodList,
                        methodList,
                        [regressionName], 
                        cv, 
                        ['FeatSel_SequentialForwardFloating'], 
                        ['PreProc_NoPreProcessing'],
                        perf
                    ]

        # Fake Parent Object
        class p(object):
            dataTable = df
            forecastEquationsTable = de
            forecastIssueDate = '2017-04-01'

        p_ = p()

        # Initialize regressor
        rg = RegressionWorker(parent = p_, modelRunTableEntry=dm.loc[1])
        rg.setData()
        #print('yrange is {0} - {1}'.format(np.nanmin(rg.y), np.nanmax(rg.y)))

        # Run RegressionWorker
        #print('There are {0} possible combinations'.format(int('1'*(len(predictors)),2)+1))
        a = time.time()
        rg.run()
        b = time.time()

        ll = []
        for model in rg.resultsList:
            if '1' in model["Model"][-4:]:
                ll.append(model)
        #print('analyzed {0} combinations'.format(len(rg.computedModels.keys())))
        #print('ran in {0} sec'.format(b-a))
        #xdata = rg.xTraining
        #swe_means = np.nanmean(xdata[:,:], axis=0)
        #swe_means = [np.round(float(i), 6) for i in swe_means]
        #swe_vars = np.nanstd(xdata[:,:], axis=0)
        #swe_vars = [np.round(float(i), 6) for i in swe_vars]
        #[print(i) for i in rg.resultsList[:5]]
        #print("{0}, {9:05}, {1:05}, {2:05}, {3:05}, {4:05}, {5:05}, {6:05}, {7:05}, {8:05}".format(date, swe_means[0], swe_means[1], swe_means[2], swe_means[3], swe_vars[0], swe_vars[1], swe_vars[2], swe_vars[3], np.mean([i["Score"]['ADJ_R2'] for i in rg.resultsList[:5]])))
        print("{0}, {1}".format(date, np.mean([i["Score"]['ADJ_R2'] for i in ll[:5]]) ))
        #print(np.mean([i["Score"]['ADJ_R2'] for i in rg.resultsList[:5]]))
    input()

    # Sort Results by score
    d = pd.DataFrame().from_dict(rg.computedModels, orient='index')
    d.sort_values(by=perf, inplace=True, ascending=True)
    d.index.name = 'model'

    print("""============================
    The best model is:
    """)
    model = [bool(int(i)) for i in rg.resultsList[0]['Model']]
    #model = [bool(int(i)) for i in d.iloc[0].name]
    print("model is ", model)
    print([predictors[i] if m else None for i,m in enumerate(model)])
    x = rg.proc_xTraining[:, list(model)]
    y = rg.proc_yTraining[~np.isnan(x).any(axis=1)]
    x = x[~np.isnan(x).any(axis=1)]

    
    module = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(regressionName))
    regressionClass = getattr(module, 'Regressor')
    regression = regressionClass(crossValidation = cv, scoringParameters = perf)

    import matplotlib.pyplot as plt
    regression.fit(x,y)
    plt.plot(regression.predict(x), y, 'ro')
    plt.show()
    plt.plot([i for i in range(len(y))], regression.residuals(), 'ro')
    plt.show()

    
    trainStart, trainEnd = rg.trainingDates

    observations = np.concatenate([rg.xTraining, rg.yTraining], axis=1)

    xxx = np.full(rg.xTraining.shape[1], np.nan)

    for i in range(len(rg.modelRunTableEntry['PredictorPool'])):

            data = resampleDataSet(
                rg.parent.dataTable.loc[(slice(None), rg.modelRunTableEntry['PredictorPool'][i]), 'Value'],
                rg.modelRunTableEntry['PredictorPeriods'][i],
                rg.modelRunTableEntry['PredictorMethods'][i]
                )
            data = data.loc[data.index[0]:pd.to_datetime(p_.forecastIssueDate)]
            xxx[i] = data.values[-1] # Training Data
            
    
    # Compute the target data
    yyy = resampleDataSet(
        rg.parent.dataTable.loc[(slice(None), rg.modelRunTableEntry['Predictand']), 'Value'],
        rg.modelRunTableEntry['PredictandPeriod'],
        rg.modelRunTableEntry['PredictandMethod']
    )
    yyy = yyy.loc[yyy.index[0]:pd.to_datetime(p_.forecastIssueDate)]
    yyy = yyy.values[-1]

    lastrow = np.concatenate([xxx, np.array([yyy])])
    
    observations = np.concatenate([observations, np.array([lastrow])])
    
    preprocessor = rg.preprocessors[0].preprocessor

    observations = observations[:, list(model)+[True]]
    print("Prediction Year Data: ", observations[-1])

    l = PredictionIntervalBootstrap.computePredictionInterval(observations, preprocessor, regressionClass, 'LOO')
    print(l)
    l = l*86400/43560000
    # Get the indices of the 10th and 90th percentile
    idx10 = int(len(l)/10)
    idx90 = len(l) - idx10

    # Plot the prediction and the interval
    #from scipy import stats
    #from sklearn.neighbors import KernelDensity
    #bandw = 1.06*min(stats.iqr(l)/1.34, np.nanstd(l))*pow(len(l),-0.2)
    #x_ = np.linspace(max(int(np.nanmin(l)), np.nanmin(rg.y)), min(int(np.nanmax(l)), np.nanmax(rg.y)), 1000)[:, np.newaxis]
    #kde = KernelDensity(bandwidth=bandw).fit(l.reshape(-1,1))
    #log_dens = kde.score_samples(x_)
    #plt.fill(x_[:, 0], np.exp(log_dens), fc="#AAAAFF")
    n, bins, patches = plt.hist(l, bins=100)
    print(len(n), len(bins))
    [pa.set_ec("k") for pa in patches]
    #mm = max(np.exp(log_dens))
    sc = 0.0019834710743801653
    print("""
Actual:     {6}
POR Median: {7}
Prediction: {0} 
10%:        {1} (prediction + {4})
90%:        {2} (prediction - {5})

yRange:     {3} - {8}
    """.format(np.median(l), l[idx10], l[idx90], sc*np.nanmin(rg.y), l[idx10] - np.median(l), np.median(l) - l[idx90], sc*lastrow[-1], sc*np.nanmedian(rg.y), sc*np.nanmax(rg.y)))
    plt.vlines([l[idx10], l[idx90], np.median(l)], [0,0,0], [8000,8000,8000], colors='r')
    plt.show()
