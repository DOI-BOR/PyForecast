from PyQt5 import QtWidgets, QtCore, QtGui
from resources.GUI.CustomWidgets.richTextButtons import richTextButton

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
            scrollarea.setMinimumHeight(400)
            scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            optionsWidget = QtWidgets.QWidget()

        #########################################################################
        # Display selected predictor info
        layout1.addWidget(QtWidgets.QLabel("Selected Predictor:"))
        layout1.addWidget(QtWidgets.QLabel("   selected predictor info and metadata - 1"))
        layout1.addWidget(QtWidgets.QLabel("   selected predictor info and metadata - 2"))
        layout1.addWidget(QtWidgets.QLabel("   selected predictor info and metadata - 3"))

        #########################################################################
        # Set predictor resampling period
        self.predictorResamplingOptions = ['M', 'D', 'Y']
        self.predictorResamplingLabels = ['Month', 'Day', 'Year']

        self.resamplingGroup = QtWidgets.QGroupBox("Define a resampling scheme:")
        self.resamplingLayout = QtWidgets.QGridLayout()
        self.resampleDescription = QtWidgets.QLabel("placeholder")
        self.resampleDescription.setWordWrap(True)
        self.resamplingLayout.addWidget(self.resampleDescription, 0, 0, 1, 3)
        # Start and end dates
        self.periodStart = QtWidgets.QDateTimeEdit()
        self.periodStart.setDisplayFormat("MMMM d yyyy")
        self.periodStart.setCalendarPopup(True)
        self.periodStart.editingFinished.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(QtWidgets.QLabel("Start Date"), 1, 0)
        self.resamplingLayout.addWidget(self.periodStart, 1, 1, 1, 2)
        # self.periodEnd = QtWidgets.QDateTimeEdit()
        # self.periodEnd.setDisplayFormat("MMMM d yyyy")
        # self.periodEnd.setCalendarPopup(True)
        # self.resamplingLayout.addWidget(QtWidgets.QLabel("End Date"), 1, 0)
        # self.resamplingLayout.addWidget(self.periodEnd, 1, 1)
        # Resampling time-step
        self.resamplingLayout.addWidget(QtWidgets.QLabel("Time-step"), 2, 0)
        self.tStepInteger = QtWidgets.QSpinBox()
        self.tStepInteger.setValue(1)
        self.tStepInteger.valueChanged.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(self.tStepInteger, 2, 1)
        self.tStepChar = QtWidgets.QComboBox()
        self.tStepChar.addItems(self.predictorResamplingLabels)
        self.tStepChar.setCurrentIndex(0)
        self.tStepChar.currentIndexChanged.connect(lambda: self.resamplingUpdate)
        self.resamplingLayout.addWidget(self.tStepChar, 2, 2)
        # Resampling frequency
        self.resamplingLayout.addWidget(QtWidgets.QLabel("Frequency"), 3, 0)
        self.freqInteger = QtWidgets.QSpinBox()
        self.freqInteger.setValue(1)
        self.freqInteger.valueChanged.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(self.freqInteger, 3, 1)
        self.freqChar = QtWidgets.QComboBox()
        self.freqChar.addItems(self.predictorResamplingLabels)
        self.freqChar.currentIndexChanged.connect(lambda: self.resamplingUpdate)
        self.freqChar.setCurrentIndex(2)
        self.resamplingUpdate()
        self.resamplingLayout.addWidget(self.freqChar, 3, 2)
        # Add to UI
        self.resamplingGroup.setLayout(self.resamplingLayout)
        layout1.addWidget(self.resamplingGroup)

        #########################################################################
        # Set predictor method
        # from /modules/miscellaneous/dataprocessor.py
        self.predictorAggregationOptions = ['accumulation', 'accumulation_cfs_kaf', 'average', 'first', 'last', 'max', 'min',
                                       'median', 'custom']
        self.predictorAggregationLabels = ['Accumulation', 'Accumulation (cfs to kaf)', 'Average', 'First', 'Last', 'Max',
                                      'Min', 'Median', 'Custom Pattern']
        self.predictorAggregationDescriptions = [
            'Sum the values for the resampling period',
            'Sum the \'cfs\' values for the resampling period and convert it to \'acre-feet\'',
            'Take the average of the values for the resampling period',
            'Take the first value for the resampling period',
            'Take the last value for the resampling period',
            'Take the maximum value for the resampling period',
            'Take the minimum value for the resampling period',
            'Take the median value for the resampling period',
            'Do some ISO8601 magickery!',
        ]
        # Build, connect, and add the radio buttons
        self.radioGroup = QtWidgets.QGroupBox("Select a predictor aggregation scheme:")
        self.radioLayout = QtWidgets.QVBoxLayout()
        self.toggleLabel = QtWidgets.QLabel("placeholder")
        self.toggleLabel.setWordWrap(True)
        self.radioLayout.addWidget(self.toggleLabel)
        for i in range(len(self.predictorAggregationOptions)):
            radio = QtWidgets.QRadioButton(self.predictorAggregationLabels[i])
            radio.toggled.connect(self.radioToggled)
            if i==2:
                radio.setChecked(True)
            self.radioLayout.addWidget(radio)

        self.customValString = QtWidgets.QLineEdit()
        self.customValString.setPlaceholderText(
            "Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        self.radioLayout.addWidget(self.customValString)
        # Add to UI
        self.radioGroup.setLayout(self.radioLayout)
        layout1.addWidget(self.radioGroup)

        #########################################################################
        # Create the apply button
        self.predictorApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.predictorApplyButton.setMaximumSize(125, 50)
        self.predictorApplyButton.clicked.connect(self.applyPredictorAggregationOption)
        layout1.addWidget(self.predictorApplyButton)

        # Add the container to the layout
        if scrollable:
            optionsWidget.setLayout(layout1)
            scrollarea.setWidget(optionsWidget)
        else:
            layout1.addItem(QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
            self.setLayout(layout1)


    def radioToggled(self):
        radioBtn = self.sender()
        desc = self.predictorAggregationDescriptions[self.predictorAggregationLabels.index(radioBtn.text())]
        if radioBtn.isChecked():
            self.toggleLabel.setText("Selected Aggregation: " + radioBtn.text() + " - " + desc)
            # set predictor object value here...

    def resamplingUpdate(self):
        tStepString = self.predictorResamplingLabels[self.tStepChar.currentIndex()]
        freqString = self.predictorResamplingLabels[self.freqChar.currentIndex()]
        self.resampleDescription.setText("Defined Resampling: " + self.periodStart.text() + ", take " + self.tStepInteger.text() + " " + tStepString + "(s) of data, and make 1 value every " + self.freqInteger.text() + " " + freqString + "(s)")

    def applyPredictorAggregationOption(self):
        print('test')