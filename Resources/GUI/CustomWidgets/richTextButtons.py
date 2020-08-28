from PyQt5 import QtWidgets, QtCore, QtGui


class richTextDescriptionButton(QtWidgets.QPushButton):

    def __init__(self, parent=None, richText=""):

        QtWidgets.QPushButton.__init__(self)
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.lab = QtWidgets.QLabel(richText, self)
        self.lab.mousePressEvent = lambda ev: self.click()
        self.lab.setTextFormat(QtCore.Qt.RichText)

        self.richTextChecked = """
        <table border=0>
        <tr><td><img src="resources/GraphicalResources/icons/check_box-24px.svg"></td>
        <td>{0}</td></tr>
        </table>
        """.format(richText)

        self.richTextUnChecked = """
        <table border=0>
        <tr><td><img src="resources/GraphicalResources/icons/check_box_outline_blank-24px.svg"></td>
        <td>{0}</td></tr>
        </table>
        """.format(richText)

        self.lab.setText(self.richTextUnChecked)
        self.lab.setWordWrap(True)
        self.lab.setContentsMargins(10, 10, 10, 10)

        self.lab.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.lab.setMinimumHeight(self.heightMM())
        self.lab.setMaximumHeight(self.heightMM() * 3)
        self.lab.setFixedWidth(self.width())
        self.setFixedHeight(self.heightMM())

        self.lab.setAlignment(QtCore.Qt.AlignTop)

    def click(self):
        QtWidgets.QAbstractButton.click(self)
        if self.isChecked():
            self.lab.setText(self.richTextChecked)
        else:
            self.lab.setText(self.richTextUnChecked)

    def resizeEvent(self, ev):
        QtWidgets.QPushButton.resizeEvent(self, ev)
        self.lab.setFixedWidth(self.width())
        self.lab.setFixedHeight(self.height() * 5)

        self.parent().parent().setMinimumHeight(self.height() * 5)
        self.parent().resizeEvent(ev)
        self.parent().parent().resizeEvent(ev)

        if ev.oldSize().width() > 0 and ev.oldSize().height() > 0 and ev.size().width() > 0:
            if ev.size().width() < 300:
                self.setFixedHeight(140)

            elif ev.size().width() < 400:
                self.setFixedHeight(110)

            elif ev.size().width() < 500:
                self.setFixedHeight(100)

            else:
                self.setFixedHeight(90)

            self.parent().resizeEvent(ev)


class richTextButtonCheckbox(QtWidgets.QPushButton):

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
        self.__lyt.setContentsMargins(2, 2, 2, 2)
        self.__lyt.setSpacing(0)
        self.setLayout(self.__lyt)

        self.__lbl.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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