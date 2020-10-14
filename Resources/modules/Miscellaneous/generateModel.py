import numpy as np
import bitarray as ba
import pandas as pd


class Model(object):

    def __init__(self, parent = None, forecastEquationTableEntry = None, *args, **kwargs):
        self.parent = parent
        method = forecastEquationTableEntry['EquationMethod'].split('/')
        self.preprocessorClass = self.parent.preProcessors[method[1]]['module']
        regressionClass = self.parent.regressors[method[2]]['module']
        crossValidator = method[3]

        # Build regression object
        self.regression = regressionClass(  parent = self,
                                            crossValidation = crossValidator,
                                            scoringParameters = list(self.parent.scorers['info']))

        return

    def generate(self, tableEntry):
        # Get data
        self.xTraining = []
        self.yTraining = []

        #TODO: GET DATA!

        self.preprocessor = self.preprocessorClass(np.concatenate([self.xTraining, self.yTraining], axis=1))

        # Compute the preprocessed dataset
        proc_xTraining = self.preprocessor.getTransformedX()
        proc_yTraining = self.preprocessor.getTransformedY()
        # Run regression
        self.regression.fit(proc_xTraining, proc_yTraining, True)

        return

    def predict(self, year):

        return

