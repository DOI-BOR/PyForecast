# Script Name:      RestServiceAdd.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      'RestServiceAdd' opens a dialog window which allows a user to 
#                   download data using a user-defined dataloader.

# Import Libraries
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import sys
import importlib
import numpy as np
from datetime import datetime, timedelta

# Create a custom table widget
class OptionsTable(QtWidgets.QTableWidget):

    # Runs when the table is first initialized by the application
    def __init__(self,parent=None):

        QtWidgets.QTableWidget.__init__(self)

        # Set the table properties
        self.setColumnCount(2)
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["Option","Value"])
        self.setShowGrid(True)
        self.setGridStyle(QtCore.Qt.DotLine)
        self.setCornerButtonEnabled(False)
        self.verticalHeader().setVisible(False)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

    # Function that clears and re=populates the table with all the custom dataloaders
    def populateOptions(self, item):

        # Clear the existing table
        self.setRowCount(0)

        # Get the selected custom loader
        selection = item

        # Import the dataloader options
        dataloader = importlib.import_module('Resources.DataLoaders.Custom.'+selection)
        dataloaderOptionsFunction = getattr(dataloader, "dataLoaderInfo")

        # Get the options
        optionsList = list(dataloaderOptionsFunction()[0])
        self.description = dataloaderOptionsFunction()[1]
        
        # Load the options into the table
        for i, option in enumerate(optionsList):

            self.insertRow(i)
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(option))

        # Stretch last section
        header = self.horizontalHeader()
        header.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)

# Create a class to hold signals
class RESTDialogSignals(QtCore.QObject):

    returnStationDict = QtCore.pyqtSignal(dict) 

# Create a dialog window
class RESTDialog1(QtWidgets.QDialog):
    
    def __init__(self):

        super(RESTDialog1, self).__init__()
        mainLayout = QtWidgets.QVBoxLayout()
        
        # INITIAL SET-UP
        self.setWindowTitle("Add Custom Dataset using a dataloader")

        hlayout = QtWidgets.QHBoxLayout()
        dloaderTitle = QtWidgets.QLabel("Choose Dataloader")
        self.dloaderChoose = QtWidgets.QComboBox()
        dloaderNamesAll = os.listdir('Resources/DataLoaders/Custom')
        for i, file in enumerate(dloaderNamesAll):
            if file[-3:] == '.py':
                self.dloaderChoose.addItem(file[:-3])
        
        self.dloaderChoose.currentTextChanged.connect(self.populateOptionsTable)

        hlayout.addWidget(dloaderTitle)
        hlayout.addWidget(self.dloaderChoose)
        mainLayout.addLayout(hlayout)

        nameEditTitle = QtWidgets.QLabel("Dataset Name")
        self.nameEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(nameEditTitle)
        hlayout.addWidget(self.nameEdit)
        mainLayout.addLayout(hlayout)

        paramEditTitle = QtWidgets.QLabel("Parameter Name")
        self.paramEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(paramEditTitle)
        hlayout.addWidget(self.paramEdit)
        mainLayout.addLayout(hlayout)

        unitsEditTitle = QtWidgets.QLabel("Units")
        self.unitsEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(unitsEditTitle)
        hlayout.addWidget(self.unitsEdit)
        mainLayout.addLayout(hlayout)

        resamplingMethodTitle = QtWidgets.QLabel("Resampling")
        self.resampleChooser = QtWidgets.QComboBox()
        self.resampleChooser.addItems(['Mean','Sample','Accumulation'])
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(resamplingMethodTitle)
        hlayout.addWidget(self.resampleChooser)
        mainLayout.addLayout(hlayout)

        decriptionTitle = QtWidgets.QLabel("Loader Description")
        self.description = QtWidgets.QPlainTextEdit()
        self.description.setMaximumHeight(50)
        self.description.setReadOnly(True)
        mainLayout.addWidget(decriptionTitle)
        mainLayout.addWidget(self.description)

        self.optionsTable = OptionsTable()
        mainLayout.addWidget(self.optionsTable)

        self.addButton = QtWidgets.QPushButton("Add Station")
        self.addButton.pressed.connect(self.packageAndReturn)
        mainLayout.addWidget(self.addButton)

        self.setLayout(mainLayout)

        self.populateOptionsTable(self.dloaderChoose.currentText())

        self.datasetDict = {}

        self.signals = RESTDialogSignals()

        self.show() #CHANGE TO EXEC
    
    def populateOptionsTable(self, text):

        self.optionsTable.populateOptions(text)
        self.description.setPlainText(self.optionsTable.description)
    
    def packageAndReturn(self):
        
        # Check to make sure the name is set
        if self.nameEdit.text() == '':
            button = QtWidgets.QMessageBox.question(self, 'Error', 'Please provide a name for this dataset.', QtWidgets.QMessageBox.Ok)
            if button == QtWidgets.QMessageBox.Ok:
                return
        
        name = self.nameEdit.text()
        parameter =  self.paramEdit.text()
        units = self.unitsEdit.text()
        
        self.datasetDict = {"TYPE":"Custom","ID":str(int(10000*np.random.rand())),"Name":name, "Parameter":parameter, "Units":units, "Resampling":self.resampleChooser.currentText(), "Decoding":{"dataLoader":self.dloaderChoose.currentText()}, "Data":{}}
        
        # Get the options
        numRows = self.optionsTable.rowCount()
        for i in range(numRows):
            option = self.optionsTable.item(i,0).text()
            value = self.optionsTable.item(i,1).text()
            self.datasetDict[option] = value

        # Check to make sure the loader is working
        testResult = self.testLoader()
        if testResult != 'Success':
            button = QtWidgets.QMessageBox.question(self, 'Error', 'Loader is not able to download data. Check script and options.', QtWidgets.QMessageBox.Ok)
            return
            
        self.signals.returnStationDict.emit(self.datasetDict) # return the station dict to the main function
        self.close()

    # Function to test the custom dataloader
    def testLoader(self):
        
        try:
            selection = self.dloaderChoose.currentText()

            # First import the loader
            print('testing loader')
            dataloader = importlib.import_module('Resources.DataLoaders.Custom.'+selection)
            dataloaderOptionsFunction = getattr(dataloader, "dataLoaderInfo")
            dataloaderGetData = getattr(dataloader, 'dataLoader')

            print('loader imported')

            # Set a start and end date
            endDate = datetime.now() - timedelta(days=5)
            startDate = endDate - timedelta(days=100)

            # Get try to get the data
            print(self.datasetDict)
            df = dataloaderGetData(self.datasetDict, startDate, endDate)
            if df.empty:
                return 'Fail'
            return 'Success'
        
        except Exception as e:
            print(e)
            return 'Fail'







    