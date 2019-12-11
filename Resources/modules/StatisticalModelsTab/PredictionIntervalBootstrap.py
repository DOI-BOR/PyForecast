
import numpy as np
from tqdm import tqdm

def computePredictionInterval(observations, preprocessor, regressor, crossValidator):
    """
    This function bootstraps the original data 10,000 times to 
    develop an estimate of the prediction interval of the 
    new prediction, unbiased by any model or parameter assumptions 
    (e.g. normality).

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
    processedObservations = preprocessor(data = observations)

    # Get the X Values and the Y Values
    x = processedObservations.getTransformedX()
    y = processedObservations.getTransformedY()

    # Initialize the regressor with the crossValidator
    model = regressor(cv = crossValidator)

    # Create a prediction using the original data
    model.fit(x[:-1],y[:-1])
    prediction = model.predict(x[-1])

    # Initialize a list of prediction errors
    predictionErrors = np.empty(10000)
    predictionErrors.fill(np.nan)

    # Function to get a prediction
    def generateBootstrap(dummy):

        # Generate a random list of indices to sample from the original data
        randomIndices = np.random.randint(low = 0, high = len(x) - 2, size = len(x) - 1)

        # Generate random cases from random indices
        randomX = x[randomIndices]
        randomY = y[randomIndices]

        # Generate the prediction from the bootstrapped model
        model.fit(randomX, randomY)
        bootstrapPrediction = model.predict(x[-1])

        # generate the bootstrap error set
        bootstrapErrors = model.residuals()

        # Calculate the prediction error
        predictionError = [prediction - bootstrapPrediction + error for error in bootstrapErrors]

        return predictionError

    # Iterate 10,000 times to create 10,000 possible predictions
    allPredictionErrors = sorted([item for sublist in map(generateBootstrap, tqdm(predictionErrors)) for item in sublist], reverse = True)

    # Generate the prediction interval series
    predictions = [prediction + error for error in allPredictionErrors]

    # Retransform the predictions back into the real space using the preprocessor
    predictions = processedObservations.inverseTransform(predictions)

    return predictions



# Debugging
if __name__ == '__main__':

    from sklearn.datasets import make_regression
    import matplotlib.pyplot as plt

    # Load up some data
    X, Y = make_regression(n_samples=35, n_features=8, n_informative=5, bias=10, noise=10, effective_rank=1, tail_strength=0.88,)
    #X = np.random.random(X.shape)
    XY = np.concatenate((X, Y.reshape(-1,1)), axis=1)
    new = np.array([[i + np.random.rand(1)[0]/1000 for i in X[0]] + [np.nan]])
    XY = np.concatenate((XY, new))

    # Define a dummy preprocessor
    class preprocessor(object):

        def __init__(self, data):

            self.data = data

        def getTransformedX(self):

            return self.data[:, :-1]

        def getTransformedY(self):

            return self.data[:,-1]
            
        def transform(self, data):

            return data

        def inverseTransform(self, data):

            return data
    
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
    l = computePredictionInterval(XY, preprocessor, regressor, None)

    # Get the indices of the 10th and 90th percentile
    idx10 = int(len(l)/10)
    idx90 = len(l) - idx10

    # Plot the prediction and the interval
    plt.hist(l, bins=30)
    plt.vlines(np.median(l), 0, 10, colors='r')

    print("""
Prediction: {0} 
10%:        {1} (prediction + {4})
90%:        {2} (prediction - {5})

yRange:     {3}
    """.format(np.median(l), l[idx10], l[idx90], (min(Y), max(Y)), l[idx10] - np.median(l), np.median(l) - l[idx90] ))

    plt.show()
        