"""
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import os


class CompositeEquationEditor(QtWidgets.QListWidget):
    """
    This widget contains an editor for defining composite datasets. 
    The widget is a ListWidget.
    """

    def __init__(self, parent = None, initialEquation = ""):

        QtWidgets.QListWidget.__init__(self, parent)
        self.parent = parent
        self.datasetTable = self.parent.parent.datasetTable
        self.addItemButtonList = []
        self.removeItemButtonList = []
        self.datasetList = []
        self.coefList = []
        self.lagList = []
        self.datasetNames = [(d['DatasetExternalID'] + ': ' + d['DatasetParameter'], d.name) for i, d in self.datasetTable.iterrows()]

        self.addIcon = QtGui.QIcon(QtGui.QPixmap('resources/GraphicalResources/icons/add_circle-24px.svg'))
        self.removeIcon = QtGui.QIcon(QtGui.QPixmap('resources/GraphicalResources/icons/remove_circle-24px.svg'))

        self.addNewDatasetRow()
        
        return

    def processEquationIntoWidget(self, equation = None):

        equation = equation.split('/')
        datasets = [int(i) for i in equation[0].split(',')]
        coefs = [float(i) for i in equation[1].split(',')]
        lags = [int(i) for i in equation[2].split(',')]

        for i, dataset in enumerate(datasets):
            idx = list(map(lambda x: x[1] == dataset, self.datasetNames)).index(True)
            self.addNewDatasetRow()
            self.datasetList[i].setCurrentIndex(idx)
            self.coefList[i].setText(coefs[i])
            self.lagList[i].setValue(lags[i])
        
        return


    def processEquationFromWidget(self):

        datasets = []
        coefs = []
        lags = []

        for i in range(len(self.datasetList)):
            datasets.append(self.datasetList[i].data(QtCore.Qt.UserRole))
            coefs.append(self.coefList[i].text())
            lags.append(self.lagList[i].value())

        datasetString = ','.join(datasets)
        coefString = ','.join(coefs)
        lagString = ','.join(lags)

        return 'C/{0}/{1}/{2}'.format(datasetString, coefString, lagString)


    def findClickedButton(self):

        addButtonIndex = -1
        removeButtonIndex = -1

        for i, button in enumerate(self.addItemButtonList):
            if button.isChecked():
                button.setChecked(False)
                addButtonIndex = i
                break
        
        for i, button in enumerate(self.removeItemButtonList):
            if button.isChecked():
                button.setChecked(False)
                removeButtonIndex = i
                break

        if addButtonIndex > -1:
            self.addNewDatasetRow()
        
        if removeButtonIndex > -1:
            self.addItemButtonList.pop(removeButtonIndex)
            self.removeItemButtonList.pop(removeButtonIndex)
            self.datasetList.pop(removeButtonIndex)
            self.coefList.pop(removeButtonIndex)
            self.lagList.pop(removeButtonIndex)
            self.takeItem(removeButtonIndex)

    
    def addNewDatasetRow(self):

        # Layout
        layout = QtWidgets.QHBoxLayout()

        # Elements
        self.addItemButtonList.append(QtWidgets.QPushButton(self.addIcon, 'Add Dataset'))
        self.addItemButtonList[-1].clicked.connect(self.findClickedButton)
        self.removeItemButtonList.append(QtWidgets.QPushButton(self.removeIcon, 'Remove'))
        self.removeItemButtonList[-1].clicked.connect(self.findClickedButton)
        self.datasetList.append(QtWidgets.QComboBox())
        for subItem in self.datasetNames:
            self.datasetList[-1].addItem(subItem[0], subItem[1])
        self.coefList.append(QtWidgets.QLineEdit())
        self.lagList.append(QtWidgets.QSpinBox())
        self.lagList[-1].setSuffix(' days')
        
        # Validators
        self.lagList[-1].setMaximum(0)
        self.lagList[-1].setMinimum(-10000)
        self.coefList[-1].setValidator(QtGui.QDoubleValidator())

        # Layout elements
        layout.addWidget(self.addItemButtonList[-1])
        layout.addWidget(self.removeItemButtonList[-1])
        layout.addWidget(QtWidgets.QLabel("Dataset"))
        layout.addWidget(self.datasetList[-1])
        layout.addWidget(QtWidgets.QLabel("Scale"))
        layout.addWidget(self.coefList[-1])
        layout.addWidget(QtWidgets.QLabel("Lag"))
        layout.addWidget(self.lagList[-1])

        # Create a new listwidget item
        item = QtWidgets.QListWidgetItem()
        widg = QtWidgets.QWidget()
        widg.setLayout(layout)
        self.addItem(item)
        self.setItemWidget(item, widg)

        return


class EditorDialog(QtWidgets.QDialog):
    """
    """

    saveDatasetSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent = None, dataset = None):

        QtWidgets.QDialog.__init__(self, parent)

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
            self.loaderEdit.addItem(fname[:fname.index('.py')])
        self.loaderEdit.addItem('No Loader')

        # Populate the UI with the dataset values
        self.populateForm(dataset)
        
        # Connect Events on the Dialog
        self.typeRadioGroup.buttonClicked[int].connect(self.processRadioButton)

        # Show the dialog
        self.show()

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

        if dataset['DatasetCompositeEquation'] != '':
            self.compRadio.setChecked(True)
            self.loaderEdit.setCurrentText('No Loader')
        
        if dataset['DatasetImportFileName'] != '':
            self.importRadio.setChecked(True)
            self.loaderEdit.setCurrentText('No Loader')

        return

    def saveAndReturnDataset(self):
        """
        """

        return

    def processRadioButton(self, buttonIndex = None):

        if buttonIndex == 0:
            self.compEquationEditor.setEnabled(False)
            self.importFileButton.setEnabled(False)
            self.loaderEdit.setEnabled(True)
        
        if buttonIndex == 1:
            self.loaderEdit.setCurrentText('No Loader')
            self.loaderEdit.setEnabled(False)
            self.importFileButton.setEnabled(False)
            self.compEquationEditor.setEnabled(True)
        
        if buttonIndex == 2:
            self.loaderEdit.setCurrentText('No Loader')
            self.loaderEdit.setEnabled(False)
            self.importFileButton.setEnabled(True)
            self.compEquationEditor.setEnabled(False)

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

        # Layout file select
        layout_file.addWidget(self.importFileName)
        layout_file.addWidget(self.importFileButton)

        # Dialog Buttons
        self.saveAndCloseButton =   QtWidgets.QPushButton("Save and Close")
        self.closeButton =          QtWidgets.QPushButton("Close")

        # Layout Dialog Buttons
        layout_buttons.addWidget(self.saveAndCloseButton)
        layout_buttons.addWidget(self.closeButton)

        # Layout the editor
        layout_form.addRow("Dataset Type",              self.typeEdit)
        layout_form.addRow("Dataset Name",              self.nameEdit)
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