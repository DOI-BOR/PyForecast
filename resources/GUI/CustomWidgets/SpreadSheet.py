"""
Script Name:    SpreadSheet.py

Description:    Implements Spreadsheet functionality for displaying
                data from the dataTable. 

                API:
                    SpreadsheetView:
                        model() = access to SpreadSheetModel
                        
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import pandas as pd
import os, copy
import sys
import numpy as np
from collections import OrderedDict
import subprocess
from resources.modules.Miscellaneous.DataProcessor import updateSingleComputedValue

class SpreadSheetModel(QtCore.QAbstractItemModel):
    """
    The SpeadsheetModel is a Qt model that works on top of PyForecast's
    DataTable to display data in the SpreadsheetView.
    """

    def __init__(self, parent = None):
        """
        """
        QtCore.QAbstractItemModel.__init__(self)
        self.parent = parent
        self.initialized = False
    
        return


    def loadDataIntoModel(self, dataTable, datasetTable):
        """
        Loads a PyForecast DataTable into the model.



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

        # Let the view know we're resetting the model
        self.beginResetModel()

        # Create references to the dataTable and the datasetTable
        self.dataTable = dataTable
        self.datasetTable = datasetTable

        # If the datasets are empty, we initialize an empty indexArray and return
        if self.dataTable.empty:
            self.indexArray = np.empty((0,0))
            self.datasetIndex = OrderedDict()
            self.initialized = True
            self.endResetModel()
            self.datasetIndexedList = []
            return
        
        # Create a list of id's that are composite datasets
        self.compDatasets = {}
        for i, equation in self.datasetTable['DatasetCompositeEquation'].dropna().iteritems():
            ids = equation.split('/')[1]
            ids = [int(j) for j in ids.split(',')]
            self.compDatasets[i] = {"Datasets":ids, "String":equation}
            

        # Create an index dictionary for dataset names (looks like: {100101: "Gibson Reservoir: Inflow", ...})
        self.datasetIndex = OrderedDict((id_,name) for id_, name in ((row[0], "{0}: {1}".format(row[1]['DatasetName'], row[1]['DatasetParameter'])) for row in self.datasetTable.iterrows()))
        
        # Create a list of the dataset numbers (looks like [100101, ...])
        self.datasetIndexedList = [item[0] for item in list(self.datasetIndex.items())]

        # Iterate through the datasets and chop up the dataset names for a prettier display in the table
        for id_ in list(self.datasetIndex):
            name = self.datasetIndex[id_]   # Get the full name
            words = name.split()            # split the name into words
            lines = []                      # create an array to store lines
            line = words[0]                 # Start the first line with the first word
            for word in words[1:]:          # Iterate over words and 
                if len(word) > 21:                # If the word is longer than 21 characters
                    lines.append(line)                  # finish the previous line
                    line = word                         # start a new line with the long word
                elif len(line + ' ' + word) > 22: # If the previous line plus the word goes over 22 characters
                    lines.append(line)                  # finish the previous line
                    line = word                         # start a new line with the long word
                else:
                    line = line + ' ' + word      # append the word to the current line    
            lines.append(line)  # add the last line
            self.datasetIndex[id_] = '\n'.join(lines) # join the lines by a newline character

        # Create an index array to associate model indices with data from the table (looks like: [[QModelIndex(...), QModelIndex(...),...],...])
        self.indexArray = np.array([[self.createIndex(i,j) for j, id_ in enumerate(self.datasetIndexedList)] for i, date in enumerate(self.dataTable.index.levels[0])])

        # Let the view know we're done resetting the model
        self.initialized = True
        self.endResetModel()

        return


    def index(self, row, column, parent = QtCore.QModelIndex()):
        """
        Return the index associated with the tableview's row and column
        """
        return self.indexArray[row][column]


    def columnCount(self, parent = QtCore.QModelIndex()):
        """
        If the model is initialized, return the number of columns
        in the index array. Otherwise, return 0
        """
        if self.initialized:
            return self.indexArray.shape[1]
        
        return 0


    def rowCount(self, parent = QtCore.QModelIndex()):
        """
        If the model is initialized, return the number of rows
        in the index array. Otherwise, return 0
        """
        if self.initialized:
            return self.indexArray.shape[0]
        
        return 0


    def data(self, index, role = QtCore.Qt.DisplayRole):
        """
        This function returns the data associated with the index if the 
        role is the displayRole. If the role is the BackgroundRole, the 
        funciton returns the color red for edited data and white for 
        un-edited data.
        """

        # Figure out the date and dataset id of the data requested
        date = self.dataTable.index.levels[0][index.row()]
        id_ = self.datasetIndexedList[index.column()]

        # Grab the associated data (if it exists) if the role is Display
        if role == QtCore.Qt.DisplayRole:
            if (date, id_) in self.dataTable.index:
                if self.dataTable.loc[(date, id_), 'EditFlag']:
                    val = QtCore.QVariant(str(self.dataTable.loc[(date, id_), 'Value']) + ' e')
                else:
                    val = QtCore.QVariant(str(self.dataTable.loc[(date, id_), 'Value']))
            else:
                val = QtCore.QVariant()
        
        # Paint the background color for edited data 
        elif role == QtCore.Qt.BackgroundRole:
            if (date, id_) in self.dataTable.index:
                if self.dataTable.loc[(date, id_), 'EditFlag']:
                    val = QtCore.QVariant(QtGui.QColor(228, 255, 181))
                else:
                    val = QtCore.QVariant(QtGui.QColor(255,255,255))
            else:
                val = QtCore.QVariant(QtGui.QColor(255,255,255))
        
        # If all else, return nothing
        else:
            val = QtCore.QVariant()

        return val


    def setData(self, index, value, role = QtCore.Qt.DisplayRole):
        """
        This function returns true when data is changed in the model. It returns
        false if the changed data is not noticable different from the previous version

        The dataChanged signal is emitted on success.
        """

        # Figure out the date and dataset id of the data changed
        date = self.dataTable.index.levels[0][index.row()]
        id_ = self.datasetIndexedList[index.column()]

        # Figure out if the value is numeric or not
        try:
            a = float(value)
            b = int(a)
            if a == b:
                value = b
            else:
                value = a

        except:
            return False
        
        # Update the value in the dataTable
        self.dataTable.loc[(date, id_), 'Value'] = value
        self.dataTable.loc[(date, id_), 'EditFlag'] = True
        
        # Check if this data change needs to update any other composite datasets
        for compDataset in self.compDatasets:
            if id_ in self.compDatasets[compDataset]["Datasets"]:
                self.dataTable.loc[(date, compDataset), 'Value'] = updateSingleComputedValue(self.dataTable, self.compDatasets[compDataset]["String"], date)
                self.dataTable.loc[(date, compDataset), 'EditFlag'] = True
                
        # Emit the dataChanged Signal
        self.dataChanged.emit(index,index)

        return True


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        """
        This function formats the row and column headers by checking the orientation
        and returning the correct QVariants from the data table
        """

        # Make sure the role is DisplayRole
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        
        # Check for horizontal orientation and return the column name if true
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            val = QtCore.QVariant(str(self.datasetIndex[self.datasetIndexedList[section]]))

        # Check for the vertical orientation and return the date if true
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            val = QtCore.QVariant(self.dataTable.index.levels[0][section].strftime('%Y-%m-%d') + ' ')
        
        else:
            val = QtCore.QVariant()

        return val


    def flags(self, index = QtCore.QModelIndex()):
        """
        Sets the universal flags for editing and selecting
        """

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable


class SpreadSheetView(QtWidgets.QTableView):
    """
    """

    def __init__(self, parent = None, *arg, **kwargs):
        """
        """
        QtWidgets.QTableView.__init__(self)
        self.parent = parent
        self.setModel(SpreadSheetModel(self))

        # Set up a highlight color for the spreadsheet
        if 'highlightColor' in list(kwargs.keys()):
            color = kwargs['highlightColor']
            if isinstance(color, tuple):
                self.highlightColor = QtGui.QColor(*color)
            else:
                self.highlightColor = QtGui.QColor(color)
        else:
            self.highlightColor = QtGui.QColor(0, 115, 150)

        colorCode = '#%02x%02x%02x' % (self.highlightColor.red(), self.highlightColor.green(), self.highlightColor.blue())
        
        # Set the display properties for the spreadsheet
        self.setStyleSheet(open(os.path.abspath('resources/GUI/stylesheets/spreadsheet.qss'), 'r').read().format(colorCode))
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)        
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)  

        # Set up a signal/slot to resize columns when the model is reset
        self.model().modelReset.connect(self.resizeColumns)

        # Set up a context menu event mapping for the table
        self.copyAction = QtWidgets.QAction('Copy')
        self.pasteAction = QtWidgets.QAction('Paste')
        self.interpAction = QtWidgets.QAction('Interpolate')
        self.excelAction = QtWidgets.QAction('Open in Excel')

        # Keyboard shortcuts
        self.copyShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self)
        self.copyShortcut.activated.connect(self.copySelectionToClipboard)
        self.pasteShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), self)
        self.pasteShortcut.activated.connect(self.pasteSelectionFromClipboard)

        # Connect signal/slots
        self.copyAction.triggered.connect(self.copySelectionToClipboard)
        self.pasteAction.triggered.connect(self.pasteSelectionFromClipboard)
        self.interpAction.triggered.connect(self.interpolateInSelection)
        self.excelAction.triggered.connect(self.openTableInExcel)

        return
    

    def openTableInExcel(self):
        """
        This function converts the datatable into a CSV file and
        attempts to open the file in the systems default spreadsheet application
        """
        # Convert the model datatable into a 2d, single index table
        excelTable = self.model().dataTable['Value'].unstack(-1)
        excelTable = pd.DataFrame(excelTable.values, columns=[self.model().datasetIndex[col].replace('\n',' ') for col in excelTable.columns], index=excelTable.index.to_flat_index())
        
        # Create a CSV file from the data
        tempFileName = "tmp"+str(int(np.random.random()*10000)) + '.csv'
        excelTable.to_csv(path_or_buf='resources/temp/'+tempFileName)
        
        # Attempt to open the excel file in the systems default spreadsheet application
        try:
            try:
                subprocess.check_call(['cmd','/c','start','resources/temp/'+tempFileName])
            except Exception as e:
                print(e)
                subprocess.check_call(['open','resources/temp/'+tempFileName])
        except:
            pass

        return


    def interpolateInSelection(self):
        """
        This function performs a linear interpolation between 2 items in 
        a 1-column selection. 
        """

        # Define a function to convert table data into NaN or float data
        def parseValue(value):
            if value == 'None' or value == 'nan' or value == None or value == np.nan:
                value = np.nan
            else:
                value = float(value.split()[0])
            return value
        
        # Get the selected cells
        selection = self.selectedIndexes()
        
        # Create a list of the data in the selected cells, also create a list of associated dates
        data_list = [parseValue(str(self.model().data(index).value())) for index in selection]
        date_list = [int(pd.to_datetime(str(self.model().headerData(index.row(), QtCore.Qt.Vertical).value())).to_datetime64()) for index in selection]
        
        # Determine the linear equation slope
        slope = (data_list[-1] - data_list[0]) / (date_list[-1] - date_list[0])
        
        # Iterate through the values and interpolate the new value from the linear equation
        for i, val in enumerate(data_list):

                newval = (date_list[i] - date_list[0])*slope + data_list[0]
                self.model().setData(selection[i], newval)

        return


    def pasteSelectionFromClipboard(self):
        """
        This function reads comma delimited data from the system clipboard and 
        inserts it into the model (thus adjusting the dataframe in the process)
        """

        # Get the clipboard object
        cb = QtWidgets.QApplication.clipboard()
        data = cb.text()
        formats = cb.mimeData().formats()

        # Get the selection from the table
        selection = self.selectedIndexes()

        # Check to make sure there is actually spreadsheet or text data in the clipboard
        if any(item in ['application/x-qt-windows-mime;value="XML Spreadsheet"', 'text/html', 'text/plain', 'application/x-qt-windows-mime;value="Csv"'] for item in formats):
            
            # Parse the data into spreadsheet rows and columns
            data = data.split('\n')[:-1]                # Parses rows
            data = [row.split('\t') for row in data]    # Parses columns

            # Create a variable to keep track of the current row and column
            current_row = selection[0].row()

            # Iterate through the data and set the model data accordingly
            for row in data:

                current_column = selection[0].column()
                
                for column in row:
                    index = self.model().index(current_row, current_column)
                    self.model().setData(index, column)
                    current_column += 1
                
                current_row += 1

        else:
            return


        return
        

    def copySelectionToClipboard(self):
        """
        This function sets the systems clipboard to the tab-delimited data
        in the current selection.
        """

        # Get the selected cells
        selection = self.selectedIndexes()
        
        # Intialize the text to be sent to the clipboard
        clipboard_text = ''

        # Initialize a variable to keep track of the rows
        previous_row = selection[0]

        # Iterate over the selection and append the data to the clipboard string
        for i, index in enumerate(selection):

            # Get the data from the model
            data = str(self.model().data(index).value())
            
            # Check if the data is empty (not nan; we want to show the nans)
            if data == "None":
                data = ''

            # Append data in the same row with tabs, and data in new rows with newlines
            if (index.row() != previous_row.row()):
                clipboard_text += '\n'
            elif i != 0:
                clipboard_text += '\t'
            clipboard_text += data
            previous_row = index

        # Set the clipboard text
        QtWidgets.QApplication.clipboard().clear()
        QtWidgets.QApplication.clipboard().setText(clipboard_text)

        return


    def contextMenuEvent(self, event):
        """
        This function reads the current selection
        and constructs the appropriate context menu pop up 
        based on the selection
        """

        # Create a menu
        self.menu = QtWidgets.QMenu(self)
        self.menu.setLayoutDirection(QtCore.Qt.RightToLeft)

        # Get the current selection
        selection = self.selectedIndexes()
        
        # Add the actions
        self.menu.addAction(self.copyAction)
        self.menu.addAction(self.pasteAction)
        self.menu.addAction(self.interpAction)
        self.menu.addAction(self.excelAction)

        # Check the selection to see if we should enable the interpolate action
        # We only enable for single-column, starting and ending with real numbers
        print("S: ", len(self.getSelectedColumns()))
        if len(self.getSelectedColumns()) == 1:
            print("S: ", self.model().data(selection[0]).value())
            if str(self.model().data(selection[0]).value()) not in ['None','nan','NaN']:
                print("S: ", self.model().data(selection[-1]).value())
                if str(self.model().data(selection[-1]).value()) not in ['None','nan','NaN']:
                    self.interpAction.setEnabled(True)
                else:
                    self.interpAction.setEnabled(False)
            else:
                self.interpAction.setEnabled(False)
        else:
            self.interpAction.setEnabled(False)
        
        # display the context menu at the mouse point
        self.menu.popup(self.mapToGlobal(event.pos()))

        return


    def resizeColumns(self):
        """
        This function resizes the table columns to be 150 pixels wide
        """
        [self.setColumnWidth(i, 150) for i in range(self.model().columnCount())]

        return


    def getSelectedColumns(self):
        """
        This function returns the selected dataset ID numbers 
        """
        cols = [i.column() for i in self.selectionModel().selection().indexes()]

        return list(set(cols))


class SpreadSheetModelOperations(QtCore.QAbstractItemModel):
    """
    The SpeadsheetModel is a Qt model that works on top of PyForecast's
    DataTable to display data in the SpreadsheetView.
    """

    updateSelectionSignal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        """
        """
        QtCore.QAbstractItemModel.__init__(self)
        # self.parent = parent
        self.initialized = False
        self.setParent(parent)

        return

    def loadDataIntoModel(self, datasetTable, datasetOperationsTable):
        """
        Loads a PyForecast DataTable into the model.



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

        # Let the view know we're resetting the model
        self.beginResetModel()

        # Create references to the dataTable and the datasetTable
        self.operationsTable = datasetOperationsTable
        self.datasetTable = datasetTable


        # If the datasets are empty, we initialize an empty indexArray and return
        self.indexArray = []
        self.datasetIndex = OrderedDict()
        self.initialized = True
        self.endResetModel()
        self.datasetIndexedList = []

        if len(self.operationsTable) == 0:
            return

        # Create an index dictionary for dataset names
        self.datasetIndex = OrderedDict((x, (self.operationsTable.index[x][0], self.operationsTable.index[x][1]))
                                 for x in range(0, len(self.operationsTable.index), 1))

        # Iterate through the datasets and chop up the dataset names for a prettier display in the table
        for id_ in list(self.datasetIndex):
            name = self.datasetTable.loc[self.datasetIndex[id_][0]]['DatasetName']  # Get the full name
            words = name.split()  # split the name into words
            lines = []  # create an array to store lines
            line = words[0]  # Start the first line with the first word
            for word in words[1:]:  # Iterate over words and
                if len(word) > 15:  # If the word is longer than 21 characters
                    lines.append(line)  # finish the previous line
                    line = word  # start a new line with the long word
                elif len(line + ' ' + word) > 16:  # If the previous line plus the word goes over 22 characters
                    lines.append(line)  # finish the previous line
                    line = word  # start a new line with the long word
                else:
                    line = line + ' ' + word  # append the word to the current line
            lines.append(line)  # add the last line
            self.datasetIndexedList.append('\n'.join(lines)) # join the lines by a newline character

        # Create an index array to layout the basic structure of the table. This is has the number of datasets as the
        # columns and the number of parameters, plus one, as the rows
        self.indexArray = [[self.createIndex(i, j) for j in range(0, len(self.operationsTable.index), 1)]
                            for i in range(0, len(self.operationsTable.columns) + 1, 1)]

        # Let the view know we're done resetting the model
        self.initialized = True
        self.endResetModel()

        return

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        If the model is initialized, return the number of columns
        in the index array. Otherwise, return 0
        """
        if self.initialized:
            if len(self.indexArray) > 0:
                return len(self.indexArray[0])

        return 0

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        If the model is initialized, return the number of rows
        in the index array. Otherwise, return 0
        """
        if self.initialized:
            return len(self.indexArray)

        return 0

    def index(self, row, column, parent = QtCore.QModelIndex()):
        """
        Return the index associated with the tableview's row and column
        """
        return self.indexArray[row][column]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        This function returns the data associated with the index if the 
        role is the displayRole. If the role is the ForegroundRole, the
        function returns the color red for undefined user options.
        """

        if role == QtCore.Qt.DisplayRole and len(self.operationsTable) > 0:
            # Grab the associated data (if it exists) if the role is Display
            if index.row() == 0:
                # Get the instance ID
                val = QtCore.QVariant(str(self.operationsTable.index[index.column()][0]) +
                                      "-" + str(self.operationsTable.index[index.column()][1]))

            else:
                # Get property values from the table
                val = QtCore.QVariant(str(self.operationsTable.iloc[index.column(), index.row() - 1]))
        # Color cells with None values
        elif role == QtCore.Qt.ForegroundRole and len(self.operationsTable) > 0 and index.row() >= 7:
            tempVal = str(self.operationsTable.iloc[index.column(), index.row() - 1])
            if tempVal == "None":
                val = QtGui.QBrush(QtCore.Qt.red)
            else:
                val = QtGui.QBrush(QtCore.Qt.darkGreen)

        else:
            val = QtCore.QVariant()

        return val




    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """
        This function formats the row and column headers by checking the orientation
        and returning the correct QVariants from the data table
        """

        replacementDict = {'FillMethod': " Fill Method", 'FillMaximumGap': " Fill Maximum Gap", 'FillOrder': " Fill Order",
                           'ExtendMethod': " Extend Method", 'ExtendDuration': " Extend Duration", 'ExtendFilter': " Extend Filter",
                           'AccumulationMethod': " Accumulation Method", 'AccumulationDateStart': " Accumulation Date Start",
                           'AccumulationDateStop': " Accumulation Date Stop", 'DatasetOperationsOptions': " Dataset Additional Options",
                           'AccumulationPeriod': " Accumulation Period", 'ForcingFlag': " Forcing Flag"}

        # Check for horizontal orientation and return the column name if true
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            # val = QtCore.QVariant(str(self.operationsTable.columns))
            val = QtCore.QVariant(self.datasetIndexedList[section])

        # Check for the vertical orientation and return the date if true
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if section == 0:
                val = QtCore.QVariant(' Instance ID')
            else:
                val = QtCore.QVariant(replacementDict[self.operationsTable.columns[section - 1]])

        else:
            val = QtCore.QVariant()

        return val

    def parent(self, index):
        """
        Returns an empty model index to allow selection

        """

        return QtCore.QModelIndex()


class SpreadSheetViewOperations(QtWidgets.QTableView):
    """
    """

    def __init__(self, datasetTable, datasetOperationsTable, parent=None):
        """
        """

        # Instantiate the inheirence variables
        QtWidgets.QTableView.__init__(self)
        self.parent = parent
        self.setModel(SpreadSheetModelOperations(self))

        # Set up a highlight color for the spreadsheet
        self.highlightColor = QtGui.QColor(0, 115, 150)
        colorCode = '#%02x%02x%02x' % (self.highlightColor.red(), self.highlightColor.green(), self.highlightColor.blue())

        # Set the display properties for the spreadsheet
        self.setStyleSheet(open(os.path.abspath('resources/GUI/stylesheets/spreadsheet.qss'), 'r').read().format(colorCode))
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        # Set the dataframes into the object
        self.datasets = datasetTable
        self.operations = datasetOperationsTable

        # Set up a signal/slot to resize columns when the model is reset
        self.model().modelReset.connect(self.resizeColumns)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)  # +++
        # self.clicked.connect(self._updateSelection)
        # self.model().updateSelectionSignal.connect(self._updateSelection)


    def resizeColumns(self):
        """
        This function resizes the table columns to be 150 pixels wide
        """
        [self.setColumnWidth(i, 150) for i in range(self.model().columnCount())]

        return

    def _updateSelection(self, test):

        # selectedBox = QtCore.QRect(row, column, 1, 1)
        self.clearSelection()
        self.setCurrentIndex(test)
        # self.setSelection(selectedBox, QtCore.QItemSelectionModel.Select)

    def clearTable(self):
        self.model().removeRows(0, self.model().rowCount())
        self.model().removeColumns(0, self.model().columnCount())


class SpreadSheetForecastEquations(QtWidgets.QWidget):
    """
    """

    def __init__(self, forecastEquationsTable, parent=None):
        """
        """

        # Instantiate the inheirence variables
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.view = QtWidgets.QTableView(self)

        # Set the dataframes into the object
        data = self.processData(forecastEquationsTable)
        self.equations = forecastEquationsTable

        # Create the combo box and set visibility to False
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setVisible(False)

        # Create the layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Set up a highlight color for the spreadsheet
        self.highlightColor = QtGui.QColor(0, 115, 150)
        colorCode = '#%02x%02x%02x' % (self.highlightColor.red(), self.highlightColor.green(), self.highlightColor.blue())

        # Set the display properties for the spreadsheet
        self.setStyleSheet(open(os.path.abspath('resources/GUI/stylesheets/spreadsheet.qss'), 'r').read().format(colorCode))
        self.view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.view.verticalHeader().setVisible(False)

        # Add the filtering into the plot
        self.model = QtGui.QStandardItemModel(10, len(data.columns))
        self.model.setHorizontalHeaderLabels(data.columns)
        self.model.setSortRole(QtCore.Qt.DisplayRole)
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)

        # Enable sorting
        self.view.setSortingEnabled(True)
        self.view.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # Enable the headers to stretch
        self.view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        # Set the header actions
        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.sectionDoubleClicked.connect(self.on_view_horizontalHeader_sectionClicked)

        # Set the size policies
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.view.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        #self.view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # Enable scrolling
        self.view.setAutoScroll(True)


    def loadDataIntoModel(self, data):
        # todo: doc string
            
        # Load the data
        data = self.processData(data)
        self.equations = data

        self.datasetIndexedList = []
        # Iterate through the datasets and chop up the dataset names for a prettier display in the table
        for id in range(0, len(self.equations), 1):
            # Get the current series
            series = self.equations.iloc[id]

            # Reduce the series to a string list
            seriesList = [str(x) for x in series.values]

            # Append into the data holder
            self.datasetIndexedList.append(seriesList)

        # Create an index array to layout the basic structure of the table. This is has the number of datasets as the
        # columns and the number of parameters, plus one, as the rows
        if len(self.datasetIndexedList) > 0:
            self.indexArray = [[self.model.createIndex(i, j) for j in range(0, len(self.datasetIndexedList[0]), 1)]
                               for i in range(0, len(self.datasetIndexedList), 1)]
        else:
            self.indexArray = [[self.model.createIndex(0, j) for j in range(0, len(self.equations.columns), 1)]]

        # Add the values into the columns
        for i in range(0, len(self.datasetIndexedList), 1):
            for j in range(0, len(self.datasetIndexedList[0]), 1):
                tableItem = QtGui.QStandardItem()
                if j == 0:
                    tableItem.setData(int(self.datasetIndexedList[i][j]), QtCore.Qt.DisplayRole)
                else:
                    tableItem.setData((self.datasetIndexedList[i][j]), QtCore.Qt.DisplayRole)
                self.model.setItem(i, j, tableItem)

        self.view.resizeColumnsToContents()


    def processData(self, dataTable):
        cols = [0, 2, 3, 4, 5, 6, 7, 11, 12, 13]
        data = dataTable.drop(dataTable.columns[cols], axis=1)
        if len(data) == 0:
            data['PIPE'] = ''
            data['EquationComment'] = ''
            data['EquationMethod'] = ''
            data['EquationSkill'] = ''
            data['EquationPredictors'] = ''
            data['Pre-ProcessingMethod'] = ''
            data['RegressionMethod'] = ''
            data['CrossValidation'] = 'No model runs found'
            data['ModelIndex'] = ''
        else:
            data[['PIPE', 'Pre-ProcessingMethod', 'RegressionMethod', 'CrossValidation']] = data[
                'EquationMethod'].str.split('/', expand=True)
            data['ModelIndex'] = data.index
            data = data.astype({"ModelIndex": int})
            # Search-replace model run option values
            for preProc in list(self.parent.parent.preProcessors):
                data.replace({'Pre-ProcessingMethod': {preProc:self.parent.parent.preProcessors[preProc]['name']}}, inplace=True)
            for regr in list(self.parent.parent.regressors):
                data.replace({'RegressionMethod': {regr:self.parent.parent.regressors[regr]['name']}}, inplace=True)
            for cVal in list(self.parent.parent.crossValidators):
                data.replace({'CrossValidation': {cVal:self.parent.parent.crossValidators[cVal]['name']}}, inplace=True)
            predCounts = list(map(str, list(data['EquationPredictors'].apply(len))))
            predLists = list(map(str, list(data['EquationPredictors'])))
            data['EquationPredictors'] = [i.zfill(2) + ' Predictors: ' + j for i, j in zip(predCounts, predLists)]
        data.drop('PIPE', axis=1, inplace=True)
        data.drop('EquationMethod', axis=1, inplace=True)
        data = data[data.columns[::-1]]
        return data
    
    
    def clearTable(self):
        nRows = self.view.model().rowCount()
        while nRows > 0:
            self.view.model().removeRow(nRows - 1)
            nRows = nRows - 1



    def selectionChanged(self, QItemSelection, QItemSelection_1):
        # todo: doc string
        # overrides the existing function
        a=1
        pass

    def resizeColumns(self):
        """
        This function resizes the table columns to be 150 pixels wide
        """
        [self.setColumnWidth(i, 150) for i in range(self.model().columnCount())]

        return

    @QtCore.pyqtSlot(int)
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        self.logicalIndex = logicalIndex
        self.menuValues = QtWidgets.QMenu(self)
        self.signalMapper = QtCore.QSignalMapper(self)

        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(self.logicalIndex)
        self.comboBox.blockSignals(True)

        valuesUnique = [self.model.item(row, self.logicalIndex).text()
                        for row in range(self.model.rowCount())
                        ]

        actionAll = QtWidgets.QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):
            action = QtWidgets.QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)
            action.triggered.connect(self.signalMapper.map)
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)

        headerPos = self.view.mapToGlobal(self.horizontalHeader.pos())

        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QtCore.QPoint(posX, posY))

    @QtCore.pyqtSlot()
    def on_actionAll_triggered(self):
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp("",
                                      QtCore.Qt.CaseInsensitive,
                                      QtCore.QRegExp.RegExp
                                      )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.pyqtSlot(int)
    def on_signalMapper_mapped(self, i):
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp(stringAction,
                                      QtCore.Qt.CaseSensitive,
                                      QtCore.QRegExp.FixedString
                                      )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        search = QtCore.QRegExp(text,
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp
                                )

        self.proxy.setFilterRegExp(search)

    @QtCore.pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)


class GenericTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(GenericTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return self._data.iloc[index.row(),index.column()]
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def rowCount(self, index):
        # The length of the outer list.
        return self._data.shape[0]

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return self._data.shape[1]


class GenericTableView(QtWidgets.QWidget):
    """
    """

    def __init__(self, inputDataTable, parent=None):
        """
        """

        # Instantiate the inheirence variables
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.view = QtWidgets.QTableView(self)

        # Set the dataframes into the object
        self.dataTable = inputDataTable

        # Create the layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Set up a highlight color for the spreadsheet
        self.highlightColor = QtGui.QColor(0, 115, 150)
        colorCode = '#%02x%02x%02x' % (self.highlightColor.red(), self.highlightColor.green(), self.highlightColor.blue())

        # Set the display properties for the spreadsheet
        self.setStyleSheet(open(os.path.abspath('resources/GUI/stylesheets/spreadsheet.qss'), 'r').read().format(colorCode))
        self.view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        #self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.view.horizontalHeader().setVisible(False)

        # Add the filtering into the plot
        self.model = QtGui.QStandardItemModel(10, len(self.dataTable.columns))
        self.model.setHorizontalHeaderLabels(self.dataTable.columns)
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)

        # Set the size policies
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.view.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        #self.view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # Enable scrolling
        self.view.setAutoScroll(True)


    def loadDataIntoModel(self, inputDataTable, rowHeaders=None, columnHeaders=None):
        # todo: doc string

        # Load the data
        self.dataTable = inputDataTable

        self.datasetIndexedList = []
        # Iterate through the datasets and chop up the dataset names for a prettier display in the table
        for id in range(0, len(self.dataTable), 1):
            # Get the current series
            series = self.dataTable.iloc[id]

            # Reduce the series to a string list
            seriesList = [str(x) for x in series.values]

            # Append into the data holder
            self.datasetIndexedList.append(seriesList)

        # Create an index array to layout the basic structure of the table. This is has the number of datasets as the
        # columns and the number of parameters, plus one, as the rows
        if len(self.datasetIndexedList) > 0:
            self.indexArray = [[self.model.createIndex(i, j) for j in range(0, len(self.datasetIndexedList[0]), 1)]
                               for i in range(0, len(self.datasetIndexedList), 1)]
        else:
            self.indexArray = [[self.model.createIndex(0, j) for j in range(0, len(self.dataTable.columns), 1)]]

        # Add the headers
        if columnHeaders is not None:
            self.model.setVerticalHeaderLabels([str(i) for i in columnHeaders])
        if rowHeaders is not None:
            self.model.setHorizontalHeaderLabels([str(i) for i in rowHeaders])

        # Add the values
        for i in range(0, len(self.datasetIndexedList), 1):
            for j in range(0, len(self.datasetIndexedList[0]), 1):
                val = self.datasetIndexedList[i][j]
                if self.isNumber(val):
                    val = "%.2f" % round(float(val), 2)
                self.model.setItem(i, j, QtGui.QStandardItem(val))

        # Finalize table
        self.syncTable()
        self.view.resizeColumnsToContents()


    def isNumber(self, n):
        is_number = True
        try:
            num = float(n)
            # check for "nan" floats
            is_number = num == num
        except:
            is_number = False
        return is_number


    def syncTable(self):
        # Remove extra rows from view
        viewRows = self.view.model().rowCount()
        tabRows = self.dataTable.shape[0]
        while viewRows > tabRows:
            self.view.model().removeRow(self.view.model().rowCount() - 1)
            viewRows = viewRows - 1
        # Remove extra columns from view
        viewCols = self.view.model().columnCount()
        tabCols = self.dataTable.shape[1]
        while viewCols > tabCols:
            self.view.model().removeColumn(self.view.model().columnCount() - 1)
            viewCols = viewCols - 1


    def selectionChanged(self, QItemSelection, QItemSelection_1):
        # todo: doc string
        # overrides the existing function
        a=1
        pass


    def resizeColumns(self):
        """
        This function resizes the table columns to be 150 pixels wide
        """
        [self.setColumnWidth(i, 150) for i in range(self.model().columnCount())]

        return





# FOR TESTING
#-----------------------------------------------
#-----------------------------------------------
if __name__ == '__main__':
    datasetTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                'DatasetUnits',             # e.g. CFS
                'DatasetDefaultResampling', # e.g. average 
                'DatasetDataloader',        # e.g. RCC_ACIS
                'DatasetHUC8',              # e.g. 10030104
                'DatasetLatitude',          # e.g. 44.352
                'DatasetLongitude',         # e.g. -112.324
                'DatasetElevation',         # e.g. 3133 (in ft)
                'DatasetPORStart',          # e.g. 1/24/1993
                'DatasetPOREnd',            # e.g. 1/22/2019
                'DatasetAdditionalOptions'
            ]
        ) 

    # The data table stores all of the raw data associated with the selected datasets.
    # Edited data is versioned as 1 and unedited data is versioned as 0
    dataTable = pd.DataFrame(
        index = pd.MultiIndex(
            levels=[[],[],],
            codes = [[],[],],
            names = [
                'Datetime',             # E.g. 1998-10-23
                'DatasetInternalID'     # E.g. 100302
                ]
        ),
        columns = [
            "Value",                    # E.g. 12.3, Nan, 0.33
            "EditFlag"                  # E.g. True, False -> NOTE: NOT IMPLEMENTED
            ],
        dtype=float
    )
    dataTable['EditFlag'] = dataTable['EditFlag'].astype(bool)

    datasetTable.loc[100101] = {'DatasetType': "STREAMGAGE",              # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID':"GIBR",        # e.g. "GIBR" or "06025500"
            'DatasetName':"GIBSON RESERVOIR, A RESERVOIR IN THE STATE OF MONTANA, IN THE SOVEREIGN NATION OF THE UNITED STATES",              # e.g. Gibson Reservoir
            'DatasetAgency':"USBR",            # e.g. USGS
            'DatasetParameter':"TEMPER",         # e.g. Temperature
            'DatasetUnits':"DEG",             # e.g. CFS
            'DatasetDefaultResampling':"ave", # e.g. average 
            'DatasetDataloader':"",        # e.g. RCC_ACIS
            'DatasetHUC8':"",              # e.g. 10030104
            'DatasetLatitude':"",          # e.g. 44.352
            'DatasetLongitude':"",         # e.g. -112.324
            'DatasetElevation':"",         # e.g. 3133 (in ft)
            'DatasetPORStart':"",          # e.g. 1/24/1993
            'DatasetPOREnd':"",            # e.g. 1/22/2019
            'DatasetAdditionalOptions':""}
        
    datasetTable.loc[100105] = {'DatasetType': "STREAMGAGE",              # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID':"FEF",        # e.g. "GIBR" or "06025500"
            'DatasetName':"FAKE RESERVOIR, FAKEOPOLIS",              # e.g. Gibson Reservoir
            'DatasetAgency':"USBR",            # e.g. USGS
            'DatasetParameter':"DFS",         # e.g. Temperature
            'DatasetUnits':"DEG",             # e.g. CFS
            'DatasetDefaultResampling':"ave", # e.g. average 
            'DatasetDataloader':"",        # e.g. RCC_ACIS
            'DatasetHUC8':"",              # e.g. 10030104
            'DatasetLatitude':"",          # e.g. 44.352
            'DatasetLongitude':"",         # e.g. -112.324
            'DatasetElevation':"",         # e.g. 3133 (in ft)
            'DatasetPORStart':"",          # e.g. 1/24/1993
            'DatasetPOREnd':"",            # e.g. 1/22/2019
            'DatasetAdditionalOptions':""}
    

    for date in pd.date_range('2019-9-25','2019-10-01', freq='D'):
        dataTable.loc[(date, 100101), 'Value'] = np.random.randint(100000)
        dataTable.loc[(date, 100101), 'EditFlag'] = False
        dataTable.loc[(date, 100105), 'Value'] = np.random.randint(100000)
        dataTable.loc[(date, 100105), 'EditFlag'] = False

    dataTable.loc[(pd.to_datetime('2018-09-05'), 100101), 'Value'] = np.random.randint(100000)
    dataTable.loc[(pd.to_datetime('2018-09-05'), 100101), 'EditFlag'] = False
    dataTable.loc[(pd.to_datetime('2018-09-03'), 100101), 'Value'] = np.nan
    dataTable.loc[(pd.to_datetime('2018-09-05'), 100101), 'EditFlag'] = False


    app = QtWidgets.QApplication(sys.argv)
    widg = SpreadSheetViewOperations()
    widg.model().loadDataIntoModel(dataTable, datasetTable)
    widg.show()
    
    sys.exit(app.exec_())