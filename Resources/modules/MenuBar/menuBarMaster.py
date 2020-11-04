from resources.modules.Miscellaneous import loggingAndErrors
from resources.modules.MenuBar import databaseViewer
from resources.GUI.Dialogs import PreferencesGUI
from datetime import datetime
import pickle
import time
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox

class menuBar(object):
    """
    """
    def setupMenuBar(self):
        """
        """
        self.appMenu.preferencesAction.triggered.connect(self.openPreferencesGUI)
        self.appMenu.saveAction.triggered.connect(self.saveForecastFile)
        self.appMenu.saveAction.setShortcut("Ctrl+S")
        self.appMenu.saveAsAction.triggered.connect(lambda: self.saveForecastFile(True))
        self.appMenu.openAction.triggered.connect(self.openForecastFile)
        self.appMenu.openAction.setShortcut("Ctrl+O")
        self.appMenu.viewTablesAction.triggered.connect(self.viewDatabase)
        return

    def viewDatabase(self):
        """
        """
        self.databaseViewerDialog = databaseViewer.viewerWindow(self)
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
        #fname = self.userOptionsConfig['FILE OPS']['file_name']
        fname = ""
        if fname == '' or saveAs == True:
            fname = QFileDialog.getSaveFileName(self, 'Save File As', 'untitled.fcst','*.fcst')[0]
            #self.userOptionsConfig['FILE OPS']['file_name'] = fname

            if fname == '':
                return
            
            if '.fcst' not in fname:
                fname = fname + '.fcst'

        #with open('resources/temp/user_options.txt', 'w') as configfile:
        #    self.userOptionsConfig.write(configfile)

        with open(fname, 'wb') as writefile:
            
            pickle.dump(self.datasetTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.dataTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.datasetOperationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.modelRunsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.forecastEquationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.savedForecastEquationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.forecastsTable, writefile, pickle.HIGHEST_PROTOCOL)

            #with open('resources/temp/user_options.txt', 'r') as readfile:
            #    pickle.dump(readfile.read(), writefile, pickle.HIGHEST_PROTOCOL)

        self.setWindowTitle("PyForecast - " + str(fname))
        

    def openForecastFile(self):
        """
        """
        if self.fileOpened:
            self.showMessageBox("Warning", "Forecast file already open",
                                "Start another PyForecast window or close and " +
                                "reopen PyForecast to open another forecast file")
            return

        fname = QFileDialog.getOpenFileName(self, 'Open File','*.fcst')[0]
        #self.applicationPrefsConfig['FILE OPS']['file_name'] = fname
        if fname == '':
            return

        self.updateStatusMessage('Loading forecast file...')
        # Load all the tables, files
        with open(fname, 'rb') as readfile:
            try:
                self.datasetTable = pickle.load(readfile)
            except:
                print('WARNING: No datasetTable in saved forecast file...')
            try:
                self.dataTable = pickle.load(readfile)
            except:
                print('WARNING: No dataTable in saved forecast file...')
            try:
                self.datasetOperationsTable = pickle.load(readfile)
            except:
                print('WARNING: No datasetOperationsTable in saved forecast file...')
            try:
                self.modelRunsTable = pickle.load(readfile)
            except:
                print('WARNING: No modelRunsTable in saved forecast file...')
            try:
                self.forecastEquationsTable = pickle.load(readfile)
            except:
                print('WARNING: No forecastEquationsTable in saved forecast file...')
            try:
                self.savedForecastEquationsTable = pickle.load(readfile)
            except:
                print('WARNING: No savedForecastEquationsTable in saved forecast file...')
            try:
                self.forecastsTable = pickle.load(readfile)
            except:
                print('WARNING: No forecastsTable in saved forecast file...')
            #with open('resources/temp/user_options.txt', 'w') as writefile:
            #    writefile.write(pickle.load(readfile))
        
        #self.userOptionsConfig.read('resources/temp/user_options.txt')
        # Apply the files and tables to the tabs
        self.setWindowTitle("PyForecast - " + str(fname))
        self.resetDatasetTab()
        self.resetDataTab()
        self.resetModelCreationTab()
        self.resetForecastsTab()
        self.fileOpened = True
        self.updateStatusMessage('Forecast file loaded!')


    def showMessageBox(self, boxTitle, mainText, subText = None, detailText = None):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(boxTitle)
        msg.setText(mainText)
        if subText is not None:
            msg.setInformativeText(subText)
        if detailText is not None:
            msg.setDetailedText(detailText)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def updateStatusMessage(self, message, messageFormat=None):
        self.statusBar().showMessage(message)
        self.statusBar().repaint()