from PyQt5 import QtWidgets, QtCore, QtGui

class AggregationOptions(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Constructor for the Aggregation Options widget class.

        Parameters
        ----------
        self: AggregationOptions

        Returns
        -------
        None

        """

        QtWidgets.QWidget.__init__(self)
        self.parent = parent

        vbox = QtWidgets.QVBoxLayout()
        self.aggOptionsGroupBox = QtWidgets.QGroupBox("Predictor Aggregation Options")

        # Create the overall layout objects
        layout = QtWidgets.QHBoxLayout(self)

        # Create the radio buttons
        self.accumOption = QtWidgets.QRadioButton("Accumulation")
        self.accumCfs2KafOption = QtWidgets.QRadioButton("Accumulation (cfs to kaf)")
        self.averageOption = QtWidgets.QRadioButton("Average")
        self.firstValOption = QtWidgets.QRadioButton("First")
        self.lastValOption = QtWidgets.QRadioButton("Last")
        self.maxValOption = QtWidgets.QRadioButton("Max")
        self.minValOption = QtWidgets.QRadioButton("Min")
        self.medianValOption = QtWidgets.QRadioButton("Median")
        self.customValOption = QtWidgets.QRadioButton("Custom Pattern")
        self.customValString = QtWidgets.QLineEdit()
        self.customValString.setDisabled(True)
        self.customValOption.toggled.connect(self.customValString.setEnabled)
        self.averageOption.setChecked(True)

        # Setup the radio button container
        layoutm = QtWidgets.QVBoxLayout()
        layoutm.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        layoutm.addWidget(self.accumOption)
        layoutm.addWidget(self.accumCfs2KafOption)
        layoutm.addWidget(self.averageOption)
        layoutm.addWidget(self.firstValOption)
        layoutm.addWidget(self.lastValOption)
        layoutm.addWidget(self.maxValOption)
        layoutm.addWidget(self.minValOption)
        layoutm.addWidget(self.medianValOption)
        layoutm.addWidget(self.customValOption)
        layoutm.addWidget(self.customValString)
        layoutm.addItem(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Add the container to the layout
        layout.addLayout(layoutm)




