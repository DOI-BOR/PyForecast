"""
Script Name:    FeatSel_SequentialForwardFloating.py

Description:    Sequential Forward Floating Selection is a feature
                selection scheme that iteratively adds features 
                to an initially empty model. Features are added if
                thier addition to the model increases the model's
                score. Features are then removed iteratively and
                the best resulting model is kept. A rough algorith 
                for this scheme is as follows 
                (taken from: http://research.cs.tamu.edu/prism/lectures/pr/pr_l11.pdf):

                For a system with 6 possible predictors

                1) Y = "000000" [no predictors in model]

                2) Select the best feature to add to the model:
                    predictor_to_add = maximize_score(Y + k)
                        (where k is one of the 6 predictors)
                    Y = Y + predictor_to_add 

                3) Select the worst feature to remove:
                    predictor_to_remove = maximize_score(Y - k)

                4) if score(Y-k) > score(Y) then 
                    Y = Y - predictor_to_remove
                    goto 3
                   else
                    goto 2
"""

import bitarray as ba
import importlib
from resources.modules.StatisticalModelsTab import ModelScoring
import numpy as np
from itertools import compress


class FeatureSelector(object):

    NAME = "Sequential Forward Floating Selection"

    def __init__(self, parent = None, **kwargs):

        # Create References to the predictors and the target
        self.predictorPool = parent.modelRunTableEntry['PredictorPool']
        self.target = parent.modelRunTableEntry['Predictand']
        self.parent = parent

        # Set up the Regression and Cross Validation
        self.regressionName = kwargs.get("regression", "Regr_MultipleLinearRegressor")
        regressionClass = self.parent.parent.regressors[self.regressionName]['module']
        self.regression = regressionClass(  parent = self.parent, 
                                            crossValidation = kwargs.get("crossValidation", None), 
                                            scoringParameters = kwargs.get("scoringParameters", None))
        
        # Create variables to store the current predictors and performance
        self.numPredictors = len(self.predictorPool)
        self.currentPredictors = kwargs.get("initialModel", ba.bitarray([False] * self.numPredictors))

        # Add in any forced predictors
        self.currentPredictors = self.currentPredictors | self.parent.forcedPredictors
        
        # Keep track of model performance with the previos predictors and the current model scores
        self.previousPredictors = self.currentPredictors.copy()
        self.currentScores = {}

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
        Iterates to perform the Sequential Forward Selection.
        The loop continues until the algorithm declines adding
        or subtracting any predictors from the model (i.e. adding
        or subtracting predictors is not increasing the score
        of the model.)
        """

        # Score the initial model
        model = self.currentPredictors.copy()
        self.currentScores = self.scoreModel(model)

        # Set up an iteration
        while True:
            
            # Search for new predictors to add
            self.tryAddition()

            # Search for predictors to remove
            self.trySubtraction()

            # Check if we've added any new predictors or removed predictors
            if self.previousPredictors == self.currentPredictors:
            
                # If the model has not changed, we're done!
                break
            
            # The model has changed, so we iterate again
            else:
                self.previousPredictors = self.currentPredictors
        
        return
        

    def tryAddition(self):
        """
        Attempt to add a predictor to the model. A predictor
        is added if it increases the score of the overall model.
        This function checks which remaining predictor (if any)
        increases the score the most, and adds that one.
        
        For example.

        1) The initial model is 001011
        2) We can potentially add the 1st, 2nd and 4th predictors
        3) compute the scores of adding each predictor individaully
        4) If any of the scores is greater than the initial score,
           that predictor is added and the function returns.
        """

        # Make a copy of the predictors that we can manipulate
        model = self.currentPredictors.copy()

        # Iterate over the predictors
        for i in range(self.numPredictors):

            # Check that the predictor is not currently in the model (i.e. it is '0')
            if not model[i]:

                # Add the predictor to the model
                model[i] = True
                model_str = model.to01()

                # Check that we haven't already computed this model combination
                if model_str in self.parent.computedModels:
                
                    # Get the score from the list of models
                    score = self.parent.computedModels[model_str]
                    
                else:
                
                    # Compute the model score
                    score = self.scoreModel(model)

                    # Log the model results so that we don't try it again if we can avoid it
                    self.logCombinationResult(model, score)

                # Check if this model has a higher score than the current model
                if ModelScoring.scoreCompare(newScores = score, oldScores = self.currentScores):
                    self.currentScores = score
                    self.currentPredictors = model.copy()

                # Revert the model
                model[i] = False
        
        return
    

    def trySubtraction(self):
        """
        Attempt to remove a predictor to the model. A predictor
        is removed if it increases the score of the overall model.
        This function checks which current predictor (if any)
        increases the score the most when removed, and removes that one.
        
        For example.

        1) The initial model is 001011
        2) We can potentially remove the 3rd, 4th and 5th predictors
        3) compute the scores of removing each predictor individaully
        4) If any of the scores is greater than the initial score,
           that predictor is removed and the function trys to remove another one.
        """

        # Make a copy of the predictors that we can manipulate
        model = self.currentPredictors.copy()

        # Keep track of whether we removed a predictor
        predictorRemoved = False

        # Iterate over the predictors
        for i in range(self.numPredictors):

            # Check that the predictor is currently in the model (i.e. it is '1') and it's not forced
            if model[i] and not self.parent.forcedPredictors[i]:
                
                # Remove the predictor from the model
                model[i] = False
                model_str = model.to01()

                 # Check that we haven't already computed this model combination
                if model_str in self.parent.computedModels:
                
                    # Get the score from the list of models
                    score = self.parent.computedModels[model_str]
                    
                else:
                
                    # Compute the model score
                    score = self.scoreModel(model)

                    # Log the model results so that we don't try it again if we can avoid it
                    self.logCombinationResult(model, score)

                # Check if this model has a higher score than the current model
                if ModelScoring.scoreCompare(newScores = score, oldScores = self.currentScores):
                    self.currentScores = score
                    self.currentPredictors = model.copy()
                    predictorRemoved = True

                # Revert the model
                model[i] = True
        
        # If we removed a predictor, try to remove another one
        if predictorRemoved:
            self.trySubtraction()

        # Otherwise, return
        else:
            return


