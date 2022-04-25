from PyQt5 import QtWidgets, QtCore
import pandas as pd

class conflictReviewDialog(QtWidgets.QDialog):

    datasetReturnSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, df=None, datasets=None):

        QtWidgets.QDialog.__init__(self)
        self.df = df
        self.returnData = df.copy()
        del self.returnData['Value_old']
        self.returnData.columns = ['Value','EditFlag']
        self.createConflictDataset(df, datasets)

        self.numDifferences = len(df)
        self.differencesResolved = 0

        self.setWindowTitle("Review Merge Conflicts")
        self.numDifferencesLabel = QtWidgets.QLabel("There are {0} conflicts between newly downloaded data and your edited data.".format(self.numDifferences))
        self.differencesResolvedLabel = QtWidgets.QLabel("{0} conflicts have been resolved. There are {1} remaining conflicts.".format(self.differencesResolved, self.numDifferences-self.differencesResolved))

        self.acceptAllButton = QtWidgets.QPushButton("Accept all changes")
        self.acceptAllRemainingButton = QtWidgets.QPushButton("Accept all remaining")
        self.rejectAllButton = QtWidgets.QPushButton("Reject all changes")
        self.rejectAllRemainingButton = QtWidgets.QPushButton("Reject all remaining")

        self.applyButton = QtWidgets.QPushButton("Apply")
        self.applyButton.pressed.connect(self.datasetReturnSignal.emit())
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelButton.pressed.connect(self.reject)

        self.exec_()

        return
    
    def createConflictDataset(self, dataframe, datasets):
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setColumnCount(4)
        datasetList = list(set(dataframe.index.get_level_values(1)))
        for ID in datasetList:
            dataset = datasets.loc[ID]
            name = dataset['DatasetName']
            param = dataset['DatasetParameter']
            unit = dataset['DatasetUnits']
            datasetItem = QtWidgets.QTreeWidgetItem()
            datasetItem.id = ID
            datasetItem.setText(0, name + ', ' + param + ', ' + unit)
            datasetItem.setFirstColumnSpanned(True)
            
            table = dataframe.xs(ID, level='DatasetInternalID',drop_level=False)
            for row in table.iterrows():
                tableItem = QtWidgets.QTreeWidgetItem()
                tableItem.date = row[0][0]
                tableItem.setText(1, row[0][0].strftime('%Y-%m-%d'))
                tableItem.setText(2, str(row[1]['Value_old']))
                tableItem.setCheckState(2, QtCore.Qt.Unchecked)
                tableItem.setText(3, str(row[1]['Value_new']))
                tableItem.setCheckState(3, QtCore.Qt.Unchecked)
                datasetItem.addChild(tableItem)
            self.treeWidget.addTopLevelItem(datasetItem)



class treeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self):
        QtWidgets.QTreeWidgetItem.__init__(self)
    def setData(self, col, role, value):
        retVal = QtWidgets.QTreeWidgetItem.setData(col,role,value)
