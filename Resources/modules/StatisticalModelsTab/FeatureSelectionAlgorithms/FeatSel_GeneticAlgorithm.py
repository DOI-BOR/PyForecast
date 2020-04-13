"""
Script Name:    FeatSel_GeneticAlgorithm.py

Description:    Genetic Algorithm is a feature scheme that
                mimics natural selection genetics in creating
                models to test with the regression scheme.

                The algorithm is described in detail in the 
                paper: 

                "glmulti: An R Package for Easy Automated Model 
                Selection with (Generalized) Linear Models"

                Calcagno, Vincent; de Mazancourt, Claire (2009)

                The algorithm is as follows for a model
                containing 6 possible predictors:

                    4 models are initialized:
                    1A: '000000',
                    1B: '110000',
                    1C: '001100',
                    1D: '000011'

                    Each model is scored and ranked (higher ranks are better)
                    J(1C) > J(1B) > J(1D) > J(1A)
                    [#4]    [#3]    [#2]    [#1]

                    Each model is assigned a fitness score
                    F(i) = 1.5 (Rank(i))

                    2 models chosen randomly from a distribution 
                    defined by the model fitness'

                    1B: '110000' / 1D: '000011'

                    The two models are recombined into 4 new models
                    (i.e a child is created by choosing a bit from
                    either parent with equal probability)
                    
                    1B: 1 1 0 0 0 0
                    1D: 0 0 0 0 1 1
                    ---------------
                    2A: 1 0 0 0 0 1
                    2B: 1 1 0 0 1 1
                    2C: 0 0 0 0 1 0
                    2D: 0 1 0 0 0 0

                    Each member of the new generation also undergoes
                    a mutation. The chance of flipping each bit in the 
                    new generation is 1/6 (or more generally, 1/p)


                The process is repeated 


"""

import bitarray as ba
import importlib
from resources.modules.StatisticalModelsTab import ModelScoring
import numpy as np

class FeatureSelector(object):
    
    name = "Genetic Algorithm"

    def __init__(self, parent = None, **kwargs):

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
        self.populationSize = 100        
        self.numGenerations = 20
        self.mutationRate = 1/self.numPredictors
        self.selectivePressure = 1.6

        # Ensure that population size is even
        if self.populationSize % 2 != 0:
            self.populationSize = self.populationSize + 1

        # Compute the total sum of ranks
        self.totalRank = self.selectivePressure * (self.populationSize/2) * (self.populationSize + 1)

        # Create a random initial population of 50 chromosomes.
        self.population = [ba.bitarray(list(np.random.randint(0, 2, self.numPredictors))) for i in range(self.populationSize)]
    

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


    def rankModels(self):
        """
        Ranks each chromosome based on the
        scoring parameters provided
        returns a dict like:
        {1001: 1.5,
         1010: 9,
         1100: 6, 
         ...}
        """

        # Sort the scores
        ModelScoring.sortScores(self.scores)

        # Generate a ranking dictionary
        ranks = [{next(iter(model)): (self.selectivePressure * (i+1))} for i, model in enumerate(self.scores)]

        return ranks


    def iterate(self):
        """
        Iterates to perform the Genetic Algorithm.
        The loop continues until we've had the pre-specified
        number of generations. 
        """

        # Start by creating a generation tracker
        genTrack = 0

        # Iterate over generations
        while genTrack < self.numGenerations:

            # Re-initialize our scores
            self.scores = []

            # Add any forced predictors
            if self.parent.forcedPredictors.any():
                self.population = [model | self.parent.forcedPredictors for model in self.population]

            # Generate Scores (first checking the computed model list to see if we got this one already)
            for model in self.population:

                model_str = model.to01()

                if model_str in self.parent.computedModels:
                    
                    # Take the score from the already computed list of scores
                    self.scores.append({model_str: self.parent.computedModels[model_str]})

                else:
                    
                    # Compute the scores and append the score to the master list of models
                    score = self.scoreModel(model)
                    self.scores.append({model_str: score})
                    self.logCombinationResult(model, score)
            
            # Rank this generation's models
            ranks = self.rankModels()

            # choose model to recombine based on thier ranked fitness
            selectionProb = [list(i.values())[0]/self.totalRank for i in ranks]
            fitModels = [self.population[np.random.choice(self.populationSize, p = selectionProb)] for i in range(int(self.populationSize/2))]

            # Recombine models
            self.recombination(fitModels)

            # Iterate
            genTrack += 1

           
    
    def recombination(self, fitModels):
        """
        Recombines the fit models into new models
        using uniform crossover recombination.
        """

        # Re-Initialize an empty population
        self.population = []

        # Iterate until we get back to the original population size
        while len(self.population) < self.populationSize:

            # Choose 2 fit models at random
            parentModels = [fitModels[np.random.choice(int(self.populationSize/2))] for i in range(2)]

            # Generate 4 children from the 2 parent models
            for i in range(4):
                model = ba.bitarray(self.numPredictors)
                for j in range(self.numPredictors):
                    if np.random.random() < 0.5:
                        model[j] = parentModels[0][j]
                    else:
                        model[j] = parentModels[1][j]

                # Mutate the model
                self.mutate(model)

                # Add to the new population
                self.population.append(model)

        # clip the population in case we added too many models
        self.population = self.population[:self.populationSize]

        return


    def mutate(self, model):
        """
        applies the mutation rate to each bit in the 
        model and flips the bit if a random number
        is below the mutation rate
        """

        for i in range(self.numPredictors):
            if np.random.random() < self.mutationRate:
                model[i] = not model[i]

        return

