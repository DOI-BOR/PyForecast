"""
Script Name:        ScaledDataViewer.py

"""
import pandas as pd
import sys
import os
sys.path.append(os.getcwd())
import numpy as np
import re
from resources.GUI.CustomWidgets import PyQtGraphs, DatasetBoxView
from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui

class ScaledDataViewer(QtWidgets.QDialog):
    """
    """

    def __init__(self, dataTable, datasetTable):
        """
        """
        super(ScaledDataViewer, self).__init__()
        self.dataTable = dataTable
        self.datasetTable = datasetTable
        self.setupUI()

        self.freqDict = {
            "Years": "Y",
            "Months": "M",
            "Weeks": "W",
            "Days": "D"
        }

    def parseAndAddDataset(self):
        """
        Reads the entry and adds the dataset to the list of datasets
        """
        dataset = self.datasetSelectionList.currentText().split(":")
        firstDate = self.calenderStart.date()
        lastDate = self.calenderEnd.date()
        perI = self.durCounter.value()
        perS = self.durChooser.currentText()
        freqI = self.freqIntCounter.value()
        freqS = self.freqChooser.currentText()
        method = self.dsFunctionChooser.currentText()
        function = self.customFuncEditor.toPlainText() if method == "custom" else None

        def parser():

            dateString = str(firstDate.toString("yyyy-MM-dd"))

            if self.durChooser.isEnabled():
                pInt = perI
                pFreq = self.freqDict[perS]
            else:
                pInt = firstDate.daysTo(lastDate)
                pFreq = 'D'
            
            fInt = freqI
            fFreq = self.freqDict[freqS]
            
            return dateString, pInt, pFreq, fInt, fFreq

        resampleString = "R/{0}/P{1}{2}/F{3}{4}".format(*parser())

        title = dataset[0]
        match = re.search(r"\(\d\d\d\d\d\d\)", dataset[1])
        subtitle1 = r"<b>Parameter:</b> " + dataset[1][:match.span()[0]-1]
        subtitle2 = r"<b>Resampling:</b> " + resampleString
        id_ = dataset[1][match.span()[0]+1:match.span()[1]-1]
        subtitle3 = r"<b>Method:</b> " + method + "{0}".format(": "+ function[:11] + '...' if method == 'custom' else '')

        d = {"Title":title, "subtitle1": subtitle1, "subtitle2": subtitle2, "subtitle3":subtitle3, "ID":id_, "resampleString":resampleString, "ResampleMethod":method, "CustomFunction":function}

        self.datasetList.addAbstractEntry(d)
        

        return

    def removeDataset(self):
        """
        Removes the selected dataset from the list
        """

        return

    def setupUI(self):
        """
        """

        bigLayout = QtWidgets.QHBoxLayout()

        layout1 = QtWidgets.QVBoxLayout()

        title = QtWidgets.QLabel("Resampled Datasets")
        layout1.addWidget(title)

        self.datasetList = DatasetBoxView.DatasetBoxView()
        self.datasetList.setContextMenu(["remove"])
        layout1.addWidget(self.datasetList)

        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Plain)
        hline.setLineWidth(0)
        layout1.addWidget(hline)

        title = QtWidgets.QLabel("Add a Dataset")
        layout1.addWidget(title)

        label = QtWidgets.QLabel("Dataset")
        layout1.addWidget(label)

        self.datasetSelectionList = QtWidgets.QComboBox()
        self.datasetSelectionList.addItems(list(["{0}: {1} ({2})".format(row[1]['DatasetName'], row[1]['DatasetParameter'], row[0]) for row in self.datasetTable.iterrows()]))
        layout1.addWidget(self.datasetSelectionList)

        label = QtWidgets.QLabel("First Sample Period")
        layout1.addWidget(label)

        self.formatGroup = QtWidgets.QGroupBox("Period Selection Format")
        self.dateEdit = QtWidgets.QRadioButton("Date Selector")
        self.durEdit = QtWidgets.QRadioButton("Duration Selector")
        self.dateEdit.toggled.connect(lambda x: self.durEdit.setChecked(not x))
        
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.dateEdit)
        
        vbox.addStretch(1)
              
        self.calenderStart = QtWidgets.QDateEdit()
        self.calenderStart.setDisplayFormat("yyyy-MM-dd")
        
        self.calenderEnd = QtWidgets.QDateEdit()
        self.calenderEnd.setDate(self.calenderStart.date().addDays(1))
        self.calenderEnd.setDisplayFormat("yyyy-MM-dd")

        self.dateEdit.toggled.connect(lambda x: self.calenderStart.setEnabled(x))
        self.dateEdit.toggled.connect(lambda x: self.calenderEnd.setEnabled(x))
        
        self.calenderStart.dateChanged.connect(lambda x: self.calenderEnd.setMinimumDate(x.addDays(1)))
        self.calenderEnd.dateChanged.connect(lambda x: self.calenderStart.setMaximumDate(x.addDays(-1)))

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.calenderStart)
        hlayout.addWidget(self.calenderEnd)
        vbox.addLayout(hlayout)
        vbox.addWidget(self.durEdit)

        self.durCounter = QtWidgets.QSpinBox()
        self.durCounter.setEnabled(False)
        self.durCounter.setRange(1, 366)
        self.durChooser = QtWidgets.QComboBox()
        self.durChooser.setEnabled(False)
        self.durChooser.addItems(['Years', 'Months', 'Weeks', 'Days'])
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.durCounter)
        hlayout.addWidget(self.durChooser)
        vbox.addLayout(hlayout)

        self.durEdit.toggled.connect(self.durCounter.setEnabled)
        self.durEdit.toggled.connect(self.durChooser.setEnabled)

        self.dateEdit.setChecked(True)

        self.formatGroup.setLayout(vbox)

        layout1.addWidget(self.formatGroup)

        label = QtWidgets.QLabel("Sampling Frequency")
        layout1.addWidget(label)

        self.freqIntCounter = QtWidgets.QSpinBox()
        self.freqIntCounter.setRange(1, 366)
        self.freqChooser = QtWidgets.QComboBox()
        self.freqChooser.addItems(['Years', 'Months', 'Weeks', 'Days'])
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.freqIntCounter)
        hlayout.addWidget(self.freqChooser)
        layout1.addLayout(hlayout)

        label = QtWidgets.QLabel("Downsample Function")
        layout1.addWidget(label)

        self.dsFunctionChooser = QtWidgets.QComboBox()
        self.dsFunctionChooser.addItems(['accumulation', 'average', 'first', 'last', 'max', 'min', 'custom'])
        layout1.addWidget(self.dsFunctionChooser)

        self.customFuncEditor = QtWidgets.QPlainTextEdit()
        self.customFuncEditor.setPlaceholderText("Enter custom functions here (python/numpy[np] syntax)\n\nExample: np.max(x)/abs(x[0])")
        self.customFuncEditor.setEnabled(False)
        layout1.addWidget(self.customFuncEditor)

        self.dsFunctionChooser.currentTextChanged.connect(lambda text: self.customFuncEditor.setEnabled(True) if text == 'custom' else self.customFuncEditor.setEnabled(False))

        self.addButton = QtWidgets.QPushButton("Add Dataset")
        self.addButton.pressed.connect(self.parseAndAddDataset)
        layout1.addWidget(self.addButton)

        self.setLayout(layout1)

class resamplePlotViewer(PyQtGraphs)

if __name__ == "__main__":
    
    import pandas as pd
    
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    dataTable = pd.DataFrame()
    datasetTable = pd.DataFrame([["Test 1", "Param1"], ["Test 2", "Param2"]], columns=['DatasetName', 'DatasetParameter'], index=[100101, 100202])
    widg = ScaledDataViewer(dataTable, datasetTable)
    window.setCentralWidget(widg)
    window.show()
    sys.exit(app.exec_())


