"""
Script Name:    FeatureSelectionV2.py
Script Author:  Kevin Foley, kfoley@usbr.gov
Description:    Performs SFFS / SBBS feature selection routines to 
                determine optimal predictor combinations. Follows the 
                algorithms outlined in http://research.cs.tamu.edu/prism/lectures/pr/pr_l11.pdf.

                The script generates a user-defined number of sub-optimal predictor sets (either
                empty or full, depending on SFFS or SBBS), and iterates through each predictor set
                performing the next iteration of SFFS or SBBS, until all predictor sets
                are optimized. Optimized in this regard means minimizing the loss function
                defined by the performance metric. 
"""

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count as CPUCount
import pandas as pd
from scipy.stats import t
import itertools
import numpy as np
from sklearn import model_selection
from sklearn.neural_network import MLPRegressor
from Resources.Functions import Metrics
from Resources.Functions import encryptions
from itertools import repeat, combinations
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable
import warnings
from Resources.Functions.miscFunctions import readConfig, writeConfig

class alternateThreadWorkerSignals(QObject):
    """
    Class to store signals that are emitted from this script back to the main program
    """

    updateProgBar = pyqtSignal(int)
    totalModelsAnalyzed = pyqtSignal(int)
    updateRunLabel = pyqtSignal(str)
    returnFcstDict = pyqtSignal(list)


class alternateThreadWorker(QRunnable):
    """
    Define a class that is a QRunnable (alternate thread worker). Any scripts / functions in this class
    will run concurrently with the main program, so we don't hold up / lock the main thread. 
    """

    def __init__(self, d):
        """
        __init__ is called when the program first initializes the class. 
        """
        super(alternateThreadWorker, self).__init__()

        # Load and parse the json object into a dataframe and an options dict
        self.dictObject = d
        self.objFunction = d['RegressionScheme']
        self.crossVal = d['CrossValidation']
        self.featScheme = d['SelectionScheme']
        self.perfMetric = d['PerformanceMetric']
        self.numModels = d['NumModels']
        self.equationDict = d['EquationDict']
        self.predictorDict = d['PredictorDict']
        self.dist = d['Distribution']

        # Load the signals that the worker will emit
        self.signals = alternateThreadWorkerSignals()

    
    def run(self):
        """
        "run" is the main entry point for the alternate thread. When the class is 'started', it begins in this function.
        """
        if self.featScheme == 'Sequential Floating Forward Selection':
            self.SFFS()
        elif self.featScheme == 'Sequential Floating Backwards Selection':
            self.SFBS()
        else:
            self.BruteForce()


    def initializeContainers(self, bruteForce = False):

        """ Set the regression scheme """
        if self.objFunction == 'MLR':
            self.ObjFunctionRun = MultipleRegression

        elif self.objFunction == 'PCAR':
            self.ObjFunctionRun = PrincipalComponentsRegression

        elif self.objFunction == 'ZSCR':
            self.ObjFunctionRun = ZScoreRegression

        elif self.objFunction == 'ANN':
            self.ObjFunctionRun = NeuralNetwork

        """ Set the Cross validation type """
        if self.crossVal == 'Leave One Out':
            self.cv = model_selection.LeaveOneOut()
        elif self.crossVal == 'K-Fold (5 folds)':
            self.cv = model_selection.KFold(n_splits=5)
        else:
            self.cv = model_selection.KFold(n_splits=10)

        """ Get minimum number of models to run """
        if bruteForce:
            self.numModels = min((2 ** len(self.equationDict['PredictorPool'])) - 1, self.numModels)

        """ Initialize a list of dictionarys to store model information """
        self.searchDictList = [{
                "fcstID"            : "",
                "Type"              : "Linear - {0}".format(self.objFunction),
                "Coef"              : [],
                "prdIDs"            : [],
                "Intercept"         : [],
                "PrincCompData"     : {},
                "Distribution"      : self.dist,
                "Metrics"           : {
                    "Cross Validated Adjusted R2"           : float("-inf"),
                    "Root Mean Squared Prediction Error"    : float("inf"),
                    "Cross Validated Nash-Sutcliffe"        : float("-inf"),
                    "Adjusted R2"                           : float("-inf"),
                    "Root Mean Squared Error"               : float("inf"),
                    "Nash-Sutcliffe"                        : float("-inf"),
                    "Sample Variance"                       : float("inf"),
                    "Mean Absolute Error"                   : float("inf")},
                "CrossValidation"                           : self.crossVal,
                "Forecasted"                                : "",
                "CV_Forecasted"     : "",
                "Years Used"        : [],
                "FeatSelectionProgress" : "Running"
        } for n in range(self.numModels)]

        """ Get the predictand Data"""
        self.predictandData = pd.DataFrame().from_dict(self.equationDict['Predictand']['Data'], orient='columns')
        self.predictandData.columns = ['Predictand']
        if self.dist != 'Normal':
            self.predictandData = np.log(self.predictandData)

        """ Initialize data for predictors """
        self.predictorData = pd.DataFrame()
        for predictorName in self.predictorDict:
            for interval in self.predictorDict[predictorName]:
                if self.predictorDict[predictorName][interval]['prdID'] in list(self.equationDict['PredictorPool']):
                    self.predictorData = pd.concat([self.predictorData, pd.DataFrame().from_dict(self.predictorDict[predictorName][interval]['Data'], orient='columns')], axis=1)

        """ Remove predictor columns whose 'nan' count is greater than half of the data period """
        nanCount = self.predictorData.isna().sum()
        for i, v in nanCount.items():
            if v > (len(self.predictandData) / 2):
                del self.predictorData[i]
        self.predictorDataNames = list(self.predictorData.columns)





    def SFBS(self):

        """ Initialize data containers needed by the feature selection algorithm """
        self.initializeContainers()

        if len(self.predictorDataNames) == 0:
            print('No predictors selected')
            self.signals.returnFcstDict.emit(self.searchDictList)
            return

        """ Begin a loop to iterate through parallized floating selection """
        iterCounter = 0
        modelsAnalyzed = 0
        modelsCompleted = 0

        """ Array to store current models """
        currentModels = [[] for i in range(self.numModels)]

        """ Set up a multiprocessing pool """
        pool = ThreadPool(processes=CPUCount()-1)

        while iterCounter <= len(self.predictorDataNames):

            print(iterCounter / (len(self.predictorDataNames)))
            iterCounter = iterCounter + 1

            """ Iterate through each model and perform 1 iteration of Sequential Floating Selection """
            for i in range(self.numModels):

                """ Check to see if this model has completed yet"""
                if self.searchDictList[i]['FeatSelectionProgress'] == 'Completed':
                    continue

                """ Set some variables for this iteration """
                modelChanged = False
                #if iterCounter == 1:  # Seed the equationDict during the 1st iteration
                #    self.searchDictList[i]['prdIDs'] = self.predictorDataNames  # self.equationDict['ForcedPredictors']

                currentPredictorSet = self.predictorDataNames #self.searchDictList[i]['prdIDs']
                predictorsToBeRemoved = currentPredictorSet

                """ Set up a pool of processes (to be run on multiple cores if there are lots of predictors) to test each predictor removal """
                results = list(map(testPredictorSet, [list(l) for l in zip( repeat(currentPredictorSet),
                                                                            predictorsToBeRemoved,
                                                                            repeat('Remove'),
                                                                            repeat(currentModels),
                                                                            repeat(self.cv),
                                                                            repeat(self.perfMetric),
                                                                            repeat(self.predictorData),
                                                                            repeat(self.predictandData),
                                                                            repeat(self.ObjFunctionRun),
                                                                            repeat(pool))]))

                """ Determine if any of the removals increased model performance """
                for result in results:

                    if result[0]['prdID'] == ['000']:
                        continue

                    if result[0]['prdID'] == ['-1000']:
                            modelsAnalyzed = modelsAnalyzed + 1
                            self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))
                            continue

                    if Metrics.metricBetterThan( newMetric = result[1][self.perfMetric], oldMetric = self.searchDictList[i]['Metrics'][self.perfMetric], perfMeasure = self.perfMetric):
                        predictorRemoved = list(set(currentPredictorSet) - set(result[0]['prdID']) )
                        self.searchDictList[i]['Metrics'] = result[1]
                        self.searchDictList[i]['prdIDs'] = result[0]['prdID']
                        self.searchDictList[i]['Forecasted'] = result[2]['Forecasted']
                        self.searchDictList[i]['CV_Forecasted'] = result[2]['CV_Forecasted']
                        self.searchDictList[i]['Coef'] = result[3]
                        self.searchDictList[i]['Intercept'] = result[4]
                        self.searchDictList[i]['PrincCompData'] = result[5]
                        currentModels[i] = result[0]['prdID']
                        modelChanged = True

                    modelsAnalyzed = modelsAnalyzed + 1
                    self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))

                    """ If we didn't remove a predictor, attempt to skip a step and try removing 2 predictors """
                    if modelChanged == False:
                        predictorsToBeRemoved = list(combinations(currentPredictorSet, 2))

                        results = list(map(testPredictorSet, [list(l) for l in zip(repeat(currentPredictorSet),
                                                                                   predictorsToBeRemoved,
                                                                                   repeat('Remove'),
                                                                                   repeat(currentModels),
                                                                                   repeat(self.cv),
                                                                                   repeat(self.perfMetric),
                                                                                   repeat(self.predictorData),
                                                                                   repeat(self.predictandData),
                                                                                   repeat(self.ObjFunctionRun),
                                                                                   repeat(pool))]))

                        for result in results:

                            if result[0]['prdID'] == ['000']:
                                continue

                            if result[0]['prdID'] == ['-1000']:
                                modelsAnalyzed = modelsAnalyzed + 1
                                self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))
                                continue

                            if Metrics.metricBetterThan(newMetric=result[1][self.perfMetric], oldMetric=self.searchDictList[i]['Metrics'][self.perfMetric], perfMeasure=self.perfMetric):
                                predictorRemoved = list(set(result[0]['prdID']) - set(currentPredictorSet))
                                self.searchDictList[i]['Metrics'] = result[1]
                                self.searchDictList[i]['prdIDs'] = result[0]['prdID']
                                self.searchDictList[i]['Forecasted'] = result[2]['Forecasted']
                                self.searchDictList[i]['CV_Forecasted'] = result[2]['CV_Forecasted']
                                self.searchDictList[i]['Coef'] = result[3]
                                self.searchDictList[i]['Intercept'] = result[4]
                                self.searchDictList[i]['PrincCompData'] = result[5]
                                self.searchDictList[i]['Years Used'] = result[6]
                                currentModels[i] = result[0]['prdID']
                                modelChanged = True

                            modelsAnalyzed = modelsAnalyzed + 1
                            self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))

                """ Try and add a variable back in, but don't add in a predictor we just removed """
                currentPredictorSet = self.searchDictList[i]['prdIDs']
                if modelChanged:
                    predictorsToBeAdded = list(set([prd for prd in self.predictorDataNames if prd not in currentPredictorSet]) - set(predictorRemoved))
                else:
                    predictorsToBeAdded = [prd for prd in self.predictorDataNames if prd not in currentPredictorSet]

                results = list(map(testPredictorSet, [list(l) for l in zip( repeat(currentPredictorSet),
                                                                            predictorsToBeAdded,
                                                                            repeat('Add'),
                                                                            repeat(currentModels),
                                                                            repeat(self.cv),
                                                                            repeat(self.perfMetric),
                                                                            repeat(self.predictorData),
                                                                            repeat(self.predictandData),
                                                                            repeat(self.ObjFunctionRun),
                                                                            repeat(pool))]))

                """ Determine if any of the additions increased model performance """
                for result in results:

                    if result[0]['prdID'] == ['000']:
                        continue

                    if result[0]['prdID'] == ['-1000']:
                        modelsAnalyzed = modelsAnalyzed + 1
                        self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))
                        continue

                    if Metrics.metricBetterThan( newMetric = result[1][self.perfMetric], oldMetric = self.searchDictList[i]['Metrics'][self.perfMetric], perfMeasure = self.perfMetric):
                        predictorRemoved = list(set(currentPredictorSet) - set(result[0]['prdID']) )
                        self.searchDictList[i]['Metrics'] = result[1]
                        self.searchDictList[i]['prdIDs'] = result[0]['prdID']
                        self.searchDictList[i]['Forecasted'] = result[2]['Forecasted']
                        self.searchDictList[i]['CV_Forecasted'] = result[2]['CV_Forecasted']
                        self.searchDictList[i]['Coef'] = result[3]
                        self.searchDictList[i]['Intercept'] = result[4]
                        self.searchDictList[i]['PrincCompData'] = result[5]
                        self.searchDictList[i]['Years Used'] = result[6]
                        currentModels[i] = result[0]['prdID']
                        modelChanged = True

                    modelsAnalyzed = modelsAnalyzed + 1
                    self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))

                    """ If the model hasn't changed, complete the model and update the progress bar """
                    if modelChanged == False and currentPredictorSet != []:
                        self.searchDictList[i]['FeatSelectionProgress'] = 'Completed'
                        modelsCompleted = modelsCompleted + 1
                        self.signals.updateProgBar.emit(int(100*modelsCompleted/self.numModels))


        for i in reversed(range(len(self.searchDictList))):
            if self.searchDictList[i]['Coef'] == []:
                fcstID = 'EMPTY'
                del self.searchDictList[i]
            else:
                fcstID = encryptions.generateFcstID(self.searchDictList[i]['Type'], self.searchDictList[i]['prdIDs'])
                self.searchDictList[i]['fcstID'] = fcstID
                self.searchDictList[i]['FeatSelectionProgress'] = 'Completed'

        pool.close()
        pool.join()

        self.signals.returnFcstDict.emit(self.searchDictList)

    """
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################


    """

    def SFFS(self):

        """ Initialize data containers needed by the feature selection algorithm """
        self.initializeContainers()

        if len(self.predictorDataNames) == 0:
            print('No predictors selected')
            self.signals.returnFcstDict.emit(self.searchDictList)
            return

        """ Begin a loop to iterate through parallized floating selection """
        iterCounter = 0
        modelsAnalyzed = 0
        modelsCompleted = 0

        """ Array to store current models """
        currentModels = [[] for i in range(self.numModels)]

        """ Set up a multiprocessing pool """
        pool = ThreadPool(processes=CPUCount()-1)

        while iterCounter <= len(self.predictorDataNames):

            print(iterCounter / (len(self.predictorDataNames)))
            iterCounter = iterCounter + 1

            """ Iterate through each model and perform 1 iteration of Sequential Floating Selection """
            for i in range(self.numModels):

                """ Check to see if this model has completed yet"""
                if self.searchDictList[i]['FeatSelectionProgress'] == 'Completed':
                    continue

                """ Set some variables for this iteration """
                modelChanged = False
                if iterCounter == 1:  # Seed the equationDict with Forced Predictors during the 1st iteration
                    self.searchDictList[i]['prdIDs'] = self.equationDict['ForcedPredictors']

                currentPredictorSet = self.searchDictList[i]['prdIDs']
                remainingPredictors = [prd for prd in self.predictorDataNames if prd not in currentPredictorSet]

                """ Set up a pool of processes (to be run on multiple cores if there are lots of predictors) to test each predictor addition """

                results = list(map(testPredictorSet, [list(l) for l in zip( repeat(currentPredictorSet),
                                                                            remainingPredictors,
                                                                            repeat('Add'),
                                                                            repeat(currentModels),
                                                                            repeat(self.cv),
                                                                            repeat(self.perfMetric),
                                                                            repeat(self.predictorData),
                                                                            repeat(self.predictandData),
                                                                            repeat(self.ObjFunctionRun),
                                                                            repeat(pool))]))

                """ Determine if any of the additions increased model performance """
                for result in results:

                    if result[0]['prdID'] == ['000']:
                        continue

                    if result[0]['prdID'] == ['-1000']:
                            modelsAnalyzed = modelsAnalyzed + 1
                            self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))
                            continue

                    if Metrics.metricBetterThan( newMetric = result[1][self.perfMetric], oldMetric = self.searchDictList[i]['Metrics'][self.perfMetric], perfMeasure = self.perfMetric):
                        predictorAdded = list(set(result[0]['prdID']) - set(currentPredictorSet))
                        self.searchDictList[i]['Metrics'] = result[1]
                        self.searchDictList[i]['prdIDs'] = result[0]['prdID']
                        self.searchDictList[i]['Forecasted'] = result[2]['Forecasted']
                        self.searchDictList[i]['CV_Forecasted'] = result[2]['CV_Forecasted']
                        self.searchDictList[i]['Coef'] = result[3]
                        self.searchDictList[i]['Intercept'] = result[4]
                        self.searchDictList[i]['PrincCompData'] = result[5]
                        self.searchDictList[i]['Years Used'] = result[6]
                        currentModels[i] = result[0]['prdID']
                        modelChanged = True

                    modelsAnalyzed = modelsAnalyzed + 1
                    self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))



                """ If we didn't add a predictor, attempt to skip a step and try adding 2 predictors """
                if modelChanged == False:
                    remainingPredictors = list(combinations(remainingPredictors, 2))

                    results = list(map(testPredictorSet, [list(l) for l in zip( repeat(currentPredictorSet),
                                                                                remainingPredictors,
                                                                                repeat('Add'),
                                                                                repeat(currentModels),
                                                                                repeat(self.cv),
                                                                                repeat(self.perfMetric),
                                                                                repeat(self.predictorData),
                                                                                repeat(self.predictandData),
                                                                                repeat(self.ObjFunctionRun),
                                                                                repeat(pool))]))

                    for result in results:

                        if result[0]['prdID'] == ['000']:
                            continue

                        if result[0]['prdID'] == ['-1000']:
                            modelsAnalyzed = modelsAnalyzed + 1
                            self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))
                            continue

                        if Metrics.metricBetterThan( newMetric = result[1][self.perfMetric], oldMetric = self.searchDictList[i]['Metrics'][self.perfMetric], perfMeasure = self.perfMetric):
                            predictorAdded = list(set(result[0]['prdID']) - set(currentPredictorSet))
                            self.searchDictList[i]['Metrics'] = result[1]
                            self.searchDictList[i]['prdIDs'] = result[0]['prdID']
                            self.searchDictList[i]['Forecasted'] = result[2]['Forecasted']
                            self.searchDictList[i]['CV_Forecasted'] = result[2]['CV_Forecasted']
                            self.searchDictList[i]['Coef'] = result[3]
                            self.searchDictList[i]['Intercept'] = result[4]
                            self.searchDictList[i]['PrincCompData'] = result[5]
                            self.searchDictList[i]['Years Used'] = result[6]
                            currentModels[i] = result[0]['prdID']
                            modelChanged = True

                        modelsAnalyzed = modelsAnalyzed + 1
                        self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))

                """ Set up a pool of processes to test each predictor removal """
                """ But don't try and remove the 1)predictor we just added or 2)Forced Predictors """
                currentPredictorSet = self.searchDictList[i]['prdIDs']
                if modelChanged:
                    predictorsToBeRemoved = list(set(currentPredictorSet) - set(predictorAdded) - set(self.equationDict['ForcedPredictors']))
                else:
                    predictorsToBeRemoved = list(set(currentPredictorSet) - set(self.equationDict['ForcedPredictors']))

                results = list(map(testPredictorSet, [list(l) for l in zip( repeat(currentPredictorSet),
                                                                            predictorsToBeRemoved,
                                                                            repeat('Remove'),
                                                                            repeat(currentModels),
                                                                            repeat(self.cv),
                                                                            repeat(self.perfMetric),
                                                                            repeat(self.predictorData),
                                                                            repeat(self.predictandData),
                                                                            repeat(self.ObjFunctionRun),
                                                                            repeat(pool))]))

                """ Determine if any of the removals increased model performance """
                for result in results:

                    if result[0]['prdID'] == ['000']:
                        continue

                    if result[0]['prdID'] == ['-1000']:
                        modelsAnalyzed = modelsAnalyzed + 1
                        self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))
                        continue

                    if Metrics.metricBetterThan( newMetric = result[1][self.perfMetric], oldMetric = self.searchDictList[i]['Metrics'][self.perfMetric], perfMeasure = self.perfMetric):
                        self.searchDictList[i]['Metrics'] = result[1]
                        self.searchDictList[i]['prdIDs'] = result[0]['prdID']
                        self.searchDictList[i]['Forecasted'] = result[2]['Forecasted']
                        self.searchDictList[i]['CV_Forecasted'] = result[2]['CV_Forecasted']
                        self.searchDictList[i]['Coef'] = result[3]
                        self.searchDictList[i]['Intercept'] = result[4]
                        self.searchDictList[i]['PrincCompData'] = result[5]
                        self.searchDictList[i]['Years Used'] = result[6]
                        currentModels[i] = result[0]['prdID']
                        modelChanged = True

                    modelsAnalyzed = modelsAnalyzed + 1
                    self.signals.updateRunLabel.emit("Models Analyzed: {0}".format(modelsAnalyzed))

                """ If the model hasn't changed, complete the model and update the progress bar """
                if modelChanged == False and currentPredictorSet != []:
                    self.searchDictList[i]['FeatSelectionProgress'] = 'Completed'
                    modelsCompleted = modelsCompleted + 1
                    self.signals.updateProgBar.emit(int(100*modelsCompleted/self.numModels))


        for i in reversed(range(len(self.searchDictList))):
            if self.searchDictList[i]['Coef'] == []:
                del self.searchDictList[i]
            else:
                fcstID = encryptions.generateFcstID(self.searchDictList[i]['Type'], self.searchDictList[i]['prdIDs'])
                self.searchDictList[i]['fcstID'] = fcstID

        pool.close()
        pool.join()

        self.signals.returnFcstDict.emit(self.searchDictList)
    """
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################


    """

    def BruteForce(self):

        """ Initialize data containers needed by the feature selection algorithm """
        self.initializeContainers(bruteForce=True)

        if len(self.predictorDataNames) == 0:
            print('No predictors selected')
            self.signals.returnFcstDict.emit(self.searchDictList)
            return

        """ Get a list of unique predictor combinations """
        predCombos = sum([list(map(list, itertools.combinations(self.predictorDataNames, i))) for i in range(len(self.predictorDataNames) + 1)], [])
        del predCombos[0] # Remove the null-set

        """ Array to store current models """
        currentModels = [[] for i in range(self.numModels)]
        modelsCompleted = 0

        """ Set up a multiprocessing pool """
        pool = ThreadPool(processes=CPUCount()-1)

        """ Iterate through each predictor combination """
        allSignificantOriginalSetting = readConfig('allsignificantoverride')
        writeConfig('allsignificantoverride','True')
        for predComboIdx in range(len(predCombos)):

            print(predComboIdx / len(predCombos))

            """ Set some variables for this iteration """
            #self.searchDictList[i]['prdIDs'] = predCombos[i]
            currentPredictorSet = predCombos[predComboIdx]#self.searchDictList[i]['prdIDs']
            remainingPredictors = []
            modelsCompleted = modelsCompleted + 1
            self.signals.updateRunLabel.emit("Models Analyzed: {0} of {1}".format(modelsCompleted, len(predCombos)))
            self.signals.updateProgBar.emit(int(100*modelsCompleted/len(predCombos)))

            """ Test model """
            result = testPredictorSet(list_=[currentPredictorSet, remainingPredictors, 'Add', currentModels,
                                             self.cv, self.perfMetric, self.predictorData, self.predictandData,
                                             self.ObjFunctionRun, pool],SFBS=False,first_iteration=False)

            if result[0]['prdID'] == ['000']: #Catch predictor combos that can't be evaluated via PCA or ZSCORE
                continue
            else:
                if predComboIdx < self.numModels: #Add results to solution pool if pool is not full
                    self.searchDictList[predComboIdx]['Metrics'] = result[1]
                    self.searchDictList[predComboIdx]['prdIDs'] = result[0]['prdID']
                    self.searchDictList[predComboIdx]['Forecasted'] = result[2]['Forecasted']
                    self.searchDictList[predComboIdx]['CV_Forecasted'] = result[2]['CV_Forecasted']
                    self.searchDictList[predComboIdx]['Coef'] = result[3]
                    self.searchDictList[predComboIdx]['Intercept'] = result[4]
                    self.searchDictList[predComboIdx]['PrincCompData'] = result[5]
                    self.searchDictList[predComboIdx]['Years Used'] = result[6]
                    currentModels[predComboIdx] = result[0]['prdID']
                else: #Process results and knock out less-performant models
                    minIndex = -1
                    if self.perfMetric == 'Root Mean Squared Error' or self.perfMetric == 'Root Mean Squared Prediction Error' or self.perfMetric == 'Mean Absolute Error':
                        minMetric = float("-inf")
                    else:
                        minMetric = float("inf")
                        
                    # Find least performant model
                    for j in range(len(self.searchDictList)):
                        ithMetric = self.searchDictList[j]['Metrics'][self.perfMetric]
                        if (ithMetric < minMetric) or (ithMetric > minMetric and (self.perfMetric == 'Root Mean Squared Error' or self.perfMetric == 'Root Mean Squared Prediction Error' or self.perfMetric == 'Mean Absolute Error')):
                            minMetric = ithMetric
                            minIndex = j

                    # Replace less-performant model if new one does better
                    if (result[1][self.perfMetric] > minMetric) or (result[1][self.perfMetric] < minMetric and (self.perfMetric == 'Root Mean Squared Error' or self.perfMetric == 'Root Mean Squared Prediction Error' or self.perfMetric == 'Mean Absolute Error')):
                        self.searchDictList[minIndex]['Metrics'] = result[1]
                        self.searchDictList[minIndex]['prdIDs'] = result[0]['prdID']
                        self.searchDictList[minIndex]['Forecasted'] = result[2]['Forecasted']
                        self.searchDictList[minIndex]['CV_Forecasted'] = result[2]['CV_Forecasted']
                        self.searchDictList[minIndex]['Coef'] = result[3]
                        self.searchDictList[minIndex]['Intercept'] = result[4]
                        self.searchDictList[minIndex]['PrincCompData'] = result[5]
                        self.searchDictList[minIndex]['Years Used'] = result[6]
                        currentModels[minIndex] = result[0]['prdID']
                    else:
                        continue


        for i in reversed(range(len(self.searchDictList))):
            if self.searchDictList[i]['Coef'] == []:
                del self.searchDictList[i]
            else:
                fcstID = encryptions.generateFcstID(self.searchDictList[i]['Type'], self.searchDictList[i]['prdIDs'])
                self.searchDictList[i]['fcstID'] = fcstID

        writeConfig('allsignificantoverride',allSignificantOriginalSetting)
        pool.close()
        pool.join()

        self.signals.returnFcstDict.emit(self.searchDictList)
    """
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################
    ########################################################################################
    #########################################################################################


    """
def testPredictorSet(list_, SFBS=False, first_iteration=False):
    """
    """
    currentPredictors = list_[0]
    potentialPredictor = list_[1]
    addOrRemove = list_[2]
    currentModels = list_[3]
    cv = list_[4]
    perfMetric = list_[5]
    predictorData_ = list_[6]
    predictandData_ = list_[7]
    ObjFunctionRun = list_[8]
    pool = list_[9]

    if addOrRemove == 'Add':
        if isinstance(potentialPredictor, str):
            testPredictors = currentPredictors + [potentialPredictor]
        else:
            testPredictors = currentPredictors + list(potentialPredictor)
    else:
        testPredictors = list(set(currentPredictors) - set([potentialPredictor]))

    testPredictors = sorted(testPredictors)


    """ Check to make sure that the predictor combo doesn't already exist """
    if testPredictors in currentModels:
        return [{'prdID':['000']}, \
        {"Cross Validated Adjusted R2":float("-inf"),
        "Root Mean Squared Prediction Error":float("inf"),
        "Cross Validated Nash-Sutcliffe":float("-inf"),
        "Adjusted R2" : float("-inf"),
        "Root Mean Squared Error" : float("inf"),
        "Nash-Sutcliffe": float("-inf"),
        "Sample Variance": float("-inf"),
        "Mean Absolute Error": float("inf") }, \
        {"Forecasted":None, "CV_Forecasted":None},None, None]

    if ObjFunctionRun != ZScoreRegression:
        testPredictorsData = predictorData_[testPredictors].dropna()
        commonIndex = predictandData_.index.intersection(testPredictorsData.index)
        testPredictorsData = testPredictorsData.loc[commonIndex]
        predictandData = predictandData_.loc[commonIndex]
        yearsUsed = commonIndex
    else:
        testPredictorsData = predictorData_[testPredictors]
        commonIndex = predictandData_.index.intersection(testPredictorsData.index)
        testPredictorsData = testPredictorsData.loc[commonIndex]
        predictandData = predictandData_.loc[commonIndex]
        yearsUsed = commonIndex

    if testPredictorsData.empty:
        return [{'prdID':['000']}, \
        {"Cross Validated Adjusted R2":float("-inf"),
        "Root Mean Squared Prediction Error":float("inf"),
        "Cross Validated Nash-Sutcliffe":float("-inf"),
        "Adjusted R2" : float("-inf"),
        "Root Mean Squared Error" : float("inf"),
        "Nash-Sutcliffe": float("-inf"),
        "Sample Variance": float("-inf"),
        "Mean Absolute Error" : float("inf") }, \
        {"Forecasted":None, "CV_Forecasted":None},None, None]
    
    if testPredictorsData.shape[1] == 1 and (ObjFunctionRun == PrincipalComponentsRegression or ObjFunctionRun == ZScoreRegression):
        return [{'prdID':['000']}, \
        {"Cross Validated Adjusted R2":float("-inf"),
        "Root Mean Squared Prediction Error":float("inf"),
        "Cross Validated Nash-Sutcliffe":float("-inf"),
        "Adjusted R2" : float("-inf"),
        "Root Mean Squared Error" : float("inf"),
        "Nash-Sutcliffe": float("-inf"),
        "Sample Variance": float("-inf"),
        "Mean Absolute Error" : float("inf") }, \
        {"Forecasted":None, "CV_Forecasted":None},None, None]


    """ Convert to numpy array """
    testPredictorsData = np.array(testPredictorsData)
    predictandData = np.array(predictandData)
    

    if ObjFunctionRun == MultipleRegression:
        metrics, forecasted, coefs, intercept, CV_Forecasted, all_significant = ObjFunctionRun(testPredictorsData, predictandData, cv, perfMetric, pool)
        princCompData = {}
    elif ObjFunctionRun == PrincipalComponentsRegression:
        try:
            metrics, forecasted, coefs, intercept, princCompData, CV_Forecasted, all_significant = ObjFunctionRun(testPredictorsData, predictandData, cv, perfMetric, pool)
        except:
            return [{'prdID':['-1000']}, \
                {"Cross Validated Adjusted R2":float("-inf"),
                "Root Mean Squared Prediction Error":float("inf"),
                "Cross Validated Nash-Sutcliffe":float("-inf"),
                "Adjusted R2" : float("-inf"),
                "Root Mean Squared Error" : float("inf"),
                "Nash-Sutcliffe": float("-inf"),
                "Sample Variance" : float("inf"),
                "Mean Absolute Error" : float("inf") }, \
                {"Forecasted":None, "CV_Forecasted":None},None, None]
    else:
        metrics, forecasted, coefs, intercept, princCompData, CV_Forecasted, all_significant = ObjFunctionRun(testPredictorsData, predictandData, cv, perfMetric, pool)

    userOverride = False
    if readConfig('allsignificantoverride') == 'True':
        all_significant = True
        userOverride = True

    if not all_significant: #Override all_significant determination by the selected regression model
        return [{'prdID':['-1000']}, \
                {"Cross Validated Adjusted R2":float("-inf"),
                "Root Mean Squared Prediction Error":float("inf"),
                "Cross Validated Nash-Sutcliffe":float("-inf"),
                "Adjusted R2" : float("-inf"),
                "Root Mean Squared Error" : float("inf"),
                "Nash-Sutcliffe": float("-inf"),
                "Sample Variance" : float("inf"),
                "Mean Absolute Error" : float("inf") }, \
                {"Forecasted":None, "CV_Forecasted":None},None, None]

    if not userOverride: #Catch Brute-Force method so it reports all possible combinations
        for i, prd in enumerate(testPredictors):
            if np.round(coefs[i],3) == 0.0:
                return [{'prdID':['000']}, \
                        {"Cross Validated Adjusted R2":float("-inf"),
                         "Root Mean Squared Prediction Error":float("inf"),
                         "Cross Validated Nash-Sutcliffe":float("-inf"),
                         "Adjusted R2" : float("-inf"),
                         "Root Mean Squared Error" : float("inf"),
                         "Nash-Sutcliffe": float("-inf"),
                         "Sample Variance" : float("inf"),
                         "Mean Absolute Error" : float("inf") }, \
                        {"Forecasted":None, "CV_Forecasted":None},None, None]

            # DO NOT ALLOW NEGATIVE COEFFICIENTS FOR SNOTEL SWE PREDICTORS
            if int(prd) >= 9000 and np.round(coefs[i], 3) <= 0:
                return [{'prdID':['000']}, \
                        {"Cross Validated Adjusted R2":float("-inf"),
                         "Root Mean Squared Prediction Error":float("inf"),
                         "Cross Validated Nash-Sutcliffe":float("-inf"),
                         "Adjusted R2" : float("-inf"),
                         "Root Mean Squared Error" : float("inf"),
                         "Nash-Sutcliffe": float("-inf"),
                         "Sample Variance" : float("inf"),
                         "Mean Absolute Error" : float("inf") }, \
                        {"Forecasted":None, "CV_Forecasted":None}, None, None]


    return [{"prdID" : testPredictors}, metrics, {"Forecasted":forecasted, "CV_Forecasted": CV_Forecasted}, coefs, intercept, princCompData, yearsUsed]

def NeuralNetwork(xData, yData, crossVal, perfMetric, pool):
    """

    """
    input_layer_size = xData.shape[1]
    nn = MLPRegressor(
        hidden_layer_sizes=(int(np.ceil(input_layer_size / 2)),int(np.ceil(input_layer_size / 2))),
        activation="tanh",
        solver="lbfgs",
        warm_start=True
    )
    xScaled = (xData - np.mean(xData, axis=0)) / np.std(xData, axis=0)
    yScaled = (yData - np.mean(yData, axis=0)) / np.std(yData, axis=0)
    yScaled = yScaled.ravel()
    cv_ypred = model_selection.cross_val_predict(nn, xScaled, yScaled, cv=crossVal, n_jobs=1)
    cv_ypred = cv_ypred*np.std(yData, axis=0) + np.mean(yData, axis=0)
    nn.fit(xScaled, yScaled)
    ypred = nn.predict(xScaled)
    ypred = ypred*np.std(yData, axis=0) + np.mean(yData, axis=0)

    return Metrics.computeMetrics(cv_ypred, ypred, yData, input_layer_size), ypred, np.random.random(input_layer_size), np.random.random(1), cv_ypred

def MultipleRegression(xData, yData, crossVal, perfMetric, pool):
    """
    Simple multiple regression model. Takes an array of training predictor data
    and creates a least-squares fit with training predictand data. Geenerates 
    and returns predictions from a testing predictor data array.
    """
    
    def regression(training_predictors, training_predictand, testing_predictors, returnCoefs = False):
        """
        Performs a simple linear OLS regression between the training predictor data and the training predictand data.
        Then it makes predictions against the testing predictor set. Optionally, it will return the trained model coefficients and intercept.
        """

        """ Append a column of ones so that we can compute an intercept """
        x = np.vstack([training_predictors.T, np.ones(len(training_predictand))])

        """ Fit the model and get the coefficients """
        model = np.linalg.lstsq(x.T, training_predictand, rcond=None)
        coefs = model[0][:-1]
        intercept = model[0][-1]

        """ Return the testing predictions """
        if returnCoefs:
            return coefs, intercept

        return np.dot(testing_predictors, coefs) + intercept

    predictors = xData
    predictand = yData

    all_significant = True
    
    p = predictors.shape[1]

    cv_splits = [[train,test] for train, test in crossVal.split(predictand)]
    cv_predictors_train = [predictors[cv_splits[i][0]] for i in range(len(cv_splits))]
    cv_predictand_train = [predictand[cv_splits[i][0]] for i in range(len(cv_splits))]
    cv_predictors_test = [predictors[cv_splits[i][1]] for i in range(len(cv_splits))]

    cv_predictand_star = pool.starmap(regression, [tuple([cv_predictors_train[i], cv_predictand_train[i], cv_predictors_test[i]]) for i in range(len(cv_splits))])
    
    cv_predictand_star = np.array(cv_predictand_star)
    cv_predictand_star = np.concatenate(cv_predictand_star).ravel()

    coef, intercept = regression(predictors, predictand, predictors, returnCoefs=True)
    predictandStar = np.dot(predictors, coef) + intercept

    metric_dict =  Metrics.computeMetrics(cv_predictand_star, predictandStar, predictand, p)

    try:
        cov = (metric_dict['Root Mean Squared Error']**2) * np.linalg.inv(np.dot(np.transpose(xData), xData))
    except:
        all_significant = False
        return metric_dict, predictandStar, coef.flatten(), intercept.flatten(), cv_predictand_star, all_significant
    se = [np.sqrt(cov[i][i]) for i in range(len(coef))]
    t_ = [coef[i]/se[i] for i in range(len(se))]
    tVal = t.ppf(1-0.05, len(predictandStar) - (p+1))

    if True in [tt > -1*tVal and tt < tVal for tt in t_]:
        all_significant = False

    if readConfig('allsignificantoverride') == 'True':
        all_significant = True

    return metric_dict, predictandStar, coef.flatten(), intercept.flatten(), cv_predictand_star, all_significant

def PrincipalComponentsRegression(xData, yData, crossVal, perfMetric, pool):
    """
    Function to perform principal components regression on a 2-D array of xData and yData. Uses 
    the Numpy linear algebra method derived by StackOverflow user 'doug' @ (https://stackoverflow.com/questions/13224362/principal-component-analysis-pca-in-python).
    The principal components are then regressed against the predictand using least squares. 

    The data is first split by cross-validation method, then each split is processed into principal componenets, which are then regressed against the training predictand. 
    """

    def toPrincipalComponents(x):
        """
        Converts a 2-D array of predictor data to a 2-D array of principal 
        components and thier associated eigenvectors and eigenvalues
        """
        """ compute the covariance matrix """
        R = np.cov(x, rowvar=False, ddof=1)
        #R = np.dot(x.T, x) / x.shape[0]
        """ Compute the eigenvectors and eigenvalues of the covariance matrix """
        evals, evecs = np.linalg.eigh(R)
        """ Sort the eigenvalues in decreasing order """
        idx = np.argsort(evals)[::-1]
        evecs = evecs[:,idx]
        evals = evals[idx]
        """ Transform the data using the eigenvectors, and return everything """
        return np.dot(x,evecs), evals, evecs


    """ Standardize the xData by subtracting means and dividing by standard deviation """
    xMean = np.mean(xData, axis=0)
    xStd = np.std(xData, axis=0, ddof=1)
    xData = (xData - xMean) / xStd

    """ Obtain the principal components of the predictors """
    principalComps, evals, evecs = toPrincipalComponents(xData)
    
    """ Now we iterate through increasing # of principal components and regress them against the predictand """
    try:
        results = list(map(MultipleRegression, [principalComps[:,:i+1] for i in range(xData.shape[1])], repeat(yData), repeat(crossVal), repeat(perfMetric), repeat(pool)))
    except Exception as E:
        print(E)

    """ Only return the best result """
    bestMetric = {"Cross Validated Adjusted R2":-1000, "Root Mean Squared Prediction Error":10000,"Cross Validated Nash-Sutcliffe":-1000, "Cross Validated Adjusted R2":-1000, "Root Mean Squared Error":10000, "Cross Validated Nash-Sutcliffe":-1000, "Sample Variance":10000, "Mean Absolute Error":10000}
    bestStarData = {"Forecasted":None}
    bestCoefs = []
    bestIntercept = []
    for i, result in enumerate(results):
      
        if Metrics.metricBetterThan(newMetric=result[0][perfMetric], oldMetric=bestMetric[perfMetric], perfMeasure=perfMetric):
            bestMetric = result[0]
            bestStarData = result[1]
            bestCoefs = result[2]
            bestIntercept = result[3]
            bestCvStarData = result[4]
            all_significant = result[5]
    
    """ Compute the actual coefficients and intercept """
    coefs = []
    intercept = bestIntercept
    for prd in range(xData.shape[1]):
        coef = 0
        for j, regrWeight in enumerate(bestCoefs):
            coef = coef + regrWeight * evecs[prd, j] / xStd[prd]
            intercept = intercept - regrWeight * evecs[prd,j] * xMean[prd] / xStd[prd]
        coefs.append(coef)

    if readConfig('allsignificantoverride') == 'True':
        all_significant = True

    return bestMetric, bestStarData, coefs, intercept, {'PC':principalComps, 'numPCs':len(bestCoefs), 'eigenVecs':evecs, 'eigenVals':evals, 'PCCoefs':bestCoefs, 'PCInt':bestIntercept, 'xMean':xMean, 'xStd':xStd}, bestCvStarData, all_significant

def ZScoreRegression(xData, yData, crossVal, perfMetric, pool):
    """
    """

    """ Convert the X-Data to Z-Scores """
    xMean = np.nanmean(xData, axis=0)
    xStd = np.nanstd(xData, axis=0, ddof=1)
    xData = (xData - xMean) / xStd

    """ Initialize a list to store z-score regression coefficients """
    r2List = []
    pos = []

    """ Regress each z-score against Y and store the r2 value """
    for i in range(xData.shape[1]):
        xDataWithOnesCol = np.vstack((xData[:,i].T, np.ones(xData.shape[0])))
        missing = np.isnan(xDataWithOnesCol.T[:,0])
        xDataWithOnesCol = xDataWithOnesCol.T[~missing]
        y = yData[~missing]
        model = np.linalg.lstsq(xDataWithOnesCol, y, rcond=None)
        if model[0][0] >= 0:
            yStar = np.dot(xDataWithOnesCol, model[0])
            #r2=computeR2(yStar, y)
            r2 =Metrics.computeR2(yStar, y)
            if r2 > 0.09:
                r2List.append(r2)
            else:
                r2List.append(0)
            pos.append(True)
        else:
            xData[:,i] = -1*xData[:,i]
            xDataWithOnesCol = np.vstack((xData[:,i].T, np.ones(xData.shape[0])))
            missing = np.isnan(xDataWithOnesCol.T[:,0])
            xDataWithOnesCol = xDataWithOnesCol.T[~missing]
            y = yData[~missing]
            model = np.linalg.lstsq(xDataWithOnesCol, y, rcond=None)
            yStar = np.dot(xDataWithOnesCol, model[0])
            #r2=computeR2(yStar, y)
            r2 =Metrics.computeR2(yStar, y)
            if r2 > 0.09:
                r2List.append(r2)
            else:
                r2List.append(0)
            pos.append(False)

    """ Return without further analysis if 0 in r2 list """
    if 0 in r2List:
        return {}, [], [], None, {}, [], False
        

    """ Consturct a composite dataset """
    C = []
    r2List = np.array(r2List)
    for row in xData:
        missing = np.isnan(row)
        r2 = r2List[~missing]
        c = np.dot(row[~missing], r2)/np.sum(r2)
        C.append(c)
    C = np.array(C).reshape(-1,1)
    
    """ Regress the composite dataset against the y data using cross validation and least squares ) """
    metrics, predictandStar, zCoefs, zIntercept, cv_predictandStar, all_significant = MultipleRegression(C, yData, crossVal, perfMetric, pool)

    """ Compute the actual coefficients and intercept """
    coefs = []
    intercept = zIntercept
    for prd in range(xData.shape[1]):
        coef = zCoefs * r2List[prd] / (np.sum(r2List) * xStd[prd])
        if not pos[prd]:
            coef = -1*coef
        intercept = intercept - coef*xMean[prd]
        coefs.append(coef)

    if readConfig('allsignificantoverride') == 'True':
        all_significant = True

    return metrics, predictandStar, coefs, intercept, {"Composite Set":C, "R2-List":r2List, "Z": xData, "CCoef":zCoefs, "CInt":zIntercept, 'xMean':xMean, 'xStd':xStd}, cv_predictandStar, all_significant





