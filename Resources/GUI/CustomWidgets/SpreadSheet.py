from PyQt5 import QtWidgets, QtCore, QtGui
import pandas as pd
import os
import numpy as np
from collections import OrderedDict

class SpreadSheetView(QtWidgets.QTableView):
    def __init__(self, parent=None, *args, **kwargs):
        QtWidgets.QTableView.__init__(self)
        self.parent=parent
        self.setModel(SpreadSheetModel(self))

        if 'highlightColor' in list(kwargs.keys()):
            color = kwargs['highlightColor']
            if isinstance(color, tuple):
                self.highlightColor = QtGui.QColor(*color)
            else:
                self.highlightColor = QtGui.QColor(color)
        else:
            self.highlightColor = QtGui.QColor(66, 134, 244)
        colorCode = '#%02x%02x%02x' % (self.highlightColor.red(), self.highlightColor.green(), self.highlightColor.blue())
        self.setStyleSheet(open(os.path.abspath('resources/GUI/stylesheets/spreadsheet.qss'), 'r').read().format(colorCode))
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)        
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)  

    def getSelectedColumns(self):
        cols = [self.model().datasetNamesList[i.column()] for i in self.selectedIndexes()]
        return list(set(cols))


class SpreadSheetModel(QtCore.QAbstractItemModel):

    changedDataSignal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self)
        self.parent=parent
        self.initialized = False

    def initialize_model_with_dataset(self, dataTable, datasetTable):
        """
        The dataTable looks like:
        datetime    datasetInternalID   value   editflag
        2018-10-01  102020              34.22   F
        2018-10-01  102321              122.33  T
        ...

        The datasetTable looks like:
        datasetID   datasetName ... ...
        102020      Big Tree SNOTEL
        102321      Horse River nr Red Willow
        ...
        """
        self.beginResetModel()
        self.dataTable = dataTable
        self.datasetTable = datasetTable
        self.datasetNames = OrderedDict((id_,name) for id_, name in ((row[0], row[1]['DatasetName']) for row in self.datasetTable.iterrows()))
        for id_ in list(self.datasetNames):
            name = self.datasetNames[id_]
            words = name.split()
            lines = []
            line = words[0]
            for word in words[1:]:
                if len(word) > 21:
                    lines.append(line)
                    line = word
                    continue
                if len(line + ' ' + word) > 22:
                    lines.append(line)
                    line = word
                    continue
                else:
                    line = line + ' ' + word
            lines.append(line)
            self.datasetNames[id_] = '\n'.join(lines)


                    
                    
        self.datasetNamesList = list(self.datasetNames)
        #self.indexArray = np.array([[self.createIndex(i,j,self.dataTable.loc[(date, id_),'Value']) if (date, id_) in self.dataTable.index else self.createIndex(i,j,np.nan) for j, id_ in enumerate(self.datasetNamesList)] for i, date in enumerate(self.dataTable.index.levels[0])])
        self.indexArray = np.array([[self.createIndex(i,j) for j, id_ in enumerate(self.datasetNamesList)] for i, date in enumerate(self.dataTable.index.levels[0])])
        self.initialized = True
        self.endResetModel()

        for i in range(self.columnCount()):
            self.parent.setColumnWidth(i, 150)
        
        return

    def index(self, row, column, parent = QtCore.QModelIndex()):
        return self.indexArray[row][column]

    
    def columnCount(self, parent=QtCore.QModelIndex()):
        if self.initialized:
            return self.indexArray.shape[1]
        return 0

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.initialized:
            return self.indexArray.shape[0]
        return 0
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        date = self.dataTable.index.levels[0][index.row()]
        id_ = self.datasetNamesList[index.column()]
        if role == QtCore.Qt.DisplayRole:
            if (date, id_) in self.dataTable.index:
                val = str(round(self.dataTable.loc[(date, id_), 'Value'], 3))
            else:
                val = QtCore.QVariant()
            # try:
            #     val = str(round(self.dataTable.loc[(date, id_), 'Value'], 3))
            # except Exception as e:
            #     print(self.dataTable.index.levels[1])
            #     print(e)
            #     print(id_)
            #     print(date)

        elif role == QtCore.Qt.BackgroundRole:
            if (date, id_) in self.dataTable.index:
                if self.dataTable.loc[(date, id_), 'EditFlag']:
                    val = QtCore.QVariant(QtGui.QColor(255, 178, 178))
                else:
                    val = QtCore.QVariant(QtGui.QColor(255,255,255))
            else:
                val = QtCore.QVariant(QtGui.QColor(255,255,255))
        else:
            val = QtCore.QVariant()
        return val

    def setData(self, index, value, role = QtCore.Qt.DisplayRole):
        date = self.dataTable.index.levels[0][index.row()]
        id_ = self.datasetNamesList[index.column()]
        oldValue = float(self.dataTable.loc[(date, id_),'Value'])
        
        try:
            try:
                value = int(value)
            except:
                value = float(value)
        except:
            value = np.nan
            return False
        if str(round(oldValue, 3)) == str(round(value,3)):
            return False
        self.changedDataSignal.emit([date, id_, oldValue, value])
        return True
        

    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            val = QtCore.QVariant(str(self.datasetNames[self.datasetNamesList[section]]))
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            val = QtCore.QVariant(self.dataTable.index.levels[0][section].strftime('%Y-%m-%d') + ' ')
        else:
            val = QtCore.QVariant()
        return val

    def flags(self, index = QtCore.QModelIndex()):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable 