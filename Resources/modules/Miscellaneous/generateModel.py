import numpy as np
import pandas as pd
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
from resources.modules.ModelCreationTab import PredictionIntervalBootstrap
from scipy.stats import iqr
from sklearn.neighbors import KernelDensity
from PyQt5 import QtGui, QtWidgets


class Model(object):

    def __init__(self, parent = None, forecastEquationTableEntry = None):
        self.parent = parent
        self.forecastEquation = forecastEquationTableEntry

        # Get Model identifiers
        method = forecastEquationTableEntry['EquationMethod'].split('/')
        self.preprocessorClass = self.parent.preProcessors[method[1]]['module']
        self.regressionClass = self.parent.regressors[method[2]]['module']
        self.crossValidator = method[3]
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
        self.regression = self.regressionClass(parent = self,
                                          crossValidation = self.crossValidator,
                                          scoringParameters = list(self.parent.scorers['info']))

        return


    def generate(self):
        """
        Data processing code adapted from Resources/Modules/ModelCreationTab/RegressionWorker.py setData()

        :return:
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

        # Build Model data arrays
        self.regressionData = pd.DataFrame(data=([self.years, self.regression.y, self.regression.y_p,
                                                  self.regression.y_p_cv, self.regression.y_p-self.regression.y,
                                                  self.regression.y_p_cv-self.regression.y]),
                                           index=['Years','Observed', 'Prediction', 'CV-Prediction','PredictionError','CV-PredictionError']).T
        self.predictorData = pd.DataFrame(data=self.regression.x, index=self.years,columns=self.forecastEquation.EquationPredictors)

        return


    def predict(self, xData=None, year=None, ):
        """

        :param xData:
        :param year:
        :return:
        """
        # Setup Bootstrap dataset
        XY_ = np.hstack((self.xTraining, self.yTraining))
        if xData is not None:
            xDataBootstrap = xData.reset_index(drop=True)
            xDataBootstrap.loc[len(xDataBootstrap)] = 0
            XY_ = np.vstack((XY_, xDataBootstrap))
            XY_ = XY_.astype(np.float)
        if year is not None:
            # Move the fore/hind-cast year to the end of the array
            yearRowIdx = self.predictorData.index.get_loc(int(year))
            yearRow = XY_[yearRowIdx]
            XY_ = np.delete(XY_, yearRowIdx, axis=0)
            XY_ = np.vstack((XY_, yearRow))
            xData = self.predictorData.loc[int(year)]
        # Run prediction interval bootstrap
        print('INFO: Running prediction bootstrap...')
        predBootstrap = PredictionIntervalBootstrap.computePredictionInterval(self, XY_, self.preprocessorClass,
                                                                              self.regressionClass,
                                                                              self.crossValidator,
                                                                              nRuns=500)
        self.predictionRange = pd.DataFrame(np.percentile(predBootstrap, range(1, 100)), index=range(1, 100))
        # Run a prediction with the input data
        try:
            self.prediction = self.regression.predict(xData)
        except:
            # Report the 50th percentile prediction bootstrap if prediction fails.
            self.prediction = self.predictionRange.loc[50]
        return


    def report(self, modelIdx, listWidget):
        listWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # Update UI with selected model metadata
        listWidget.clear()
        listWidget.addItem('----- MODEL REGRESSION -----')
        listWidget.addItem('Model Index: ' + str(modelIdx))
        listWidget.addItem(
            'Model Processes: ' + str(self.forecastEquation.EquationMethod))
        listWidget.addItem(
            'Model Predictor IDs: ' + str(self.forecastEquation.EquationPredictors))
        listWidget.addItem(
            'Selected Range (years): ' + str(self.trainingDates))
        usedYears = ", ".join([str(years) for years in self.years])
        listWidget.addItem('Used Range (years): ' + usedYears)
        listWidget.addItem(' ')

        listWidget.addItem('----- MODEL VARIABLES -----')
        listWidget.addItem('Predictand Y: ' + str(
            self.parent.datasetTable.loc[self.yID].DatasetName) + ' - ' + str(
            self.parent.datasetTable.loc[self.yID].DatasetParameter))
        equation = 'Y ='
        hasCoefs = True
        hasNegativeCoef = False
        for i in range(len(self.xIDs)):
            listWidget.addItem('Predictor X' + str(i + 1) + ': ' + str(
                self.parent.datasetTable.loc[
                    self.xIDs[i]].DatasetName) + ' - ' + str(
                self.parent.datasetTable.loc[self.xIDs[i]].DatasetParameter))
            try:
                if hasCoefs:
                    coef = self.regression.coef[i]
                    const = 'X' + str(i + 1)
                    if coef >= 0:
                        equation = equation + ' + (' + ("%0.5f" % coef) + ')' + const
                    else:
                        equation = equation + ' - (' + ("%0.5f" % (coef * -1.0)) + ')' + const
                        hasNegativeCoef = True
            except:
                hasCoefs = False

        listWidget.addItem(' ')
        if hasCoefs:
            listWidget.addItem('----- MODEL EQUATION -----')
            if self.regression.intercept >= 0:
                equation = equation + ' + ' + ("%0.5f" % self.regression.intercept)
            else:
                equation = equation + ' - ' + ("%0.5f" % (self.regression.intercept * -1.0))
            listWidget.addItem('' + equation)
            if hasNegativeCoef:
                widg = QtWidgets.QListWidgetItem('WARNING: Generated equation has at least 1 negative coefficient')
                widg.setForeground(QtGui.QColor("#FF0000"))
                listWidget.addItem(widg)
            listWidget.addItem(' ')

        isPrinComp = True if self.regression.NAME == 'Principal Components Regression' else False
        if isPrinComp:
            listWidget.addItem('----- MODEL COMPONENTS -----')
            listWidget.addItem(
                'Principal Components Count: ' + str(self.regression.num_pcs))
            usedCoefs = self.regression.pc_coef[
                        :self.regression.num_pcs]
            coefVals = ", ".join([("%0.5f" % coef) for coef in usedCoefs])
            listWidget.addItem('Principal Components Coefficients: ' + coefVals)
            eigVecs = self.regression.eigenvectors[:,
                      :self.regression.num_pcs]
            for i in range(len(self.xIDs)):
                listWidget.addItem(
                    'X' + str(i + 1) + ' Eigenvector: ' + ("%0.5f" % eigVecs[i]))
            listWidget.addItem(' ')

        isZScore = True if self.regression.NAME == 'Z-Score Regression' else False
        if isZScore:
            listWidget.addItem('----- MODEL COMPONENTS -----')
            for i in range(len(self.xIDs)):
                listWidget.addItem('X' + str(i + 1) + ' Y Correlation: ' + (
                            "%0.5f" % self.regression.zRsq[i]))
            equation = 'Z-Score Equation: Y = ('
            if self.regression.zcoef[0] > 0:
                equation = equation + ("%0.5f" % self.regression.zcoef[0]) + ')MC'
            else:
                equation = equation + '-' + ("%0.5f" % self.regression.zcoef[0]) + ')MC'
            if self.regression.zintercept > 0:
                equation = equation + ' + ' + ("%0.5f" % self.regression.zintercept)
            else:
                equation = equation + ' - ' + ("%0.5f" % self.regression.zintercept)
            listWidget.addItem(equation)
            listWidget.addItem(
                '               MC: Weighted Z-Score Multiple Component Indexed Value')
            listWidget.addItem(' ')

        listWidget.addItem('----- MODEL SCORES (Regular | Cross-Validated) -----')
        for scorer in self.regression.scoringParameters:
            try:
                regScore = self.regression.scores[scorer]
                cvScore = self.regression.cv_scores[scorer]
                listWidget.addItem(
                    scorer + ': ' + ("%0.5f" % regScore) + ' | ' + ("%0.5f" % cvScore))
            except:
                pass
        return