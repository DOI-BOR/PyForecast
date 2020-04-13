import importlib
from resources.modules.StatisticalModelsTab import ModelScoring
import bitarray as ba
import numpy as np


class FeatureSelector(object):

    name = "Brute Force Selection"

    def __init__(self, parent = None, **kwargs):
        """
        """
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
        x = self.parent.proc_xTraining[:, list(model)]

        # Check if we're using a regression model that requires non-NaN data
        if any(map(lambda x: self.regressionName in x, ["Regr_ZScore"])):
            y = self.parent.proc_yTraining

        else:
            y = self.parent.proc_yTraining[~np.isnan(x).any(axis=1)]
            x = x[~np.isnan(x).any(axis=1)]

        # Fit the model with the regression method and get the resulting score
        try:
            _, _, score, _ = self.regression.fit(x, y, crossValidate = True)

        except Exception as E:
            print(E)
            score = {self.regression.scoringParameters[i]: np.nan for i, scorer in enumerate(self.regression.scorers)}

        return score
    

    def logCombinationResult(self, model = None, score = None):
        """
        Under-defined function. Currently just adds the model to 
        the model list. Theoretically, we could use this 
        function to update graphics of model building, or
        do real-time analysis of models as they are being 
        built
        """
        # Update the visualization
        self.parent.updateViz(currentModel = model)

        # Get the model string
        modelStr = model.to01()

        # Store the score in the computed models dict 
        self.parent.computedModels[modelStr] = score

        # Store the results in the more comprehensive resultsList
        self.parent.resultsList.append(
            {"Model":modelStr, "Score":score, 
             "Method":"PIPE/{0}/{1}/{2}".format(self.parent.preprocessor.FILE_NAME, 
                                      self.regressionName,  
                                      self.regression.crossValidation)})

        return


    def iterate(self):
        """
        Iterates to perform the Brute Force Selection.
        Iterates over the combinations '0000000' to
        '1111111' for a 7 predictor system.
        """

        # Set up an iteration
        for i in range(self.totalNumModels + 1):
            
            # Create a model for the i-th iteration
            model_str = format(i, self.formatString)
            model = ba.bitarray(model_str)
            
            # Include any forced predictor flags
            if True in self.parent.forcedPredictors:
                model = model | self.parent.forcedPredictors

                # Check if model has been analyzed
                if model_str in self.parent.computedModels:
                    
                    # Use already computed score
                    score = self.parent.computedModels[model_str]
            
                else:

                    # Score the model
                    score = self.scoreModel(model)

            # Score model (this model is guaranteed to not have been analyzed before)
            else:
                score = self.scoreModel(model)
            
            # Log the results
            self.logCombinationResult(model, score)

        return