from PyQt5 import QtWidgets, QtCore, QtGui
from .DatasetList_HTML_Formatted import DatasetList_HTML_Formatted
import pandas as pd
import numpy as np

class DoubleList(QtWidgets.QWidget):
    
    updatedOutputList = QtCore.pyqtSignal(pd.DataFrame)

    def __init__(self, initialDataframe, inputTitle, outputTitle, parent=None):
        """
        Constructor for the DoubleList widget class. This creates side-by-side linked lists. The user is able to move
        data entries from the left list to the right list to include the dataset in the analysis. The datasets in the
        right list can be reordered based on priority.

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Call the super constructor
        QtWidgets.QWidget.__init__(self)

        # Create the overall layout objects
        layout = QtWidgets.QHBoxLayout(self)
        self.listInput = DatasetList_HTML_Formatted()
        self.listOutput = DatasetList_HTML_Formatted()

        # Create the title widgets
        inputTitleWidget = QtWidgets.QLabel(inputTitle)
        outputTitleWidget = QtWidgets.QLabel(outputTitle)

        # Create the buttons to move items between lists
        self.buttonAllToOuput = QtWidgets.QPushButton(">>")
        self.buttonSingleToOutput = QtWidgets.QPushButton(">")
        self.buttonSingleToInput = QtWidgets.QPushButton("<")
        self.buttonAllToInput = QtWidgets.QPushButton("<<")

        # Add the input table to the layout
        layoutInput = QtWidgets.QVBoxLayout()
        layoutInput.addWidget(inputTitleWidget)
        layoutInput.addWidget(self.listInput)

        layoutInputWidget = QtWidgets.QWidget()
        layoutInputWidget.setLayout(layoutInput)
        layout.addWidget(layoutInputWidget)

        # Setup the button box
        layoutm = QtWidgets.QVBoxLayout()
        layoutm.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        layoutm.addWidget(self.buttonAllToOuput)
        layoutm.addWidget(self.buttonSingleToOutput)
        layoutm.addWidget(self.buttonSingleToInput)
        layoutm.addWidget(self.buttonAllToInput)
        layoutm.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Add the buttons to the layout
        layout.addLayout(layoutm)

        # Create the output column layout
        layoutOutput = QtWidgets.QVBoxLayout()
        layoutOutput.addWidget(outputTitleWidget)
        layoutOutput.addWidget(self.listOutput)

        layoutOutputWidget = QtWidgets.QWidget()
        layoutOutputWidget.setLayout(layoutOutput)
        layout.addWidget(layoutOutputWidget)

        # Create buttons to move items up and down in the order
        self.buttonUp = QtWidgets.QPushButton("Up")
        self.buttonDown = QtWidgets.QPushButton("Down")

        # Create the layout for the up/down buttons
        layoutl = QtWidgets.QVBoxLayout()
        layoutl.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        layoutl.addWidget(self.buttonUp)
        layoutl.addWidget(self.buttonDown)
        layoutl.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        layout.addLayout(layoutl)

        # Set the initial dataframe from the parent object
        self.data_frame = initialDataframe

        # Set the status button
        self._setStatusButton()

        # Create the connections between the DoubleList objects
        self.connections()

    def connections(self):
        """
        Creates connections between the lists and buttons. This allows the buttons to dynamically adjust the items
        in the lists

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Setup the connections between the lists and the status button
        self.listOutput.itemSelectionChanged.connect(self._setStatusButton)
        self.listInput.itemSelectionChanged.connect(self._setStatusButton)

        # Set the move button connections
        self.buttonSingleToOutput.clicked.connect(self._setSingleOutputItem)
        self.buttonSingleToInput.clicked.connect(self._setSingleInputItem)

        self.buttonAllToInput.clicked.connect(self._setAllInputItems)
        self.buttonAllToOuput.clicked.connect(self._setAllOutputItems)

        # Set the up/down button connections
        self.buttonUp.clicked.connect(self._setButtonUpClicked)
        self.buttonDown.clicked.connect(self._setButtonDownClicked)

        # List connection
        #self.htmlListWidget.buttonPress.connect(self.update)

    def _setStatusButton(self):
        """
        Dynamically adjusts the available buttons based on the contents of the lists. If the lists do not contain the
        correct number of entries to execute but button action, the action will be disabled.

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        self.buttonUp.setDisabled(not self.listOutput.selectedItems() or self.listOutput.currentRow() == 0)
        self.buttonDown.setDisabled(not self.listOutput.selectedItems() or self.listOutput.currentRow() == self.listOutput.count() - 1)
        self.buttonSingleToOutput.setDisabled(not self.listInput.selectedItems())
        self.buttonAllToOuput.setDisabled(not self.listInput.selectedItems())

    def addAvailableItems(self, listItems):
        """
        Adds entries to the input list of the widget

        Parameters
        ----------
        self: DoubleList
        listItems: QStringList
            List of strings to add to the input list widget

        Returns
        -------
        None

        """

        self.listInput.addItems(listItems)

    def resetAvailableItems(self):
        """
        Clears all list entries and adds items back to the list items

        Parameters
        ----------
        self: DoubleList
        listItems: QStringList
            List of strings to add to the input list widget

        Returns
        -------
        None.

        """

        # Clear the input and output lists
        self.listInput.clear()
        self.listOutput.clear()

        # Add the items to the input list and refresh the input list
        self.listInput.datasetTable = self.data_frame
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

    def seletedItems(self):
        """
        Returns of the list of items in the output list in order from top to bottom

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """
        # todo: not sure if this works with the updated dataframe syntax

        # Create a item list to hold the output
        itemSelected = QtWidgets.QStringList()

        # Get each selected item from the output list and add it to the output list
        for i_item_entry in range(0, self.listOutput.count(), 1):
            itemSelected.append(self.listOutput.item(i_item_entry).text())

        # Return the output list to the calling function
        return itemSelected

    def _setAllInputItems(self):
        """
        Move all items from the output list to the input list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Swap the tables between the objects
        self.listInput.datasetTable = self.listInput.datasetTable.append(self.listOutput.datasetTable)

        # Clear the output list
        self.listOutput.datasetTable = self.listOutput.datasetTable.drop(self.listOutput.datasetTable.index)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

    def _setAllOutputItems(self):
        """
        Moves all items from the input list to the output list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Swap the tables between the objects
        self.listOutput.datasetTable = self.listOutput.datasetTable.append(self.listInput.datasetTable)

        # Clear the input list
        self.listInput.datasetTable = self.listInput.datasetTable.drop(self.listInput.datasetTable.index)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

    def _setSingleInputItem(self):
        """
        Moves a single entry from the output list to the input list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Get the current row of index
        input_row_index = self.listOutput.currentRow()

        # Append the row into the output table
        rows = self.listOutput.datasetTable.iloc[input_row_index, :]
        self.listInput.datasetTable = self.listInput.datasetTable.append(rows, ignore_index=True)

        # Remove from the input table
        self.listOutput.datasetTable.drop(self.listOutput.datasetTable.index[input_row_index], inplace=True)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()


    def _setSingleOutputItem(self):
        """
        Moves the single selected item in the input list to the output list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Get the current row of index
        input_row_index = self.listInput.currentRow()

        # Append the row into the output table
        rows = self.listInput.datasetTable.iloc[input_row_index, :]
        self.listOutput.datasetTable = self.listOutput.datasetTable.append(rows, ignore_index=True)

        # Remove from the input table
        self.listInput.datasetTable.drop(self.listInput.datasetTable.index[input_row_index], inplace=True)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()


    def _setButtonUpClicked(self):
        """
        Moves a selected dataset up within the output list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Get the current item in the list
        i_current_row = self.listOutput.currentRow()

        # Get the current row of the output table
        ia_indices = np.arange(0, len(self.listOutput.datasetTable), 1)

        # Swap the indices
        i_current_index = np.argwhere(ia_indices == i_current_row).flatten()[0]
        ia_indices[i_current_index] = ia_indices[i_current_index - 1]
        ia_indices[i_current_index - 1] = i_current_row

        # Reindex the table
        self.listOutput.datasetTable = self.listOutput.datasetTable.reindex(self.listOutput.datasetTable.index[ia_indices])

        # Refresh the table
        self.listOutput.refreshDatasetList()

    def _setButtonDownClicked(self):
        """
        Moves a selected dataset down within the output list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """

        # Get the current item in the list
        i_current_row = self.listOutput.currentRow()

        # Get the current row of the output table
        ia_indices = np.arange(0, len(self.listOutput.datasetTable), 1)

        # Swap the indices
        i_current_index = np.argwhere(ia_indices == i_current_row).flatten()[0]
        ia_indices[i_current_index] = ia_indices[i_current_index + 1]
        ia_indices[i_current_index + 1] = i_current_row

        # Reindex the table
        self.listOutput.datasetTable = self.listOutput.datasetTable.reindex(self.listOutput.datasetTable.index[ia_indices])

        # Refresh the table
        self.listOutput.refreshDatasetList()

    def update(self, datasetTable):
        """
        Update the double list object based on the input of another widget

        Parameters
        ----------
        self: DoubleList
        datasetTable: dataframe
            Pandas dataframe containing the updated dataset information

        """

        # Output the table for debug purposes
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(datasetTable)

        # Update the DoubleList dataframe
        self.data_frame = datasetTable

        # Reset the list entries
        self.resetAvailableItems()

