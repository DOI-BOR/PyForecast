from PyQt5 import QtWidgets, QtCore

class viewerWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.datasetTable = parent.datasetTable
        self.datasetOperationsTable = parent.datasetOperationsTable
        self.dataTable = parent.dataTable
        self.modelRunsTable = parent.modelRunsTable
        self.forecastEquationsTable = parent.forecastEquationsTable
        self.savedForecastEquationsTable = parent.savedForecastEquationsTable
        self.forecastsTable = parent.forecastsTable

        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(datasetTableDisplay(self.datasetTable.copy()), "Dataset Table")
        tabWidget.addTab(datasetTableDisplay(self.datasetOperationsTable.copy()), "Dataset Operations Table")
        #tabWidget.addTab(datasetTableDisplay(self.dataTable), "Raw Data Table")
        tabWidget.addTab(datasetTableDisplay(self.modelRunsTable.copy()), "Defined Model Regression Table")
        #tabWidget.addTab(datasetTableDisplay(self.forecastEquationsTable), "Generated Forecast Models Table")
        tabWidget.addTab(datasetTableDisplay(self.savedForecastEquationsTable.copy()), "Saved Forecast Models Table")
        #tabWidget.addTab(datasetTableDisplay(self.forecastsTable), "Forecasts Table")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabWidget)
        self.setLayout(layout)
        self.setWindowTitle("Database Viewer")
        self.exec_()
        return


class datasetTableDisplay(QtWidgets.QWidget):

    def __init__(self, datasetTable):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout()
        dataTable = QtWidgets.QTableView()
        datasetTable.insert(0, "ID", list(datasetTable.index))
        model = PandasModel(datasetTable)
        dataTable.setModel(model)
        layout.addWidget(dataTable)
        self.setLayout(layout)
        return


"""
This model abstracts a QAbstractTableModel to display a 
pandas data frame. 
"""
class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._data.columns[section]
            if orientation == QtCore.Qt.Vertical:
                return self._data.index[section]

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.values[index.row()][index.column()]))
        return QtCore.QVariant()