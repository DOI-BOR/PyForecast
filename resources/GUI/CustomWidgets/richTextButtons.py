from PyQt5 import QtWidgets, QtCore, QtGui


class richTextButtonCheckbox(QtWidgets.QPushButton):

    updateLinkedButton = QtCore.pyqtSignal(bool)

    def __init__(self, text=None):
        """
        Constructor for the richTextButtonCheckbox class

        Parameters
        ----------
        self: richTextButton

        Returns
        -------
        None

        """

        QtWidgets.QPushButton.__init__(self)
        self.__lbl = QtWidgets.QLabel(self)

        self.setCheckable(True)
        self.setAutoExclusive(False)

        self.__lyt = QtWidgets.QHBoxLayout()
        self.__lyt.setContentsMargins(2, 5, 10, 10)
        self.__lyt.setSpacing(0)
        self.setLayout(self.__lyt)

        self.__lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.__lbl.setTextFormat(QtCore.Qt.RichText)
        self.__lyt.addWidget(self.__lbl)

        # Create the label position modifications
        self.__lbl.setWordWrap(True)
        self.__lbl.setAlignment(QtCore.Qt.AlignTop)

        self.richTextChecked = """
        <table border=0>
        <tr><td><img src="resources/GraphicalResources/icons/check_box-24px.svg"></td>
        <td>{0}</td></tr>
        </table>
        """.format(text)

        self.richTextUnChecked = """
        <table border=0>
        <tr><td><img src="resources/GraphicalResources/icons/check_box_outline_blank-24px.svg"></td>
        <td>{0}</td></tr>
        </table>
        """.format(text)

        # Set the initial state to unchecked
        if text is not None:
            self.__lbl.setText(self.richTextUnChecked)

        # Connect the clicked event to the update function
        self.clicked.connect(self.clicked_update)

    def setText(self, text):
        """
        Set the text of the button

        Parameters
        ----------
        self: richTextButtonCheckbox
        text: str
            Text to add to the button

        Returns
        -------
        None

        """

        self.__lbl.setText(text)
        self.updateGeometry()

    def clicked_update(self):
        """
        Update the widget state based on the check event

        """

        if self.isChecked():
            self.__lbl.setText(self.richTextChecked)
        else:
            self.__lbl.setText(self.richTextUnChecked)

        # Update the button geometry
        self.updateGeometry()

        # Emit an update signal to allow status update on linked buttons
        self.updateLinkedButton.emit(self.isChecked())


    def sizeHint(self):
        """
        Overload the size hint function to sync the label and button sizes

        """

        s = QtWidgets.QPushButton.sizeHint(self)

        # Get the size of the label
        labelSize = self.__lbl.sizeHint()
        labelWidth = labelSize.width()
        labelHeight = labelSize.height()

        # Set the width of the label
        s.setWidth(labelWidth)

        # Set the height as the row height
        s.setHeight(labelHeight)

        # Return the size hint to avoid thrown errors
        return labelSize

    def update_from_external(self, externalStatus):
        """
        Updates clicked state from a linked external button

        """

        if externalStatus:
            self.setChecked(True)
            self.__lbl.setText(self.richTextChecked)
        else:
            self.setChecked(False)
            self.__lbl.setText(self.richTextUnChecked)


class richTextButton(QtWidgets.QPushButton):

    def __init__(self, text=None):
        """
        Constructor for the richTextButton class

        Parameters
        ----------
        self: richTextButton

        Returns
        -------
        None

        """

        QtWidgets.QPushButton.__init__(self)
        self.__lbl = QtWidgets.QLabel(self)

        self.setCheckable(True)
        self.setAutoExclusive(False)

        self.__lyt = QtWidgets.QHBoxLayout()
        self.__lyt.setContentsMargins(5, 5, 5, 5)
        self.__lyt.setSpacing(0)
        self.setLayout(self.__lyt)

        self.__lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.__lbl.setTextFormat(QtCore.Qt.RichText)
        self.__lyt.addWidget(self.__lbl)

        # Create the label position modifications
        self.__lbl.setWordWrap(True)
        self.__lbl.setAlignment(QtCore.Qt.AlignCenter)

        # Set the initial state to unchecked
        if text is not None:
            self.__lbl.setText(text)

    def setText(self, text):
        """
        Set the text of the button

        Parameters
        ----------
        self: richTextButton
        text: str
            Text to add to the button

        Returns
        -------
        None

        """

        self.__lbl.setText(text)
        self.updateGeometry()

    def sizeHint(self):
        """
        Overload the size hint function to sync the label and button sizes

        """

        s = QtWidgets.QPushButton.sizeHint(self)

        # Get the size of the label
        labelSize = self.__lbl.sizeHint()
        labelWidth = labelSize.width()
        labelHeight = labelSize.height()

        # Set the width of the label
        s.setWidth(labelWidth)

        # Set the height as the row height
        s.setHeight(labelHeight)

        # Return the size hint to avoid thrown errors
        return labelSize