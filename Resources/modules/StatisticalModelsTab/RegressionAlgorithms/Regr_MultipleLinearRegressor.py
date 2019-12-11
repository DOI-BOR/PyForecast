"""
Script Name:    Regr_MultipleLinearRegressor

Description:    Defines a numpy algorithm to perform Multiple Linear Regression on a dataset.
"""

from resources.modules.StatisticalModelsTab import CrossValidationAlgorithms, ModelScoring
import numpy as np

class Regressor(object):

    name = "Multiple Linear Regression"

    def __init__(self, crossValidation = None, scoringParameters = None):

        # Parse arguments
        self.crossValidation = crossValidation if crossValidation != None else "KFOLD_5"
        self.scoringParameters = scoringParameters if scoringParameters != None else ["ADJ_R2"]

        # Data Initializations
        self.x = np.array([[]])     # Raw X Data
        self.y = np.array([])       # Raw Y Data
        self.y_p = np.array([])     # Model Predictions

        # Fitting Parameters
        self.coef = []
        self.intercept = 0

        # Set up cross validator and scorers
        self.scorers = [getattr(ModelScoring, param) for param in self.scoringParameters]
        self.crossValidator = getattr(CrossValidationAlgorithms, self.crossValidation)
        self.cv_scores = {}
        self.scores = {}
        self.y_p_cv = []

        return


    def regress(self, x, y):
        """
        Performs the MLR/OLS regression between x and y.
        Standard Ordinary Least Squares. Solves the
        matrix formulation of OLS, as seen at
        https://en.wikipedia.org/wiki/Ordinary_least_squares
        """

        # Concatenate a row of 1's to the data so that we can compute an intercept
        X_ = np.concatenate((np.ones(shape=x.shape[0]).reshape(-1,1), x), 1)

        # Compute the coefficients and the intercept
        coef_all = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(y)
        coef = coef_all[1:]
        intercept = coef_all[0]

        return coef, intercept


    def fit(self, x, y, crossValidate = False):
        """
        Fits the model with the x and y data, optionally
        cross validates the model and stores cross validation
        scores in the self.cv_scores variable.
        """

        # Set the data references
        self.x = x
        self.y = y

        # Fit the model
        self.coef, self.intercept = self.regress(self.x, self.y)

        # Compute the predicted values
        self.y_p = self.predict(self.x)

        # Compute a score array
        self.scores = self.score()

        # Cross Validate if necessary
        if crossValidate:

            # Create a list to store cross validated predictions
            self.y_p_cv = np.array([])

            # Iterate over the cross validation samples and compute regression scores
            for xsample, ysample, xtest, _ in self.crossValidator.yield_samples(X = self.x, Y = self.y):

                coef, intercept = self.regress(xsample, ysample)
                self.y_p_cv = np.append(self.y_p_cv, np.dot(xtest, coef) + intercept)
                
            # Compute CV Score
            self.cv_scores = self.score(self.y, self.y_p_cv, self.x.shape[1])
    
        return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)

    
    def residuals(self):
        """
        Returns the residual time series 
        from the model.
        """
        return self.y - self.y_p


    def predict(self, x):
        """
        Makes a prediction on 'x'
        using the fitted model.
        """
        return np.dot(x, self.coef) + self.intercept


    def score(self, y_obs = [], y_p = [], n_features = None):
        """
        Scores the model using the supplied scorers.
        Scores y_obs against y_p. Uses the supplied
        y_p and y_obs (if given), otherwise uses
        the fitted model.
        """

        y_obs = self.y if (y_obs == []) else y_obs
        y_p = self.y_p if (y_p == []) else y_p
        n_features = self.x.shape[1] if (n_features == None) else n_features

        return {self.scoringParameters[i]: scorer(y_obs, y_p, n_features) for i, scorer in enumerate(self.scorers)}