import numpy as np
import pandas as pd
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
from resources.modules.ModelCreationTab import PredictionIntervalBootstrap
from scipy.stats import iqr
from sklearn.neighbors import KernelDensity
from PyQt5 import QtGui, QtWidgets
import tempfile, os, csv
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

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


    def generate(self, excludeYears = True):
        """
        Data processing code adapted from Resources/Modules/ModelCreationTab/RegressionWorker.py setData()

        :return:
        """
        # Iterate over predictor datasets and append to arrays
        popindex = []
        self.xTraining = []
        self.x = []
        if not excludeYears:
            self.excludeYears = []
        for i in range(len(self.xIDs)):

            data = resampleDataSet(
                self.parent.dataTable.loc[(slice(None), self.xIDs[i]), 'Value'],
                self.xPeriods[i],
                self.xMethods[i]
            )

            data.set_axis([idx.year if idx.month < 10 else idx.year + 1 for idx in data.index], axis=0, inplace=True)
            idx = list(filter(lambda date: date not in self.excludeYears, data.index))
            self.dataDates = idx
            self.x.append(list(data.loc[idx]))  # X-Data
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
        maxListLength = max([len(i) for i in self.x])
        [i.append(np.nan) for i in self.x if len(i) < maxListLength]

        # Convert data lists to numpy arrays
        self.x = np.array(self.x).T
        self.xTraining = np.array(self.xTraining).T
        self.yTraining = np.array(self.yTraining).reshape(-1, 1)

        # Handle missing data
        # MICE imputation
        imp = IterativeImputer(max_iter=50, min_value=0, verbose=0)
        imp.fit(self.xTraining)
        self.xTraining = imp.transform(self.xTraining)
        #[JR] - Fill data with column average if NaN/missing -- need a place to turn this on/off
        #colMeans = np.nanmean(self.xTraining, axis=0)
        #nanIdxs = np.where(np.isnan(self.xTraining))
        #self.xTraining[nanIdxs] = np.take(colMeans, nanIdxs[1])

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
        self.x = pd.DataFrame(data=self.x[:len(self.dataDates)], index=self.dataDates,columns=self.forecastEquation.EquationPredictors)

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
                                                                              nRuns=1000)
        self.predictionRange = pd.DataFrame(np.percentile(predBootstrap, range(1, 100)), index=range(1, 100))
        print('INFO: Prediction[5,10,25,50,75,90,95]=[' + str(self.predictionRange.loc[5][0]) + ',' +
              str(self.predictionRange.loc[10][0]) + ',' + str(self.predictionRange.loc[25][0]) + ',' +
              str(self.predictionRange.loc[50][0]) + ',' + str(self.predictionRange.loc[75][0]) + ',' +
              str(self.predictionRange.loc[90][0]) + ',' + str(self.predictionRange.loc[95][0]) + ']')
        # Run a prediction with the input data
        try:
            self.prediction = self.regression.predict(xData)
        except:
            # Report the 50th percentile prediction bootstrap if prediction fails.
            self.prediction = self.predictionRange.loc[50]
        return


    def report(self, listWidget):
        listWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # Update UI with selected model metadata
        listWidget.clear()
        list = self.buildReportList()
        for i in range(len(list)):
            text = list[i]
            if 'WARNING' in text:
                widg = QtWidgets.QListWidgetItem(text)
                widg.setForeground(QtGui.QColor("#FF0000"))
                listWidget.addItem(widg)
            else:
                listWidget.addItem(text)

        return


    def buildReportList(self):
        list = []
        list.append('----- MODEL REGRESSION -----')
        #list.append('Model Index: ' + str(modelIdx))
        list.append(
            'Model Processes: ' + str(self.forecastEquation.EquationMethod))
        list.append(
            'Model Predictor IDs: ' + str(self.forecastEquation.EquationPredictors))
        list.append(
            'Selected Range (years): ' + str(self.trainingDates))
        list.append(
            'Excluded Range (years): ' + str(self.excludeYears))
        usedYears = ", ".join([str(years) for years in self.years])
        list.append('Used Range (years): ' + usedYears)
        list.append(' ')

        list.append('----- MODEL VARIABLES -----')
        list.append('Predictand Y: ' + str(self.parent.datasetTable.loc[self.yID].DatasetName) + ' - ' +
                    str(self.parent.datasetTable.loc[self.yID].DatasetParameter) + ' {Period: ' +
                    str(self.yPeriod) + ', Resampling: ' +
                    str(self.yMethod) + '}')
        equation = 'Y ='
        hasCoefs = True
        hasNegativeCoef = False
        for i in range(len(self.xIDs)):
            list.append('Predictor X' + str(i + 1) + ': ' +
                        str(self.parent.datasetTable.loc[self.xIDs[i]].DatasetName) + ' - ' +
                        str(self.parent.datasetTable.loc[self.xIDs[i]].DatasetParameter) + ' {Period: ' +
                        str(self.xPeriods[i]) + ', Resampling: ' +
                        str(self.xMethods[i]) + '}')
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

        list.append(' ')
        if hasCoefs:
            list.append('----- MODEL EQUATION -----')
            if self.regression.intercept >= 0:
                equation = equation + ' + ' + ("%0.5f" % self.regression.intercept)
            else:
                equation = equation + ' - ' + ("%0.5f" % (self.regression.intercept * -1.0))
            list.append('' + equation)
            if hasNegativeCoef:
                #widg = QtWidgets.QListWidgetItem('WARNING: Generated equation has at least 1 negative coefficient')
                #widg.setForeground(QtGui.QColor("#FF0000"))
                list.append('WARNING: Generated equation has at least 1 negative coefficient')
            list.append(' ')

        isPrinComp = True if self.regression.NAME == 'Principal Components Regression' else False
        if isPrinComp:
            list.append('----- MODEL COMPONENTS -----')
            list.append(
                'Principal Components Count: ' + str(self.regression.num_pcs))
            usedCoefs = self.regression.pc_coef[
                        :self.regression.num_pcs]
            coefVals = ", ".join([("%0.5f" % coef) for coef in usedCoefs])
            list.append('Principal Components Coefficients: ' + coefVals)
            eigVecs = self.regression.eigenvectors[:,
                      :self.regression.num_pcs]
            for i in range(len(self.xIDs)):
                list.append(
                    'X' + str(i + 1) + ' Eigenvector: ' + ("%0.5f" % eigVecs[i]))
            list.append(' ')

        isZScore = True if self.regression.NAME == 'Z-Score Regression' else False
        if isZScore:
            list.append('----- MODEL COMPONENTS -----')
            for i in range(len(self.xIDs)):
                list.append('X' + str(i + 1) + ' Y Correlation: ' + (
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
            list.append(equation)
            list.append(
                '               MC: Weighted Z-Score Multiple Component Indexed Value')
            list.append(' ')

        list.append('----- MODEL SCORES (Regular | Cross-Validated) -----')
        for scorer in self.regression.scoringParameters:
            try:
                regScore = self.regression.scores[scorer]
                cvScore = self.regression.cv_scores[scorer]
                list.append(
                    scorer + ': ' + ("%0.5f" % regScore) + ' | ' + ("%0.5f" % cvScore))
            except:
                pass

        return list


    def export(self):
        # Get regular displayed model info
        list = self.buildReportList()
        list = [w.replace(',', ';') for w in list]
        # Get underlying data
        xy = pd.DataFrame(np.column_stack((self.years,self.regression.x,self.regression.y,self.regression.y_p)))
        headerList = ['Year']
        headerList.extend(['X' + str(i+1) for i in range(0,len(self.xIDs))])
        headerList.append('Y')
        headerList.append('Ymodeled')
        xy.columns = headerList
        # Combine lists
        xyVals = xy.to_string(header=True, index=False, index_names=True).split('\n')
        xyStrings = [','.join(i.split()) for i in xyVals]
        list.append(' ')
        list.append('----- MODELING DATASET -----')
        list.extend(xyStrings)
        # Write to temp csv file and open
        handle, fn = tempfile.mkstemp(suffix='.csv')
        with os.fdopen(handle, "w", encoding='utf8', errors='surrogateescape', newline='\n') as f:
            writer = csv.writer(f)
            try:
                for line in list:
                    writer.writerow([line,])
                print('INFO: Model exported to file ' + fn)
                os.startfile(fn)
            except Exception as e:
                print('WARNING: Model export error:', e)

        return