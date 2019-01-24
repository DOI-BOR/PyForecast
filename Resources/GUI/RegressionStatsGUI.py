from PyQt5 import QtWidgets, QtGui, QtCore
import os
import sys
import traceback
import time
import numpy as np
import pandas as pd
import subprocess

# Create a dialog window
class regrStatsWindow(QtWidgets.QDialog):
    """
    Dialog window to display regression statistics
    """
    def __init__(self, forecastDict):

        super(regrStatsWindow, self).__init__()
        self.forecastDict = forecastDict
        if "PC" in self.forecastDict['PrincCompData'].keys():
            self.initLayoutPCA()
            self.initData()
            self.setLayout(self.layout)
            self.setWindowTitle('View Principal Components')
        else:
            print(self.forecastDict)
            self.initLayoutZ()
            self.initDataZ()
            self.setLayout(self.layout)
            self.setWindowTitle("View Z-Score Steps")
        self.exec_()
    
    def initLayoutPCA(self):
        self.layout = QtWidgets.QFormLayout()
        self.PCTable = CustomTableView(menuFunctions=['COPY','OPEN'])
        self.eigValTable = CustomTableView(menuFunctions=['COPY','OPEN'])
        self.eigVecTable = CustomTableView(menuFunctions=['COPY','OPEN'])
        self.pcLabel = QtWidgets.QLabel()
        self.layout.addRow("PC's used in equation: ", self.pcLabel)
        self.layout.addRow("Princ. Comps: ", self.PCTable)
        self.layout.addRow("Eigenvalues: ", self.eigValTable)
        self.layout.addRow("Eigenvectors: ", self.eigVecTable)
    
    def initLayoutZ(self):
        self.layout = QtWidgets.QFormLayout()
        self.ZTable = CustomTableView(menuFunctions=['COPY','OPEN'])
        self.rTable = CustomTableView(menuFunctions=['COPY','OPEN'])
        self.CTable = CustomTableView(menuFunctions=['COPY','OPEN'])
        self.layout.addRow("Standardized Data:", self.ZTable)
        self.layout.addRow("R2 List:", self.rTable)
        self.layout.addRow("Composite Dataset:", self.CTable)

    def initDataZ(self):
        Z = self.forecastDict['PrincCompData']["Z"]
        R = self.forecastDict['PrincCompData']["R2-List"]
        C = self.forecastDict['PrincCompData']['Composite Set']
        prdids = self.forecastDict['prdIDs']

        zdf = pd.DataFrame(Z, columns = prdids)
        self.ZTable.createTableFromDataFrame(zdf)

        rdf = pd.DataFrame(R, columns = ['R2-Value'])
        rdf['PRDID'] = prdids
        self.rTable.createTableFromDataFrame(rdf)

        cdf = pd.DataFrame(C, columns = ['Composite Dataset'])
        self.CTable.createTableFromDataFrame(cdf)

    def initData(self):
        PC_data = self.forecastDict['PrincCompData']['PC']
        evecs = self.forecastDict['PrincCompData']['eigenVecs']
        evals = self.forecastDict['PrincCompData']['eigenVals']
        npcs = self.forecastDict['PrincCompData']['numPCs']
        prdids = self.forecastDict['prdIDs']

        print('vecs: ',evecs)
        print('vals: ',evals) 

        pcs = ['PC{0}'.format(i) for i in range(1,npcs+1)]
        self.pcLabel.setText(', '.join(pcs))

        header = []
        for i in range(PC_data.shape[1]):
            header.append('PC{0}'.format(i+1))
        pcdf = pd.DataFrame(PC_data, columns = header)
        print(pcdf)
        self.PCTable.createTableFromDataFrame(pcdf)

        #header = []
        #for i in range(evals.shape[0]):
        #    header.append('PC{0}'.format(i+1))
        valdf = pd.DataFrame(evals.reshape(1,-1), columns=header)
        self.eigValTable.createTableFromDataFrame(valdf)

       
        vecdf = pd.DataFrame(evecs, columns = header, index=prdids)
        self.eigVecTable.createTableFromDataFrame(vecdf) 







class CustomTableView(QtWidgets.QTableWidget):

    deletedRowEmission = QtCore.pyqtSignal(list)
    deletedColumnEmission = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, rowLock = False, colLock = False, cols = 0, rows = 0, headers = [''], menuFunctions = [''], readOnly = False, dragFrom=False):

        # Initialize the tableview with options
        QtWidgets.QTableWidget.__init__(self)
        self.setColumnCount(cols)
        self.setRowCount(rows)
        self.readOnly = readOnly
        if rowLock:
            self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        elif colLock:
            pass
            #self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectColumns)
        else:
            pass
        if dragFrom:
            self.setDragEnabled(True)

        if readOnly:
            self.readOnly = True
        else:
            self.readOnly = False



        #self.setGridStyle(QtCore.Qt.DotLine)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.verticalHeader().setVisible(False)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.setHorizontalHeaderLabels(headers)
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)


        # Create a context menu for the tableview
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        if 'COPY' in menuFunctions:
            self.copyAction = QtWidgets.QAction("Copy selection", None)
            self.addAction(self.copyAction)
            self.copyAction.triggered.connect(self.copyFromTable)
        
        if 'OPEN' in menuFunctions:
            self.openAction = QtWidgets.QAction("Open in spreadsheet", None)
            self.addAction(self.openAction)
            self.openAction.triggered.connect(self.openInSpreadsheet)
        
        if 'DELETEROW' in menuFunctions:
            self.deleteRowAction = QtWidgets.QAction("Delete table row", None)
            self.addAction(self.deleteRowAction)
            self.deleteRowAction.triggered.connect(lambda: self.deleteFromTable('row'))

        if 'DELETECOL' in menuFunctions:
            self.deleteColAction = QtWidgets.QAction("Delete table column", None)
            self.addAction(self.deleteColAction)
            self.deleteColAction.triggered.connect(lambda: self.deleteFromTable('col'))
        
        if 'SAVEFCST' in menuFunctions:
            self.saveFcstAction = QtWidgets.QAction("Save Forecast", None)
            self.addAction(self.saveFcstAction)
        
        if "REGSTAT" in menuFunctions:
            self.regStatAction = QtWidgets.QAction("View Principal Components", None)
            self.addAction(self.regStatAction)




    # Define a function to copy items from the table
    def copyFromTable(self):

        # Set up and clear the clipboard
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode = cb.Clipboard)
        prev_row = -1

        # Get the selected items
        items = self.selectedItems()

        # Initialize a string to store the copied items
        clip_string = ""

        # Loop through items and add them to the clipboard
        for i, item in enumerate(items):

            if i == 0:
                clip_string += item.text()
                prev_row = item.row()
                continue
            
            if item.row() == prev_row:
                clip_string += '\t'
                clip_string += item.text()
                prev_row = item.row()
            
            else:
                clip_string += '\n'
                clip_string += item.text()
                prev_row = item.row()
        
        # Set the clipboard with the clip_text
        cb.setText(clip_string, mode = cb.Clipboard)

        return clip_string


    # Define a function to convert a table to a dataframe
    def toDataFrame(self):

        # get the number of rows and column, and the header
        rows = self.rowCount()
        cols = self.columnCount()
        headers = [self.horizontalHeaderItem(i).text() for i in range(cols)]

        # Convert to a stringIO csv file
        if rows != 0:
            self.selectAll()

            from io import StringIO
            rawString = self.copyFromTable()
            rawString = StringIO(rawString)

            df = pd.read_csv(rawString, sep="\t", names = headers, dtype = str)

            # If the first column contains datetimes, use that as the index
            try:
                df.set_index(pd.DatetimeIndex(pd.to_datetime(df[df.columns[0]])), inplace = True)
                del df[df.columns[0]]
                return df
            except:
                print('couldnt convert times')
                return df
        
        else:
            return pd.DataFrame()


    # Define a function to add a dataframe to the table
    def createTableFromDataFrame(self, data):

        # Clear any existing data
        self.setRowCount(0)
        self.setColumnCount(0)

        # Intitialize the dimensions and headers
        self.setRowCount(len(data.index))
        self.setColumnCount(len(data.columns)+1)

        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem(str("...")))
        for i in range(len(data.columns)):
            colHeader = data.columns[i].split('|')
            name = colHeader[0]
            self.setHorizontalHeaderItem(i+1, QtWidgets.QTableWidgetItem(str(
                "{0}".format(name)
            )))

        # Iterate through the dataframe and set each item
        for i in range(len(data.index)):
            item = QtWidgets.QTableWidgetItem(str(data.index[i])[0:10])
            self.setItem(i, 0, item)
            for j in range(len(data.columns)):    
                col = list(data.columns)[j]
                val = data[col].iloc[i]
                item = QtWidgets.QTableWidgetItem(str(val))
                if self.readOnly:
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j+1, item)
        #self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        self.resizeColumnsToContents()
    
    # Open in spreadsheet
    def openInSpreadsheet(self):
        data = self.toDataFrame()
        tempFileName = "tmp"+str(int(np.random.random()*10000)) + '.csv'
        data.to_csv(path_or_buf='Resources/tempFiles/'+tempFileName)
        try:
            try:
                subprocess.check_call(['cmd','/c','start','Resources/tempFiles/'+tempFileName])
            except Exception as e:
                print(e)
                subprocess.check_call(['open','Resources/tempFiles/'+tempfilename])
        except:
            pass