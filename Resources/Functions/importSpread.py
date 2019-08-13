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

        self.setWindowTitle("Add dataset from file")

        datasetNameTitle = QtWidgets.QLabel("Dataset Name")
        self.datasetNameEdit = QtWidgets.QLineEdit()
        self.datasetNameEdit.setText('Dataset1')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(datasetNameTitle)
        hlayout.addWidget(self.datasetNameEdit)
        mainLayout.addLayout(hlayout)

        paramNameTitle = QtWidgets.QLabel("Parameter Name")
        self.paramNameEdit = QtWidgets.QLineEdit()
        self.paramNameEdit.setText('Parameter1')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(paramNameTitle)
        hlayout.addWidget(self.paramNameEdit)
        mainLayout.addLayout(hlayout)

        unitNameTitle = QtWidgets.QLabel("Unit Name")
        self.unitNameEdit = QtWidgets.QLineEdit()
        self.unitNameEdit.setText('cfs')
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

        self.arrayImportCheck = QtWidgets.QCheckBox("Import Data Array")
        self.arrayImportCheck.setChecked(False)
        mainLayout.addWidget(self.arrayImportCheck)

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
        try:
            headerRowIdx = 0
            # Data Array import override
            if self.arrayImportCheck.isChecked():
                headerRowIdx = 4 #skip first 4 rows since this is where the Dataset Name, Parameter Name, Unit, and Resampling should be
            # Try to import CSV File
            if '.csv' in self.filename:
                # Read headers for data array import
                dfHeaders = pd.read_csv(self.filename, nrows=headerRowIdx, header=None)
                # Try to read the data into a dataframe
                df = pd.read_csv(self.filename, header=headerRowIdx, index_col=0, parse_dates=True, infer_datetime_format=True)
            # Try to import XLSX file
            elif '.xlsx' in self.filename:
                # Read headers for data array import
                dfHeaders = pd.read_excel(self.filename, nrows=headerRowIdx, header=None)
                # Try to read the data into a dataframe
                df = pd.read_excel(self.filename, header=headerRowIdx, index_col=0, parse_dates=True, infer_datetime_format=True)
            # Data Array import override
            if self.arrayImportCheck.isChecked():
                dfHeaders = dfHeaders.drop(dfHeaders.columns[0], axis=1)
                if len(dfHeaders.columns) == len(df.columns):
                    for i in range(len(df)):
                        # Get a random ID
                        ithId = 'IMPORT' + str(int(100000 * np.random.rand()))
                        ithDf = df[df.columns[i]].to_frame()
                        ithHeaders = dfHeaders[dfHeaders.columns[i]]
                        ithName = ithHeaders[0]
                        ithDf.columns = [ithName]
                        ithPar = ithHeaders[1]
                        ithUnits = ithHeaders[2]
                        ithResampling  = ithHeaders[3]
                        # Set up the data dictionary
                        ithDataDict = {"PYID":"", "TYPE":"IMPORT","ID":ithId,"Name":ithName,"Parameter":ithPar,"Units":ithUnits,"Resampling":ithResampling,"Decoding":{"dataLoader":"IMPORT"}, "Data":ithDf.to_dict(orient='dict')}
                        print(ithDataDict)
                        self.signals.returnDatasetSignal.emit(ithDataDict)
                else:
                    self.fileLabel.setText('Header column count does not match the Data column count! Check your input data file...')
                    return
            else:
                # Get a random ID
                id = 'IMPORT' + str(int(100000 * np.random.rand()))
                # Set the column name
                df.columns = [self.datasetNameEdit.text()]
                # Set up the data dictionary
                dataDict = {"PYID":"", "TYPE":"IMPORT","ID":id,"Name":self.datasetNameEdit.text(),"Parameter":self.paramNameEdit.text(),"Units":self.unitNameEdit.text(),"Resampling":self.resampleChooser.currentText(),"Decoding":{"dataLoader":"IMPORT"}, "Data":df.to_dict(orient='dict')}
                print(dataDict)
                self.signals.returnDatasetSignal.emit(dataDict)
        except Exception as e:
            print(e)
            return

        self.close()
        

    