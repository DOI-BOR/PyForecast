from PyQt5 import QtWidgets, QtCore, QtGui


class DoubleList(QtWidgets.QWidget):

    def __init__(self, parent=None):
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
        self.listInput = QtWidgets.QListWidget()
        self.listOuput = QtWidgets.QListWidget()

        # Create the buttons to move items between lists
        self.buttonAllToOuput = QtWidgets.QPushButton(">>")
        self.buttonSingleToOutput = QtWidgets.QPushButton(">")
        self.buttonSingleToInput = QtWidgets.QPushButton("<")
        self.buttonAllToInput = QtWidgets.QPushButton("<<")

        # Add the input table to the layout
        layout.addWidget(self.listInput)

        # Setup the button box
        layoutm = QtWidgets.QVBoxLayout()
        layoutm.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        layoutm.addWidget(self.buttonAllToOuput)
        layoutm.addWidget(self.buttonSingleToOutput)
        layoutm.addWidget(self.buttonSingleToInput)
        layoutm.addWidget(self.buttonAllToInput)
        layoutm.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Add the buttons and output list to the layout
        layout.addLayout(layoutm)
        layout.addWidget(self.listOuput)

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
        self._setStatusButton()
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
        self.listOuput.itemSelectionChanged.connect(self._setStatusButton)
        self.listInput.itemSelectionChanged.connect(self._setStatusButton)

        # Set the move button connections
        self.buttonSingleToOutput.clicked.connect(self._setSingleOutputItem)
        self.buttonSingleToInput.clicked.connect(self._setSingleInputItem)

        self.buttonAllToInput.clicked.connect(self._setAllInputItems)
        self.buttonAllToOuput.clicked.connect(self._setAllOutputItems)

        # Set the up/down button connections
        self.buttonUp.clicked.connect(self._setButtonUpClicked)
        self.buttonDown.clicked.connect(self._setButtonDownClicked)

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


        self.buttonUp.setDisabled(not self.listOuput.selectedItems() or self.listOuput.currentRow() == 0)
        self.buttonDown.setDisabled(not self.listOuput.selectedItems() or self.listOuput.currentRow() == self.listOuput.count() - 1)
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

        self.listInput.addItems(listItems);


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

        # Create a item list to hold the output
        itemSelected = QtWidgets.QStringList()

        # Get each selected item from the output list and add it to the output list
        for i_item_entry in range(0, self.listOuput.count(), 1):
            itemSelected.append(self.listOuput.item(i_item_entry).text())

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

        while self.listOuput.count() > 0:
            self.listInput.addItem(self.listOuput.takeItem(0))

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

        while self.listInput.count() > 0:
            self.listOuput.addItem(self.listInput.takeItem(0))

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

        self.listInput.addItem(self.listOuput.takeItem(self.listOuput.currentRow()))

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

        self.listOuput.addItem(self.listInput.takeItem(self.listInput.currentRow()))

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
        i_current_row = self.listOuput.currentRow()

        # Get the current item from the list
        currentItem = self.listOuput.takeItem(i_current_row)

        # Insert the item one above and update the the current row
        self.listOuput.insertItem(i_current_row - 1, currentItem)
        self.listOuput.setCurrentRow(i_current_row - 1)

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
        i_current_row = self.listOuput.currentRow()

        # Get the current item from the list
        currentItem = self.listOuput.takeItem(i_current_row)

        # Insert the item one below and update the the current row
        self.listOuput.insertItem(i_current_row + 1, currentItem)
        self.listOuput.setCurrentRow(i_current_row + 1)
