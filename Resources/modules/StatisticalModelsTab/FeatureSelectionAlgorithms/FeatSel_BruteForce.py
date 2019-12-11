import importlib
from resources.modules.StatisticalModelsTab import ModelScoring
import bitarray as ba


class FeatureSelector(object):

    name = "Brute Force Selection"

    def __init__(self, parent = None, **kwargs):
        """
        """

        #

        # Create References to the predictors and the target
        self.predictorPool = parent.modelRunTableEntry['PredictorPool']
        self.target = parent.modelRunTableEntry['Predictand']
        self.parent = parent

        # Set up the Regression and Cross Validation
        self.regressionName = kwargs.get("regression", "Regr_MultipleLinearRegressor")
        module = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(self.regressionName))
        regressionClass = getattr(module, 'Regressor')
        self.regression = regressionClass(crossValidation = kwargs.get("crossValidation", None), scoringParameters = kwargs.get("scoringParameters", None))
        
        # Create variables to store the current predictors and performance
        self.numPredictors = len(self.predictorPool)
        self.totalNumModels = int('1'*self.numPredictors, 2) # Total number of models
        self.formatString = '0{0}b'.format(self.numPredictors)

        return
    

    def scoreModel(self, model):
        """
        Scores the model using the provided
        regression scheme. 
        """

        # Compile the data to fit with the regression method
        x = self.parent.x[:, list(model)]

        # Fit the model with the regression method and get the resulting score
        _, _, score, _ = self.regression.fit(x, self.parent.y, crossValidate = True)

        return score
    

    def logCombinationResult(self, model_str = None, score = None):
        """
        Under-defined function. Currently just adds the model to 
        the model list. Theoretically, we could use this 
        function to update graphics of model building, or
        do real-time analysis of models as they are being 
        built
        """
        self.parent.computedModels[model_str] = score
        
        return


    def iterate(self):
        """
        Iterates to perform the Sequential Forward Selection.
        The loop continues until the algorithm declines adding
        or subtracting any predictors from the model (i.e. adding
        or subtracting predictors is not increasing the score
        of the model.)
        """

        # Set up an iteration
        for i in range(self.totalNumModels + 1):
            
            model_str = format(i, self.formatString)
            model = ba.bitarray(model_str)
            score = self.scoreModel(model)
            self.logCombinationResult(model_str, score)

        return