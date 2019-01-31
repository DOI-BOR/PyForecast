"""

Script Name:        application.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      Nov 13, 2018

Description:        'application.py' is the main processing script for the 
                    PyForecast application. This script loads the GUI and directs
                    all events and function calls. This script also handles loading
                    and saving documents, as well as exporting tables.

Disclaimer:         This script, and the overall PyForecast Application have been
                    reviewed and the methodology has been deemed sound. However, 
                    the resulting forecasts and forecast equations generated from 
                    this program are not in any way guarnateed to be reliable or accurate, 
                    and should be used in conjuction with other forecasts and forecast methods. 

"""

"""
0.0 IMPORT LIBRARIES
'application.py' REQUIRES VARIOUS LIBRARIES TO BE IMPORTED IN ORDER TO RUN PROPERLY. HERE WE 
IMPORT THOSE LIBRARIES AND MODULES. ADDITIONALLY, WE ADD THE 'GUI' FOLDER TO THE SYSTEM PATH.
"""

import sys
import os

# Import GUI
from Resources.GUI import PyForecast_GUI, DocumentationGUI, MissingNoGUI, editDataLoaders, RegressionStatsGUI

# Import PyQt5 GUI functions
from PyQt5 import QtGui, QtCore, QtWidgets

# Import other scripts 
from Resources.GIS import CLIMATE_DIVISIONS
from Resources.Functions.miscFunctions import isValidHUC, monthLookup, current_date, readConfig, writeConfig
from Resources.Functions import DataDownloadV4, ProcessDataV2, RestServiceV2, encryptions, importSpread, FeatureSelectionV3, kernelDensity

# Import additional libraries
import json
import pickle
import pandas as pd
import time
import numpy as np
import math
import subprocess
import traceback
from datetime import datetime
from scipy import stats, integrate
from dateutil import parser
import multiprocessing as mp
import configparser


"""
1.0 INSTANTIATE GUI AND ASCRIBE FUNCTIONALITY
HERE WE CREATE AN INSTANCE OF THE APPLICATION'S GUI (LOCATED IN 'GUI.PyForcast_GUI.py') AND BEGIN
TO CONNECT SPECIFIC USERS' ACTIONS TO FUNCTIONS AND PROCESSES. 
"""

class mainWindow(QtWidgets.QMainWindow, PyForecast_GUI.UI_MainWindow):
    """
    This class is an instance of the main PyForecast GUI. It adds to the GUI by defining additional functions,
    and connecting GUI elements such as buttons, menus, etc to specific functions. 
    """
    
    def __init__(self, customDatetime):
        """
        The __init__ method runs when the GUI is first instantiated. Here we define the 'self' variable as a 
        reference to the mainWindow class, as well as build the GUI and connect all the functionality to the buttons
        and events in the GUI.

        'customDatetime' optionally allows the software to "change the system date" (really, we're just re-directing calls
        to the system date to a function that looks to this customDatetime instead of the system).

        Additionally, we assign a style sheet to the application (located in 'GUI.PyForecastStyle.qss'). We also
        start a threadpool to allow ourselves to work on multiple threads later on.
        """
        
        super(self.__class__, self).__init__()
        
        self.setupUi(self)

        self.purgeOldFiles()

        self.setDate(customDatetime)

        with open(os.path.abspath('Resources/GUI/PyForecastStyle.qss'), 'r') as styleFile:
            self.setStyleSheet(styleFile.read())
        
        self.show()

        self.connectEventsMenuBar()
        self.initDirectory()
        self.connectEventsSummaryTab()
        self.connectEventsStationsTab()
        self.connectEventsDataTab()  
        self.connectEventsForecastOptionsTab()
        self.connectEventsRegressionTab()
        self.connectEventsDensityTab()

        self.threadPool = QtCore.QThreadPool()
        writeConfig('savefilename','')

        return

    def purgeOldFiles(self):
        """
        This function removes any old csv files from the tempFiles directory
        """
        for file_ in os.listdir('Resources/tempFiles'):
            if file_ == '__pycache__' or 'pyforecast.cfg':
                continue
            filename = os.path.abspath('Resources/tempFiles/' + file_)
            try:
                os.remove(filename)
            except:
                pass
    def setDate(self, date):
        """
        This function sets the date in the software. It stores the time in a config file called 'Resources/tempFiles/pyforecast.cfg'
        """
        
        writeConfig('programtime',date)
        
        # Need to change the dates in porT1 and porT2
        yearT2 = pd.to_datetime(date).year
        yearT1 = (pd.to_datetime(date) - pd.DateOffset(years=30)).year
        self.dataTab.dataOptions.porT1.setText(str(yearT1))
        self.dataTab.dataOptions.porT2.setText(str(yearT2))

        return

    
    def initDirectory(self):
        """
        Initializes the 2 main dictionaries that the PyForecast application uses to store data for the forecasts.
        """
        self.datasetDirectory = {"datasets":[]}
        self.forecastDict = {"PredictorPool":{},"EquationPools":{},"Options":{}}

        return


    """
    Purposely left blank






















    """

    """"
    1.1 MENU BAR
    HERE WE CONNECT THE MENU BAR BUTTONS TO SPECIFIC FUNCTIONS AND DEFINE THOSE SPECIFIC FUNCTIONS.
    """

    def connectEventsMenuBar(self):
        """
        Connects the button-press signals (emitted when a user pressed a menu-bar button) to their 
        respective functions. For example, when a user presses the docAction button ('Documentation'),
        the function 'openDocs' is triggered.
        """

        self.docAction.triggered.connect(self.openDocs)
        self.versionAction.triggered.connect(self.openVersion)
        self.saveAction.triggered.connect(self.saveFile)
        self.saveAsAction.triggered.connect(self.saveFileAs)
        self.openAction.triggered.connect(self.openFile)
        self.addLoaderAction.triggered.connect(self.addLoader)
        self.newAction.triggered.connect(self.newForecast)
        self.setCustomDatetimeAction.triggered.connect(self.setCustomDatetimeDialog)
    
        return

    def newForecast(self):
        """
        Restarts the program with a new process. Starts the user with a fresh, clean GUI.
        """
        
        #Ensure that the user wants a new forecast
        button = QtWidgets.QMessageBox.question(self, 'New Forecast','Are you sure you want to start over?', QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if button != QtWidgets.QMessageBox.Ok:
            return

        subprocess.Popen("pythonw PyForecast.pyw --splash=False")

        return


    def openDocs(self):
        """
        Self explanatory. Instantiates the documentation GUI. See GUI.DocumentationGUI.py for more information
        """
        self.docs = DocumentationGUI.DocumentationWindow()

        return


    def openVersion(self):
        """
        Self explanatory. Instantiates the version GUI. See GUI.DocumentationGUI.py for more information
        """
        self.vers = DocumentationGUI.VersionWindow()

        return


    def saveFileAs(self):
        self.saveFile(True)
        return

    def saveFile(self, saveNew=False):
        """
        Function to save the 2 main dictionaries into a pickled .fcst file. Additionally sets the 
        file name in the window title.
        """    
        filename = readConfig('savefilename')

        if filename == '' or saveNew:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File As', 'unititled.fcst','*.fcst')[0]
            writeConfig('savefilename',filename)

            if filename == '':
                return

            if '.' not in filename:
                filename = filename + '.fcst'

        pkl = {
            "datasetDirectory":self.datasetDirectory,
            "forecastDict":self.forecastDict
        }

        with open(filename, 'wb') as writefile:
            pickle.dump(pkl, writefile, pickle.HIGHEST_PROTOCOL)

        self.setWindowTitle("PyForecast v2.0 - {0}".format(filename))

        return

  
    def openFile(self):
        """
        Function to read a pickled .fcst file and extract the 2 main dictionaries. Then, uses the 2 dictionaries
        to populate the stations tab table, the data table, and the forecast options tables. Additionally,
        sets the window title with the file name. If unseuccessfull, it prints a traceback error to a messagebox.
        """
        
        try:
           
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File','*.fcst')[0]
            writeConfig('savefilename',filename)

            if filename == '':
                return  

            with open(filename, 'rb') as readfile:
                j = pickle.load(readfile)

            self.datasetDirectory = j['datasetDirectory']
            self.forecastDict = j['forecastDict']

            self.stationsTab.stationInfoPane.stationTable.setRowCount(0) 

            for station in self.datasetDirectory['datasets']:
                dataID = station['PYID']
                stationType = station['TYPE']
                stationNumber = station['ID']
                stationName = station['Name']
                stationParam = station['Parameter']
                self.stationsTab.stationInfoPane.stationTable.addRow([dataID, stationType, stationNumber, stationName, stationParam])
            
            self.dataTab.dataTable.setRowCount(0)
            self.dataTab.dataTable.setColumnCount(0) 

            try:
                self.dataTab.dataTable.cellChanged.disconnect()
                self.dataTab.dataTable.TableFromDatasetDirectory(self.datasetDirectory['datasets'])
                self.dataTab.dataTable.cellChanged.connect(self.userEditedData)
            except:
                self.dataTab.dataTable.cellChanged.connect(self.userEditedData)
                pass

            try:
                self.displayForecastDict(self.forecastDict)
                self.populateEquationsDropDown(4)
                self.populateDensityEquations(5)
            except:
                pass

            self.reDrawForecastDict()

            self.setWindowTitle("PyForecast v2.0 - {0}".format(filename))

            return
        
        except Exception as e:
            button = QtWidgets.QMessageBox.question(self, 'Error','File could not load. See the following error: \n{0}'.format(traceback.format_exc()), QtWidgets.QMessageBox.Ok)
            if button == QtWidgets.QMessageBox.Ok:
                return


    def addLoader(self):
        """
        Instantiates the dataloader editing dialog GUI. See 'GUI.editDataLoaders.py' for more information about this dialog window.
        """
        self.loaderDialog = editDataLoaders.dataloaderDialog()

        return
    
    def setCustomDatetimeDialog(self):
        """
        """
        def is_date(string):
            try: 
                parser.parse(string)
                return True
            except ValueError:
                return False
        self.setCustomDatetimeDialogText, ok = QtWidgets.QInputDialog.getText(self, 'Set Custom Date for PyForecast', 'Set Date (YYYY-MM-DD)',text=readConfig('programtime'))
        if ok and is_date(self.setCustomDatetimeDialogText):
            self.setDate(self.setCustomDatetimeDialogText)
        return
    """
    Purposely left blank





















    """

    """
    1.1 SUMMARY TAB
    THE SUMMARY TAB ALLOWS USERS TO VIEW SAVED FORECAST EQUATIONS AND TO GENERATE CURRENT WATER YEAR FORECASTS BASED ON THOSE EQUATIONS. 
    IN THIS SECTION WE ASCRIBE ALL THE FUNCIONALITY TO THE FORECAST TAB. THIS LAYOUT OF THE TAB IS DESCRIBED IN THE GUI FILE.
    """

    def connectEventsSummaryTab(self):
        """
        This function connects functions to tiggered events from button or menu presses.
        """
        self.summaryTab.fcstTree.delAction.triggered.connect(self.deleteForecast)
        self.summaryTab.fcstTree.genAction.triggered.connect(self.genForecastButtonClicked)
        self.summaryTab.fcstTree.clicked.connect(self.fcstSelectedToView)
        
        return


    def genForecastButtonClicked(self):
        """
        This function figures out which forecast equation was selected by the user,
        and uses current water year data to generate a current water year forceast 
        based on that equation. 

        It begins by storing the equations predictor data (x-data, aka design matrix) into 
        a dataframe. This is the predictor data that was used to generate the equation.

        Next, it uses the predictor ID's to identify the data for the current water year (the
        data that we'll use to generate the forecast). Lastly, it uses the forecast metrics
        and the predictor data to generate a forecast (with uncertainty) using the method
        outlined at https://onlinecourses.science.psu.edu/stat501/node/315/
        """

        # Retrieve the forecast that the user selected to view
        index = self.summaryTab.fcstTree.selectedIndexes()[0]
        fcst = self.fcstSelectedToView(index, returnFcstOnly=True)
        if fcst == None:
            return
        
        # Reconstruct the predictor data that was used to generate the equation.
        prdIDs = fcst['PrdIDs']
        coefs = fcst['Coef']
        predictorDataDF = pd.DataFrame()
        predictorData = np.array([[]])

        for prdid in prdIDs:
            for predictorName in self.forecastDict['PredictorPool']:
                for interval in self.forecastDict['PredictorPool'][predictorName]:
                    if self.forecastDict['PredictorPool'][predictorName][interval]['prdID'] == prdid:
                        predictorData_temp = pd.DataFrame().from_dict(self.forecastDict['PredictorPool'][predictorName][interval]['Data'], orient='columns')
                        predictorData_temp = predictorData_temp.loc[fcst['Water Years']]
                        if predictorData.size == 0:
                            predictorData = predictorData_temp.values
                        else:
                            predictorData = np.concatenate((predictorData, predictorData_temp),axis=1)
                        predictorDataDF = pd.concat([predictorDataDF, pd.DataFrame().from_dict(self.forecastDict['PredictorPool'][predictorName][interval]['Data'], orient='columns')], axis=1)
        
        # Retrieve the current water year predictor data for the equation's predictors. 
        # If the current data is unavailable, replace it with NaN
        currentData = []

        currentMonth = current_date().month
        if currentMonth >= 10:
            currentWaterYear = current_date().year + 1
        
        else:
            currentWaterYear = current_date().year 
        
        for prdid in prdIDs:
            if predictorDataDF[prdid].index[-1].year != currentWaterYear:
                currentData.append(np.nan)
            else:
                currentData.append(predictorDataDF[prdid][-1])

        # Iterate through the equations prdIDs and add the associated data to a dataframe, only including the water years that the equation 
        # was generated from.
        if 'MLR' in fcst['Type']:
            
            
            # This section uses the current water year data to generate a current water year forecast
            # If the program couldn't retrieve data for a predictor, it will not try to generate a forecast.
            if True not in np.isnan(currentData):

                """ Compute the forecast """
                forecast = np.dot(currentData, coefs) + fcst['Intercept']

                """ Compute prediction interval """
                predictorData = np.vstack([predictorData.T, np.ones(predictorData.shape[0])]).T
                print('predictorData ', predictorData)
                xH = np.array(currentData + [1]).reshape(-1,1)
                print('xH ', xH)
                j = np.linalg.inv(np.dot(np.transpose(predictorData), predictorData))
                print('j ', j)
                j = np.dot(np.transpose(xH), j)
                j = np.dot(j, xH)
                mse = fcst['Metrics']['Root Mean Squared Error']**2
                se_yh = np.sqrt(mse * j)
                se_pred = np.sqrt(mse + se_yh**2)
                n = predictorData.shape[0]
                p = len(xH)
                degF = n - p
                t_stat_10 = stats.t.ppf(1-0.05, degF)
                t_stat_30 = stats.t.ppf(1-0.15, degF)
                predInt10 = forecast - t_stat_10*np.sqrt(mse + se_yh**2)
                predInt30 = forecast - t_stat_30*np.sqrt(mse + se_yh**2)
                predInt70 = forecast + t_stat_30*np.sqrt(mse + se_yh**2)
                predInt90 = forecast + t_stat_10*np.sqrt(mse + se_yh**2)

                """ Append to the forecast dict entry"""
                self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear] = {}
                self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['Intervals'] = {
                    "10%":float(np.round(predInt10,1)), 
                    "30%":float(np.round(predInt30,1)), 
                    "50%":float(np.round(forecast,1)), 
                    "70%":float(np.round(predInt70,1)), 
                    "90%":float(np.round(predInt90,1)) }   
                self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['CurrentData'] = currentData
                self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['StdErrPred'] = se_pred
                self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['degFreedom'] = degF

                """ Plot the resulting forecast and prediction interval """
                self.plotForecastSummaryTab(self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']])
                self.fcstSelectedToView(index)
                self.reDrawForecastDict()
                self.summaryTab.fcstTree.setExpanded(index, True)

            else:
                print(currentData)
                button = QtWidgets.QMessageBox.question(self, 'No data..','There is not enough current water year data to generate a forecast.', QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                print('current data incomplete')

                return

        if 'PCAR' in fcst['Type']:

            numComps = fcst['Extras']['numPCs']
            predictorData = pd.DataFrame(fcst['Extras']['PC'][:,:numComps])
            evals = fcst['Extras']['eigenVals']
            evecs = fcst['Extras']['eigenVecs']
            pcoefs = fcst['Extras']['PCCoefs']
            pint = fcst['Extras']['PCInt']
            xMean = fcst['Extras']['xMean']
            xStd = fcst['Extras']['xStd']

            # standardize current data
            currentData2 = (np.array(currentData) - np.array(xMean))/np.array(xStd)
            currentData2 = np.dot(currentData2, evecs)[:numComps]
            forecast = float(np.dot(currentData2, pcoefs)) + pint
            
            predictorData = np.vstack([predictorData.T, np.ones(predictorData.shape[0])]).T
            print('predictor ', predictorData)
            xH = np.array(list(currentData2) + [1]).reshape(-1,1)
            print('xH ', xH)
            j = np.linalg.inv(np.dot(np.transpose(predictorData), predictorData))
            print('j1 ', j)
            j = np.dot(np.transpose(xH), j)
            print('j2 ', j)
            j = np.dot(j, xH)
            print('j3 ', j)
            mse = fcst['Metrics']['Root Mean Squared Error']**2
            se_yh = np.sqrt(mse * j)
            se_pred = np.sqrt(mse + se_yh**2)
            n = predictorData.shape[0]
            p = len(xH)
            degF = n - p
            t_stat_10 = stats.t.ppf(1-0.05, degF)
            t_stat_30 = stats.t.ppf(1-0.15, degF)
            predInt10 = forecast - t_stat_10*np.sqrt(mse + se_yh**2)
            predInt30 = forecast - t_stat_30*np.sqrt(mse + se_yh**2)
            predInt70 = forecast + t_stat_30*np.sqrt(mse + se_yh**2)
            predInt90 = forecast + t_stat_10*np.sqrt(mse + se_yh**2)

            """ Append to the forecast dict entry"""
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear] = {}
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['Intervals'] = {
                "10%":float(np.round(predInt10,1)), 
                "30%":float(np.round(predInt30,1)), 
                "50%":float(np.round(forecast,1)), 
                "70%":float(np.round(predInt70,1)), 
                "90%":float(np.round(predInt90,1)) }   
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['CurrentData'] = currentData
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['StdErrPred'] = se_pred
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['degFreedom'] = degF

            """ Plot the resulting forecast and prediction interval """
            self.plotForecastSummaryTab(self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']])
            self.fcstSelectedToView(index)
            self.reDrawForecastDict()
            self.summaryTab.fcstTree.setExpanded(index, True)

        if 'ZSCR' in fcst['Type']:

            xStd = fcst['Extras']['xStd']
            xMean = fcst['Extras']['xMean']
            zCoef = fcst['Extras']['CCoef']
            zInt = fcst['Extras']['CInt']
            predictorData = fcst['Extras']['Composite Set']
            r2List = fcst['Extras']['R2-List']

            # Generate the current forecast
            currentData2 = (np.array(currentData) - np.array(xMean))/np.array(xStd)
            missing = np.isnan(currentData2)
            currentData3 = currentData2[~missing]
            r2List = r2List[~missing]
            C = np.sum([currentData3[i]*r2List[i] for i in range(len(currentData3))])/np.sum(r2List)
            forecast = float(C*zCoef) + zInt

            predictorData = np.vstack([predictorData.T, np.ones(predictorData.shape[0])]).T
            xH = np.array(list([C]) + [1]).reshape(-1,1)
            j = np.linalg.inv(np.dot(np.transpose(predictorData), predictorData))
            j = np.dot(np.transpose(xH), j)
            j = np.dot(j, xH)
            mse = fcst['Metrics']['Root Mean Squared Error']**2
            se_yh = np.sqrt(mse * j)
            se_pred = np.sqrt(mse + se_yh**2)
            n = predictorData.shape[0]
            p = len(xH)
            degF = n - p
            t_stat_10 = stats.t.ppf(1-0.05, degF)
            t_stat_30 = stats.t.ppf(1-0.15, degF)
            predInt10 = forecast - t_stat_10*np.sqrt(mse + se_yh**2)
            predInt30 = forecast - t_stat_30*np.sqrt(mse + se_yh**2)
            predInt70 = forecast + t_stat_30*np.sqrt(mse + se_yh**2)
            predInt90 = forecast + t_stat_10*np.sqrt(mse + se_yh**2)

            """ Append to the forecast dict entry"""
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear] = {}
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['Intervals'] = {
                "10%":float(np.round(predInt10,1)), 
                "30%":float(np.round(predInt30,1)), 
                "50%":float(np.round(forecast,1)), 
                "70%":float(np.round(predInt70,1)), 
                "90%":float(np.round(predInt90,1)) }   
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['CurrentData'] = currentData
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['StdErrPred'] = se_pred
            self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']]['Forecasts'][currentWaterYear]['degFreedom'] = degF

            """ Plot the resulting forecast and prediction interval """
            self.plotForecastSummaryTab(self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'][fcst['fcstID']])
            self.fcstSelectedToView(index)
            self.reDrawForecastDict()
            self.summaryTab.fcstTree.setExpanded(index, True)


            return
        

        return


    def plotForecastSummaryTab(self, fcst):
        """
        This function is used to create the plots for a selected forecast on the summary tab. It retrieves the 
        predictand data (the complete set of observed inflows) and it retrieves the cross-validated predictand
        data from the equation. 
        """

        """ Get the actual data """
        equation = fcst['Equation']
        commonIndex = fcst['Water Years']
        
        predictand = self.forecastDict['EquationPools'][equation]['Predictand']
        predictandName = predictand['Name']
        predictandUnits = predictand['Unit']
        predictandDataAll = pd.DataFrame().from_dict(predictand['Data'])

        predictandData = predictandDataAll.loc[commonIndex]

        residuals = [predictandData.values[i] - fcst['Predicted'][i] for i in range(len(commonIndex))]
        print('\n')
        [print(i[0]) for i in residuals]
        print('\n')
        self.summaryTab.plots.clear_plot()
        self.summaryTab.plots.add_to_plot1(fcst['Predicted'], np.array(predictandData), color='#0a85cc', marker='o', linestyle = '')
        self.summaryTab.plots.add_to_plot1(fcst['Predicted'], fcst['Predicted'], color='#203b72', marker=None, linestyle = '-')
        self.summaryTab.plots.add_to_plot2(list(commonIndex), fcst['Predicted'], color='#0a85cc', marker='o',linestyle='-',label='Predicted')
        self.summaryTab.plots.add_to_plot2(predictandDataAll.index, predictandDataAll, color='#203b72', marker='o',linestyle='-',label='Observed')
        self.summaryTab.plots.add_to_plot3(list(commonIndex), residuals)
        

        currentMonth = current_date().month
        if currentMonth >= 10:
            currentWaterYear = current_date().year + 1
        else:
            currentWaterYear = current_date().year

        year = pd.DatetimeIndex([pd.to_datetime(str(currentWaterYear) + '-01-01')], freq='AS-JAN')
        if currentWaterYear in fcst['Forecasts']:
            lowLeft = (fcst['Forecasts'][currentWaterYear]['Intervals']['10%'],fcst['Forecasts'][currentWaterYear]['Intervals']['10%'])
            width = fcst['Forecasts'][currentWaterYear]['Intervals']['90%'] - fcst['Forecasts'][currentWaterYear]['Intervals']['10%']
            self.summaryTab.plots.draw_box(lowLeft, width)
            self.summaryTab.plots.axes1.errorbar(fcst['Forecasts'][currentWaterYear]['Intervals']['50%'], fcst['Forecasts'][currentWaterYear]['Intervals']['50%'], xerr = fcst['Forecasts'][currentWaterYear]['Intervals']['50%'] - fcst['Forecasts'][currentWaterYear]['Intervals']['10%'], yerr = fcst['Forecasts'][currentWaterYear]['Intervals']['50%'] - fcst['Forecasts'][currentWaterYear]['Intervals']['10%'],  fmt='D', color='red', ecolor='red' )
            self.summaryTab.plots.axes2.errorbar(year, fcst['Forecasts'][currentWaterYear]['Intervals']['50%'], xerr=0, yerr=fcst['Forecasts'][currentWaterYear]['Intervals']['50%'] - fcst['Forecasts'][currentWaterYear]['Intervals']['10%'], color='red', fmt='D')
        self.summaryTab.plots.draw_plot()

        return


    def reDrawForecastDict(self):
        """
        This function draws the Forecast Dictionary Tree View on the summary page after its been updated
        """
        self.summaryTab.fcstTree.addToTree(self.forecastDict['EquationPools'], levels_in_max=8, exclude_keys=['PredictorPool','Predictand', 'PrdIDs', 'Water Years', 'PrincCompData'])
    
    def deleteForecast(self):
        """
        This function deletes the selected forecast from the forecast dictionary
        """
        """ Get the selected Forecast """
        index = self.summaryTab.fcstTree.selectedIndexes()[0]
        fcst = self.fcstSelectedToView(index, returnFcstOnly=True)

        """ Delete the selected Forecast"""
        self.forecastDict['EquationPools'][fcst['Equation']]['ForecastEquations'].pop(fcst['fcstID'])

        """ Redraw the dictionary"""
        self.reDrawForecastDict()

        return


    def fcstSelectedToView(self, index, returnFcstOnly=False):
        item = self.summaryTab.fcstTree.model.itemFromIndex(index)
        parent = item.parent()
        if parent == None:
            return None
        if parent.text() == 'ForecastEquations':
            fcstID = item.text()
            grandParent = parent.parent()
            equation = grandParent.text()
            fcst = self.forecastDict['EquationPools'][equation]['ForecastEquations'][fcstID]
            if returnFcstOnly:
                return fcst
        else:
            return None

        currentMonth = current_date().month
        if currentMonth >= 10:
            currentWaterYear = current_date().year + 1
        else:
            currentWaterYear = current_date().year
        
        """ Set the forecast information stuff """
        self.summaryTab.fcstInfoPane.forecastMeta_ForecastIDLine.setText(fcst['fcstID'])
        self.summaryTab.fcstInfoPane.forecastMeta_TargetLine.setText(self.forecastDict['EquationPools'][equation]['Predictand']['Name'])
        self.summaryTab.fcstInfoPane.forecastMeta_PeriodLine.setText(self.forecastDict['Options']['fcstPeriodStart'] + ' - ' + self.forecastDict['Options']['fcstPeriodEnd'])
        self.summaryTab.fcstInfoPane.forecastMeta_FrequencyLine.setText(self.forecastDict['Options']['fcstFreq'])
        self.summaryTab.fcstInfoPane.forecastMeta_ForecasterLine.setText(self.forecastDict['Options']['forecaster'])
        self.summaryTab.fcstInfoPane.forecastInfo_Heading1Line.setPlainText(self.forecastDict['Options']['fcstNotes'])
        
        self.summaryTab.fcstInfoPane.forecastInfoTable.setRowCount(0)
        self.summaryTab.fcstInfoPane.forecastCurrentData.setRowCount(0)
        print('coefs:', fcst['Coef'])
        for i, prd in enumerate(fcst['PrdIDs']):
            name = self.forecastDict['EquationPools'][equation]['PredictorPool'][prd]
            self.summaryTab.fcstInfoPane.forecastInfoTable.addRow([name, str(fcst['Coef'][i])])
            if currentWaterYear in fcst['Forecasts']:
                self.summaryTab.fcstInfoPane.forecastCurrentData.addRow([name, str(fcst['Forecasts'][currentWaterYear]['CurrentData'][i])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['Intercept', str(list(fcst['Intercept'])[0])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['',''])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['CV Adj. R2',str(fcst['Metrics']['Cross Validated Adjusted R2'])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['RMSPE',str(fcst['Metrics']['Root Mean Squared Prediction Error'])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['Cross Validated Nash-Sutcliffe',str(fcst['Metrics']['Cross Validated Nash-Sutcliffe'])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['',''])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['Adj. R2',str(fcst['Metrics']['Adjusted R2'])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['RMSE',str(fcst['Metrics']['Root Mean Squared Error'])])
        self.summaryTab.fcstInfoPane.forecastInfoTable.addRow(['Nash-Sutcliffe',str(fcst['Metrics']['Nash-Sutcliffe'])])

        
        if currentWaterYear in fcst['Forecasts']:
            self.summaryTab.fcstInfoPane.forecastInfo_10FcstLine.setText(str(fcst['Forecasts'][currentWaterYear]['Intervals']['10%']))
            self.summaryTab.fcstInfoPane.forecastInfo_30FcstLine.setText(str(fcst['Forecasts'][currentWaterYear]['Intervals']['30%']))
            self.summaryTab.fcstInfoPane.forecastInfo_50FcstLine.setText(str(fcst['Forecasts'][currentWaterYear]['Intervals']['50%']))
            self.summaryTab.fcstInfoPane.forecastInfo_70FcstLine.setText(str(fcst['Forecasts'][currentWaterYear]['Intervals']['70%']))
            self.summaryTab.fcstInfoPane.forecastInfo_90FcstLine.setText(str(fcst['Forecasts'][currentWaterYear]['Intervals']['90%']))
            
        
        self.plotForecastSummaryTab(fcst)




    """
    Purposely left blank






















    """

    """
    1.2 STATIONS TAB
    HERE WE CONNECT EVENTS AND BUTTONS LOCATED IN THE STATIONS TAB TO SPECIFIC FUNCTIONS AND ACTIONS.
    WE ALSO DEFINE THOSE FUNCTIONS. PRIMARILY, USERS WILL USE THIS TAB TO ADD AND DELETE DATASETS FROM
    THE DATASET DIRECTORY DICTIONARY
    """

    def connectEventsStationsTab(self):
        """
        Connects button press events from the GUI and the javascript web map to functions also described in this
        section. 
        """
        self.stationsTab.page.java_msg_signal.connect(self.addToStationsList) 
        self.stationsTab.stationInfoPane.nrccButton.clicked.connect(lambda: self.addToStationsList("nrcc"))
        self.stationsTab.stationInfoPane.prismButton.clicked.connect(lambda: self.addToStationsList("prism"))
        self.stationsTab.stationInfoPane.pdsiButton.clicked.connect(lambda: self.addToStationsList("pdsi"))
        self.stationsTab.stationInfoPane.ensoButton.clicked.connect(lambda: self.addToStationsList("clim"))
        self.stationsTab.stationInfoPane.webServiceButton.clicked.connect(self.loadCustomWebServiceDialog)
        self.stationsTab.stationInfoPane.stationTable.deletedRowEmission.connect(self.deleteStationFromDirectory)

        return

   
    @QtCore.pyqtSlot(list)
    def deleteStationFromDirectory(self, items):
        """
        Locates and deletes a dataset from the datasetDirectory dictionary. When the user right clicks an
        item on the station tab table and chooses delete, this function reads the item's text and identifies the
        PYID. It then locates the dataset in the dataset directory and deletes said dataset.
        """
        dataID = items[0]
        
        index = -1
        for i, station in enumerate(self.datasetDirectory['datasets']):
            if station['PYID'] == dataID:
                index = i
        
        self.datasetDirectory['datasets'].pop(index)

        return


    def loadCustomWebServiceDialog(self):
        """
        Instantiates the REST Service dialog window which allows users to add datasets using a custom dataloader. See the 'Functions.RestServiceV2.py' 
        script for more information about this dialog. Connects the 'returnStationDict' signal from that dialog to the 'addCustomWebService' function.
        This dialog begins the process of adding a custom web service dataset by creating a dictionary entry and sending it to the 'addCustomWebService' function
        via the 'returnStationDict' signal.
        """

        self.restDialog = RestServiceV2.RESTDialog1()
        self.restDialog.signals.returnStationDict.connect(self.addCustomWebService)

        return


    @QtCore.pyqtSlot(dict)
    def addCustomWebService(self, stationDict):
        """
        Completes the process of adding a custom web service dataset to the dataset directory by appending a pyID to the dictionary entry
        and adding the entry to the dataset directory. Additionally, this function adds the new dataset to the stations tab dataset table.
        """

        stationType = stationDict['TYPE']
        stationNumber = stationDict['ID']
        stationName = stationDict['Name']
        stationParam = stationDict['Parameter']

        dataID = encryptions.generateStationID(stationType, stationName, stationParam, stationDict['Decoding']['dataLoader'])

        stationDict['PYID'] = dataID
        
        self.datasetDirectory['datasets'].append(stationDict)
        self.stationsTab.stationInfoPane.stationTable.addRow([dataID, stationType, stationNumber, stationName, stationParam])

        return

    def appendDatasetDictionaryItem(self, dataID, stationType, stationNumber, stationName, stationParam, stationUnits, resamplingMethod, decodeOptions):
        """
        This function adds an entry to the datasetDictionary and adds it to the Station Tab table
        """
        duplicateDataset = False
        #Add validation code to see if dataset already exists in datasetDirectory

        for dCounter in range(0, len(self.datasetDirectory['datasets'])):
            if self.datasetDirectory['datasets'][dCounter]["TYPE"] == stationType and self.datasetDirectory['datasets'][dCounter]["ID"] == stationNumber and self.datasetDirectory['datasets'][dCounter]["Name"] == stationName and self.datasetDirectory['datasets'][dCounter]["Parameter"] == stationParam and self.datasetDirectory['datasets'][dCounter]["Units"] == stationUnits:
                duplicateDataset = True
                break
           
        if not duplicateDataset:
            self.datasetDirectory['datasets'].append({"PYID":dataID,"TYPE":stationType,"ID":stationNumber,"Name":stationName,"Parameter":stationParam,"Units":stationUnits,"Resampling":resamplingMethod,"Decoding":decodeOptions, "Data":{}, "lastDateTime":None})
            self.stationsTab.stationInfoPane.stationTable.addRow([dataID, stationType, stationNumber, stationName, stationParam])
        else:
            button = QtWidgets.QMessageBox.question(self, 'Error','Dataset has already been selected...'.format(traceback.format_exc()), QtWidgets.QMessageBox.Ok)
            if button == QtWidgets.QMessageBox.Ok:
                return

        return

    def addToStationsList(self, stationString = ""):
        """
        This function takes a 'stationString' (retrieved when a user clicks the 'Add Station' button on the web map,
        or when a users tries to add a station from the PRISM/NRCC/CLIMATE buttons), and generates
        a dataset directory dictionary entry, and then it adds that entry to the dataset directory.

        The input for this function is a 'stationString' that is generated originally in the javascript web map (see 'WebResources.WebMap.js').
        The stationString is of the form: "<instruction>|<stationName>|<stationNumber>|<stationType>|<parameter>|<specialArg>".

        Example:
        stationString: "stationSelect|GIBSON RESERVOIR; MONTANA|gibr|USBR|Inflow|IN|GP"
        This string will be passed to the 'USBR' section of this script where it will be parsed into the dictionary entry:
        [
            "PYID"      :   "BV3130LB",
            "TYPE"      :   "USBR",
            "ID"        :   "gibr",
            "Name"      :   "GIBSON RESERVOIR; MONTANA",
            "Parameter" :   "Inflow",
            "Units"     :   "CFS",
            "Resampling":   "Mean",
            "Decoding"  :   {"dataLoader" : "USBR"},
            "Data"      :   {},
            "lastDateTime": "timestamp(2011-10-02)"
        ]
        """
        instructionList = stationString.split('|')
        
        if instructionList[0] == 'StationSelect':
            stationType = instructionList[3]
            stationName = instructionList[1]
            stationNumber = instructionList[2]
            stationParam = instructionList[4]
            
            if stationType == 'USGS':                
                decodeOptions = {"dataLoader":"USGS_NWIS"}
                dataID = encryptions.generateStationID(stationType, stationName, stationParam, decodeOptions['dataLoader'])
                units = "CFS"
                resample = "Mean"
                #self.datasetDirectory['datasets'].append({"PYID":dataID,"TYPE":stationType,"ID":stationNumber,"Name":stationName,"Parameter":stationParam,"Units":"CFS","Resampling":"Mean", "Decoding":decodeOptions, "Data":{}, "lastDateTime":None})

            elif stationType == 'SNOTEL':
                decodeOptions = {"dataLoader":"NRCS_WCC"}
                dataID = encryptions.generateStationID(stationType, stationName, stationParam, decodeOptions['dataLoader'])
                if stationParam == 'SWE':
                    resample = 'Sample'
                    units = 'inches'
                elif stationParam == 'SOIL':
                    resample = 'Mean'
                    units = 'pct'
                else:
                    resample = 'Accumulation'
                    units = 'inches'
                #self.datasetDirectory['datasets'].append({"PYID":dataID,"TYPE":stationType,"ID":stationNumber,"Name":stationName,"Parameter":stationParam,"Units":units,"Resampling":resample,"Decoding":decodeOptions, "Data":{}, "lastDateTime":None})

            elif stationType == 'SNOWCOURSE':
                decodeOptions = {"dataLoader":"NRCS_WCC"}
                dataID = encryptions.generateStationID(stationType, stationName, stationParam, decodeOptions['dataLoader'])
                units = "inches"
                resample = "Sample"
                #self.datasetDirectory['datasets'].append({"PYID":dataID,"TYPE":stationType,"ID":stationNumber,"Name":stationName,"Parameter":stationParam,"Units":"inches","Resampling":"Sample","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})

            elif stationType == 'USBR':
                region = instructionList[5]
                pcode = instructionList[6]
                decodeOptions = {"dataLoader":"USBR", "Region":region,"PCODE":pcode}
                dataID = encryptions.generateStationID(stationType, stationName, stationParam, decodeOptions['dataLoader'])
                units = "CFS"
                resample = "Mean"
                #self.datasetDirectory['datasets'].append({"PYID":dataID,"TYPE":stationType,"ID":stationNumber,"Name":stationName,"Parameter":stationParam,"Units":"CFS","Resampling":"Mean","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})

            else:
                return
            
            self.appendDatasetDictionaryItem(dataID, stationType, stationNumber, stationName, stationParam, units, resample, decodeOptions)

        elif instructionList[0] == 'nrcc':

            stationNumber = self.stationsTab.stationInfoPane.nrccInput.text()

            # Check to ensure the HUC is valid
            if not isValidHUC(stationNumber):
                button = QtWidgets.QMessageBox.question(self, 'Error','HUC entered is not a valid 8-digit HUC'.format(traceback.format_exc()), QtWidgets.QMessageBox.Ok)
                if button == QtWidgets.QMessageBox.Ok:
                    return

            decodeOptions = {"dataLoader":"PRISM_NRCC_RCC_ACIS"}

            dataIDT = encryptions.generateStationID('NRCC', stationNumber, 'Temp', decodeOptions['dataLoader'])
            dataIDP = encryptions.generateStationID('NRCC', stationNumber, 'Precip', decodeOptions['dataLoader'])
            nameP = "{0} Precipitation".format(stationNumber)
            nameT = "{0} Temperature".format(stationNumber)

            self.datasetDirectory['datasets'].append({"PYID": dataIDT, "TYPE":'NRCC',"ID":stationNumber,"Name":nameT,"Parameter":"Temperature","Units":"degF","Resampling":"Mean","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})
            self.datasetDirectory['datasets'].append({"PYID": dataIDP, "TYPE":'NRCC',"ID":stationNumber,"Name":nameP,"Parameter":"Precipitation","Units":"inches","Resampling":"Accumulation","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})
            
            self.stationsTab.stationInfoPane.stationTable.addRow([dataIDT,'NRCC',stationNumber,nameT,'Temperature'])
            self.stationsTab.stationInfoPane.stationTable.addRow([dataIDP,'NRCC',stationNumber,nameP,'Precipitation'])
            self.stationsTab.stationInfoPane.nrccInput.clear()

        elif instructionList[0] == 'prism':

            stationNumber = self.stationsTab.stationInfoPane.prismInput.text()

            # Check to ensure the HUC is valid
            if not isValidHUC(stationNumber):
                button = QtWidgets.QMessageBox.question(self, 'Error','HUC entered is not a valid 8-digit HUC'.format(traceback.format_exc()), QtWidgets.QMessageBox.Ok)
                if button == QtWidgets.QMessageBox.Ok:
                    return

            decodeOptions = {"dataLoader":"PRISM_NRCC_RCC_ACIS"}

            dataIDT = encryptions.generateStationID('PRISM', stationNumber, 'Temp', decodeOptions['dataLoader'])
            dataIDP = encryptions.generateStationID('PRISM', stationNumber, 'Precip', decodeOptions['dataLoader'])
            nameP = "{0} Precipitation".format(stationNumber)
            nameT = "{0} Temperature".format(stationNumber)

            self.datasetDirectory['datasets'].append({"PYID": dataIDT, "TYPE":'PRISM',"ID":stationNumber,"Name":nameT,"Parameter":"Temperature","Units":"degF","Resampling":"Mean","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})
            self.datasetDirectory['datasets'].append({"PYID": dataIDP, "TYPE":'PRISM',"ID":stationNumber,"Name":nameP,"Parameter":"Precipitation","Units":"inches","Resampling":"Accumulation","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})
 
            self.stationsTab.stationInfoPane.stationTable.addRow([dataIDT, 'PRISM',stationNumber,nameT,'Temperature'])
            self.stationsTab.stationInfoPane.stationTable.addRow([dataIDP, 'PRISM',stationNumber,nameP,'Precipitation'])
            self.stationsTab.stationInfoPane.prismInput.clear()

        elif instructionList[0] == 'pdsi':

            decodeOptions = {"dataLoader":"PDSI_LOADER"}
            name = self.stationsTab.stationInfoPane.pdsiInput.currentText()
            stationDict = CLIMATE_DIVISIONS.divisions[name]
            stationNumber = str(stationDict["CLIMDIV"])
            
            dataID = encryptions.generateStationID("PDSI", stationNumber, 'Index', decodeOptions['dataLoader'])

            self.datasetDirectory['datasets'].append({"PYID":dataID, "TYPE":"PDSI", "ID":stationNumber, "Name": name+' PDSI', "Parameter":"PDSI","Units":"indices","Resampling":"Mean","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})

            self.stationsTab.stationInfoPane.stationTable.addRow([dataID, 'PDSI', stationNumber, name+' PDSI', 'PDSI'])

        elif instructionList[0] == 'clim':
            
            stationName = self.stationsTab.stationInfoPane.ensoInput.currentText()
            stationNumber = self.stationsTab.stationInfoPane.ensoInput.currentIndex() + 1

            decodeOptions = {'dataLoader':"CPC_CLIMATE"}

            dataID = encryptions.generateStationID("CLIMATE",stationName, "Indice", decodeOptions['dataLoader'])

            units = {
                1:"degC",
                2:"degC",
                3:"Unitless",
                4:"Unitless",
                #5:"ppm",
                5:"Unitless"}
            
            self.datasetDirectory['datasets'].append({"PYID":dataID, "TYPE":"CLIMATE","ID":str(stationNumber),"Name":stationName,"Parameter":"Indices","Units":units[stationNumber],"Resampling":"Mean","Decoding":decodeOptions, "Data":{}, "lastDateTime":None})

            self.stationsTab.stationInfoPane.stationTable.addRow([dataID, "CLIMATE",str(stationNumber),stationName,'Indices'])

        else:
            return

        return
    """
    Purposely left blank





















    """



    """
    1.3 DATA TAB
    HERE WE CONNECT EVENTS AND BUTTONS LOCATED IN THE DATA TAB TO SPECIFIC FUNCTIONS AND ACTIONS.
    WE ALSO DEFINE THOSE FUNCTIONS. PRIMARILY, USERS WILL USE THIS TAB TO DOWNLOAD AND EDIT DATASETS,
    REFERENCING THE DATASET DIRECTORY.
    """

    def connectEventsDataTab(self):
        """
        Connects button presses and events on the Data Tab to their respective functions.
        """

        self.dataTab.dataOptions.downloadButton.pressed.connect(lambda x = "False": self.downloadData(x))
        self.dataTab.dataOptions.updateButton.pressed.connect(lambda x = "True": self.downloadData(x))
        self.dataTab.dataOptions.importButton.pressed.connect(self.importData)
        self.dataTab.dataTable.horizontalHeader().sectionClicked.connect(self.plotColumn)
        self.dataTab.dataOptions.missingButton.pressed.connect(self.missingDataViz)
        self.dataTab.dataTable.deletedColumnEmission.connect(self.deleteDatasetFromDataTable)
        self.dataTab.dataTable.cellChanged.connect(self.userEditedData)

        return


    def userEditedData(self, row, col):
        """
        This function updates the dataset directory everytime a user edits data in the 
        data tab. Specifically, a signal is sent from the data table when a cell is changed.
        The signal reports the 'row' and 'col' (both integers) of the cell that was changed.
        The function first ensures that the newly enterd value is a valid floating point number,
        then it determines the dataset and the date corresponding to the cell that was changed.
        It indexes into the correct dataset in the dataset directory and updates the 'data' section
        with the correct new value.
        """

        newVal = self.dataTab.dataTable.item(row,col).text()

        try:
            newVal = np.float(newVal)
        except:
            QtWidgets.QMessageBox.question(self, 'Error','Invalid cell entry. Value will not be updated in the dataset.', QtWidgets.QMessageBox.Ok)
            return
        
        
        dateValue = self.dataTab.dataTable.item(row,0).text()
        colName = self.dataTab.dataTable.horizontalHeaderItem(col).text().split('\n')[0]
        index = -1
        for i, station in enumerate(self.datasetDirectory['datasets']):
            if colName in station['Name']:
                index = i
        print('The user edited entered value {0} for column {1}'.format(str(newVal), colName))
        
        pyid = self.datasetDirectory['datasets'][index]['PYID']

        print('the column name has PyId: {0}'.format(pyid))
        
        ts = pd.Timestamp(dateValue, freq='D')
        self.datasetDirectory['datasets'][index]['Data'][pyid][ts] = newVal

        return
        

    def plotColumn(self, colNum):
        """
        This function plots a column (or columns) of data when a user clicks on the column
        header of the data tab's datatable. Specifically: 
        
        When the user clicks on a header, the data table emits a signal with the column number that the user clicked. 
        The program makes sure that the user isn't trying to view the 'date' column, and then it iterates through 
        the selected columns and determines the names of the columns. 
        It uses the names of the columns to index into the dataset directory and find the datasets corresponding
        to the names. It then plots each selected dataset on the tie series plot.
        """

        if colNum == 0:
            return
     
        items = self.dataTab.dataTable.selectedItems()
        columns = list(set([self.dataTab.dataTable.indexFromItem(item).column() for item in items]))

        colors = ['#000000','#007a4d', '#de3831','#002395','#ff8a01', '#965994', '#52aafb','#c7a478']
        self.dataTab.plots.clear_plot()

        for column in columns:
            
            colHeader = self.dataTab.dataTable.horizontalHeaderItem(column).text().split('\n')
            col_name = colHeader[0]
            parameter = colHeader[1].split(':')[1].strip()

            index = -1
            for i, station in enumerate(self.datasetDirectory['datasets']):
                if station['Name'] == col_name and station['Parameter'] == parameter:
                    index = i
                    break

            data = pd.DataFrame().from_dict(self.datasetDirectory['datasets'][index]['Data'], orient='columns')
            if data[data.columns[0]].isnull().all():
                continue
            x = data.index
            y = data.values
            
            self.dataTab.plots.add_to_plot(x, y, label=col_name, color=colors[np.mod(column,8)])
        
        self.dataTab.plots.draw_plot()
        
        return


    def importData(self):
        """
        This function instantiates a dialog that allows users to import datasets from flat files (CSV/XLSX). For
        more information about that process, see the "Functions.importSpread.py" script. The 'importSpread' dialog
        will return a dictionary entry via a signal that is connected to the addImportToDatasets function
        """

        self.importDialog = importSpread.importDialog()
        self.importDialog.signals.returnDatasetSignal.connect(self.addImportToDatasets)

        return

    def addImportToDatasets(self, dict_):
        """
        This function takes the dictionary entry retrieved from the 'returnDatasetSignal' and generates
        a PYID. It then appends that PYID to the entry and adds the entry to the dataset directory
        and the stations table in the stations tab. Additionally, it updates the data tab's datatable 
        with the new data.
        """

        typ = dict_['TYPE']
        name = dict_['Name']
        param = dict_['Parameter']
        pyid = encryptions.generateStationID(typ, name, param, 'IMPORT')

        dict_['PYID'] = pyid

        self.datasetDirectory['datasets'].append(dict_)

        self.dataTab.dataTable.cellChanged.disconnect()
        self.dataTab.dataTable.TableFromDatasetDirectory(self.datasetDirectory['datasets'])
        self.dataTab.dataTable.cellChanged.connect(self.userEditedData)

        self.stationsTab.stationInfoPane.stationTable.addRow([pyid, typ, 'NA', name, param])

        return
    
    
    def missingDataViz(self):
        """
        This function instantiates a dialog window that displays the serial completeness of the datasets. See 
        'GUI.MissingNoGUI.py' for more information on this function.
        """

        data = self.dataTab.dataTable.toDataFrame()
        if data.empty:
            return
        dialog = MissingNoGUI.missingDialog(data)

        return

    def downloadData(self, update):
        """
        This function is called when the user selects the 'download' button. When this function begins,
        it starts by validating the inputs:
            - checks whether the user selected the 'fill NaN's' options
            - checks to make sure that there are stations in the datasetDir dictionary
            - Ensures that the POR is a real positive integer
        Next, it starts an alternate thread, initiating the download process. It passes a dictionary
        containing the options and the stations to the alternate thread, which in turn runs the 
        'Functions.DataDownloadV3' function. That function fills the 'data' key of the datasetDir 
        for each station. 
        """

        fill = str(self.dataTab.dataOptions.interpInputYes.isChecked())
        
        if self.datasetDirectory['datasets'] == []:
            self.dataTab.dataOptions.downloadButton.setEnabled(True)
            button = QtWidgets.QMessageBox.question(self, 'Error', 'No stations were selected...', QtWidgets.QMessageBox.Ok)
            if button == QtWidgets.QMessageBox.Ok:
                return
            return

        try:
            if self.dataTab.dataOptions.porYes.isChecked():
                por = int(self.dataTab.dataOptions.porInput.text())
            else:
                if int(self.dataTab.dataOptions.porT1.text()) <= 1901:
                    test = math.sqrt("a")
                por = int(self.dataTab.dataOptions.porT2.text()) - int(self.dataTab.dataOptions.porT1.text())
            test = math.sqrt(por) 
        except:
            if update == "True":
                pass
            else:
                button = QtWidgets.QMessageBox.question(self, 'Error', 'Invalid POR', QtWidgets.QMessageBox.Ok)
                return
        
        DICT = {
            "STATIONS": self.datasetDirectory,
            "POR": por,
            "UPDATE": update,
            "FILL": fill}

        self.dataTab.dataOptions.downloadButton.setDisabled(True)
        self.dataTab.dataOptions.updateButton.setDisabled(True)

        downloadWorker = DataDownloadV4.alternateThreadWorker(DICT)
        downloadWorker.signals.updateProgBar.connect(self.dataTab.dataOptions.progressBar.setValue)
        downloadWorker.signals.finished.connect(self.downloadCompleted)
        downloadWorker.signals.ReturnDataToDatasetDirectory.connect(self.updateDataInDatasetDirectory)
        self.threadPool.start(downloadWorker)

        return


    def downloadCompleted(self, true):
        """
        This function runs when the download is completed. It re-enables the download button,
        and populates the GUI datatable with the downloaded data.
        """
        time.sleep(1)
        self.dataTab.dataOptions.downloadButton.setEnabled(True)
        self.dataTab.dataOptions.updateButton.setEnabled(True)
        self.dataTab.dataTable.cellChanged.disconnect()
        self.dataTab.dataTable.TableFromDatasetDirectory(self.datasetDirectory['datasets'])
        self.dataTab.dataTable.cellChanged.connect(self.userEditedData)

        return



    def updateDataInDatasetDirectory(self, dataDict):
        """
        This function executes everytime the user changes the value of a datapoint in the
        GUI datatable. This function locates the value that was changed, and updates the 
        corresponding value in the datasetDir dicitonary entry. 
        """
        
        self.datasetDirectory['datasets'] = dataDict

        return



    def deleteDatasetFromDataTable(self, colName):
        """
        This function executes when the user elects to delete a column from the GUI datatable.
        It locates the dataset to delete, and removes the dataset from the stations table and
        the datasetDirectory dictionary.
        """

        # Find the dataset
        index = -1
        name, param, units = colName.split('\n')
        param = param.split(':')[1].strip(' ')
        print(name, param)
        for i, station in enumerate(self.datasetDirectory['datasets']):
            if station['Name'] == name and station['Parameter'] == param:
                index = i
                pyid = station['PYID']
        
        # Delete the station from the stations tab
        self.stationsTab.stationInfoPane.stationTable.deleteFromTable(option='customrow',rowID=index)

        # Delete the station from the dataset directory
        self.deleteStationFromDirectory([pyid])

        return


    """
    Purposely left blank






















    """

    """
    1.4 FORECAST OPTIONS TAB
    Here we connect the buttons and events from the froecast options tab to their respective 
    functions. We also define some functions here as well. USers will use this tab to process daily
    data into seasonal forecast predictors. 
    """
 
    def connectEventsForecastOptionsTab(self):
        """
        Connects events on the forecast options tab to their respective functions
        """
        self.tabWidget.currentChanged.connect(self.updateFcstOptionsTargetList)
        self.fcstOptionsTab.optionsPane.applyButton.clicked.connect(self.processData)
        self.fcstOptionsTab.optionsPane.updateButton.clicked.connect(self.updateFcstData)
        self.fcstOptionsTab.optionsPane.precipInputYes.clicked.connect(self.fcstOptionsTab.optionsPane.accumStart.setEnabled)
        self.fcstOptionsTab.optionsPane.precipInputNo.clicked.connect(self.fcstOptionsTab.optionsPane.accumStart.setDisabled)
        self.fcstOptionsTab.plotsPane.clearButton.pressed.connect(self.clear_fcstOptions_plots)
        self.fcstOptionsTab.plotsPane.corrButton.pressed.connect(self.fcstOptionsCorrPlot)
        self.fcstOptionsTab.plotsPane.prdIDSignal.connect(self.addTofcstOptionsPlot)
        self.fcstOptionsTab.dualTreeView.tree2.droppedPredictor.connect(self.addPredictorToEquation)
        self.fcstOptionsTab.dualTreeView.tree2.deletedItem.connect(self.deletePredictor)
        self.fcstOptionsTab.dualTreeView.tree2.forcedItem.connect(self.forcePredictor)
        self.fcstOptionsTab.dualTreeView.tree1.openExcelAction.triggered.connect(self.exportDataFromForecastOptionsTab)

        return


    def exportDataFromForecastOptionsTab(self):
        """ 
        Function to export the seasonal predictors from the 'forecastDict' to an excel spreadsheet. This
        function reads the forecast dict, and creates one worksheet per predictor on an excel spreadsheet.
        Each sheet is composed of one column per predictor interval.
        """
        
        """ Open an excel spreadsheet """
        filename = "Resources/tempFiles/Output{0}.xlsx".format(int(1000*np.random.random(1)))
        writer = pd.ExcelWriter(filename)

        """ Define a function to save a predictors data to a worksheet """
        def writeToExcelSheet(predictor):
            dataframe = pd.DataFrame()
            for interval in list(self.forecastDict['PredictorPool'][predictor]):
                dataframe = pd.concat([dataframe, pd.DataFrame().from_dict(self.forecastDict['PredictorPool'][predictor][interval]['Data'], orient='columns')], axis=1)
            dataframe.columns = list(self.forecastDict['PredictorPool'][predictor])
            dataframe.to_excel(writer, str(predictor))
        
        """ Save each predictor to a worksheet """
        [writeToExcelSheet(predictor) for predictor in list(self.forecastDict['PredictorPool'])]

        """ Save and open the workbook """
        writer.save()

        try:
            try:
                subprocess.check_call(['cmd','/c','start',filename])
            except Exception as e:
                print(e)
                subprocess.check_call(['open',filename])
        except:
            pass

        return

    
    @QtCore.pyqtSlot(list)
    def deletePredictor(self, list_):
        """
        Function to delete a predictor from the PredictorPool section of a forecast equation. The function pops
        the prdID from the specified equation and re-draws the forecast dictionary.
        
        input: list_ = [prdID, equation]

        """
        prdID = list_[0]
        equation = list_[1]
        self.forecastDict['EquationPools'][equation]['PredictorPool'].pop(prdID)
        self.displayForecastDict(self.forecastDict, onlyEquations=True)
        
        return

    @QtCore.pyqtSlot(list)
    def forcePredictor(self, list_):
        """
        Function to add a selected predictor (prdID) to a selected equation. This function is called when a predictor
        is dragged into an equaton. The program reads the prdID, and the drop-location equation and appends the prdID into 
        the forecast equation predictors.
        
        input: list_ = [prdID, equation]
        
        """
        prdID = list_[0]
        equation = list_[1]
        #for predictor in self.forecastDict['PredictorPool']:
        #    for interval in self.forecastDict['PredictorPool'][predictor]:
        #        if self.forecastDict['PredictorPool'][predictor][interval]['prdID'] == prdID:
        if prdID in self.forecastDict['EquationPools'][equation]['ForcedPredictors']:
            self.forecastDict['EquationPools'][equation]['ForcedPredictors'].remove(prdID)
        else:
            self.forecastDict['EquationPools'][equation]['ForcedPredictors'].append(prdID)
        self.displayForecastDict(self.forecastDict, onlyEquations = True)
        item = self.fcstOptionsTab.dualTreeView.tree2.model.findItems(equation)[0]
        predictorPoolChild = item.child(0,0)
        index = self.fcstOptionsTab.dualTreeView.tree2.model.indexFromItem(predictorPoolChild)
        index2 = self.fcstOptionsTab.dualTreeView.tree2.model.indexFromItem(item)
        self.fcstOptionsTab.dualTreeView.tree2.setExpanded(index2, True)
        self.fcstOptionsTab.dualTreeView.tree2.setExpanded(index, True)

        return


    @QtCore.pyqtSlot(list)
    def addPredictorToEquation(self, list_):
        """
        Function to add a selected predictor (prdID) to a selected equation. This function is called when a predictor
        is dragged into an equaton. The program reads the prdID, and the drop-location equation and appends the prdID into 
        the forecast equation predictors.
        """
        prdID = list_[0]
        equation = list_[1]
        for predictor in self.forecastDict['PredictorPool']:
            for interval in self.forecastDict['PredictorPool'][predictor]:
                if self.forecastDict['PredictorPool'][predictor][interval]['prdID'] == prdID:
                    self.forecastDict['EquationPools'][equation]['PredictorPool'][prdID] = predictor + ': ' + interval
        self.displayForecastDict(self.forecastDict, onlyEquations = True)
        item = self.fcstOptionsTab.dualTreeView.tree2.model.findItems(equation)[0]
        predictorPoolChild = item.child(0,0)
        index = self.fcstOptionsTab.dualTreeView.tree2.model.indexFromItem(predictorPoolChild)
        index2 = self.fcstOptionsTab.dualTreeView.tree2.model.indexFromItem(item) 
        self.fcstOptionsTab.dualTreeView.tree2.setExpanded(index2, True)
        self.fcstOptionsTab.dualTreeView.tree2.setExpanded(index, True)

        return


    def updateFcstData(self):
        """
        This function updates the seasonal forecast predictors in the predictor pool with any new data obtained by updating data in the data tab. 
        The function (similar to the processData function) opens an alternate thread that runs the ProcessDataV2 script (Resources/Functions/ProcessDataV2.py).
        """

        if self.forecastDict['Options'] == {}:
            button = QtWidgets.QMessageBox.question(self, 'Error','No predictors to update. Apply options first.', QtWidgets.QMessageBox.Ok)
            return

        d = {"OPTIONS":self.forecastDict['Options'],
            "DATA":self.datasetDirectory['datasets'],
            "UPDATE":True}

        self.fcstOptionsTab.optionsPane.updateButton.setEnabled(False)
        self.fcstOptionsTab.optionsPane.applyButton.setEnabled(False)
        processWorker = ProcessDataV2.alternateThreadWorker(d)
        processWorker.signals.returnPredictorDict.connect(self.updatePredictors)
        self.threadPool.start(processWorker)

        return


    def updatePredictors(self, dict_):
        """
        This funciton is called when the alternate thread returns a new predictorPool. The program copies the updated predictorPool 
        into the forecastDict and re-draws the dictionaries.
        """

        self.forecastDict['PredictorPool'] = dict_[0]
        equationPools = dict_[1]
        for equation in equationPools:
            self.forecastDict['EquationPools'][equation]['Predictand']['Data'] = equationPools[equation]['Predictand']['Data']
        self.fcstOptionsTab.optionsPane.updateButton.setEnabled(True)
        self.fcstOptionsTab.optionsPane.applyButton.setEnabled(True)
        self.displayForecastDict(self.forecastDict)

        return


    # Function to convert daily data into forecast predictors
    def processData(self):
        """
        This function creates seasonal forecast predictors as well as a data structure to store forecast equation information. The program reads the user's selected options and sends them along with the 
        daily data to an alternate thread where the program runs the 'ProcessDataV2.py' script. 
        """
        
        # Print a warning to the screen
        button = QtWidgets.QMessageBox.question(self, 'Warning','Continuing with this option will delete all exising forecasts. Continue?', QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if button != QtWidgets.QMessageBox.Ok:
            return

        # Package the options as a dict
        optionsDict = {
            "fcstPeriodStart" : self.fcstOptionsTab.optionsPane.periodStartInput.currentText(),
            "fcstPeriodEnd" : self.fcstOptionsTab.optionsPane.periodEndInput.currentText(),
            "fcstFreq" : self.fcstOptionsTab.optionsPane.freqInput.currentText(),
            "fcstStart": self.fcstOptionsTab.optionsPane.eqStartInput.currentText(),
            "wateryearStart" : self.fcstOptionsTab.optionsPane.wateryearStartInput.currentText(),
            "fcstTarget" : self.fcstOptionsTab.optionsPane.targetInput.currentText(),
            "forecaster" : self.fcstOptionsTab.optionsPane.forecasterInput.text(),
            "fcstNotes" : self.fcstOptionsTab.optionsPane.forecastNotes.toPlainText(),
            "accumSelect" : self.fcstOptionsTab.optionsPane.precipInputYes.isChecked(),
            "accumStart" : self.fcstOptionsTab.optionsPane.accumStart.currentText()
        }

        # Store all the stuff in a dict
        d = {"OPTIONS":optionsDict,
            "DATA":self.datasetDirectory['datasets'],
            "UPDATE":False}

        # Pass the arguments to the process data thread worker.
        self.fcstOptionsTab.optionsPane.applyButton.setEnabled(False)
        self.fcstOptionsTab.optionsPane.updateButton.setEnabled(False)
        processWorker = ProcessDataV2.alternateThreadWorker(d)
        processWorker.signals.returnForecastDict.connect(self.finishedProcessing)
        self.threadPool.start(processWorker)

        return
        
    
    def finishedProcessing(self, dict_):
        """ After the predictors have been processed, this function populates the other tabs' drop downs and """
        self.populateDensityEquations(5)
        self.displayForecastDict(dict_)
        self.populateEquationsDropDown(4)

        return


    def clear_fcstOptions_plots(self):
        """
        This function clears the data from the plots on the Forecast options pane and re-draws the empty plots. 
        """
        self.fcstOptionsTab.plotsPane.tsPlot.clear_plot()
        self.fcstOptionsTab.plotsPane.corrPlot.clear_plot()
        self.fcstOptionsTab.plotsPane.tsPlot.draw_plot()
        self.fcstOptionsTab.plotsPane.corrPlot.draw_plot()

        return


    def fcstOptionsCorrPlot(self):
        """
        This function retieves the time-series data from the time-series plots on 
        the Forecast options tab (using matplotlibs internal data functions) and 
        uses the data values to draw a correlation plot.
        """

        # Check that there are only 2 lines selected
        lines = list(self.fcstOptionsTab.plotsPane.tsPlot.axes.get_lines())
        if len(lines) != 2:
            return

        # Get the labels
        labelLine1 = lines[0].get_label()
        labelLine2 = lines[1].get_label()
        
        # Get the xdata and ydata for line1
        xdataLine1 = list(lines[0].get_xdata())
        ydataLine1 = list(lines[0].get_ydata())

        # Get the xdata and ydata for line2
        xdataLine2 = list(lines[1].get_xdata())
        ydataLine2 = list(lines[1].get_ydata())

        # Get the common xdata
        commonX = list(set(xdataLine1).intersection(xdataLine2))
        indicesLine1 = [xdataLine1.index(i) for i in commonX]
        newY1 = [ydataLine1[i] for i in indicesLine1]
        indicesLine2 = [xdataLine2.index(i) for i in commonX]
        newY2 = [ydataLine2[i] for i in indicesLine2]
        
        # Plot the regression
        try:
            self.fcstOptionsTab.plotsPane.corrPlot.draw_corr_plot(newY1, newY2, labelLine1, labelLine2)
        except:
            print('could not draw corr plot')
        return


    def displayForecastDict(self, dict_, onlyEquations=False):
        """
        This function is triggered at the completion of the processData function. It sets the global
        self.fcstDict dictionary to the results of the processData function and displays the predictorPool
        and EquationPool from that dict (see the Documentation/PyForecastDictionaryStructure document) in the
        tree views on the screen.
        """

        self.forecastDict = dict_
        if onlyEquations:
            self.fcstOptionsTab.dualTreeView.tree2.addToTree(self.forecastDict['EquationPools'], levels_in_max=10, exclude_keys=['ForecastEquations','ForcedPredictors'])
        else:
            self.fcstOptionsTab.dualTreeView.tree2.addToTree(self.forecastDict['EquationPools'], levels_in_max=10, exclude_keys=['ForecastEquations','ForcedPredictors'])
            self.fcstOptionsTab.dualTreeView.tree1.addToTree(self.forecastDict['PredictorPool'], levels_in_max=10)
        self.fcstOptionsTab.optionsPane.applyButton.setEnabled(True)
        self.fcstOptionsTab.optionsPane.updateButton.setEnabled(True)

        return


    def addTofcstOptionsPlot(self, prdID):
        """
        This function is responsible for plotting predictors in the ploting window on the forecastOptions tab. It begins by clearing the 
        plots. When a user drags a predictor from the predictordict, this function is called with the argument of the prdID (e.g. 00321).
        When a user drags a predictand to the plot, the function is called with an argument of (e.g. Name: Inflow Apr-Jul). It then parses the
        argument and searched the forecastDict for the specified dataset, which it then plots in the plotting window.
        """

        try:
            self.lastInt = self.lastInt + 1
        except:
            self.lastInt = 1
            self.fcstOptionsTab.plotsPane.tsPlot.clear_plot()
            self.fcstOptionsTab.plotsPane.corrPlot.clear_plot()

        if "Name:" in prdID:
            col_name = prdID.split(":")[1].strip(' ')
            for equation in self.forecastDict['EquationPools']:
                if self.forecastDict['EquationPools'][equation]['Predictand']['Name'] == col_name:
                    data = pd.DataFrame().from_dict(self.forecastDict['EquationPools'][equation]['Predictand']['Data'], orient='columns')
                    break
        else:

            try:
                prdID = int(prdID)
            except:
                return
            
            data = pd.DataFrame()
            col_name = ''

            

            # Find the correct dataset
            for predictor in self.forecastDict['PredictorPool']:

                for interval in self.forecastDict['PredictorPool'][predictor]:

                    if int(self.forecastDict['PredictorPool'][predictor][interval]['prdID']) == prdID:
                        data = data.from_dict(self.forecastDict['PredictorPool'][predictor][interval]['Data'], orient='columns')
                        col_name = predictor + ' ' + interval
                        break

        # Use a color list to plot multiple columns in different colors
        colors = ['#000000','#007a4d', '#de3831','#002395','#ff8a01', '#965994', '#52aafb','#c7a478']

        # Plot the data
        x = data.index.to_pydatetime()
        y = data.values

        self.fcstOptionsTab.plotsPane.tsPlot.add_to_plot(x, y, label=col_name, color=colors[np.mod(self.lastInt,8)])
        self.fcstOptionsTab.plotsPane.tsPlot.draw_plot()

        return


    def updateFcstOptionsTargetList(self, tabNo):
        """
        This function updates the 'target' selection box in the forecast options specification window. It is called
        whenever the user switches to tab 3 (the forecastOptions tab). It searches the datasetDirectory for datasets
        with 'INFLOW, STREAMFLOW, FLOW' in the dataset name. 
        """

        if tabNo == 3:
            
            # Clear the current target list
            self.fcstOptionsTab.optionsPane.targetInput.clear()

            # Get all the stramflow stations
            for station in self.datasetDirectory['datasets']:
              
                if 'INFLOW' in station['Parameter'].upper() or 'STREAMFLOW' in station['Parameter'].upper() or 'FLOW' in station['Parameter'].upper():
                    self.fcstOptionsTab.optionsPane.targetInput.addItem(station['Name'])
        
        return


    """
    Purposely left blank






















    """

    #/////////////////////////// REGRESSION TAB ///////////////////////////////////////// 
    #// Here we connect the buttons and events from the regression tab to their respective 
    #// functions. We also define some functions here as well. 

    def populateEquationsDropDown(self, tabNo):
        """
        This function is called everytime the user switches tabs in the application.
        If the user switches to the RegressionTab (tab no. 4) then this function will
        fill the equation selection drop down box with the months and dates from the
        forecast dictionary.
        """

        if tabNo == 4:

            self.regressionTab.regrSelectPane.mlrTab.eqSelect.clear()
            self.regressionTab.regrSelectPane.pcarTab.eqSelect.clear()
            self.regressionTab.regrSelectPane.zscrTab.eqSelect.clear()
            self.regressionTab.regrSelectPane.annTab.eqSelect.clear()

            for key in self.forecastDict['EquationPools'].keys():
                self.regressionTab.regrSelectPane.mlrTab.eqSelect.addItem(str(key))
                self.regressionTab.regrSelectPane.zscrTab.eqSelect.addItem(str(key))
                self.regressionTab.regrSelectPane.pcarTab.eqSelect.addItem(str(key))
                self.regressionTab.regrSelectPane.annTab.eqSelect.addItem(str(key))
        
        return


    def connectEventsRegressionTab(self):
        """
        This function assigns all the functionality to the buttons and events on the forecast tab.
        """

        self.regressionTab.regrSelectPane.mlrTab.regrButton.pressed.connect(self.runFeatureSelection)
        self.regressionTab.regrSelectPane.pcarTab.regrButton.pressed.connect(self.runFeatureSelection)
        self.regressionTab.regrSelectPane.zscrTab.regrButton.pressed.connect(self.runFeatureSelection)
        self.regressionTab.regrSelectPane.annTab.regrButton.pressed.connect(self.runFeatureSelection)
        self.regressionTab.toggleButton.pressed.connect(self.plotFcstEntryRegressionTab)
        self.regressionTab.regrSelectPane.mlrTab.bestModelTable.saveFcstAction.triggered.connect(self.saveFcst)
        self.regressionTab.regrSelectPane.pcarTab.bestModelTable.saveFcstAction.triggered.connect(self.saveFcst)
        self.regressionTab.regrSelectPane.zscrTab.bestModelTable.saveFcstAction.triggered.connect(self.saveFcst)
        self.regressionTab.regrSelectPane.mlrTab.bestModelTable.regStatAction.triggered.connect(self.showRegStats)
        self.regressionTab.regrSelectPane.pcarTab.bestModelTable.regStatAction.triggered.connect(self.showRegStats)
        self.regressionTab.regrSelectPane.zscrTab.bestModelTable.regStatAction.triggered.connect(self.showRegStats)

        return


    def runFeatureSelection(self):
        """
        This function is the application's starting point for running feature selection
        on a chosen dataset / algorithm combination. The program first determines
        which regression scheme the user wants to run by checking the current tab.
        Then, it constructs a dictionary to send the predictor/predictand data along 
        with the feature selection options to the 'FeatureSelectionVx' Script in the 
        Functions folder.
        """

        if self.regressionTab.regrSelectPane.tabWidget.currentIndex() == 0:
            regrScheme = 'MLR'
            self.regrButton = self.regressionTab.regrSelectPane.mlrTab.regrButton
            numModels = int(self.regressionTab.regrSelectPane.mlrTab.numModelsInput.text())
            crossVal = self.regressionTab.regrSelectPane.mlrTab.crossValInput.currentText()
            self.perfMetric = self.regressionTab.regrSelectPane.mlrTab.scoreInput.currentText()
            self.equation = self.regressionTab.regrSelectPane.mlrTab.eqSelect.currentText()
            self.progBar = self.regressionTab.regrSelectPane.mlrTab.regrProgress
            label = self.regressionTab.regrSelectPane.mlrTab.regModLabel
            self.table = self.regressionTab.regrSelectPane.mlrTab.bestModelTable
            selScheme = self.regressionTab.regrSelectPane.mlrTab.featSelInput.currentText()
            dist = self.regressionTab.regrSelectPane.mlrTab.distInput.currentText()

        elif self.regressionTab.regrSelectPane.tabWidget.currentIndex() == 1:
            regrScheme = 'PCAR'
            self.regrButton = self.regressionTab.regrSelectPane.pcarTab.regrButton
            numModels = int(self.regressionTab.regrSelectPane.pcarTab.numModelsInput.text())
            crossVal = self.regressionTab.regrSelectPane.pcarTab.crossValInput.currentText()
            self.perfMetric = self.regressionTab.regrSelectPane.pcarTab.scoreInput.currentText()
            self.equation = self.regressionTab.regrSelectPane.pcarTab.eqSelect.currentText()
            self.progBar = self.regressionTab.regrSelectPane.pcarTab.regrProgress
            label = self.regressionTab.regrSelectPane.pcarTab.regModLabel
            self.table = self.regressionTab.regrSelectPane.pcarTab.bestModelTable
            selScheme = self.regressionTab.regrSelectPane.pcarTab.featSelInput.currentText()
            dist = self.regressionTab.regrSelectPane.pcarTab.distInput.currentText()
        
        elif self.regressionTab.regrSelectPane.tabWidget.currentIndex() == 2:
            regrScheme = 'ZSCR'
            self.regrButton = self.regressionTab.regrSelectPane.zscrTab.regrButton
            numModels = int(self.regressionTab.regrSelectPane.zscrTab.numModelsInput.text())
            crossVal = self.regressionTab.regrSelectPane.zscrTab.crossValInput.currentText()
            self.perfMetric = self.regressionTab.regrSelectPane.zscrTab.scoreInput.currentText()
            self.equation = self.regressionTab.regrSelectPane.zscrTab.eqSelect.currentText()
            self.progBar = self.regressionTab.regrSelectPane.zscrTab.regrProgress
            label = self.regressionTab.regrSelectPane.zscrTab.regModLabel
            self.table = self.regressionTab.regrSelectPane.zscrTab.bestModelTable
            selScheme = self.regressionTab.regrSelectPane.zscrTab.featSelInput.currentText()
            dist = self.regressionTab.regrSelectPane.zscrTab.distInput.currentText()
        
        elif self.regressionTab.regrSelectPane.tabWidget.currentIndex() == 3:
            regrScheme = 'ANN'
            self.regrButton = self.regressionTab.regrSelectPane.annTab.regrButton
            numModels = int(self.regressionTab.regrSelectPane.annTab.numModelsInput.text())
            crossVal = self.regressionTab.regrSelectPane.annTab.crossValInput.currentText()
            self.perfMetric = self.regressionTab.regrSelectPane.annTab.scoreInput.currentText()
            self.equation = self.regressionTab.regrSelectPane.annTab.eqSelect.currentText()
            self.progBar = self.regressionTab.regrSelectPane.annTab.regrProgress
            label = self.regressionTab.regrSelectPane.annTab.regModLabel
            self.table = self.regressionTab.regrSelectPane.annTab.bestModelTable
            selScheme = self.regressionTab.regrSelectPane.annTab.featSelInput.currentText()

        else:
            return

        d = {
            "RegressionScheme" : regrScheme,
            "CrossValidation" : crossVal,
            "PerformanceMetric" : self.perfMetric,
            "SelectionScheme" : selScheme,
            "NumModels" : numModels,
            "Distribution" : dist,
            "EquationDict" : self.forecastDict['EquationPools'][self.equation],
            "PredictorDict" : self.forecastDict['PredictorPool']
        }

        """ Backwards selection is not supported yet """
        #if selScheme == "Sequential Floating Backwards Selection":
        #    button = QtWidgets.QMessageBox.question(self, 'Error','Backwards selection not yet supported', QtWidgets.QMessageBox.Ok)
        #    return

        self.regrButton.setEnabled(False)
        self.progBar.setValue(0)
        regressionWorker = FeatureSelectionV3.alternateThreadWorker(d)
        regressionWorker.signals.updateProgBar.connect(self.progBar.setValue)
        regressionWorker.signals.returnFcstDict.connect(self.finishedRegression)
        regressionWorker.signals.updateRunLabel.connect(label.setText)
        self.table.cellClicked.connect(self.fcstClicked)
        self.threadPool.start(regressionWorker)

        return


    def finishedRegression(self, fcstDictList):
        """
        This function is run automatically when the feature selection algorithm above completes. The algorithm returns a 
        list of forecast equations which are stored in 'fcstDictList'). Those forecasts are then sorted according to the 
        chosen performance metric and displayed in the table. Additionally, this script checks each forecast equation
        in the list to see if the user has previously saved that equation to the global fcstDictionary. If they have,
        then that option in the table is appended with a check mark.
        """

        self.progBar.setValue(100)
        self.regrButton.setEnabled(True)
        self.table.setRowCount(0)

        if self.perfMetric == 'Root Mean Squared Prediction Error':
            fcstDictList = sorted(fcstDictList, key=lambda i: i['Metrics'][self.perfMetric])
        else:
            fcstDictList = sorted(fcstDictList, key=lambda i: i['Metrics'][self.perfMetric], reverse=True)
        
        currentFcsts = [self.forecastDict['EquationPools'][self.equation]['ForecastEquations'][f]['PrdIDs'] for f in list(self.forecastDict['EquationPools'][self.equation]['ForecastEquations'])]
        
        for fcst in fcstDictList:
            if fcst['prdIDs'] in currentFcsts:
                curIndex = currentFcsts.index(fcst['prdIDs'])
                curFcst = list(self.forecastDict['EquationPools'][self.equation]['ForecastEquations'])[curIndex]
                if fcst['Type'] == self.forecastDict['EquationPools'][self.equation]['ForecastEquations'][curFcst]['Type']:
                    prdIDs = u"\u2705" + ', '.join(fcst['prdIDs'])
                else:
                    prdIDs = ', '.join(fcst['prdIDs'])
            else:    
                prdIDs = ', '.join(fcst['prdIDs'])
            
            r2 = str(np.round(fcst['Metrics']['Cross Validated Adjusted R2'],2))
            rmse = str(np.round(fcst['Metrics']['Root Mean Squared Prediction Error'],1))
            nse = str(np.round(fcst['Metrics']['Cross Validated Nash-Sutcliffe'],2))
            self.table.addRow([prdIDs, r2, rmse, nse])
        
        currentRegScheme = self.regressionTab.regrSelectPane.tabWidget.currentIndex()

        if currentRegScheme == 0:
            self.mlrFcstList = fcstDictList
        elif currentRegScheme == 1:
            self.pcarFcstList = fcstDictList
        elif currentRegScheme == 2:
            self.zscrFcstList = fcstDictList
        else:
            self.annFcstList = fcstDictList

        return

    
    def plotFcstEntryRegressionTab(self, fcstDict = None, toggle_cv = 0):
        """
        This function is called at the end of the fcstClicked function below. After a user clicks a forecast, this function 
        will take the data in the fcstDictionary entry and plot the forecasted values against the observed values.
        Note that the program will only plot the INTERSECTION of the two sets of values (i.e. the 'commonIndex')
        """

        if fcstDict == None:
            if hasattr(self, 'lastFcstDict'):
                fcstDict = self.lastFcstDict
            else:
                return

        if toggle_cv == 999:
            toggle_cv = 0
        else:
            toggle_cv = self.regressionTab.toggleButton.toggleStatus

        self.lastFcstDict = fcstDict

        """ Get the data """  
        prdIDs = fcstDict['PrdIDs']
        predictorData = pd.DataFrame()
        predictorNames = {}

        for predictorName in self.forecastDict['PredictorPool']:
            for interval in self.forecastDict['PredictorPool'][predictorName]:
                if self.forecastDict['PredictorPool'][predictorName][interval]['prdID'] in prdIDs:
                    predictorNames[self.forecastDict['PredictorPool'][predictorName][interval]['prdID']] = str(predictorName)+ ', ' + str(interval)
                    predictorData = pd.concat([predictorData, pd.DataFrame().from_dict(self.forecastDict['PredictorPool'][predictorName][interval]['Data'], orient='columns')], axis=1)

        predictorData = predictorData.dropna()

        commonIndex = fcstDict['Water Years']

        equation = fcstDict['Equation']
        
        predictand = self.forecastDict['EquationPools'][equation]['Predictand']
        predictandName = predictand['Name']
        predictandUnits = predictand['Unit']
        predictandData = pd.DataFrame().from_dict(predictand['Data'])
        if fcstDict['Distribution'] == 'Lognormal':
            predictandData = np.log(predictandData)
            predictandName = "[LOG] " + predictandName

        predictandData = predictandData.loc[commonIndex]
        predictorData = predictorData.loc[commonIndex]

        """ Construct Equation Text """
        equationText = "{0} = ".format(predictandName + ', ' + predictandUnits)
        for i, prd in enumerate(fcstDict['PrdIDs']):
            try:
                equationText = equationText + u"\n{0} \u00D7 {1} +".format(round(fcstDict['Coef'][i],4), predictorNames[prd])
            except:
                equationText = equationText + u"\n{0} \u00D7 {1} +".format(round(fcstDict['Coef'][i][0],4), predictorNames[prd])
        equationText = equationText + "\n" + str(round(fcstDict['Intercept'][0], 4))
        equationText = equationText + "\n\n"
        equationText = equationText + "{0:<36}{1:<36}\n".format("Metric","Value")
        equationText = equationText + 70*"-" + "\n"
        for metr in fcstDict['Metrics'].keys():
            equationText = equationText + "{0:<36}{1:<36}\n".format(metr,round(fcstDict['Metrics'][metr], 4))
        self.regressionTab.equationBox.setPlainText(equationText)

        """ Compute Residuals """
        if toggle_cv == 1:
            residuals = [predictandData.values[i] - fcstDict['CV_Predicted'][i] for i in range(len(commonIndex))]
        if toggle_cv == 2:
            residuals = [predictandData.values[i] - fcstDict['CV_Predicted'][i] for i in range(len(commonIndex))]
            residuals2 = [predictandData.values[i] - fcstDict['Predicted'][i] for i in range(len(commonIndex))]
            
        else:
            residuals = [predictandData.values[i] - fcstDict['Predicted'][i] for i in range(len(commonIndex))]


        """ Plot Everything"""

        if toggle_cv == 1:
            yStar = fcstDict['CV_Predicted']
            label = 'CV Predictions'
            color = '#67ba37'

        elif toggle_cv == 2:
            yStar = fcstDict['CV_Predicted']
            yStar2 = fcstDict['Predicted']
            label = 'CV Predictions'
            label2 = 'Predictions'
            color = '#67ba37'
            color2 = '#0a85cc'

        else:
            yStar = fcstDict['Predicted']
            label = 'Predicted'
            color = '#0a85cc'

        self.regressionTab.plots.clear_plot()
        if toggle_cv == 2:
            self.regressionTab.plots.add_to_plot1(yStar2, np.array(predictandData), color = color2,marker='o',linestyle='')
            self.regressionTab.plots.add_to_plot2(list(commonIndex), yStar2, color=color2, marker='o',linestyle='-',label=label2)
            self.regressionTab.plots.add_to_plot3(list(commonIndex), residuals2, color=color2)
        self.regressionTab.plots.add_to_plot1(yStar, np.array(predictandData), color = color,marker='o',linestyle='')
        self.regressionTab.plots.add_to_plot1(yStar,yStar,color='#203b72', marker=None, linestyle='-')
        self.regressionTab.plots.add_to_plot2(list(commonIndex), yStar, color=color, marker='o',linestyle='-',label=label)
        self.regressionTab.plots.add_to_plot2(list(commonIndex), np.array(predictandData), color='#203b72', marker='o',linestyle='-',label='Observed')
        self.regressionTab.plots.add_to_plot3(list(commonIndex), residuals, color = color)

        self.regressionTab.plots.draw_plot()


    def fcstClicked(self, rowNum, colNum):
        """
        Function that runs when a forecast is clicked for analysis in the regression tab. The function takes the
        rowNumber that was clicked as input. It first figures out which regression scheme we're talking about (by
        checking which tab is active), then it gets the specific forecast stored in the fcstList (returned by
        the featureSelection routine) and plots the results of that forecast. It returns the fcstDict that was clicked.
        """

        

        currentRegScheme = self.regressionTab.regrSelectPane.tabWidget.currentIndex()
        if currentRegScheme == 0:
            currentEquation = self.regressionTab.regrSelectPane.mlrTab.eqSelect.currentText()
            fcst = self.mlrFcstList[rowNum]
        elif currentRegScheme == 1:
            currentEquation = self.regressionTab.regrSelectPane.pcarTab.eqSelect.currentText()
            fcst = self.pcarFcstList[rowNum]
        elif currentRegScheme == 2:
            currentEquation = self.regressionTab.regrSelectPane.zscrTab.eqSelect.currentText()
            fcst = self.zscrFcstList[rowNum]
        else:
            currentEquation = self.regressionTab.regrSelectPane.annTab.eqSelect.currentText()
            fcst = self.annFcstList[rowNum]

        # Make sure the fcst is valid
        if fcst['prdIDs'] == []:
            return
        
        prdIDs = fcst['prdIDs']
        predictorData = pd.DataFrame()
        predictorNames = {}
        for predictorName in self.forecastDict['PredictorPool']:
            for interval in self.forecastDict['PredictorPool'][predictorName]:
                if self.forecastDict['PredictorPool'][predictorName][interval]['prdID'] in prdIDs:
                    predictorNames[str(self.forecastDict['PredictorPool'][predictorName][interval]['prdID'])] = str(predictorName) + ', ' + str(interval)
                    predictorData = pd.concat([predictorData, pd.DataFrame().from_dict(self.forecastDict['PredictorPool'][predictorName][interval]['Data'], orient='columns')], axis=1)
        
        predictorData = predictorData.dropna()

        predictand = self.forecastDict['EquationPools'][currentEquation]['Predictand']
        predictandName = predictand['Name']
        predictandUnits = predictand['Unit']
        predictandData = pd.DataFrame().from_dict(predictand['Data'])

        commonIndex = predictandData.index.intersection(predictorData.index)
        predictandData = predictandData.loc[commonIndex]
        predictorData = predictorData.loc[commonIndex]
 
        fcstID =fcst['fcstID']

        """ populate a forecast dict entry """
        dictEntry = {
            "fcstID"            : fcstID,
            "Equation"          : currentEquation,
            "Water Years"       : fcst['Years Used'],
            "PrdIDs"            : fcst['prdIDs'],
            "Type"              : fcst['Type'],
            "Coef"              : fcst['Coef'],
            "Intercept"         : fcst['Intercept'],
            "Metrics"           : fcst['Metrics'],
            "Cross Validation"  : fcst['CrossValidation'],
            "Predicted"         : fcst['Forecasted'],
            "CV_Predicted"      : fcst['CV_Forecasted'],
            "Forecasts"         : {},
            "Extras"            : fcst['PrincCompData'],
            "Distribution"     : fcst['Distribution']
        }

        self.plotFcstEntryRegressionTab(dictEntry, toggle_cv=999)

        return dictEntry
        
    
    def showRegStats(self):
        """
        This function will send the regression forecast dictionary of the current selection to the RegressionStatsGUI (assuming
        it's a PCA forecast). 
        """

        currentRegScheme = self.regressionTab.regrSelectPane.tabWidget.currentIndex()
        if currentRegScheme == 0:
            button = QtWidgets.QMessageBox.question(self, '','Not implemented for this regression type', QtWidgets.QMessageBox.Ok )
            return
        elif currentRegScheme == 1:
            rowNum = self.regressionTab.regrSelectPane.pcarTab.bestModelTable.currentRow()
            currentEquation = self.regressionTab.regrSelectPane.pcarTab.eqSelect.currentText()
            try:
                fcst = self.pcarFcstList[rowNum]
            except:
                return

        else:
            rowNum = self.regressionTab.regrSelectPane.zscrTab.bestModelTable.currentRow()
            currentEquation = self.regressionTab.regrSelectPane.pcarTab.eqSelect.currentText()
            try:
                fcst = self.zscrFcstList[rowNum]
            except:
                return
            #button = QtWidgets.QMessageBox.question(self, '','Not implemented for this regression type', QtWidgets.QMessageBox.Ok )
            #return
        print(fcst)
        self.regStats = RegressionStatsGUI.regrStatsWindow(fcst)

        return


    def saveFcst(self):
        """
        This function grabs the selected forecast from the volatile memory (self.pcarFcstList) and stores it 
        permanently in the self.forecastDict, which is saved in the file. Additionally, it appends a check mark to 
        the displayed forecast list so that the user knows whcih forecasts have already been saved.
        """

        def printError():
            button = QtWidgets.QMessageBox.question(self, 'Already stored','This forecast is already saved.', QtWidgets.QMessageBox.Ok )
            return

        currentRegScheme = self.regressionTab.regrSelectPane.tabWidget.currentIndex()
        if currentRegScheme == 0:
            currentEquation = self.regressionTab.regrSelectPane.mlrTab.eqSelect.currentText()
            rowNum = self.regressionTab.regrSelectPane.mlrTab.bestModelTable.currentRow()
            fcst = self.mlrFcstList[rowNum]
            text = self.regressionTab.regrSelectPane.mlrTab.bestModelTable.currentItem().text()
            if u"\u2705" in text:
                printError()
                return
            self.regressionTab.regrSelectPane.mlrTab.bestModelTable.setItem(rowNum, 0, QtWidgets.QTableWidgetItem(u"\u2705" + text))
        elif currentRegScheme == 1:
            currentEquation = self.regressionTab.regrSelectPane.pcarTab.eqSelect.currentText()
            rowNum = self.regressionTab.regrSelectPane.pcarTab.bestModelTable.currentRow()       
            fcst = self.pcarFcstList[rowNum]
            text = self.regressionTab.regrSelectPane.pcarTab.bestModelTable.currentItem().text()
            if u"\u2705" in text:
                printError()
                return
            self.regressionTab.regrSelectPane.pcarTab.bestModelTable.setItem(rowNum, 0, QtWidgets.QTableWidgetItem(u"\u2705" + text))
        elif currentRegScheme == 2:
            currentEquation = self.regressionTab.regrSelectPane.zscrTab.eqSelect.currentText()
            rowNum = self.regressionTab.regrSelectPane.zscrTab.bestModelTable.currentRow()
            fcst = self.zscrFcstList[rowNum]
            text = self.regressionTab.regrSelectPane.zscrTab.bestModelTable.currentItem().text()
            if u"\u2705" in text:
                printError()
                return
            self.regressionTab.regrSelectPane.zscrTab.bestModelTable.setItem(rowNum, 0, QtWidgets.QTableWidgetItem(u"\u2705" + text))
        else:
            currentEquation = self.regressionTab.regrSelectPane.annTab.eqSelect.currentText()
            rowNum = self.regressionTab.regrSelectPane.annTab.bestModelTable.currentRow()
            fcst = self.annFcstList[rowNum]
            text = self.regressionTab.regrSelectPane.annTab.bestModelTable.currentItem().text()
            if u"\u2705" in text:
                printError()
                return
            self.regressionTab.regrSelectPane.annTab.bestModelTable.setItem(rowNum, 0, QtWidgets.QTableWidgetItem(u"\u2705" + text))
        fcstID = fcst['fcstID']
        self.forecastDict['EquationPools'][currentEquation]['ForecastEquations'][fcstID] = self.fcstClicked(rowNum, 0)
        self.reDrawForecastDict()

        return

























    #/////////////////////////// DENSITY TAB ///////////////////////////////////////// 
    #// Here we connect the buttons and events from the density tab to their respective 
    #// functions. We also define some functions here as well. 

    def connectEventsDensityTab(self):
        self.tabWidget.currentChanged.connect(self.populateDensityEquations)
        self.densityAnalysisTab.densityPane.forecastEquationSelect.currentIndexChanged.connect(self.loadNewDensityList)
        self.densityAnalysisTab.densityPane.runButton.clicked.connect(self.runAnalysis)
        
        pass

    def populateDensityEquations(self, tabNo):
        if tabNo == 5:
            self.densityAnalysisTab.densityPane.forecastEquationSelect.clear()
            for equation in self.forecastDict['EquationPools']:
                self.densityAnalysisTab.densityPane.forecastEquationSelect.addItem(str(equation))

    def loadNewDensityList(self, equationIndex):
        time.sleep(1)
        equation = self.densityAnalysisTab.densityPane.forecastEquationSelect.currentText()
        if equation == '':
            return
        self.densityAnalysisTab.densityPane.selectedFcstTable.setRowCount(0)

        for fcst in self.forecastDict['EquationPools'][equation]['ForecastEquations']:
            #currentMonth = datetime.now().month
            currentMonth = current_date().month
            if currentMonth >= monthLookup(self.forecastDict['Options']['wateryearStart']):
                #currentWaterYear = datetime.now().year + 1
                currentWaterYear = current_date().year + 1
            else:
                #currentWaterYear = datetime.now().year
                currentWaterYear = current_date().year
            if currentWaterYear in list(self.forecastDict['EquationPools'][equation]['ForecastEquations'][fcst]['Forecasts']):
                name = self.forecastDict['EquationPools'][equation]['ForecastEquations'][fcst]['fcstID']
                forecasted = self.forecastDict['EquationPools'][equation]['ForecastEquations'][fcst]['Forecasts'][currentWaterYear]['Intervals']['50%']
                self.densityAnalysisTab.densityPane.selectedFcstTable.addRow([name, str(forecasted)])
        self.densityAnalysisTab.densityPane.selectedFcstTable.horizontalHeader().setStretchLastSection(True)

    def runAnalysis(self):
        
        """ Get selected indices """
        items = self.densityAnalysisTab.densityPane.selectedFcstTable.selectedItems()
        if items == []:
            return

        fcstList = []
        for item in items:
            if item.column() == 0:
                fcstList.append(item.text())

        """ Get the equation """
        equation = self.densityAnalysisTab.densityPane.forecastEquationSelect.currentText()

        currentMonth = current_date().month
        if currentMonth >= monthLookup(self.forecastDict['Options']['wateryearStart']):
            #currentWaterYear = datetime.now().year + 1
            currentWaterYear = current_date().year + 1
        else:
            #currentWaterYear = datetime.now().year
            currentWaterYear = current_date().year

        self.densityAnalysisTab.plots.clear_plot()

        minFcst = np.min([self.forecastDict['EquationPools'][equation]['ForecastEquations'][forecast]['Forecasts'][currentWaterYear]['Intervals']['10%'] for forecast in fcstList])
        maxFcst = np.max([self.forecastDict['EquationPools'][equation]['ForecastEquations'][forecast]['Forecasts'][currentWaterYear]['Intervals']['90%'] for forecast in fcstList])
        rang = maxFcst - minFcst
        x = np.linspace(minFcst - rang/1, maxFcst + rang/1, 1000)

        meanList = []
        scaleList = []
        bwidth_text = self.densityAnalysisTab.densityPane.bwidthEdit.text()

        def triggerError():
            button = QtWidgets.QMessageBox.question(self, 'Bad Bandwidth Value','Use a valid bandwidth or specify "AUTO"', QtWidgets.QMessageBox.Ok)
            return

        try:
            bwidth = float(bwidth_text)
            if bwidth < 0:
                triggerError()
                return
        except:
            try:
                if bwidth_text.upper() == 'AUTO':
                    bwidth = -999.9
                else:
                    triggerError()
                    return
            except:
                triggerError()
                return


        for i, forecast in enumerate(fcstList):
            fcst = self.forecastDict['EquationPools'][equation]['ForecastEquations'][forecast]
            meanList.append(fcst['Forecasts'][list(fcst['Forecasts'])[0]]['Intervals']['50%'])
            s = (fcst['Forecasts'][list(fcst['Forecasts'])[0]]['Intervals']['90%'] - fcst['Forecasts'][list(fcst['Forecasts'])[0]]['Intervals']['50%']) / 1.28155157
            scaleList.append(s)

            
            y = stats.norm.pdf(x,  loc=fcst['Forecasts'][list(fcst['Forecasts'])[0]]['Intervals']['50%'], scale=s)
            yc = stats.norm.cdf(x,  loc=fcst['Forecasts'][list(fcst['Forecasts'])[0]]['Intervals']['50%'], scale=s)

            self.densityAnalysisTab.plots.add_to_plot1(x, y, color='#0a85cc',marker=None,linestyle='--', zorder=1)
            self.densityAnalysisTab.plots.add_to_plot2(x, yc, color='#0a85cc',marker=None,linestyle='--', zorder=1)
        
        kdens, samples, bandwidth = kernelDensity.performKernelDensity(meanList, scaleList, bwidth, x)
        self.densityAnalysisTab.plots.axes1.plot(samples[:,0], -0.00005 - 0.0003 * np.random.random(samples.shape[0]), '+k')
        self.densityAnalysisTab.plots.axes1.annotate('Bandwidth: {0}'.format(np.round(bandwidth, 1)), (0.12, 0.85), xycoords='figure fraction')

        self.densityAnalysisTab.plots.axes1.fill_between(x, 0, kdens, facecolor=(1,0,0,0.3), edgecolor=(1,0,0,1), linewidth=2, zorder=2)
        cumulativeSum = [np.trapz(kdens[0:i+1], x[0:i+1]) for i in range(len(kdens))]
       
        self.densityAnalysisTab.plots.axes2.fill_between(x, 0, cumulativeSum, facecolor=(1,0,0,0.3), edgecolor=(1,0,0,1), linewidth=2, zorder=2)
        self.densityAnalysisTab.plots.axes1.set_xlim(minFcst - rang/2, maxFcst + rang/2)
        self.densityAnalysisTab.plots.axes2.set_xlim(minFcst - rang/2, maxFcst + rang/2)
        
        intervals = [self.findIntervalValue(x, cumulativeSum, i) for i in [0.1, 0.3, 0.5, 0.7, 0.9]]
        self.densityAnalysisTab.pct10Edit.setText(str(intervals[0]))
        self.densityAnalysisTab.pct30Edit.setText(str(intervals[1]))
        self.densityAnalysisTab.pct50Edit.setText(str(intervals[2]))
        self.densityAnalysisTab.pct70Edit.setText(str(intervals[3]))
        self.densityAnalysisTab.pct90Edit.setText(str(intervals[4]))

        self.densityAnalysisTab.plots.axes2.vlines(intervals, [0,0,0,0,0], [0.1, 0.3, 0.5, 0.7, 0.9], colors = ['red' for _ in intervals], linewidth=2, zorder=2)

        self.densityAnalysisTab.plots.draw_plot()

    
    def findIntervalValue(self, xVals, yVals, interval):

        for i, val in enumerate(xVals):
            if yVals[i] < interval:
                lowX = val
                lowY = yVals[i]
            else:
                highX = val
                highY = yVals[i]
                break
      
        x = lowX + (interval - lowY)*(highX - lowX)/(highY - lowY)
        return np.round(x, 1)



        



        



