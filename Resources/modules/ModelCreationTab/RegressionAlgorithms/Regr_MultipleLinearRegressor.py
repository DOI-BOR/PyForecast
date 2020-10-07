"""
Script Name:    Regr_MultipleLinearRegressor

Description:    Defines a simple numpy algorithm to perform Multiple Linear 
                Regression on a dataset.

                Multiple Linear Regression is defined in many publicly 
                available sources. Here is one from Penn State University
                that covers the topic extensively:
                https://online.stat.psu.edu/stat501/lesson/5/5.4

"""

from resources.modules.ModelCreationTab import CrossValidationAlgorithms, ModelScoring
import numpy as np
import sys

class Regressor(object):

    NAME = "Multiple Linear Regression"
    WEBSITE = "https://en.wikipedia.org/wiki/Ordinary_least_squares"
    DESCRIPTION = "Solves the Ordinary Least Squares formulation"

    def __init__(self, parent = None, crossValidation = None, scoringParameters = None):
        """
        Class Initializer.

        arguments:
            -crossValidation:   string describing which cross validation
                                method to use when using this regression
                                class. As of this writing, the options are
                                "KFOLD_5" (5 fold cross validation)
                                "KFOLD_10" (10 fold cross validation)
                                "LOO" (Leave-one-out AKA jacknife)
            -scoringParameters: list of scoring metrics to score models.
                                e.g. ['ADJ_R2', 'MSE', 'AIC_C']
        """

        # Parse arguments
        self.parent = parent
        self.crossValidation = crossValidation if crossValidation != None else "KFOLD_5"
        self.scoringParameters = scoringParameters if scoringParameters != None else ["ADJ_R2"]

        # Data Initializations
        self.x = np.array([[]])     # Raw X Data
        self.y = np.array([])       # Raw Y Data
        self.y_p = np.array([])     # Model Predictions

        # Fitting Parameters
        self.coef = []
        self.intercept = 0

        # Set up cross validator, and scorers
        self.scorerClass = self.parent.parent.scorers['class']()
        self.scorers = [getattr(self.scorerClass, scorer) for scorer in self.scoringParameters]
        self.crossValidator = self.parent.parent.crossValidators[self.crossValidation]['module']()
        
        # Intialize dictionaries to store scores
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

        try:
            # Compute the coefficients and the intercept
            coef_all = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(y)
            coef = coef_all[1:]
            intercept = coef_all[0]

        except:
            # Handle the case where the matrix formulation cannot be solved.
            coef_all = np.array([0]*X_.shape[1])
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
            self.y_p_cv = np.array([], dtype=np.float32)

            # Iterate over the cross validation samples and compute regression scores
            for xsample, ysample, xtest, _ in self.crossValidator.yield_samples(X = self.x, Y = self.y):

                coef, intercept = self.regress(xsample, ysample)
                self.y_p_cv = np.append(self.y_p_cv, np.dot(xtest, coef) + intercept)
                
            # Compute CV Score
            self.cv_scores = self.score(self.y, self.y_p_cv, self.x.shape[1])
    
        return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)

    
    def leverage(self):
        """
        Returns the leverage of the response data for this model fit
        """
        X = np.concatenate((np.ones(shape=self.x.shape[0]).reshape(-1,1), self.x), 1)

        return np.diag(X.dot(np.linalg.inv(np.transpose(X).dot(X))).dot(np.transpose(X)))
        

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

        # Check that the model is actually valid 
        # that is, there are less than n-1 predictors
        #       - There cannot be more than n-2 predictors
        #         or else the scoring does not work. Adjusted
        #         r2 and AICc rely on the fact that there are
        #         less predictors than observations
        if n_features > len(y_p) - 2:
            return {self.scoringParameters[i]: np.nan for i, scorer in enumerate(self.scorers)}

        return {self.scoringParameters[i]: scorer(y_obs, y_p, n_features) for i, scorer in enumerate(self.scorers)}