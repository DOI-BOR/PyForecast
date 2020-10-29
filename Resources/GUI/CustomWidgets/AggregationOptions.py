from PyQt5 import QtWidgets, QtCore, QtGui
from resources.GUI.CustomWidgets.richTextButtons import richTextButton
from .DatasetList_HTML_Formatted import DatasetListHTMLFormattedMultiple

class AggregationOptions(QtWidgets.QWidget):

    def __init__(self, scrollable, orientation, parent=None):
        """
        Constructor for the Aggregation Options widget class.

        Parameters
        ----------
        self: AggregationOptions
        scrollable: bool
            True - Widget is in a QScrollArea, False - Widget is in a QVBoxLayout
        orientation: str
            Determines layout of the widget. Valid options are 'vertical' or 'horizontal'

        Returns
        -------
        None

        """
        QtWidgets.QWidget.__init__(self)
        self.parent = parent

        # Validate the layout orientation
        assert orientation == 'vertical' or orientation == 'horizontal', "Aggregation layout orientation is not understood."

        # Create the overall layout objects
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setContentsMargins(0, 0, 0, 0)

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
        self.activeSelection = DatasetListHTMLFormattedMultiple(self, addButtons=False)
        self.activeSelection.setContentsMargins(0, 0, 0, 0)
        self.activeSelection.setFixedHeight(114)
        self.activeSelection.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        layout1.addWidget(self.activeSelection)

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
        self.periodStart = QtWidgets.QDateEdit()
        self.periodStart.setDisplayFormat("MMMM d")
        self.periodStart.setCalendarPopup(True)
        #self.periodStart.calendarWidget().setNavigationBarVisible(False)
        self.periodStart.editingFinished.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(QtWidgets.QLabel("Start Date"), 1, 0)
        self.resamplingLayout.addWidget(self.periodStart, 1, 1, 1, 2)
        # Start month and day
        # self.periodStartMonth = QtWidgets.QDateEdit()
        # self.periodStartMonth.setDisplayFormat("MMMM")
        # self.periodStartMonth.setMinimumDate(QtCore.QDate(1999,10,1))
        # self.periodStartMonth.setMaximumDate(QtCore.QDate(2000,9,30))
        # self.periodStartMonth.setDate(QtCore.QDate(1999,10,1))
        # self.periodStartDay = QtWidgets.QDateEdit()
        # self.periodStartDay.setDisplayFormat("d")
        # self.periodStartMonth.editingFinished.connect(self.resamplingUpdate)
        # self.periodStartDay.editingFinished.connect(self.resamplingUpdate)
        # self.resamplingLayout.addWidget(QtWidgets.QLabel("Start Date"), 1, 0)
        # self.resamplingLayout.addWidget(self.periodStartMonth, 1, 1)
        # self.resamplingLayout.addWidget(self.periodStartDay, 1, 2)
        # Resampling time-step
        self.resamplingLayout.addWidget(QtWidgets.QLabel("Time-step"), 2, 0)
        self.tStepInteger = QtWidgets.QSpinBox()
        self.tStepInteger.setValue(1)
        self.tStepInteger.valueChanged.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(self.tStepInteger, 2, 1)
        self.tStepChar = QtWidgets.QComboBox()
        self.tStepChar.addItems(self.predictorResamplingLabels)
        self.tStepChar.setCurrentIndex(0)
        self.tStepChar.currentTextChanged.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(self.tStepChar, 2, 2)
        # Resampling frequency
        self.resamplingLayout.addWidget(QtWidgets.QLabel("Frequency"), 3, 0)
        self.freqInteger = QtWidgets.QSpinBox()
        self.freqInteger.setValue(1)
        self.freqInteger.valueChanged.connect(self.resamplingUpdate)
        self.resamplingLayout.addWidget(self.freqInteger, 3, 1)
        self.freqChar = QtWidgets.QComboBox()
        self.freqChar.addItems(self.predictorResamplingLabels)
        self.freqChar.currentTextChanged.connect(self.resamplingUpdate)
        self.freqChar.setCurrentIndex(2)
        self.resamplingUpdate()
        self.resamplingLayout.addWidget(self.freqChar, 3, 2)
        # Add to UI
        self.resamplingGroup.setLayout(self.resamplingLayout)


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
        self.radioLayout = QtWidgets.QGridLayout()
        self.radioButtons = QtWidgets.QButtonGroup()
        self.toggleLabel = QtWidgets.QLabel("placeholder")
        self.toggleLabel.setWordWrap(True)
        self.radioLayout.addWidget(self.toggleLabel, 0, 0, 1, 2)
        for i in range(len(self.predictorAggregationOptions)):
            radio = QtWidgets.QRadioButton(self.predictorAggregationLabels[i])
            radio.toggled.connect(self.radioToggled)
            if i==2:
                radio.setChecked(True)
            self.radioLayout.addWidget(radio)
            self.radioButtons.addButton(radio,i)

        self.customValString = QtWidgets.QLineEdit()
        self.customValString.setPlaceholderText(
            "Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        self.radioLayout.addWidget(self.customValString)
        # Add to UI
        self.radioGroup.setLayout(self.radioLayout)


        #########################################################################
        # Create predictor forcing checkbox
        self.predForceCheckBox = QtWidgets.QCheckBox("Force Predictor: Ensures that this predictor is used in every model.")
        self.predForceCheckBox.setChecked(False)
        layout1.addWidget(self.predForceCheckBox)

        #########################################################################
        # Add the container to the layout
        if scrollable:
            if orientation == 'vertical':
                # Setup a vertical layout orientation
                layoutVertical = QtWidgets.QVBoxLayout()
                layoutVertical.setContentsMargins(0, 0, 0, 0)

                # Cast the layout to a widget
                layout1Widget = QtWidgets.QWidget()
                layout1Widget.setLayout(layout1)

                # Add widgets into the vertical layout
                layoutVertical.addWidget(layout1Widget)
                layoutVertical.addWidget(self.resamplingGroup)
                layoutVertical.addWidget(self.radioGroup)
                layoutVertical.addWidget(self.predForceCheckBox)

                optionsWidget.setLayout(layoutVertical)
                scrollarea.setWidget(optionsWidget)

            else:
                # Setup a horizontal orientation
                layoutVertical = QtWidgets.QVBoxLayout()
                layoutVertical.setContentsMargins(0, 0, 0, 0)

                # Cast the layout to a widget
                layout1Widget = QtWidgets.QWidget()
                layout1Widget.setLayout(layout1)

                # Create a horizontal layout
                layoutHorizontal = QtWidgets.QHBoxLayout()
                layoutHorizontal.addWidget(layout1Widget)
                layoutHorizontal.addWidget(self.resamplingGroup)
                layoutHorizontal.addWidget(self.radioGroup)

                # Cast the layout to a widget
                layoutHorizontalWidget = QtWidgets.QWidget()
                layoutHorizontalWidget.setLayout(layoutHorizontal)

                # Add widgets into the vertical layout
                layoutVertical.addWidget(layoutHorizontalWidget)
                layoutVertical.addWidget(self.predForceCheckBox)

                optionsWidget.setLayout(layoutVertical)
                scrollarea.setWidget(optionsWidget)

        else:
            if orientation == 'vertical':
                # Setup a vertical layout orientation
                layoutVertical = QtWidgets.QVBoxLayout()
                layoutVertical.setContentsMargins(0, 0, 0, 0)

                # Cast the layout to a widget
                layout1Widget = QtWidgets.QWidget()
                layout1Widget.setLayout(layout1)

                # Add widgets into the vertical layout
                layoutVertical.addWidget(layout1Widget)
                layoutVertical.addWidget(self.resamplingGroup)
                layoutVertical.addWidget(self.radioGroup)
                layoutVertical.addWidget(self.predForceCheckBox)

                layoutVertical.addItem(QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
                self.setLayout(layoutVertical)

            else:
                # Setup a horizontal orientation
                layoutVertical = QtWidgets.QVBoxLayout()
                layoutVertical.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
                layoutVertical.setContentsMargins(0, 0, 0, 0)

                # Cast the layout to a widget
                layout1Widget = QtWidgets.QWidget()
                layout1Widget.setLayout(layout1)

                # Create a horizontal layout
                layoutHorizontal = QtWidgets.QHBoxLayout()
                layoutHorizontal.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
                # layoutHorizontal.addWidget(layout1Widget, QtCore.Qt.AlignCenter)
                layoutHorizontal.addWidget(self.resamplingGroup, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
                layoutHorizontal.addWidget(self.radioGroup, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

                # Cast the layout to a widget
                layoutHorizontalWidget = QtWidgets.QWidget()
                layoutHorizontalWidget.setLayout(layoutHorizontal)

                # Add widgets into the vertical layout
                layoutVertical.addWidget(layoutHorizontalWidget)
                layoutVertical.addWidget(self.predForceCheckBox)

                # layoutVertical.addItem(QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum))
                self.setLayout(layoutVertical)


    def radioToggled(self):
        radioBtn = self.sender()
        desc = self.predictorAggregationDescriptions[self.predictorAggregationLabels.index(radioBtn.text())]
        opt = self.predictorAggregationOptions[self.predictorAggregationLabels.index(radioBtn.text())]
        if radioBtn.isChecked():
            self.toggleLabel.setText("Selected Aggregation: " + radioBtn.text() + " - " + desc)
            self.selectedAggOption = opt


    def resamplingUpdate(self):
        tStepString = self.predictorResamplingLabels[self.tStepChar.currentIndex()]
        freqString = self.predictorResamplingLabels[self.freqChar.currentIndex()]
        tStepOption = self.predictorResamplingOptions[self.tStepChar.currentIndex()]
        freqOption = self.predictorResamplingOptions[self.freqChar.currentIndex()]
        self.selectedAggPeriod = "R/" + self.periodStart.date().toString('yyyy-MM-dd') + "/P" + self.tStepInteger.text() + tStepOption + \
                                 "/" + "F" + self.freqInteger.text() + freqOption  # (e.g. R/1978-02-01/P1M/F1Y)
        self.resampleDescription.setText("Defined Resampling: Starting " + self.periodStart.text() + ", take " + self.tStepInteger.text() +
                                         " " + tStepString + "(s) of data, and make 1 value every " + self.freqInteger.text() + " " +
                                         freqString + "(s) (ISO 8601 Pattern: " + self.selectedAggPeriod + ")")
