# Script Name:      importSpread.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      'ImportSpread' is a dialog window that allows users
#                   to import datasets from flat files (csv/xlsx).

# Import Libraries
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Create a class to describe signals
class importSignals(QtCore.QObject):

    returnDatasetSignal = QtCore.pyqtSignal(dict)

# Create a dialog window
class importDialog(QtWidgets.QDialog):

    def __init__(self):

        super(importDialog, self).__init__()
        mainLayout = QtWidgets.QVBoxLayout()

        self.setWindowTitle("Add Custom Dataset from flat file")

        datasetNameTitle = QtWidgets.QLabel("Dataset Name")
        self.datasetNameEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(datasetNameTitle)
        hlayout.addWidget(self.datasetNameEdit)
        mainLayout.addLayout(hlayout)

        paramNameTitle = QtWidgets.QLabel("Parameter Name")
        self.paramNameEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(paramNameTitle)
        hlayout.addWidget(self.paramNameEdit)
        mainLayout.addLayout(hlayout)

        unitNameTitle = QtWidgets.QLabel("Unit Name")
        self.unitNameEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(unitNameTitle)
        hlayout.addWidget(self.unitNameEdit)
        mainLayout.addLayout(hlayout)

        resamplingMethodTitle = QtWidgets.QLabel("Resampling")
        self.resampleChooser = QtWidgets.QComboBox()
        self.resampleChooser.addItems(['Mean','Sample','Accumulation'])
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(resamplingMethodTitle)
        hlayout.addWidget(self.resampleChooser)
        mainLayout.addLayout(hlayout)

        fileNameTitle = QtWidgets.QLabel("Select File: ")
        self.fileButton = QtWidgets.QPushButton("Browse")
        self.fileButton.pressed.connect(self.getFile)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(fileNameTitle)
        hlayout.addWidget(self.fileButton)
        mainLayout.addLayout(hlayout)

        self.fileLabel = QtWidgets.QLabel("file not set...")
        mainLayout.addWidget(self.fileLabel)

        self.importButton = QtWidgets.QPushButton("Import")
        self.importButton.pressed.connect(self.importSheet)
        mainLayout.addWidget(self.importButton)

        self.signals = importSignals()
        self.filename = None
        self.setLayout(mainLayout)
        self.show()
    
    def getFile(self):

        # Open a file dialog
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Import data', os.path.abspath(os.sep),'Flat files (*.csv *.xlsx)')[0]
        if self.filename == '':
            return  
        
        self.fileLabel.setText(self.filename)


    def importSheet(self):
        if self.filename == None:
            return
        # Try to import CSV File
        if '.csv' in self.filename:

            try:
                # Try to read the data into a dataframe
                df = pd.read_csv(self.filename, header=0, index_col=0, parse_dates=True, infer_datetime_format=True)
                
                # Set the column name 
                df.columns = [self.datasetNameEdit.text()]

                # Give it a unique ID
                id = 'CSV'+str(int(1000*np.random.rand()))

                # Set up the data dictionary
                dataDict = {"PYID":"", "TYPE":"IMPORT","ID":id,"Name":self.datasetNameEdit.text(),"Parameter":self.paramNameEdit.text(),"Units":self.unitNameEdit.text(),"Resampling":self.resampleChooser.currentText(),"Decoding":{"dataLoader":"IMPORT"}, "Data":df.to_dict(orient='dict')}

            except Exception as e:
                print(e)
                return
        elif '.xlsx' in self.filename:

            try:
                # Try to read the data into a dataframe
                df = pd.read_excel(self.filename, header=0, index_col=0, parse_dates=True, infer_datetime_format=True)

                # Set the collumn name
                df.columns = [self.datasetNameEdit.text()]

                # Give it a unique ID
                id = 'XLSX'+str(int(1000*np.random.rand()))

                # Set up the data directory
                dataDict = {"PYID":"", "TYPE":"IMPORT","ID":id,"Name":self.datasetNameEdit.text(),"Parameter":self.paramNameEdit.text(),"Units":self.unitNameEdit.text(),"Resampling":self.resampleChooser.currentText(),"Decoding":{"dataLoader":"IMPORT"}, "Data":df.to_dict(orient='dict')}

            except Exception as e:
                print(e)
                return

        print(dataDict)
        self.signals.returnDatasetSignal.emit(dataDict)
        self.close()
        

    