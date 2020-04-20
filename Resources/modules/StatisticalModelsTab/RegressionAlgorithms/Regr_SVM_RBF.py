"""
Script Name:    Regr_SVM_RBF

Description:    Defines an algorithm to perform
                support vector machine regression
                using a radial basis function kernel.
"""

from resources.modules.StatisticalModelsTab import CrossValidationAlgorithms, ModelScoring
import numpy as np
import sys
from sklearn.svm import SVR


class Regressor(object):

    NAME = "Support Vector Machine - RBF Regression"
    WEBSITE = "https://en.wikipedia.org/wiki/Support-vector_machine"

    def __init__(self, parent = None, crossValidation = None, scoringParameters = None):

        # Parse arguments
        self.parent = parent
        self.crossValidation = crossValidation if crossValidation != None else "KFOLD_5"
        self.scoringParameters = scoringParameters if scoringParameters != None else ["ADJ_R2"]

        # Data Initializations
        self.x = np.array([[]])     # Raw X Data
        self.y = np.array([])       # Raw Y Data
        self.y_p = np.array([])     # Model Predictions

        # Set up cross validator, and scorers
        self.scorerClass = self.parent.parent.scorers['class']()
        self.scorers = [getattr(self.scorerClass, self.parent.parent.scorers[scorer]) for scorer in self.scoringParameters]
        self.crossValidator = self.parent.parent.crossValidators[self.crossValidation]['module']()
        
        # Intialize dictionaries to store scores
        self.cv_scores = {}
        self.scores = {}
        self.y_p_cv = []

        # Initialize the regressor
        self.regressor = SVR(C=5.0)

        return

    def regress(self, x, y):
        """
        """
        X_ = np.concatenate((np.ones(shape=x.shape[0]).reshape(-1,1), x), 1)
        self.regressor.fit(X_,y)

        return np.nan, np.nan


    def fit(self, x, y, crossValidate = False):
        """
        """
        # Set the data references
        self.x = x
        self.y = y

        # Cross Validate if necessary
        if crossValidate:

            # Create a list to store cross validated predictions
            self.y_p_cv = np.array([], dtype=np.float32)

            # Iterate over the cross validation samples and compute regression scores
            for xsample, ysample, xtest, _ in self.crossValidator.yield_samples(X = self.x, Y = self.y):

                coef, intercept = self.regress(xsample, ysample)
                self.y_p_cv = np.append(self.y_p_cv, self.predict(xtest))
                
            # Compute CV Score
            self.cv_scores = self.score(self.y, self.y_p_cv, self.x.shape[1])
        
        # Fit the model
        self.coef, self.intercept = self.regress(self.x, self.y)

        # Compute the predicted values
        self.y_p = self.predict(self.x)

        # Compute a score array
        self.scores = self.score()
    
        return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)


    def predict(self, x):

        if len(x.shape) == 1:
            x_ = np.array([np.concatenate((np.array([1]), x))])
        else:
            x_ = np.concatenate((np.ones(shape=x.shape[0]).reshape(-1,1), x), 1)
        

        return np.array(self.regressor.predict(x_))
    
    def residuals(self):

        return self.y - self.y_p


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
        