
import numpy as np
from tqdm import tqdm
import os
import sys
sys.path.append(os.getcwd())


def computePredictionInterval(parent, observations, preprocessor, regressor, crossValidator, scoringParameters = None, nRuns=10000):
    """
    This function bootstraps the original data nRuns (10,000 by default) times to
    develop an estimate of the prediction interval of the 
    new prediction, unbiased by any model or parameter assumptions 
    (e.g. normality).
    
     TAKEN FROM THIS REFERENCE:
     https://stats.stackexchange.com/questions/226565/bootstrap-prediction-interval

    inputs:
        -observations = a matrix of the observations used to create the prediction
                        The matrix is of the form:
                        [
                            [X1, X2, X3, ..., Y]
                            [...]
                            [X1, X2, X3, ..., NaN]
                        ]
                        Note that the last Y value is unfilled, as we don't have a prediction yet
        -preprocessor = function to use as the preprocessor.
        -regressor =    function to use as the regressor.
        -crossValidator=function to use as the crossValidator.
    
    outputs:
        -predictions =  array of predictions from the bootstrapping, corresponding to 
                        1% to 99% exceedance probabilities. i.e. the predictions[50] value
                        is the median forecast, and the predictions[10] value is the forecast
                        corresponding to the 10% exceedance probability.
    """

    # Begin by processing the observations
    processedObservations = preprocessor(data = observations[:-1])

    # Get the X Values and the Y Values
    x = processedObservations.getTransformedX()
    y = processedObservations.getTransformedY()

    y = y[~np.isnan(x).any(axis=1)]
    x = x[~np.isnan(x).any(axis=1)]

    # Initialize the regressor with the crossValidator
    model = regressor(parent, crossValidation = crossValidator, scoringParameters = scoringParameters if scoringParameters != None else None)

    # Create a prediction using the original data
    model.fit(x,y)
    xTest = processedObservations.transform(observations[-1])
    prediction = model.predict(xTest[:-1].reshape(1,-1))

    # Initialize a list of prediction errors
    nCount = nRuns# int(nRuns/5)
    predictionErrors = np.full(nCount, np.nan)

    # Function to get a prediction
    def generateBootstrap(dummy):

        # Generate a random list of indices to sample from the original data (Ensure we have at least 20% of samples)
        randomIndices = np.random.randint(low = 0, high = len(x) - 1, size = len(x))
        while len(np.unique(randomIndices)) < len(x)/5:
            randomIndices = np.random.randint(low = 0, high = len(x) - 1, size = len(x))

        # Generate random cases from random indices
        randomX = x[randomIndices]
        randomY = y[randomIndices]

        # Generate the prediction from the bootstrapped model
        model.fit(randomX, randomY)
        bootstrapPrediction = model.predict(xTest[:-1].reshape(1,-1))

        # generate the bootstrap error set
        bootstrapErrors = model.residuals()

        # Calculate the prediction error
        predictionError = bootstrapErrors + prediction - bootstrapPrediction

        return predictionError

    # Iterate 10,000 times to create 10,000 possible predictions
    allPredictionErrors = np.array(sorted([item for sublist in map(generateBootstrap, tqdm(predictionErrors)) for item in sublist], reverse = True))

    # Generate the prediction interval series
    predictions = allPredictionErrors + prediction 
   
    # Retransform the predictions back into the real space using the preprocessor
    predictions = np.concatenate([np.full((len(predictions), x.shape[1]), np.nan),predictions.reshape(-1,1)], axis=1)
    predictions = processedObservations.inverseTransform(predictions)[:,-1].ravel()

    return predictions



# Debugging
if __name__ == '__main__':

    from sklearn.datasets import make_regression, load_boston, load_diabetes
    import matplotlib.pyplot as plt
    import pandas as pd
    import bitarray as ba
    from resources.modules.ModelCreationTab.RegressionAlgorithms import Regr_GammaGLM, Regr_MultipleLinearRegressor
    from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
    from resources.modules.ModelCreationTab import RegressionWorker
    #from resources.modules.ModelCreationTab.PreProcessingAlgorithms import PreProc_NoPreProcessing
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

    models = [ba.bitarray('11100010110001110011011'), ba.bitarray('11100010110001110011011'), ba.bitarray('11100010110001110011011')]

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

    # Set up predictors from toy dataset
    predictors = ['HucPrecip'] + ['Nino3.4']*3 + datasets[2:]
    periodList = ["R/1990-02-01/P2M/F1Y","R/1990-02-01/P1M/F1Y","R/1990-01-01/P1M/F1Y","R/1990-03-01/P1M/F1Y",'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-04-01/P1D/F1Y', 'R/1990-03-01/P1M/F1Y', 'R/1989-10-01/P6M/F1Y', 'R/1990-03-01/P1M/F1Y']
    methodList = ["accumulation","average","average","average",'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'first', 'average', 'accumulation', 'average']

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
                    ['Regr_MultipleLinearRegressor'], 
                    'KFOLD_5', 
                    ['FeatSel_SequentialForwardFloating'], 
                    ["PreProc_NoPreProcessing"],
                    ['MSE']
                ]

    # Fake Parent Object
    class p(object):
        dataTable = df

    p_ = p()

    rg = RegressionWorker.RegressionWorker(parent = p_, modelRunTableEntry=dm.loc[1])

    # Load up some data
    #X, Y = load_boston(return_X_y=True)
    #X,Y = load_diabetes(return_X_y=True)
    #X, Y = make_regression(n_samples=35, n_features=8, n_informative=5, bias=10, noise=10, effective_rank=1, tail_strength=0.88,)
    #X = np.random.random(X.shape)
    #XY = np.concatenate((X, Y.reshape(-1,1)), axis=1)
    #new = np.array([[i + np.random.rand(1)[0]/1000 for i in X[0]] + [np.nan]])
    #XY = np.concatenate((XY, new))

    rg.setData()

    # Get the data back

    X, Y = rg.xTraining, rg.yTraining

    Y = Y[~np.isnan(X).any(axis=1)]
    X = X[~np.isnan(X).any(axis=1)]

    rdn = list(zip(X,Y))
    np.random.shuffle(rdn)

    X = np.array([i[0] for i in rdn])
    Y = np.array([i[1] for i in rdn])

    #Y = np.append(Y, np.nan)
    if Y.shape[0] != X.shape[0]:
        print('ERROR')
        input()

    XY = np.concatenate((X, Y.reshape(-1,1)), axis=1)

    # Define a dummy preprocessor
    class preprocessor(object):

        def __init__(self, data):

            self.data = data

        def getTransformedX(self):

            return self.data[:, :-1]

        def getTransformedY(self):

            return np.log(self.data[:,-1])
            
        def transform(self, data):

            return data

        def inverseTransform(self, data):

            return np.exp(data)
    
    # Define a dummy regressor
    class regressor(object):

        def __init__(self, cv):

            self.cv = cv
            self.coef = []
        
        def fit(self, X, Y):

            self.X = X
            X_ = np.concatenate((np.ones(shape=X.shape[0]).reshape(-1,1), X), 1)
            self.Y = Y
            self.coef = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(Y)
        
        def residuals(self):

            return [self.Y[i] - self.predict(x) for i, x in enumerate(self.X)]

        def predict(self, X):
            
            intercept = self.coef[0]
            coefs = self.coef[1:]
            p = intercept
            for xi, bi in zip(X, coefs): p += (bi*xi)
            return np.float16(p)

    

    # Compute a prediction interval for the new observation
    l = computePredictionInterval(XY, preprocessor, Regr_MultipleLinearRegressor.Regressor, 'KFOLD_5')

    # Get the indices of the 10th and 90th percentile
    idx10 = int(len(l)/10)
    idx90 = len(l) - idx10

    # Plot the prediction and the interval
    n, bins, patches = plt.hist(l, bins=100)
    print(len(n), len(bins))
    [pa.set_ec("k") for pa in patches]

    print("""
Actual:     {6}
Prediction: {0} 
10%:        {1} (prediction + {4})
90%:        {2} (prediction - {5})

yRange:     {3}
    """.format(np.median(l), l[idx10], l[idx90], (min(Y), max(Y)), l[idx10] - np.median(l), np.median(l) - l[idx90], Y[-1] ))
    plt.vlines([l[idx10], l[idx90], np.median(l)], [0,0,0], [8000,8000,8000], colors='r')
    plt.show()
        