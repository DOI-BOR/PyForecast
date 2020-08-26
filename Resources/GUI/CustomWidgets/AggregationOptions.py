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

        # from /modules/miscellaneous/dataprocessor.py
        predictorAggregationOptions = ['accumulation', 'accumulation_cfs_kaf', 'average', 'first', 'last', 'max', 'min',
                                       'median', 'custom']
        predictorAggregationLabels = ['Accumulation', 'Accumulation (cfs to kaf)', 'Average', 'First', 'Last', 'Max',
                                      'Min', 'Median', 'Custom Pattern']


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

        # Display selected predictor info
        layout1.addWidget(QtWidgets.QLabel("Selected Predictor:"))
        layout1.addWidget(QtWidgets.QLabel("   selected predictor info and metadata - 1"))
        layout1.addWidget(QtWidgets.QLabel("   selected predictor info and metadata - 2"))
        layout1.addWidget(QtWidgets.QLabel("   selected predictor info and metadata - 3"))
        
        # Build, connect, and add the radio buttons
        self.radioGroup = QtWidgets.QGroupBox("Select a predictor aggregation scheme:")
        self.radioLayout = QtWidgets.QVBoxLayout()
        for i in range(len(predictorAggregationOptions)):
            radio = QtWidgets.QRadioButton(predictorAggregationLabels[i])
            radio.toggled.connect(self.radioToggled)
            self.radioLayout.addWidget(radio)

        self.customValString = QtWidgets.QLineEdit()
        self.customValString.setPlaceholderText(
            "Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        self.radioLayout.addWidget(self.customValString)
        self.radioGroup.setLayout(self.radioLayout)
        layout1.addWidget(self.radioGroup)
        
        # Create the help label
        self.toggleLabel = QtWidgets.QLabel("")
        layout1.addWidget(self.toggleLabel)

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
        if radioBtn.isChecked():
            self.toggleLabel.setText("Aggregation Scheme Info: " + radioBtn.text() + " option description goes here")
            # set predictor object value here...


    def applyPredictorAggregationOption(self):
        print('test')