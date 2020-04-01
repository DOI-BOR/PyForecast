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

from PyQt5 import QtWidgets, QtCore
from datetime import datetime
from resources.GUI import NextFlowGUI
from resources.modules.DatasetTab import datasetTabMaster 
from resources.modules.DataTab import dataTabMaster
from resources.modules.MenuBar import menuBarMaster
from resources.modules.StatisticalModelsTab import StatisticalModelsTabMaster
from resources.modules.Miscellaneous import initUserOptions
from datetime import datetime
import configparser
import pandas as pd


class mainWindow(QtWidgets.QMainWindow, NextFlowGUI.UI_MainWindow, datasetTabMaster.datasetTab, dataTabMaster.dataTab, menuBarMaster.menuBar, StatisticalModelsTabMaster.statisticalModelsTab):
    """
    GLOBAL APPLICATION INITIALIZATION
    This section of the script deals with the initialization of the software. These subroutines 
    run immediately after the software begins.
    """

    def __init__(self):
        """
        The __init__ method runs when the GUI is first instantiated. Here we define the 'self' variable as a 
        reference to the mainWindow class, as well as build the GUI and connect all the functionality to the buttons
        and events in the GUI.
        """

        # Initialize the class as a QMainWindow and setup its User Interface
        super(self.__class__, self).__init__()
        
        # Create the data structures.
        # The dataset table stores information about all the datasets being used in the forecast file.
        self.datasetTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                "DatasetParameterCode",     # e.g. avgt
                'DatasetUnits',             # e.g. CFS
                'DatasetDefaultResampling', # e.g. average 
                'DatasetDataloader',        # e.g. RCC_ACIS
                'DatasetHUC8',              # e.g. 10030104
                'DatasetLatitude',          # e.g. 44.352
                'DatasetLongitude',         # e.g. -112.324
                'DatasetElevation',         # e.g. 3133 (in ft)
                'DatasetPORStart',          # e.g. 1/24/1993
                'DatasetPOREnd',            # e.g. 1/22/2019\
                'DatasetCompositeEquation', # e.g. C/100121,102331,504423/1.0,0.5,4.3/0,0,5
                'DatasetImportFileName',    # e.g. 'C://Users//JoeDow//Dataset.CSV'
                'DatasetAdditionalOptions'
            ],
        ) 
        self.datasetTable['DatasetHUC8'] = self.datasetTable['DatasetHUC8'].astype(str)

        # The data table stores all of the raw data associated with the selected datasets.
        # Edited data is versioned as 1 and unedited data is versioned as 0
        self.dataTable = pd.DataFrame(
            index = pd.MultiIndex(
                levels=[[],[],],
                codes = [[],[],],
                names = [
                    'Datetime',             # E.g. 1998-10-23
                    'DatasetInternalID'     # E.g. 100302
                    ]
            ),
            columns = [
                "Value",                    # E.g. 12.3, Nan, 0.33
                "EditFlag"                  # E.g. True, False -> NOTE: NOT IMPLEMENTED
                ],
            dtype=float
        )
        self.dataTable['EditFlag'] = self.dataTable['EditFlag'].astype(bool)
        
        # This table will keep track of all the model runs initial conditions
        self.modelRunsTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ModelRunID'),
            columns = [
                "ModelTrainingPeriod",  # E.g. 1978-10-01/2019-09-30 (model trained on  WY1979-WY2019 data)
                "ForecastIssueDate",    # E.g. January 13th
                "Predictand",           # E.g. 100302 (datasetInternalID)
                "PredictandPeriod",     # E.g. R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",     # E.g. Accumulation, Average, Max, etc
                "PredictorGroups",      # E.g. ["SNOTEL SITES", "CLIMATE INDICES", ...]
                "PredictorGroupMapping",# E.g. [0, 0, 0, 1, 4, 2, 1, 3, ...] maps each predictor in the pool to a predictor group
                "PredictorPool",        # E.g. [100204, 100101, ...]
                "PredictorForceFlag",   # E.g. [False, False, True, ...]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, ...]
                "PredictorMethods",     # E.g. ['Accumulation', 'First', 'Last', ...]
                "RegressionTypes",      # E.g. ['Regr_MultipleLinearRegression', 'Regr_ZScoreRegression']
                "CrossValidationType",  # E.g. K-Fold (10 folds)
                "FeatureSelectionTypes",# E.g. ['FeatSel_SequentialFloatingSelection', 'FeatSel_GeneticAlgorithm']
                "ScoringParameters",    # E.g. ['ADJ_R2', 'MSE']
                "Preprocessors"         # E.g. ['PreProc_Logarithmic', 'PreProc_YAware']
            ]
        )

        # The forecastEquationsTable stores all of the forecast equations saved or imported by the user.
        self.forecastEquationsTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ForecastEquationID'),
            columns = [
                "EquationSource",       # e.g. 'PyForecast','NRCS', 'CustomImport'
                "EquationComment",      # E.g. 'Equation Used for 2000-2010 Forecasts'
                "EquationPredictand",   # E.g. 103011
                "PredictandPeriod",     # R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",      # E.g. Accumulation, Average, Max, etc
                "EquationCreatedOn",    # E.g. 2019-10-04
                "EquationIssueDate",    # E.g. 2019-02-01
                "EquationMethod",       # E.g. Pipeline string (e.g. PIPE/PreProc_Logistic/Regr_Gamma/KFOLD_5)
                "EquationSkill",        # E.g. Score metric dictionary (e.g. {"AIC_C": 433, "ADJ_R2":0.32, ...})
                "EquationPredictors",   # E.g. [100204, 100101, 500232]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M]
                "PredictorMethods"      # E.g. ['Average', 'First', 'Max']
            ]
        )

        # The forecastsTable stores all of the forecasts created from forecast equations in the forecastEquationsTable
        self.forecastsTable = pd.DataFrame(
            index = pd.MultiIndex(
                levels=[[],[],[]],
                codes= [[],[],[]],
                names=[
                    'ForecastEquationID',   # E.g. 1010010 (999999 for user imported forecast)
                    'Year',                 # E.g. 2019
                    'ForecastIssuedOn'      # E.g. 2019-04-02
                    ]
            ),
            columns = [
                "ForecastExceedanceKey",    # e.g. [0.01, 0.02, ..., 0.98, 0.99]
                "ForecastValues",           # in order of 0-100% exceedance
                ],
        )
        
        # Initialize the software with default values for the user configuration and any stored values for the application preferences
        initUserOptions.initOptions()
        self.userOptionsConfig = configparser.ConfigParser()
        self.userOptionsConfig.read('resources/temp/user_options.txt')

        self.setUI()

        # Set-up all the tabs and menu bars
        self.initializeDatasetTab()
        self.initializeDataTab()
        self.initializeStatisticalModelsTab()
        self.setupMenuBar()

        # Intiate a threadpool
        self.threadPool = QtCore.QThreadPool()

        # Show the application
        self.showMaximized()

        return