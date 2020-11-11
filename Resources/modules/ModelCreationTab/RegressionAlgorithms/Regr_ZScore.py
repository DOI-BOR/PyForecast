"""
Script Name:    Regr_ZScore

Description:    Computes a composite predictor by
                converting each predictor to a z-score,
                then regressing the z scores against 
                the target, then createing one predictor
                as the r2 weighted sums of the 
                z score predictors

"""

import numpy as np
import pandas as pd
from resources.modules.ModelCreationTab import CrossValidationAlgorithms, ModelScoring

class Regressor(object):
    """
    """
    NAME = "Z-Score Regression"
    WEBSITE = "https://directives.sc.egov.usda.gov/OpenNonWebContent.aspx?content=34239.wba"
    DESCRIPTION = "Applies a Z-Score dimensionality reduction to the input data and solves the Ordinary Least Squares Formulation for the Composite Z-Score data."

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
        self.zcoef = []
        self.zintercept = []
        self.zRsq = []

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
        """

        # Don't score empty or single-variable combinations
        if x.shape[1] <= 1:
            self.cv_scores = {self.scoringParameters[i]: np.nan for i, scorer in enumerate(self.scorers)}
            self.scores, self.y_p_cv, self.y_p = np.nan, np.nan, np.nan

            return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)

        # Set the data references
        self.x = x
        self.y = y
        self.xMean = np.nanmean(x, axis = 0)
        self.xStd = np.nanstd(x, axis = 0, ddof = 1)

        # Convert all the x data to z-scores
        self.z = (self.x - self.xMean) / self.xStd
        # Get RSQ values of each Z with Y
        yz = pd.DataFrame(np.column_stack((self.y, self.z)))
        zRsq = yz.corr()[0] * yz.corr()[0]
        self.zRsq = zRsq[1:]
        self.zRsq.reset_index(drop=True, inplace=True)

        # Calculate multi-component values MC
        mc = self.ConvertToMultiComponentIndex(self.x)

        # Fit a linear y=mx+b model
        self.zcoef, self.zintercept = self.regress(mc, self.y)

        # Convert model coefficients to regular coefficients
        self.coef = [0] * len(self.zRsq)
        self.intercept = self.zintercept
        for ithTerm in range(0, len(self.zRsq)):
            coeffTerm = self.zcoef[0] * self.zRsq[ithTerm] / (self.xStd[ithTerm] * sum(self.zRsq))
            self.coef[ithTerm] = coeffTerm
            self.intercept = self.intercept + coeffTerm * self.xMean[ithTerm] * -1

        # Compute the predicted values
        self.y_p = self.predict(self.x)

        # Compute a score array
        self.scores = self.score()

        # Cross Validate if necessary
        if crossValidate:

            # Create a list to store cross validated predictions
            self.y_p_cv = np.array([], dtype=np.float32)

            # Iterate over the cross validation samples and compute regression scores
            for xsample, ysample, xtest, _ in self.crossValidator.yield_samples(X=mc, Y=self.y):
                coef, intercept = self.regress(xsample, ysample)
                self.y_p_cv = np.append(self.y_p_cv, np.dot(xtest, coef) + intercept)

            # Compute CV Score
            self.cv_scores = self.score(self.y, self.y_p_cv, mc.shape[1])

        return (self.scores, self.y_p, self.cv_scores, self.y_p_cv) if crossValidate else (self.scores, self.y_p)


    def ConvertToMultiComponentIndex(self, x):
        z = pd.DataFrame(((x - self.xMean) / self.xStd))
        # catch case when issuing a single model prediction via 1-row of data
        if z.shape[1] == 1:
            z.reset_index(drop=True,inplace=True)
            z = z.T
            z.reset_index(drop=True,inplace=True)
        zWeighted = z.multiply(self.zRsq)

        # Calculate multi-component values MC
        # Create dframe of RSQ values
        zRsqds = pd.DataFrame(index=range(0, len(zWeighted)), columns=zWeighted.columns, dtype='float')
        zRsqds.loc[0] = self.zRsq.T
        zRsqds.ffill(inplace=True)
        # Create mask to locate NaNs
        zWeightedNan = zWeighted.isna()
        zeros = pd.DataFrame(np.zeros((zRsqds.shape[0], zRsqds.shape[1])))
        # Replace NaNs with zeros
        zRsqds.mask(zWeightedNan, zeros)
        zWeighted.mask(zWeightedNan, zeros)
        # Calculate numerators and denominators for the weighted multi-component index
        numerators = zWeighted.sum(axis=1)
        denominators = zRsqds.sum(axis=1)
        mc = numerators / denominators
        mc = np.array(mc)
        mc = np.reshape(mc, (len(mc), 1))

        return mc


    def residuals(self):
        return self.y - self.y_p


    def predict(self, x):
        """
        Makes a prediction on 'x'
        using the fitted model.
        """
        # Convert X to MC index
        mc = self.ConvertToMultiComponentIndex(x)

        return np.dot(mc, self.zcoef) + self.zintercept


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