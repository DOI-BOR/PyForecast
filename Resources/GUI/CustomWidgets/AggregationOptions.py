from PyQt5 import QtWidgets, QtCore, QtGui

class AggregationOptions(QtWidgets.QWidget):

    def __init__(self, scrollable, parent=None):
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

        # Create the overall layout objects
        layout1 = QtWidgets.QVBoxLayout()
        if scrollable:
            scrollarea = QtWidgets.QScrollArea(self)
            scrollarea.setWidgetResizable(True)
            scrollarea.setMinimumWidth(300)
            scrollarea.setMinimumHeight(400) # would be better if resizable
            scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            optionsWidget = QtWidgets.QWidget()


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
        self.toggleLabel = QtWidgets.QLabel("")

        # Connect radio button actions
        self.accumOption.toggled.connect(self.accumToggled)
        self.accumCfs2KafOption.toggled.connect(self.accumCfs2KafToggled)
        self.averageOption.toggled.connect(self.averageToggled)
        self.firstValOption.toggled.connect(self.firstToggled)
        self.lastValOption.toggled.connect(self.lastToggled)
        self.maxValOption.toggled.connect(self.maxToggled)
        self.minValOption.toggled.connect(self.minToggled)
        self.medianValOption.toggled.connect(self.medianToggled)
        self.customValOption.toggled.connect(self.customToggled)
        self.averageOption.setChecked(True)

        # Setup the radio button container
        layout1.addWidget(QtWidgets.QLabel("SELECTED PREDICTOR"))
        layout1.addWidget(QtWidgets.QLabel("selected predictor info and metadata - 1"))
        layout1.addWidget(QtWidgets.QLabel("selected predictor info and metadata - 2"))
        layout1.addWidget(QtWidgets.QLabel("selected predictor info and metadata - 3"))
        layout1.addWidget(QtWidgets.QLabel("selected predictor info and metadata - 4"))
        layout1.addWidget(self.accumOption)
        layout1.addWidget(self.accumCfs2KafOption)
        layout1.addWidget(self.averageOption)
        layout1.addWidget(self.firstValOption)
        layout1.addWidget(self.lastValOption)
        layout1.addWidget(self.maxValOption)
        layout1.addWidget(self.minValOption)
        layout1.addWidget(self.medianValOption)
        layout1.addWidget(self.customValOption)
        layout1.addWidget(self.customValString)
        layout1.addWidget(self.toggleLabel)
        vertSpacer = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)


        # Add the container to the layout
        if scrollable:
            optionsWidget.setLayout(layout1)
            scrollarea.setWidget(optionsWidget)
        else:
            layout1.addItem(vertSpacer)
            self.setLayout(layout1)


    def accumToggled(self):
        self.toggleLabel.setText("Accumulation option description goes here...")
        #set predictor object value here...

    def accumCfs2KafToggled(self):
        self.toggleLabel.setText("Accumulation conversion option description goes here...")
        #set predictor object value here...

    def averageToggled(self):
        self.toggleLabel.setText("Average option description goes here...")
        #set predictor object value here...

    def firstToggled(self):
        self.toggleLabel.setText("First option description goes here...")
        #set predictor object value here...

    def lastToggled(self):
        self.toggleLabel.setText("Last option description goes here...")
        #set predictor object value here...

    def maxToggled(self):
        self.toggleLabel.setText("Max option description goes here...")
        #set predictor object value here...

    def minToggled(self):
        self.toggleLabel.setText("Min option description goes here...")
        #set predictor object value here...

    def medianToggled(self):
        self.toggleLabel.setText("Median option description goes here...")
        #set predictor object value here...

    def customToggled(self):
        self.toggleLabel.setText("Custom option description goes here...")
        #set predictor object value here...





