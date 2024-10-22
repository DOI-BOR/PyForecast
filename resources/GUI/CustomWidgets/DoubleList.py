from PyQt5 import QtWidgets, QtCore, QtGui
from .DatasetList_HTML_Formatted import DatasetListHTMLFormatted, DatasetListHTMLFormattedMultiple
import pandas as pd
import numpy as np
import copy

class DoubleListUniqueInstance(QtWidgets.QWidget):

    updatedOutputList = QtCore.pyqtSignal(pd.DataFrame)
    updatedLinkedList = QtCore.pyqtSignal(DatasetListHTMLFormatted, DatasetListHTMLFormatted)

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
        self.listInput = DatasetListHTMLFormatted()
        self.listOutput = DatasetListHTMLFormatted()

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
        self.dataset_dataframe = initialDataframe

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

    def resetAvailableItems(self):
        """
        Clears all list entries and adds items back to the list items

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None.

        """

        # Clear the input and output lists
        self.listInput.clear()
        self.listOutput.clear()

        # Add the items to the input list and refresh the input list
        self.listInput.datasetTable = self.dataset_dataframe
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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

        self.listInput.datasetTable = self.listInput.datasetTable.append(rows)

        # Remove from the input table
        self.listOutput.datasetTable.drop(self.listOutput.datasetTable.index[input_row_index], inplace=True)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)


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
        self.listOutput.datasetTable = self.listOutput.datasetTable.append(rows)

        # Remove from the input table
        self.listInput.datasetTable.drop(self.listInput.datasetTable.index[input_row_index], inplace=True)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)


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

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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
        self.dataset_dataframe = datasetTable

        # Reset the list entries
        self.resetAvailableItems()

    def updateLinkedDoubleLists(self, inputList, outputList):
        """
        Syncronizes the DoubleList with another external DoubleList by copying the tables

        Parameters
        ----------
        inputList: html list
            Qt list of the input series from the other double list
        outputList: html list
            Qt list of the output series from the other double list

        Returns
        -------
        None.

        """

        # Sync the lists
        self.listInput.datasetTable = copy.copy(inputList.datasetTable)
        self.listOutput.datasetTable = copy.copy(outputList.datasetTable)

        # Refresh the object
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()




class DoubleListMultipleInstance(QtWidgets.QWidget):

    updatedOutputList = QtCore.pyqtSignal()
    predictorAdded = QtCore.pyqtSignal()
    predictorRemoved = QtCore.pyqtSignal()
    updatedLinkedList = QtCore.pyqtSignal(DatasetListHTMLFormatted, DatasetListHTMLFormattedMultiple)

    def __init__(self, initialDataframe, inputTitle, outputTitle, inputDefaultColor=QtCore.Qt.white,
                 outputDefaultColor=QtCore.Qt.white, parent=None, operations_dataframe=None):
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
        self.listInput = DatasetListHTMLFormatted()
        self.listOutput = DatasetListHTMLFormattedMultiple()

        # Set the default colors when moving items
        self.inputDefaultColor = inputDefaultColor
        self.outputDefaultColor = outputDefaultColor

        # Create the title widgets
        inputTitleWidget = QtWidgets.QLabel(inputTitle)
        outputTitleWidget = QtWidgets.QLabel(outputTitle)

        # Create the buttons to move items between lists
        self.buttonAllToOuput = QtWidgets.QPushButton(">>")
        self.buttonSingleToOutput = QtWidgets.QPushButton(">")
        self.buttonSingleToInput = QtWidgets.QPushButton("<")
        self.buttonAllToInput = QtWidgets.QPushButton("<<")

        # Add the input table to the layout
        self.layoutInput = QtWidgets.QVBoxLayout()
        self.layoutInput.addWidget(inputTitleWidget)
        self.layoutInput.addWidget(self.listInput)

        layoutInputWidget = QtWidgets.QWidget()
        layoutInputWidget.setLayout(self.layoutInput)
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
        self.layoutOutput = QtWidgets.QVBoxLayout()
        self.layoutOutput.addWidget(outputTitleWidget)
        self.layoutOutput.addWidget(self.listOutput)

        layoutOutputWidget = QtWidgets.QWidget()
        layoutOutputWidget.setLayout(self.layoutOutput)
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
        self.dataset_dataframe = initialDataframe
        self.operations_dataframe = operations_dataframe

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
        # self.htmlListWidget.buttonPress.connect(self.update)

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

    def resetAvailableItems(self):
        """
        Clears all list entries and adds items back to the list items

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None.

        """

        # Clear the input and output lists
        self.listInput.clear()
        self.listOutput.clear()

        # Clear coloration on the lists
        if self.listInput.itemColors is not None:
            self.listInput.itemColors = [self.inputDefaultColor for x in range(0, self.listInput.count(), 1)]

        if self.listOutput.itemColors is not None:
            self.listOutput.itemColors = [self.outputDefaultColor for x in range(0, self.listInput.count(), 1)]

        # Add the items to the input list and refresh the input list
        self.listInput.datasetTable = self.dataset_dataframe
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)
        self.updatedOutputList.emit()

    def resetOutputItems(self):
        """
        Clears all output list entries

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None.

        """

        # Clear the output lists
        self.listOutput.datasetTable.drop(self.listOutput.datasetTable.index, inplace=True)

        # Clear the coloration
        if self.listOutput.itemColors is not None:
            self.listOutput.itemColors = []

        # Update the GUI
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)
        self.updatedOutputList.emit()


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

        # Clear the output list
        self.listOutput.datasetTable = self.listOutput.datasetTable.drop(self.listOutput.datasetTable.index)

        # Clear the color list
        if self.listOutput.itemColors is not None:
            self.listOutput.itemColors = []

        # Trigger refreshes of the input and output lists
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)
        self.updatedOutputList.emit()
        self.predictorRemoved.emit()

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

        # Check for each input list entry in the output list
        for entry, value in enumerate(self.listInput.datasetTable.index):
            #i_number_of_existing = len(self.listOutput.datasetTable.loc[[value]])
            #if i_number_of_existing == 0:
            self._setSingleOutputItem(False, row_index=entry, refresh=False)

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)
        self.updatedOutputList.emit()
        self.predictorAdded.emit()

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

        # Remove from the input table
        self.listOutput.datasetTable.drop(self.listOutput.datasetTable.iloc[input_row_index].name, inplace=True)

        # Remove the coloration from the index
        del self.listOutput.itemColors[input_row_index]

        # Trigger refreshes of the input and output lists
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)
        self.updatedOutputList.emit()
        self.predictorRemoved.emit()

    def _setSingleOutputItem(self, event_status, row_index=None, refresh=True):
        """
        Moves the single selected item in the input list to the output list

        Parameters
        ----------
        self: DoubleList

        Returns
        -------
        None

        """
        # Get the selected row indeces
        if row_index is None:
            input_row_indices = [x.row() for x in self.listInput.selectedIndexes()]
        else:
            input_row_indices = [row_index]
            
        # Loop through the selected row indices
        for input_row_index in input_row_indices:
            # Append the row into the output table
            rows = self.listInput.datasetTable.iloc[input_row_index, :]

            # Determine the instance number to assign to the entry
            try:
                i_number_of_existing = len(self.listOutput.datasetTable.loc[[rows.name]])
            except:
                i_number_of_existing = 0

            # Check that there's not a gap in the numbering scheme
            if i_number_of_existing > 0:
                # Get the instance numbers of the datasets
                indices = [x[1] for x in self.listOutput.datasetTable.loc[[rows.name]].index]

                # Determine if there are gaps in the values
                indicesOrdered = [True if x == indices[x] else False for x in range(0, len(indices), 1)]

                # Replace with the first available missing index
                if not all(indicesOrdered):
                    # Replace with the first missing index
                    for entry in range(0, len(indicesOrdered), 1):
                        if not indicesOrdered[entry]:
                            i_number_of_existing = entry
                            break

            self.listOutput.datasetTable.loc[(rows.name, i_number_of_existing), :] = rows

            # Add an entry into the color table
            if self.listOutput.itemColors is not None:
                self.listOutput.itemColors.append(self.outputDefaultColor)

            # Trigger refreshes of the input and output lists
            if refresh:
                self.listInput.refreshDatasetList()
                self.listOutput.refreshDatasetList()

                # Emit for the updated linked doublelists
                self.updatedLinkedList.emit(self.listInput, self.listOutput)
                self.updatedOutputList.emit()
                self.predictorAdded.emit()



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

        # Swap the color indices if active
        if self.listOutput.itemColors is not None:
            currentValue = self.listOutput.itemColors[i_current_index]
            self.listOutput.itemColors[i_current_index] = self.listOutput.itemColors[i_current_index - 1]
            self.listOutput.itemColors[i_current_index - 1] = currentValue

        # Reindex the table
        self.listOutput.datasetTable = self.listOutput.datasetTable.reindex(self.listOutput.datasetTable.index[ia_indices])

        # Refresh the table
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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

        # Swap the color indices if active
        if self.listOutput.itemColors is not None:
            currentValue = self.listOutput.itemColors[i_current_index]
            self.listOutput.itemColors[i_current_index] = self.listOutput.itemColors[i_current_index + 1]
            self.listOutput.itemColors[i_current_index + 1] = currentValue

        # Reindex the table
        self.listOutput.datasetTable = self.listOutput.datasetTable.reindex(self.listOutput.datasetTable.index[ia_indices])

        # Refresh the table
        self.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.updatedLinkedList.emit(self.listInput, self.listOutput)

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
        self.dataset_dataframe = datasetTable

        # Reset the list entries
        self.resetAvailableItems()

    def updateLinkedDoubleLists(self, inputList, outputList):
        """
        Syncronizes the DoubleList with another external DoubleList by copying the tables

        Parameters
        ----------
        inputList: html list
            Qt list of the input series from the other double list
        outputList: html list
            Qt list of the output series from the other double list

        Returns
        -------
        None.

        """

        # Sync the lists
        self.listInput.datasetTable = copy.copy(inputList.datasetTable)
        self.listOutput.datasetTable = copy.copy(outputList.datasetTable)

        # Refresh the coloration
        if self.listInput.itemColors is not None:
            self.listInput.itemColors = [self.inputDefaultColor for x in self.listInput.datasetTable]

        if self.listOutput.itemColors is not None:
            self.listOutput.itemColors = [self.outputDefaultColor for x in self.listOutput.datasetTable]

        # Refresh the object
        self.listInput.refreshDatasetList()
        self.listOutput.refreshDatasetList()

        # Emit the updated output table sync signal
        self.updatedOutputList.emit()

    def updateLinkedOperationsTables(self):
        """
        Propagates changes in the doublelist output table to the linked operations table

        Parameters
        ----------
        self: DoubleListMultipleInstance
        syncedTable: dataframe
            Operations table that needs to be synced across the application

        Returns
        -------
        None. Modfies the linked table stored within the list object

        """

        # Determine if a row has been added for removed
        rowRemoved = len(self.listOutput.datasetTable) < len(self.operations_dataframe)
        rowAdded = len(self.listOutput.datasetTable) > len(self.operations_dataframe)

        # Take action based on the table change
        if rowRemoved:
            # Determine which row has been removed from the dataset table
            targetTuples = [x for x in self.operations_dataframe.index if x not in self.listOutput.datasetTable.index]

            # Drop the value from the operations table
            for targetTuple in targetTuples:
                self.operations_dataframe.drop(targetTuple, inplace=True)

        if rowAdded:
            # Determine which row has be added to the dataset table
            targetTuples = [x for x in self.listOutput.datasetTable.index if x not in self.operations_dataframe.index]

            # Add the information into the table
            for targetTuple in targetTuples:
                self.operations_dataframe.loc[(targetTuple[0],targetTuple[1]),:] = None