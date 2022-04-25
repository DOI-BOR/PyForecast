# Script Name:      editDataLoaders.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      Provides the code, layout, and functionality for the
#                   "edit dataloaders" dialog window.

# Import Libraries
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import sys
import traceback
import time
import numpy as np
from Resources.Functions.SyntaxHighlighter import syntaxHighlighter
import importlib

# Create a custom table widget to handle the list of custom datloaders
class dataloaderTable(QtWidgets.QTableWidget):

    # Runs when the table is first initialized by the application
    def __init__(self,parent=None):

        QtWidgets.QTableWidget.__init__(self)

        # Set the table properties
        self.setColumnCount(3)
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["Loader Name","Last Modified","Size"])
        self.setShowGrid(True)
        self.setGridStyle(QtCore.Qt.DotLine)
        self.setCornerButtonEnabled(False)
        self.verticalHeader().setVisible(False)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        self.populate()

    # Function that clears and re=populates the table with all the custom dataloaders
    def populate(self):

        print('attempting to populate table')

        # Clear the existing table
        self.setRowCount(0)

        # Get the list of custom dataloaders
        self.dataloaderList = os.listdir('Resources/DataLoaders/Custom')
        print(self.dataloaderList)
        j = -1

        # iteratively add the files to the table
        for i, fileName in enumerate(self.dataloaderList):
            print(fileName)

            # Check to ensure it's a python file
            if fileName[-3:] != '.py':
                continue
            else:
                j = j + 1

            # Add a new row to the table at position i
            self.insertRow(j)

            # Get the file information
            fileInfo = os.stat('Resources/DataLoaders/Custom/'+fileName)
            
            name = fileName[:-3]
            lastModified = time.strftime("%Y-%m-%d", time.localtime(fileInfo[9]))
            size = str(round(fileInfo[6]/1000, 2)) + ' kB'

            # Populate the table
            self.setItem(j, 0, QtWidgets.QTableWidgetItem(name)) 
            self.setItem(j, 1, QtWidgets.QTableWidgetItem(lastModified))
            self.setItem(j, 2, QtWidgets.QTableWidgetItem(size))

        # Stretch last section
        header = self.horizontalHeader()
        header.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
    
# Create a dialog window
class dataloaderDialog(QtWidgets.QDialog):
    
    def __init__(self):

        super(dataloaderDialog, self).__init__()
        mainWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout()

        # Horizontal layout with table and buttons
        hlayout = QtWidgets.QHBoxLayout()
        self.fileTable = dataloaderTable()
        hlayout.addWidget(self.fileTable)
        vlayout = QtWidgets.QVBoxLayout()
        self.editButton = QtWidgets.QPushButton("Edit Selected")
        self.deleteButton = QtWidgets.QPushButton("Delete Selected")
        self.addButton = QtWidgets.QPushButton("Add New Loader")
        vlayout.addWidget(self.editButton)
        vlayout.addWidget(self.deleteButton)
        vlayout.addWidget(self.addButton)
        hlayout.addLayout(vlayout)

        mainLayout.addLayout(hlayout)

        line1 = QtWidgets.QFrame()
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Plain)
        mainLayout.addWidget(line1)

        # Dataloader edit section
        hlayout = QtWidgets.QHBoxLayout()
        nameEditTitle = QtWidgets.QLabel("Dataloader Name")
        self.nameEdit = QtWidgets.QLineEdit()
        self.nameEdit.setReadOnly(True)
        self.saveButton = QtWidgets.QPushButton("Save Changes")
        self.cancelButton = QtWidgets.QPushButton("Cancel Changes")
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        hlayout.addWidget(nameEditTitle)
        hlayout.addWidget(self.nameEdit)
        hlayout.addWidget(self.saveButton)
        hlayout.addWidget(self.cancelButton)
        mainLayout.addLayout(hlayout)

        # Text editor for script writing
        #self.editor = QtWidgets.QPlainTextEdit()
        self.editor = syntaxHighlighter.CustomCodeEditor()
        self.editor.setStyleSheet("""QPlainTextEdit{
            font-family:'Consolas'; 
            color: #ffffff; 
            background-color: #33363a;}""")
        highlight = syntaxHighlighter.PythonHighlighter(self.editor.document())
        self.editor.setReadOnly(True)
        self.editor.setMinimumHeight(400)
        self.editor.setTabStopWidth(15)

        mainLayout.addWidget(self.editor)
        mainWidget.setLayout(mainLayout)

        # INITIAL SET-UP
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(mainWidget)

        self.setLayout(layout)
        self.setWindowTitle("Add New Dataloader")
        self.setMinimumWidth(600)

        self.connectEvents()

        self.exec_()

    # Define a function to connect button presses to other functions
    def connectEvents(self):

        self.editButton.pressed.connect(self.editLoader)
        self.deleteButton.pressed.connect(self.deleteLoader)
        self.addButton.pressed.connect(self.addLoader)
        self.saveButton.pressed.connect(self.saveChanges)
        self.cancelButton.pressed.connect(self.cancelChanges)

    # Define a function to edit a current dataloader
    def editLoader(self):

        # ENsure that there is a selection
        items = self.fileTable.selectedItems()
        if items == []:
            return

        # Get the current selection from the table
        name = items[0].text()
       
        # Set the file name edit and enable editing
        self.nameEdit.setText(name)
        self.nameEdit.setReadOnly(False)

        # Open the python file and read the contents
        with open('Resources/DataLoaders/Custom/'+name+'.py','r') as readfile:
            scriptText = readfile.read()

        # Set the editor contents
        self.editor.setPlainText(scriptText)

        # allow editing
        self.editor.setReadOnly(False)

        # Don't let users delete or edit or add until saved or canceled
        self.addButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

    # Define a function to delete a dataloader
    def deleteLoader(self):

        # ENsure that there is a selection
        items = self.fileTable.selectedItems()
        if items == []:
            return

        # Get the current selection from the table
        name = items[0].text()

        # Bring up a dialog box and ask the user if they are sure they want to delete
        button = QtWidgets.QMessageBox.question(self, 'Delete loader', 'Are you sure you want to delete the "{0}" loader?'.format(name), QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if button != QtWidgets.QMessageBox.Ok:
            return
        
        # Delete the loader
        os.remove('Resources/DataLoaders/Custom/'+name+'.py')

        # Repopulate the table
        self.fileTable.populate()
    
    # Function to add a new dataloader
    def addLoader(self):

        # Initially set the name of the new loader to UntitledLoader
        name = 'untitledLoader'

        # Add a row to the filetable
        self.fileTable.insertRow(self.fileTable.rowCount())
        self.fileTable.setItem(self.fileTable.rowCount()-1, 0, QtWidgets.QTableWidgetItem("untitledLoader*"))
        self.fileTable.setItem(self.fileTable.rowCount()-1, 1, QtWidgets.QTableWidgetItem("*"))
        self.fileTable.setItem(self.fileTable.rowCount()-1, 2, QtWidgets.QTableWidgetItem("*"))

        # Set the nameEdit
        self.nameEdit.setText("untitledLoader")
        self.nameEdit.setReadOnly(False)

        # Set the initial code for a new loader
        self.editor.setPlainText("""
# Loader name:        <insert name here>
# Loader author:      <your name>
# Loader created:     {0}
 
# WRITE LOADER BELOW ---------------------""".format(time.strftime('%Y-%m-%d',time.localtime(time.time()))))

        # Allow editing
        self.editor.setReadOnly(False)

        # Don't let users delete or edit or add until saved or canceled
        self.addButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)


    # Function to save the changes to a custom dataloader
    def saveChanges(self):

        randomNum = str(int(np.random.rand()*100000))

        # First, check to make sure there are no errors in the loader
        # We'll create a temporary file and try and import it

        fileName = 'tempLoader{0}.py'.format(randomNum)

        tempWriteFile =  open('Resources/tempFiles/'+fileName,'w')
        tempWriteFile.write(self.editor.toPlainText())
        tempWriteFile.close()

        try:
            importlib.invalidate_caches() # Clear out any caches
            mod = importlib.import_module('Resources.tempFiles.'+fileName[:-3]) # Attempt to import
            testInfoFunc = getattr(mod, 'dataLoaderInfo') # Attempt to retrieve function
            options = testInfoFunc() # Try out the info function
            loaderFunc = getattr(mod, 'dataLoader') # Make sure there is a loader function
            del mod, testInfoFunc, options, loaderFunc # unload the module
            os.remove('Resources/tempFiles/'+fileName) # Delete the temporary file

        except Exception as e: 
            button = QtWidgets.QMessageBox.question(self, 'Error', 'Error in reading the script: {0}'.format(e), QtWidgets.QMessageBox.Ok)
            os.remove('Resources/tempFiles/'+fileName) # Delete the temporary file
            return

        # Determine if we're talking about an existing dataloader
        name = self.nameEdit.text() #Get the dataloader name
        if name == 'untitledLoader':
            button = QtWidgets.QMessageBox.question(self, 'Name Error', 'Please give the dataloader a meaningful name.', QtWidgets.QMessageBox.Ok)
            if button == QtWidgets.QMessageBox.Ok:
                return
        if name + '.py' in self.fileTable.dataloaderList:
            # The file already exists, we just need to update the contents
            button = QtWidgets.QMessageBox.question(self, 'Save Changes', 'Save changes to the exisiting {0} loader?'.format(name), QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if button == QtWidgets.QMessageBox.Ok:
                os.remove('Resources/DataLoaders/Custom/'+name+'.py') # Remove the old file
                # Write the new file
                with open('Resources/DataLoaders/Custom/'+name+'.py','w') as writefile:
                    writefile.write(self.editor.toPlainText())
                #Reload the table
                self.fileTable.populate()
                self.editor.setPlainText('')
                self.nameEdit.setText('')
                self.nameEdit.setReadOnly(True)
                self.editor.setReadOnly(True)

                # Let user's edit buttons again
                self.addButton.setEnabled(True)
                self.deleteButton.setEnabled(True)
                self.editButton.setEnabled(True)
                self.saveButton.setEnabled(False)
                self.cancelButton.setEnabled(False)
                return
            else:
                return

        else: # THis is a brand new dataloader
            # The file already exists, we just need to update the contents
            button = QtWidgets.QMessageBox.question(self, 'Save Changes', 'Create new file: {0} loader?'.format(name), QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if button == QtWidgets.QMessageBox.Ok:
                # Write the new file
                with open('Resources/DataLoaders/Custom/'+name+'.py','w') as writefile:
                    writefile.write(self.editor.toPlainText())
                self.fileTable.populate()
                self.editor.setPlainText('')
                self.nameEdit.setText('')
                self.nameEdit.setReadOnly(True)
                self.editor.setReadOnly(True)

                # Let user's edit buttons again
                self.addButton.setEnabled(True)
                self.deleteButton.setEnabled(True)
                self.editButton.setEnabled(True)
                self.saveButton.setEnabled(False)
                self.cancelButton.setEnabled(False)
                return
            
            else:
                return
        
        # Diable the editor
        self.editor.setReadOnly(True)
    
    # Function to cancel any changes
    def cancelChanges(self):
        button = QtWidgets.QMessageBox.question(self, 'Cancel Changes', 'Disregard all changes?', QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if button == QtWidgets.QMessageBox.Ok:
            # Let user's edit buttons again
            self.addButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
            self.editButton.setEnabled(True)
            self.editor.setPlainText('')
            self.fileTable.populate()
            self.nameEdit.setText('')
            self.nameEdit.setReadOnly(True)
            self.editor.setReadOnly(True)
            self.saveButton.setEnabled(False)
            self.cancelButton.setEnabled(False)
            return
        else:
            return