"""
Script Name:    Regr_PCARegressor

Description:    Performs PCA Regression as defined by 
                https://ncss-wpengine.netdna-ssl.com/wp-content/themes/ncss/pdf/Procedures/NCSS/Principal_Components_Regression.pdf
"""

from resources.modules.ModelCreationTab import CrossValidationAlgorithms, ModelScoring
import numpy as np
import sys

class Regressor(object):

    NAME = "Principal Components Regression"
    WEBSITE = "https://en.wikipedia.org/wiki/Principal_component_analysis"
    DESCRIPTION = "Applies Principal Component dimensionality reduction and solves the ordinary least squares formulation for the optimal number of principal components."

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

        # PCA parameters

        # Set up cross validator, and scorers
        self.scorerClass = self.parent.parent.scorers['class']()
        self.scorers = [getattr(self.scorerClass, scorer) for scorer in self.scoringParameters]
        self.crossValidator = self.parent.parent.crossValidators[self.crossValidation]['module']()
        
        # Intialize dictionaries to store scores
        self.cv_scores = {}
        self.scores = {}
        self.y_p_cv = []

        return


    def regress(self, PCs, y):
        """
        Iterate over the PCs and create the regressions
        """

        # Create an array to score PC combinations
        score = {}
        oldScore = {}

        # Iterate over the PCs and score the combinations
        for i in range(1, PCs.shape[1]):
            
            # Create the X data
            X_ = PCs[:, :i]

            # append 1's to the X data
            X_ = np.hstack([X_, np.full((X_.shape[0], 1), 1)])

            # Compute the coefficients and the intercept
            coef_all = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(y)

            # Compute the score
            score = self.score(y, np.dot(X_, coef_all), self.x.shape[1])

            # Initialize score / num_pcs
            if i == 1:
                oldScore = score
                num_pcs = i
                coef_ = coef_all

            # Check if the new score is better than the old score and if it is, save the model parameters
            if ModelScoring.scoreCompare(score, oldScore) and i > 1:
                oldScore = score
                num_pcs = i
                coef_ = coef_all

        return coef_, num_pcs


    def fit(self, x, y, crossValidate = False):
        """
        """

        # Don't score empty or single-variable combinations
        if x.shape[1] <= 1:

            self.cv_scores = {self.scoringParameters[i]: np.nan for i, scorer in enumerate(self.scorers)}
            self.scores, self.y_p_cv, self.y_p = np.nan, np.nan, np.nan

            return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)


        # Set the data references
        self.x = x
        self.y = y

        # Scale the data by subtracting the mean and dividing by stdev
        self.xMean = np.nanmean(x, axis = 0)
        self.xStd = np.nanstd(x, axis = 0, ddof = 1)
        self.standardX = (x - self.xMean) / self.xStd

        # Scale the y data
        self.yMean = np.nanmean(y)
        self.yStd = np.nanstd(y)
        self.standardY = (y - self.yMean) / self.yStd

        # Construct the Principal Components
        self.PCs, self.eigenvalues, self.eigenvectors = self.transformToPC(self.standardX)

        # Perform the regression to find the best equation
        self.pc_coef, self.num_pcs = self.regress(self.PCs, self.standardY)

        # Compute the predictions
        self.y_p = self.predict(self.x)

        # Compute the score
        self.scores = self.score(self.y, self.y_p_cv, self.x.shape[1])

        # Perform the cross-validation if needed
        if crossValidate:

            # Create a list to store cross validated predictions
            self.y_p_cv = np.array([], dtype=np.float32)

            # Iterate over the cross validation samples and compute regression scores
            for xsample, ysample, xtest, _ in self.crossValidator.yield_samples(X = self.standardX, Y = self.standardY):

                # Create sample PCs
                PCs, evals, evecs = self.transformToPC(xsample)

                # Create the X data
                X_ = PCs[:, :self.num_pcs]

                # Append a column of 1s to the PC data
                X_ = np.hstack([X_, np.full((X_.shape[0], 1), 1)])

                # Compute the coefficients and the intercept
                coef_all = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(ysample)

                # Convert the test set to PCs
                xtest = np.hstack([np.dot(xtest, evecs)[:,:self.num_pcs],np.full((xtest.shape[0], 1), 1)])

                self.y_p_cv = np.append(self.y_p_cv, (np.dot(xtest, coef_all)*self.yStd) + self.yMean)
                
            # Compute CV Score
            self.cv_scores = self.score(self.y, self.y_p_cv, self.x.shape[1])

        return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)


    def transformToPC(self, x):
        """
        Converts a 2-D array of predictor data to a 2-D array of principal 
        components and thier associated eigenvectors and eigenvalues
        """

        # Compute the covariance matrix
        cov = np.cov(x, rowvar = False, ddof = 1)

        # Compute the eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(cov)

        # Sort the eigenvalues in decreasing order
        idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, idx]
        eigenvalues = eigenvalues[idx]

        # Transform and return the parameters
        return np.dot(x, eigenvectors), eigenvalues, eigenvectors


    def leverage(self):
        """
        Returns the leverage of the response data for this model fit
        """
        X_ = self.PCs[:,:self.num_pcs]
        X = np.hstack([X_, np.full((X_.shape[0], 1), 1)])

        return np.diag(X.dot(np.linalg.inv(np.transpose(X).dot(X))).dot(np.transpose(X)))


    def residuals(self):
        """
        Returns the residual time series 
        from the model.
        """
        return self.y - self.y_p


    def predict(self, x):
        """
        """

        # Standardize the x-vector
        standardX  = (x - self.xMean) / self.xStd

        # Convert the x-vector into PC's
        PCs = np.dot(standardX, self.eigenvectors)

        X_ = PCs[:,:self.num_pcs]
        X_ = np.hstack([X_, np.full((X_.shape[0], 1), 1)])

        # Pare down to the number of PCs and make the predictions
        return (np.dot(X_, self.pc_coef)*self.yStd) + self.yMean
        

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
