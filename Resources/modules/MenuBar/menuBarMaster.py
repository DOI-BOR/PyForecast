from resources.modules.Miscellaneous import loggingAndErrors
from resources.GUI.Dialogs import PreferencesGUI
from datetime import datetime
import pickle
import time
from PyQt5.QtWidgets import QFileDialog

class menuBar(object):
    """
    """
    def setupMenuBar(self):
        """
        """
        self.appMenu.preferencesAction.triggered.connect(self.openPreferencesGUI)
        self.appMenu.saveAction.triggered.connect(self.saveForecastFile)
        self.appMenu.saveAsAction.triggered.connect(lambda: self.saveForecastFile(True))
        self.appMenu.openAction.triggered.connect(self.openForecastFile)
        return
    
    def openPreferencesGUI(self):
        """
        """
        self.preferences = PreferencesGUI.preferencesDialog()

    def applyNewPreferences(self):
        """
        """
        return

    def saveForecastFile(self, saveAs=False):
        """
        """
        fname = self.userOptionsConfig['FILE OPS']['file_name']
        if fname == '' or saveAs == True:
            fname = QFileDialog.getSaveFileName(self, 'Save File As', 'untitled.fcst','*.fcst')[0]
            self.userOptionsConfig['FILE OPS']['file_name'] = fname

            if fname == '':
                return
            
            if '.' not in fname:
                fname = fname + '.fcst'
            
        self.storeMapInformation()
        self.storeDataTabInformation()

        with open('resources/temp/user_options.txt', 'w') as configfile:
            self.userOptionsConfig.write(configfile)

        with open(fname, 'wb') as writefile:
            
            pickle.dump(self.datasetTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.dataTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.modelRunsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.forecastEquationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.forecastsTable, writefile, pickle.HIGHEST_PROTOCOL)

            with open('resources/temp/user_options.txt', 'r') as readfile:
                pickle.dump(readfile.read(), writefile, pickle.HIGHEST_PROTOCOL)
        

    def openForecastFile(self):
        """
        """
        fname = QFileDialog.getOpenFileName(self, 'Open File','*.fcst')[0]
        self.applicationPrefsConfig['FILE OPS']['file_name'] = fname

        if fname == '':
            return 
        
        # Load all the tables, files
        with open(fname, 'rb') as readfile:
            self.datasetTable = pickle.load(readfile)
            self.dataTable = pickle.load(readfile)
            self.modelRunsTable = pickle.load(readfile)
            self.forecastEquationsTable = pickle.load(readfile) 
            self.forecastsTable = pickle.load(readfile)
            with open('resources/temp/user_options.txt', 'w') as writefile:
                writefile.write(pickle.load(readfile))
        
        self.userOptionsConfig.read('resources/temp/user_options.txt')

        # Apply the files and tables to the tabs
        self.resetDatasetTab()
        self.resetDataTab()