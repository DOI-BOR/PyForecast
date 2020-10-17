import numpy as np
import bitarray as ba
import pandas as pd
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet


class Model(object):

    def __init__(self, parent = None, forecastEquationTableEntry = None):
        self.parent = parent
        self.forecastEquation = forecastEquationTableEntry

        # Get Model identifiers
        method = forecastEquationTableEntry['EquationMethod'].split('/')
        self.preprocessorClass = self.parent.preProcessors[method[1]]['module']
        regressionClass = self.parent.regressors[method[2]]['module']
        crossValidator = method[3]
        self.yID = forecastEquationTableEntry['EquationPredictand']
        self.yPeriod = forecastEquationTableEntry['PredictandPeriod']
        self.yMethod = forecastEquationTableEntry['PredictandMethod']
        self.xIDs = forecastEquationTableEntry['EquationPredictors']
        self.xPeriods = forecastEquationTableEntry['PredictorPeriods']
        self.xMethods = forecastEquationTableEntry['PredictorMethods']
        # Set the start and end dates for the model training period
        modelTrainingStrings = forecastEquationTableEntry['ModelTrainingPeriod'].split('/')
        self.trainingDates = list(map(int, modelTrainingStrings[:2]))
        if len(modelTrainingStrings) > 2:
            self.excludeYears = list(map(int, modelTrainingStrings[2].split(',')))

        # Build regression object
        self.regression = regressionClass(parent = self,
                                          crossValidation = crossValidator,
                                          scoringParameters = list(self.parent.scorers['info']))

        return


    def generate(self):
        """
        Data processing code adapted from Resources/Modules/ModelCreationTab/RegressionWorker.py setData()

        """

        # Iterate over predictor datasets and append to arrays
        popindex = []
        self.xTraining = []
        for i in range(len(self.xIDs)):

            data = resampleDataSet(
                self.parent.dataTable.loc[(slice(None), self.xIDs[i]), 'Value'],
                self.xPeriods[i],
                self.xMethods[i]
            )

            data.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in data.index], axis=0, inplace=True)
            data = data.loc[self.trainingDates[0]: self.trainingDates[1]]
            idx = list(filter(lambda date: date not in self.excludeYears, data.index))
            self.xTraining.append(list(data.loc[idx]))  # Training Data

        # Compute the target data
        self.y = resampleDataSet(
            self.parent.dataTable.loc[(slice(None), self.yID), 'Value'],
            self.yPeriod,
            self.yMethod
        )
        self.y.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in self.y.index], axis=0, inplace=True)
        data = self.y.loc[self.trainingDates[0]: self.trainingDates[1]]
        idx = list(filter(lambda date: date not in self.excludeYears, data.index))
        self.yTraining = self.y.loc[idx].values  # Training Data

        # Add any missing data for the current water year to the arrays
        maxListLength = max([len(i) for i in self.xTraining])
        [i.append(np.nan) for i in self.xTraining if len(i) < maxListLength]

        # Convert data lists to numpy arrays
        self.xTraining = np.array(self.xTraining).T
        self.yTraining = np.array(self.yTraining).reshape(-1, 1)

        # Compute the preprocessed dataset
        self.preprocessor = self.preprocessorClass(np.concatenate([self.xTraining, self.yTraining], axis=1))
        proc_xTraining = self.preprocessor.getTransformedX()
        proc_yTraining = self.preprocessor.getTransformedY()

        # Remove Nans
        xNans = np.argwhere(np.isnan(proc_xTraining))
        yNans = np.argwhere(np.isnan(proc_yTraining))
        popIndex = []
        for item in xNans:
            popIndex.append(item[0])
        for item in yNans:
            popIndex.append(item[0])
        proc_xTraining = np.delete(proc_xTraining, popIndex, axis=0)
        proc_yTraining = np.delete(proc_yTraining, popIndex, axis=0)
        self.years = np.delete(idx, popIndex, axis=0)

        # Run regression
        self.regression.fit(proc_xTraining, proc_yTraining, True)


        return


    def predict(self, year):

        return

