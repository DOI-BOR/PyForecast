from PyQt5 import QtWidgets, QtCore
from datetime import datetime
from resources.modules.Miscellaneous import  loggingAndErrors

import pandas as pd
import os
from collections import OrderedDict
import importlib

class UserDefinedDatasetDialog(QtWidgets.QDialog):
    """
    """

    returnDatasetSignal = QtCore.pyqtSignal(object)
    updatedDatasetSignal = QtCore.pyqtSignal(object)
    returnDataFromImportSignal = QtCore.pyqtSignal(object)

    def __init__(self, loadOptions=None, parent=None, datasetTypes=None, importDatasetFlag=False,):
        super(UserDefinedDatasetDialog, self).__init__()
        self.importDatasetFlag = importDatasetFlag
        if 'USER DEFINED' not in datasetTypes:
            datasetTypes.append('USER DEFINED')
        mainLayout = QtWidgets.QVBoxLayout()
        self.parent = parent
        self.setWindowTitle("Add or Edit Dataset")

        nameEditTitle = QtWidgets.QLabel("Dataset Name *")
        self.nameEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(nameEditTitle)
        hlayout.addWidget(self.nameEdit)
        mainLayout.addLayout(hlayout)

        idEditTitle = QtWidgets.QLabel("Dataset ID *")
        self.idEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(idEditTitle)
        hlayout.addWidget(self.idEdit)
        mainLayout.addLayout(hlayout)

        agencyEditTitle = QtWidgets.QLabel("Dataset Agency")
        self.agencyEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(agencyEditTitle)
        hlayout.addWidget(self.agencyEdit)
        mainLayout.addLayout(hlayout)

        typeTitle =  QtWidgets.QLabel("Dataset Type")
        self.typeDropDown = QtWidgets.QComboBox()
        self.typeDropDown.addItems(datasetTypes)
        self.typeDropDown.setCurrentText("USER DEFINED")
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(typeTitle)
        hlayout.addWidget(self.typeDropDown)
        mainLayout.addLayout(hlayout)

        paramEditTitle = QtWidgets.QLabel("Dataset Parameter *")
        self.paramEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(paramEditTitle)
        hlayout.addWidget(self.paramEdit)
        mainLayout.addLayout(hlayout)

        unitsEditTitle = QtWidgets.QLabel("Parameter Units *")
        self.unitsEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(unitsEditTitle)
        hlayout.addWidget(self.unitsEdit)
        mainLayout.addLayout(hlayout)

        resamplingMethodTitle = QtWidgets.QLabel("Resampling")
        self.resampleChooser = QtWidgets.QComboBox()
        self.resampleChooser.addItems(['average','sample','accumulation'])
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(resamplingMethodTitle)
        hlayout.addWidget(self.resampleChooser)
        mainLayout.addLayout(hlayout)

        latTitle = QtWidgets.QLabel("Dataset Latitude")
        self.latEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(latTitle)
        hlayout.addWidget(self.latEdit)
        mainLayout.addLayout(hlayout)

        longTitle = QtWidgets.QLabel("Dataset Longitude")
        self.longEdit = QtWidgets.QLineEdit()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(longTitle)
        hlayout.addWidget(self.longEdit)
        mainLayout.addLayout(hlayout)

        loaderSelectTitle = QtWidgets.QLabel("Select Loader")
        self.loaderDropDown = QtWidgets.QComboBox()
        self.defaultLoaders = os.listdir("resources/DataLoaders/")
        self.customLoaders = os.listdir("resources/DataLoaders/CustomDataLoaders/")
        if not importDatasetFlag:
            for i, file in enumerate(self.defaultLoaders + self.customLoaders):
                if file[-3:] == '.py':
                    self.loaderDropDown.addItem(file[:-3])

            self.loaderDropDown.currentTextChanged.connect(self.populateOptions)
        else:
            self.loaderDropDown.addItem("IMPORT")
            
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(loaderSelectTitle)
        hlayout.addWidget(self.loaderDropDown)
        mainLayout.addLayout(hlayout)

        decriptionTitle = QtWidgets.QLabel("Loader Description")
        self.description = QtWidgets.QTextEdit()
        self.description.setMinimumHeight(70)
        self.description.setReadOnly(True)
        self.description.setFontFamily('consolas')
        mainLayout.addWidget(decriptionTitle)
        mainLayout.addWidget(self.description)

        if not importDatasetFlag:
            self.optionsTable = OptionsTable()
            mainLayout.addWidget(self.optionsTable)
        else:
            self.loadFileButton = QtWidgets.QPushButton("Choose File")
            self.loadFileButton.clicked.connect(self.setFileName)
            self.fileNameText = QtWidgets.QLabel("No file chosen...")
            self.fileName = ""
            hlayout = QtWidgets.QHBoxLayout()
            hlayout.addWidget(self.loadFileButton)
            hlayout.addWidget(self.fileNameText)
            mainLayout.addLayout(hlayout)

        addButton = QtWidgets.QPushButton("Confirm")
        addButton.clicked.connect(self.packageAndReturn)
        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(addButton)
        hlayout.addWidget(cancelButton)
        mainLayout.addLayout(hlayout)

        self.setLayout(mainLayout)
        if not importDatasetFlag:
            self.populateOptions()
        else:
            self.setImportLayout()
        self.editFlag = False

        if isinstance(loadOptions, pd.Series):
            self.editFlag = True
            self.loadOptions(loadOptions)
        
        self.show()
        return

    def setImportLayout(self):
        self.description.setPlainText("""
Load data from a CSV or XLSX file. 
Data should be formatted in two columns
with headers similar to:

Date        |   Data Value
------------|--------------
2018-10-01  |   2342.2
2018-10-02  |   2345.3
...         |   ....""")
        return

    def setFileName(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Import File', 'C:\\', 'Flat Files (*.csv *.xlsx *.xls)')[0]
        if fname != '':
            self.fileName = fname
            self.fileNameText.setText(fname)
        else:
            return

        return

    def packageAndReturn(self):
        """
        """
        # Set up a dataframe to store data
        df = pd.DataFrame(index = [1])

        # Check to make sure required fields are entered
        if '' in [self.nameEdit.text(), self.idEdit.text(), self.paramEdit.text(), self.unitsEdit.text()]:
            loggingAndErrors.showErrorMessage(self, "Name, ID, Parameter, and Units are all required arguments")
            return 

        additionalOptionsDict = OrderedDict()
        df['DatasetExternalID'] = self.idEdit.text()
        df['DatasetName'] = self.nameEdit.text()
        df['DatasetType'] = self.typeDropDown.currentText()
        df['DatasetParameter'] = self.paramEdit.text()
        df['DatasetUnits'] = self.unitsEdit.text()
        df['DatasetAgency'] = self.agencyEdit.text()
        df['DatasetDataloader'] = self.loaderDropDown.currentText()
        df['DatasetLatitude'] = self.latEdit.text()
        df['DatasetLongitude'] = self.longEdit.text()
        df['DatasetDefaultResampling'] = self.resampleChooser.currentText()

        if not self.importDatasetFlag:
            for row in range(self.optionsTable.rowCount()):
                key = self.optionsTable.item(row, 0).text()
                value = self.optionsTable.item(row, 1).text()
                if key in self.parent.datasetTable.columns:
                    df[key] = value
                else:
                    additionalOptionsDict[key] = value
        else:
            if self.fileName == '':
                return
            additionalOptionsDict['Import Filename'] = self.fileName

        if additionalOptionsDict != {}:
            df['DatasetAdditionalOptions'] = [additionalOptionsDict]

        # Check to make sure the dataloader works with the provided data
        if not self.testLoader(df):
            return

        if self.editFlag:
            df.set_index(pd.Index([self.storedIDX]), inplace=True)
            self.updatedDatasetSignal.emit(df)
            self.close()
            return

        # Emit the dataset information
        self.returnDatasetSignal.emit(df)
        if self.importDatasetFlag:
            self.returnDataFromImportSignal.emit(self.datasetToReturnEventually)
        self.close()
        return

    def populateOptions(self):
        """
        Reads the docstring of the dataloader and adds that data to the loader description.
        It also reads the required subarguments to load into the table
        """
        # Clear the existing table
        self.optionsTable.setRowCount(0)

        # Clear the existing description
        self.description.clear()
        
        # Import the selected dataloader
        loader = self.loaderDropDown.currentText()
        if loader+'.py' in self.defaultLoaders:
            dataloader = importlib.import_module('resources.DataLoaders.'+ loader)
        else:
            dataloader = importlib.import_module('resources.DataLoaders.CustomDataLoaders.'+ loader)
        
        # Load the dataloaders description and options
        docstring = dataloader.dataLoader.__doc__
        description = docstring.split('DEFAULT OPTIONS')[0]
        description = description.replace('\n', '')
        options = docstring.split("DEFAULT OPTIONS")[1]

        self.description.setPlainText(description)

        for option in options.splitlines():
            if option.strip() == '':
                continue
            else:
                key = option.split(':')[0].strip()
                value = option.split(':')[1].strip()
                currentRow = self.optionsTable.rowCount()
                self.optionsTable.insertRow(currentRow)
                item = QtWidgets.QTableWidgetItem(key)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.optionsTable.setItem(currentRow, 0, item)
                self.optionsTable.setItem(currentRow, 1, QtWidgets.QTableWidgetItem(value))

        return

    def loadOptions(self, dataset):
        """
        Loads data from an existing dataset into the dialog for editing. 
        """
        self.storedIDX = dataset.name
        self.nameEdit.setText(str(dataset['DatasetName']))
        self.idEdit.setText(str(dataset['DatasetExternalID']))
        self.agencyEdit.setText(str(dataset['DatasetAgency']))
        self.paramEdit.setText(str(dataset['DatasetParameter']))
        self.unitsEdit.setText(str(dataset['DatasetUnits']))
        self.typeDropDown.setCurrentText(str(dataset['DatasetType']))
        self.loaderDropDown.setCurrentText(dataset['DatasetDataloader'])
        self.resampleChooser.setCurrentText(dataset['DatasetDefaultResampling'])
        self.latEdit.setText(str(dataset['DatasetLatitude']))
        self.longEdit.setText(str(dataset['DatasetLongitude']))
        
        if self.importDatasetFlag:
            self.fileNameText.setText(dataset['DatasetAdditionalOptions']['Import Filename'])
            return

        loader = self.loaderDropDown.currentText()
        if loader+'.py' in self.defaultLoaders:
            dataloader = importlib.import_module('resources.DataLoaders.'+ loader)
        else:
            dataloader = importlib.import_module('resources.DataLoaders.CustomDataLoaders.'+ loader)

        docstring = dataloader.dataLoader.__doc__
        description = docstring.split('DEFAULT OPTIONS')[0]
        description = description.replace('\n', '')
        options = docstring.split("DEFAULT OPTIONS")[1]

        self.description.setPlainText(description)

        self.optionsTable.setRowCount(0)

        for option in options.splitlines():
            if option.strip() == '':
                continue
            else:
                key = option.split(':')[0].strip()
                value = option.split(':')[1].strip()
                if key in self.parent.datasetTable.columns:
                    filledVal = dataset[key]
                else:
                    try:
                        filledVal = dataset['DatasetAdditionalOptions'][key]
                    except:
                        filledVal = value
                currentRow = self.optionsTable.rowCount()
                self.optionsTable.insertRow(currentRow)
                item = QtWidgets.QTableWidgetItem(key)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.optionsTable.setItem(currentRow, 0, item)
                self.optionsTable.setItem(currentRow, 1, QtWidgets.QTableWidgetItem(filledVal))
        return

    def testLoader(self, dataset):
        """
        Reads the dataset and tests the parameters with the specified dataloader to ensure that 
        the dataset can be properly downloaded or imported. 
        """
        if self.importDatasetFlag:
            fileName = dataset['DatasetAdditionalOptions'].iloc[0]['Import Filename']
            try:
                if fileName[-4:] == '.csv':
                    df = pd.read_csv(fileName, index_col=0, parse_dates=True)
                elif '.xls' in fileName[-5:]:
                    df = pd.read_excel(fileName, index_col=0, parse_dates=True)
                else:
                    return False
                self.datasetToReturnEventually = df
                return True
            except:
                return False


        # Attempt to import the loader
        try:
            loaderName = list(dataset['DatasetDataloader'])[0]
            if loaderName + '.py' in  self.defaultLoaders:
                loader = importlib.import_module('resources.DataLoaders.'+ loaderName)
            else:
                loader = importlib.import_module('resources.DataLoaders.CustomDataLoaders'+ loaderName)
        
        except Exception as E:
            loggingAndErrors.showErrorMessage(self, "Error: Could not initialize the selected dataloader. Please check the dataloader for errors.\n"+str(E))
            return False

        # Try and use the loader to load the last 10 days of data
        try:
            currentDate = pd.to_datetime(self.parent.userOptionsConfig['GENERAL']['application_datetime'])
            startDate = currentDate - pd.DateOffset(10)
            data = loader.dataLoader(dataset.loc[1], startDate, currentDate)
        except Exception as E:
            loggingAndErrors.showErrorMessage(self, "Error: Dataloader could not return data for the past 10 days. Check dataloader for errors.\n"+str(E))
            return False

        return True


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