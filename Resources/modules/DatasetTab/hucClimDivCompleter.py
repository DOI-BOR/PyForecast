"""
Script Name:    hucClimDivCompleter.py

Description:    This script provides a completer for the lineEdits on the
                datasets tab for entering in HUC and Climate Divisions. 
"""

from PyQt5 import QtWidgets, QtCore
import pandas as pd
import numpy as np

class completerModel(QtCore.QAbstractItemModel):
    def __init__(self, parent = None, data = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._data = data
        self.indexArray = np.array([[self.createIndex(i, j) for j in range(data.shape[1])] for i in range(data.size)])
        self.columns = self._data.columns
        self.index_ = self._data.index
        return
    def index(self, row, column, parent = QtCore.QModelIndex()):
        return self.indexArray[row][column]
    def rowCount(self, parent=None):
        return len(self._data.values)
    def columnCount(self, parent=None):
        return self._data.columns.size
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data[self.columns[index.column()]][self.index_[index.row()]]))
                    #self._data.values[index.row()][index.column()]))
        return QtCore.QVariant()

class hucClimDivCompleter(QtWidgets.QCompleter):
    def __init__(self, parent=None):
        QtWidgets.QCompleter.__init__(self, parent)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterMode(QtCore.Qt.MatchContains)
        self.setCompletionRole(QtCore.Qt.DisplayRole)
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        self.activated[str].connect(self.setCompleterSelection)
        
        return

    def setCompleterSelection(self, completionString):

        self.selectedDataset = self.model()._data.loc[self.model()._data['MatchColumn'] == completionString]
        return

    def setModelWithDataFrame(self, dataframe):
        dataframe['MatchColumn'] = '[' + dataframe['DatasetExternalID'] + '] ' + dataframe['DatasetName']
        self.model_ = completerModel(data = dataframe)
        self.setModel(self.model_)
        self.setCompletionColumn(9)
        return