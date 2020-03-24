"""
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import os
import numpy as np





class CompositeEquationEditor(QtWidgets.QListWidget):
    """
    This widget contains an editor for defining composite datasets. 
    The widget is a ListWidget.
    """

    def __init__(self, parent = None, initialEquation = ""):

        # Instantiate the widget and set a reference tot he parent
        QtWidgets.QListWidget.__init__(self, parent)
        self.parent = parent

        # Get a reference to the PyForecast dataset Table
        self.datasetTable = self.parent.parent.datasetTable

        # Intanstiate some list to keep track of the buttons and inputs
        self.addItemButtonList = []
        self.removeItemButtonList = []
        self.datasetList = []
        self.coefList = []
        self.lagList = []
        self.datasetNames = [(d['DatasetExternalID'] + ': ' + d['DatasetParameter'], d.name) for i, d in self.datasetTable.iterrows()]

        # Create icons for the buttons
        self.addIcon = QtGui.QIcon(QtGui.QPixmap('resources/GraphicalResources/icons/add_circle-24px.svg'))
        self.removeIcon = QtGui.QIcon(QtGui.QPixmap('resources/GraphicalResources/icons/remove_circle-24px.svg'))

        # Check if there is an initial equation, and load it. Otherwise, create an empty row
        if initialEquation == "" or np.isnan(initialEquation):
            self.addNewDatasetRow()
        
        else:
            self.processEquationIntoWidget(initialEquation)

        return


    def processEquationIntoWidget(self, equation = None):
        """
        Reads the equation from the argument and loads it
        into the widget.
        """

        # Parse the equation into sections
        equation = equation.split('/')
        datasets = [int(i) for i in equation[1].split(',')]
        coefs = [i for i in equation[2].split(',')]
        lags = [int(i) for i in equation[3].split(',')]

        # Load the equation into the widget
        for i, dataset in enumerate(datasets):
            idx = list(map(lambda x: x[1] == dataset, self.datasetNames)).index(True)
            self.addNewDatasetRow()
            self.datasetList[i].setCurrentIndex(idx)
            self.coefList[i].setText(coefs[i])
            self.lagList[i].setValue(lags[i])
        
        return


    def processEquationFromWidget(self):
        """
        Reads the widget lists and formats the current equation
        into a equation string
        """

        # Instantiate some lists to store equation information
        datasets = []
        coefs = []
        lags = []

        # Read the widget lists and get the specific values
        for i in range(len(self.datasetList)):
            datasets.append(self.datasetList[i].currentData(QtCore.Qt.UserRole))
            coefs.append(self.coefList[i].text())
            lags.append(self.lagList[i].value())

        # Put together the equation string
        datasetString = ','.join(map(str,datasets))
        coefString = ','.join(map(str,coefs))
        lagString = ','.join(map(str,lags))

        return 'C/{0}/{1}/{2}'.format(datasetString, coefString, lagString)


    def findClickedButton(self):
        """
        This function is called when an add or remove button is clicked. It 
        determines which button was clicked and acts appropriately.
        """

        addButtonIndex = -1
        removeButtonIndex = -1

        # Figure out if an 'add' button was clicked
        for i, button in enumerate(self.addItemButtonList):
            if button.isChecked():
                button.setChecked(False)
                addButtonIndex = i
                break
        
        # Figure out if a 'remove' button was clicked
        for i, button in enumerate(self.removeItemButtonList):
            if button.isChecked():
                button.setChecked(False)
                removeButtonIndex = i
                break

        # Do 'add' button stuff
        if addButtonIndex > -1:
            self.addNewDatasetRow()
        
        # Do 'remove' button stuff
        if removeButtonIndex > -1:
            if len(self.removeItemButtonList) == 1:
                return
            self.addItemButtonList.pop(removeButtonIndex)
            self.removeItemButtonList.pop(removeButtonIndex)
            self.datasetList.pop(removeButtonIndex)
            self.coefList.pop(removeButtonIndex)
            self.lagList.pop(removeButtonIndex)
            self.takeItem(removeButtonIndex)

        return


    def addNewDatasetRow(self):

        # Layout
        layout_ = QtWidgets.QHBoxLayout()

        # Elements
        self.addItemButtonList.append(QtWidgets.QPushButton(self.addIcon, 'Add Dataset'))
        self.addItemButtonList[-1].setCheckable(True)
        self.addItemButtonList[-1].clicked.connect(self.findClickedButton)
        self.removeItemButtonList.append(QtWidgets.QPushButton(self.removeIcon, 'Remove'))
        self.removeItemButtonList[-1].setCheckable(True)
        self.removeItemButtonList[-1].clicked.connect(self.findClickedButton)
        self.datasetList.append(QtWidgets.QComboBox())
        for subItem in self.datasetNames:
            self.datasetList[-1].addItem(subItem[0], subItem[1])
        self.coefList.append(QtWidgets.QLineEdit())
        self.coefList[-1].setText('1.0')
        self.coefList[-1].setMaximumWidth(70)
        self.lagList.append(QtWidgets.QSpinBox())
        self.lagList[-1].setSuffix(' days')
        self.lagList[-1].setValue(0)

        
        # Validators
        self.lagList[-1].setMaximum(0)
        self.lagList[-1].setMinimum(-10000)
        self.coefList[-1].setValidator(QtGui.QDoubleValidator())

        # Layout elements
        layout_.addWidget(self.addItemButtonList[-1])
        layout_.addWidget(self.removeItemButtonList[-1])
        layout_.addWidget(QtWidgets.QLabel("Dataset"))
        layout_.addWidget(self.datasetList[-1])
        layout_.addWidget(QtWidgets.QLabel("Scale"))
        layout_.addWidget(self.coefList[-1])
        layout_.addWidget(QtWidgets.QLabel("Lag"))
        layout_.addWidget(self.lagList[-1])

        # Create a new listwidget item
        item = QtWidgets.QListWidgetItem()
        item.setText("")
        widg = QtWidgets.QWidget()
        widg.setLayout(layout_)
        item.setSizeHint(QtCore.QSize(widg.sizeHint().width() + 20,widg.sizeHint().height() + 15))
        self.addItem(item)
        self.setItemWidget(item, widg)

        return





class EditorDialog(QtWidgets.QDialog):
    """
    """

    saveDatasetSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent = None, dataset = None):

        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle("User Defined Dataset")

        # Create a reference to the dataset
        self.dataset = dataset
        self.parent = parent

        # Set up the UI
        self.layoutUI()

        # Populate the combo boxes on the form, starting with the dataset type box
        datasetTypes = list(set(self.parent.searchableDatasetsTable['DatasetType'])) + list(set(self.parent.additionalDatasetsTable['DatasetType'])) + ['OTHER']
        self.typeEdit.addItems(datasetTypes)

        # Populate the dataloader edit
        for fname in os.listdir('resources/DataLoaders'):
            if '.py' in fname:
                self.loaderEdit.addItem(fname[:fname.index('.py')])
        self.loaderEdit.addItem('No Loader')

        # Connect Events on the Dialog
        self.compRadio.toggled.connect(self.processRadioButton)
        self.regRadio.toggled.connect(self.processRadioButton)
        self.importRadio.toggled.connect(self.processRadioButton)

        # Populate the UI with the dataset values
        self.populateForm(dataset)

        # If there is a import file, store the input file directory location
        self.fileLocation = os.path.dirname(self.dataset['DatasetImportFileName'])

        # Show the dialog
        self.show()

        # resize to fit contents
        self.resize(self.sizeHint().width() + 100, self.sizeHint().height())

        return

    def populateForm(self, dataset = None):
        """
        """

        if dataset['DatasetType'] == '':
            self.typeEdit.setCurrentText("OTHER")
        else:
            self.typeEdit.setCurrentText(dataset['DatasetType'])
        
        self.nameEdit.setText(      dataset["DatasetName"])
        self.agencyEdit.setText(    dataset['DatasetAgency'])
        self.paramEdit.setText(     dataset['DatasetParameter'])
        self.pcodeEdit.setText(     dataset['DatasetParameterCode'])
        self.unitEdit.setText(      dataset['DatasetUnits'])
        
        if dataset['DatasetDataloader'] == '':
            self.loaderEdit.setCurrentText('No Loader')
        else:
            self.loaderEdit.setCurrentText(dataset['DatasetDataloader'])
        
        self.hucEdit.setText(       dataset['DatasetHUC8'])
        self.latEdit.setText(       str(dataset['DatasetLatitude']))
        self.longEdit.setText(      str(dataset['DatasetLongitude']))
        self.elevEdit.setText(      str(dataset['DatasetElevation']))

        self.importFileButton.setEnabled(False)
        self.compEquationEditor.setEnabled(False)

        if dataset['DatasetCompositeEquation'] != '':
            self.compRadio.setChecked(True)
            self.loaderEdit.setCurrentText('No Loader')
            self.compEquationEditor.processEquationIntoWidget(dataset['DatasetCompositeEquation'])
        
        if dataset['DatasetImportFileName'] != '':
            self.importRadio.setChecked(True)
            self.loaderEdit.setCurrentText('No Loader')
            self.importFileName.setText(dataset['DatasetImportFileName'])

        return


    def saveAndReturnDataset(self):
        """
        """
        
        # Figure out the data source first and foremost
        if self.typeRadioGroup.checkedId() == -2:
            # Regular Dataloader
            self.dataset['DatasetCompositeEquation'] = np.nan
            self.dataset['DatasetImportFileName'] = np.nan
            self.dataset['DatasetDataloader'] = self.loaderEdit.currentText()

        elif self.typeRadioGroup.checkedId() == -3:
            # Composite Equation
            self.dataset['DatasetCompositeEquation'] = self.compEquationEditor.processEquationFromWidget()
            self.dataset['DatasetDataloader'] = np.nan
            self.dataset['DatasetImportFileName'] = np.nan

        elif self.typeRadioGroup.checkedId() == -4:
            # import file 
            self.dataset['DatasetImportFileName'] = self.importFileName.text()
            self.dataset['DatasetDataloader'] = 'IMPORTED_FILE'
            self.dataset['DatasetCompositeEquation'] = np.nan

        self.dataset['DatasetType'] = self.typeEdit.currentText()
        self.dataset['DatasetName'] = self.nameEdit.text()
        self.dataset['DatasetAgency'] = self.agencyEdit.text()
        self.dataset['DatasetParameter'] = self.paramEdit.text()
        self.dataset['DatasetParameterCode'] = self.pcodeEdit.text()
        self.dataset['DatasetUnits'] = self.unitEdit.text()
        self.dataset['DatasetHUC8'] = self.hucEdit.text()
        self.dataset['DatasetLatitude'] = float(self.latEdit.text())
        self.dataset['DatasetLongitude'] = float(self.longEdit.text())
        self.dataset['DatasetElevation'] = float(self.elevEdit.text())
        self.dataset['DatasetExternalID'] = str(self.idEdit.text())

        self.saveDatasetSignal.emit(self.dataset)

        self.close()

        return

    def processRadioButton(self, dummy):

        # Get the toggled button
        buttonIndex = self.typeRadioGroup.checkedId()

        if buttonIndex == -2:
            self.compEquationEditor.setEnabled(False)
            self.importFileButton.setEnabled(False)
            self.loaderEdit.setEnabled(True)
        
        if buttonIndex == -3:
            self.loaderEdit.setCurrentText('No Loader')
            self.loaderEdit.setEnabled(False)
            self.importFileButton.setEnabled(False)
            self.compEquationEditor.setEnabled(True)
        
        if buttonIndex == -4:
            self.loaderEdit.setCurrentText('No Loader')
            self.loaderEdit.setEnabled(False)
            self.importFileButton.setEnabled(True)
            self.compEquationEditor.setEnabled(False)

        return


    def fileSelectDialog(self, location = os.getcwd()):

        fname = self.importFileName.text()

        ret, _ = QtWidgets.QFileDialog().getOpenFileName(self, "Select Import File", location, "Flat Files (*.csv *.xlsx *.xls)")

        if ret != "":
            fname = ret
            self.importFileName.setText(fname)
        return 

    def layoutUI(self):

        # Layouts
        layout_form =       QtWidgets.QFormLayout()
        layout_buttons =    QtWidgets.QHBoxLayout()
        layout_radio =      QtWidgets.QFormLayout()
        layout_file =       QtWidgets.QHBoxLayout()

        # Form
        self.typeEdit =     QtWidgets.QComboBox()
        self.nameEdit =     QtWidgets.QLineEdit()
        self.idEdit =       QtWidgets.QLineEdit()
        self.agencyEdit =   QtWidgets.QLineEdit()
        self.paramEdit =    QtWidgets.QLineEdit()
        self.pcodeEdit =    QtWidgets.QLineEdit()
        self.unitEdit =     QtWidgets.QLineEdit()
        self.loaderEdit =   QtWidgets.QComboBox()
        self.hucEdit =      QtWidgets.QLineEdit()
        self.latEdit =      QtWidgets.QLineEdit()
        self.longEdit =     QtWidgets.QLineEdit()
        self.elevEdit =     QtWidgets.QLineEdit()
        
        # Type Radio
        self.typeRadioGroup =   QtWidgets.QButtonGroup()
        self.regRadio =         QtWidgets.QRadioButton()
        self.compRadio =        QtWidgets.QRadioButton()
        self.importRadio =      QtWidgets.QRadioButton()
        self.typeRadioGroup.addButton(self.regRadio)
        self.typeRadioGroup.addButton(self.compRadio)
        self.typeRadioGroup.addButton(self.importRadio)
        self.regRadio.setChecked(True)
        
        # Layout the radio buttons
        layout_radio.addRow("Regular Dataloader",   self.regRadio)
        layout_radio.addRow("Composite Dataset",    self.compRadio)
        layout_radio.addRow("File Import",          self.importRadio)

        # Composite Equation Editor
        self.compEquationEditor = CompositeEquationEditor(self)
        
        # Import files select widget
        self.importFileName =       QtWidgets.QLabel("No File Selected")
        self.importFileButton =     QtWidgets.QPushButton("Select File")
        self.importFileButton.clicked.connect(lambda x: self.fileSelectDialog(self.fileLocation))

        # Layout file select
        layout_file.addWidget(self.importFileName)
        layout_file.addWidget(self.importFileButton)

        # Dialog Buttons
        self.saveAndCloseButton =   QtWidgets.QPushButton("Save and Close")
        self.closeButton =          QtWidgets.QPushButton("Close")
        self.saveAndCloseButton.clicked.connect(self.saveAndReturnDataset)
        self.closeButton.clicked.connect(self.close)

        # Layout Dialog Buttons
        layout_buttons.addWidget(self.saveAndCloseButton)
        layout_buttons.addWidget(self.closeButton)

        # Layout the editor
        layout_form.addRow("Dataset Type",              self.typeEdit)
        layout_form.addRow("Dataset Name",              self.nameEdit)
        layout_form.addRow("Dataset ID",                self.idEdit)
        layout_form.addRow("Dataset Agency",            self.agencyEdit)
        layout_form.addRow("Dataset Parameter",         self.paramEdit)
        layout_form.addRow("Dataset Parameter Code",    self.pcodeEdit)
        layout_form.addRow("Dataset Units",             self.unitEdit)
        layout_form.addRow("Dataset Loader",            self.loaderEdit)
        layout_form.addRow("Dataset HUC8",              self.hucEdit)
        layout_form.addRow("Dataset Latitude",          self.latEdit)
        layout_form.addRow("Dataset Longitude",         self.longEdit)
        layout_form.addRow("Dataset Elevation",         self.elevEdit)
        layout_form.addRow("Source",                    layout_radio)
        layout_form.addRow("Composite Equation",        self.compEquationEditor)
        layout_form.addRow("Import File",               layout_file)
        layout_form.addRow(layout_buttons)

        # Assign the layout
        self.setLayout(layout_form)