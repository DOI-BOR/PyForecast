from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
from resources.modules.Miscellaneous import  loggingAndErrors, DataProcessor
from resources.GUI.CustomWidgets.hoverLabel import hoverButton


import pandas as pd
import numpy as np
import os
from collections import OrderedDict
import importlib

class compositeDatasetDialog(QtWidgets.QDialog):
    """
    """

    returnDatasetSignal = QtCore.pyqtSignal(object)

    def __init__(self, datasetTable, dataTable, predefinedOptions = None):
        super(compositeDatasetDialog, self).__init__()
        self.datasetTable = datasetTable

        if datasetTable.empty:
            print('No datasets')
            return

        self.dataTable = dataTable
        self.setupUI()
        self.loadPredifinedOptions(predefinedOptions)
        return

    def setupUI(self):
        layout = QtWidgets.QVBoxLayout()

        self.label0 = QtWidgets.QLabel("New Dataset Name:")
        self.nameEdit = QtWidgets.QLineEdit()

        layout.addWidget(self.label0)
        layout.addWidget(self.nameEdit)

        label1 = QtWidgets.QLabel("New Dataset Expression:")
        self.expressionFields = ExpressionFields(self.datasetTable)
        layout.addWidget(label1)
        layout.addWidget(self.expressionFields)

        label2 = QtWidgets.QLabel("+ Additional Dataset Descriptors: ")
        self.descriptorTable = QtWidgets.QTableWidget()
        self.descriptorTable.setColumnCount(2)
        self.descriptorTable.setRowCount(0)
        self.descriptorTable.horizontalHeader().hide()
        self.descriptorTable.verticalHeader().hide()
        for itemName in self.datasetTable.columns:
            if itemName == 'DatasetName' or itemName == 'DatasetAdditionalOptions' or itemName == 'DatasetDataLoader':
                continue
            item = QtWidgets.QTableWidgetItem(itemName)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.descriptorTable.insertRow(self.descriptorTable.rowCount())
            self.descriptorTable.setItem(self.descriptorTable.rowCount()-1, 0, item)
            self.descriptorTable.setItem(self.descriptorTable.rowCount()-1, 1, QtWidgets.QTableWidgetItem(''))
        self.descriptorTable.resizeColumnsToContents()
        self.descriptorTable.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(label2)
        layout.addWidget(self.descriptorTable)

        submitButton = QtWidgets.QPushButton("Submit")
        submitButton.clicked.connect(self.constructString)
        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Plain)
        hline.setLineWidth(0)
        layout.addWidget(hline)
        layout.addWidget(submitButton)
        self.setLayout(layout)

        return
    
    def loadPredifinedOptions(self, options):
        if not isinstance(options, pd.Series):
            self.predifinedIndex = -100
            return
        self.predifinedIndex = options.name

        comboString = options['DatasetAdditionalOptions']['CompositeString']
        
        def parser(idx, parseString):
            if idx == 0:
                return None
            elif idx == 1 or idx == 3:
                return [int(i) for i in parseString.split(',')]
            elif idx == 2:
                return [float(i) for i in parseString.split(',')]

        null, IDs, CFs, LGs = [parser(i, x) for i,x in enumerate(comboString.split('/'))]

        for i, idx in enumerate(IDs):
            dataset = self.datasetTable.loc[idx]
            NameString = "{0}: {1} ({2})".format(dataset['DatasetName'], dataset['DatasetParameter'], idx)
            if i == 0:
                self.expressionFields.elements[0].datasetName.setCurrentText(NameString)
                self.expressionFields.elements[0].coefEnter.setText(str(CFs[0]))
                self.expressionFields.elements[0].tshiftEnter.setValue(LGs[0])
            else:
                self.expressionFields.addElement()
                self.expressionFields.elements[i].datasetName.setCurrentText(NameString)
                self.expressionFields.elements[i].coefEnter.setText(str(CFs[i]))
                self.expressionFields.elements[i].tshiftEnter.setValue(LGs[i])
        
        self.nameEdit.setText(options['DatasetName'])

        for i in range(self.descriptorTable.rowCount()):
            key = self.descriptorTable.item(i, 0).text()
            value = options[key]
            self.descriptorTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(value)))


    def tableToDict(self):
        """
        """
        d = {}
        for row in range(self.descriptorTable.rowCount()):
            key = self.descriptorTable.item(row, 0).text()
            value = self.descriptorTable.item(row, 1).text()
            if value != '':
                d[key] = value
        return d

    def constructString(self):
        """
        """
        datasetName = self.nameEdit.text()
        if datasetName == '': 
            if '*' not in self.label0.text():
                self.label0.setText('*'+self.label0.text())
            return
        s = "C/{0}/{1}/{2}"
        ids = []
        coefs = []
        tsfts = []
        for element in self.expressionFields.elements:
            for subElementLabel, subElement in [(element.label0, element.datasetName), (element.label1, element.coefEnter), (element.label2, element.tshiftEnter)]:
                try:
                    if subElement == element.datasetName:
                        idx = subElement.currentIndex()
                        ids.append(str(element.datasetTable.iloc[idx].name))
                        subElementLabel.setText(subElementLabel.text().replace("*",""))
                    elif subElement == element.coefEnter:
                        coefs.append(subElement.text())
                        subElementLabel.setText(subElementLabel.text().replace("*",""))
                    else:
                        tsfts.append(str(subElement.value()))
                        subElementLabel.setText(subElementLabel.text().replace("*",""))
                
                except Exception as E:
                    print(E)
                    if not '*' in subElementLabel.text():
                        subElementLabel.setText('*' + subElementLabel.text())
                    return
        
        s = s.format(','.join(ids), ','.join(coefs), ','.join(tsfts))
        d = self.tableToDict()
        d['DatasetName'] = datasetName

        datasetEntry, dataEntry = DataProcessor.combinedDataSet(self.dataTable, self.datasetTable, s, d, self.predifinedIndex)
        self.returnDatasetSignal.emit([datasetEntry, dataEntry])
        self.close()
        return

class ExpressionFields(QtWidgets.QWidget):
    """
    """
    def __init__(self, datasetTable):
        self.datasetTable = datasetTable
        QtWidgets.QWidget.__init__(self)
        
        
        self.elements = []
        self.layout = QtWidgets.QVBoxLayout()
        self.label1 = QtWidgets.QLabel("Input Datasets")
        self.label1.setFixedHeight(20)
        self.addButton = hoverButton('resources/GraphicalResources/icons/plusIcon.png', 'resources/GraphicalResources/icons/plusIconDark.png')
        self.addButton.triggered.connect(self.addElement)
        self.addButton.setFixedHeight(20)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.label1)
        hlayout.addWidget(self.addButton)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(100, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.layout.addLayout(hlayout)
        self.addElement()
        self.setLayout(self.layout)

        return
    
    def addElement(self, b=False):
        ee = ExpressionElement()
        ee.destroySig.connect(self.removeElement)
        ee.setUpInputs(self.datasetTable)
        self.elements.append(ee)
        self.layout.addWidget(ee)
        self.layout.update()

    def removeElement(self, item):
        if len(self.elements) == 1:
            return
        item.hide()
        self.elements.remove(item)
        self.layout.update()

class ExpressionElement(QtWidgets.QWidget):
    """
    """
    destroySig = QtCore.pyqtSignal(object)
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setObjectName("ExElement")
        self.label0 = QtWidgets.QLabel("Dataset: ")
        self.label1 = QtWidgets.QLabel("Coefficient: ")
        self.label2 = QtWidgets.QLabel("Time Shift: ")
        self.datasetName = QtWidgets.QComboBox()
        self.coefEnter = QtWidgets.QLineEdit()
        self.coefEnter.setText('1.0')
        self.coefEnter.setValidator(QtGui.QDoubleValidator(-np.inf, np.inf, 5))
        self.tshiftEnter = QtWidgets.QSpinBox()
        self.tshiftEnter.setMinimum(-999)
        self.tshiftEnter.setMaximum(999)
        layout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.label0)
        hlayout.addWidget(self.datasetName)
        layout.addLayout(hlayout)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.label1)
        hlayout.addWidget(self.coefEnter)
        layout.addLayout(hlayout)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.label2)
        hlayout.addWidget(self.tshiftEnter)
        layout.addLayout(hlayout)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.removeAction = QtWidgets.QAction("Remove Dataset")
        self.addAction(self.removeAction)
        self.removeAction.triggered.connect(self.removeCurrentDataset)
        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Plain)
        hline.setLineWidth(0)
        layout.addWidget(hline)
        self.setLayout(layout)
    
    def removeCurrentDataset(self):
        self.destroySig.emit(self)
        #self.destroy()


    def setUpInputs(self, datasetTable):
        self.datasetTable = datasetTable
        self.datasetName.clear()
        for idx, dataset in self.datasetTable.iterrows():
            self.datasetName.addItem("{0}: {1} ({2})".format(dataset['DatasetName'], dataset['DatasetParameter'], idx))
        self.tshiftEnter.setValue(0)
