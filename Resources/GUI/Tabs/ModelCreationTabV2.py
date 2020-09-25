"""
Script Name:    ModelCreationTabV2.py

Description:    Defines the layout for the Model Creation Tab. Includes all the sub-widgets
                for the stacked widget.
"""

# Import Libraries
from PyQt5 import QtWidgets, QtCore, QtGui

from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetListHTMLFormatted, DatasetListHTMLFormattedMultiple
from resources.GUI.CustomWidgets.DoubleList import DoubleListMultipleInstance
from resources.GUI.CustomWidgets.AggregationOptions import AggregationOptions
from resources.GUI.CustomWidgets.PyQtGraphs import ModelTabPlots, TimeSeriesLineBarPlot, DatasetTimeseriesPlots
from resources.GUI.CustomWidgets.customTabs import EnhancedTabWidget
from resources.GUI.CustomWidgets.richTextButtons import richTextButton, richTextButtonCheckbox, richTextDescriptionButton
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetViewOperations
from resources.GUI.WebMap import webMapView
# import pandas as pd
import numpy as np
from dateutil import parser

from resources.modules.StatisticalModelsTab.Operations.Fill import *

class ModelCreationTab(QtWidgets.QWidget):
    """
    This is the overall tab layout. 
    """

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent, objectName = 'tabPage')
        
        self.parent = parent

        # Set up the overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        overallLayout.setContentsMargins(0,0,0,0)
        overallLayout.setSpacing(0)
        self.overallStackWidget = QtWidgets.QStackedWidget()
        targetSelectLayout = QtWidgets.QVBoxLayout()
        predictorLayout = QtWidgets.QVBoxLayout()
        optionsLayout = QtWidgets.QVBoxLayout()
        summaryLayout = QtWidgets.QVBoxLayout()
        workflowLayout = QtWidgets.QVBoxLayout()


        self.workflowWidget = EnhancedTabWidget(self, 'above', 'vertical', True, False, True)

        # ===================================================================================================================

        # Layout the Target Selection Widget
        widg = QtWidgets.QWidget()
        widg.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        layout = QtWidgets.QGridLayout()
        self.dataPlot = ModelTabPlots(self, objectName='ModelTabPlot')
        self.dataPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.targetSelect = QtWidgets.QComboBox()
        self.datasetList = DatasetListHTMLFormatted(self, datasetTable = self.parent.datasetTable, addButtons=False)
        self.targetSelect.setModel(self.datasetList.model())
        self.targetSelect.setView(self.datasetList)

        #layout.addRow("Forecast Target", self.targetSelect)
        layout.addWidget(QtWidgets.QLabel("Forecast Target"), 0, 0)
        layout.addWidget(self.targetSelect, 0, 1)
        
        self.selectedItemDisplay = DatasetListHTMLFormatted(self, addButtons=False, objectName='ModelTargetList')
        self.selectedItemDisplay.setFixedHeight(99)
        self.selectedItemDisplay.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        layout.addWidget(self.selectedItemDisplay, 1, 0, 1, 2)
        
        self.periodStart = QtWidgets.QDateTimeEdit()
        self.periodStart.setDisplayFormat("MMMM d")
        self.periodStart.setCalendarPopup(True)
        self.periodStart.setMinimumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1))
        self.periodStart.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))
        self.periodEnd = QtWidgets.QDateTimeEdit()
        self.periodEnd.setDisplayFormat("MMMM d")
        self.periodEnd.setCalendarPopup(True)
        self.periodEnd.setMinimumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1))
        self.periodEnd.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))

        #layout.addRow("Target Period (Start)", self.periodStart)
        layout.addWidget(QtWidgets.QLabel("Target Period (Start)"), 2, 0)
        layout.addWidget(self.periodStart, 2,1)
        
        #layout.addRow("Target Period (End)", self.periodEnd)
        layout.addWidget(QtWidgets.QLabel("Target Period (End)"), 3, 0)
        layout.addWidget(self.periodEnd, 3,1)

        # Initialize dates
        self.periodStart.setDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 4, 1))
        self.periodEnd.setDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 7, 31))

        self.methodCombo = QtWidgets.QComboBox()
        itemList = [
            ("Accumulation - CFS to KAF (Accumulate the values over the period and convert to 1000 Acre-Feet)", "accumulation_cfs_kaf"),
            ("Accumulation (Accumulate the values over the period)", "accumulation"),
            ("Average (Average value over the forecast period)","average"),
            ("Minimum (Minimum value over the forecast period)", "min"),
            ("Maximum (Maximum value over the forecast period)", "max"),
            ("First (First value of the forecast period)", "first"),
            ("Custom (Define a custom aggregator function)", "custom")
        ]
        for item in itemList:
            self.methodCombo.addItem(item[0], item[1])
        #layout.addRow("Period Calculation", self.methodCombo)
        layout.addWidget(QtWidgets.QLabel("Period Calculation"), 4, 0)
        layout.addWidget(self.methodCombo, 4,1)

        self.customMethodSpecEdit = QtWidgets.QLineEdit()
        self.customMethodSpecEdit.setPlaceholderText("Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        layout.addWidget(self.customMethodSpecEdit, 5, 0, 1, 2)
        self.customMethodSpecEdit.hide()

        # Create the apply button
        self.predictandApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.predictandApplyButton.setMaximumSize(125, 50)
        self.predictandApplyButton.clicked.connect(self.applyPredictandAggregationOption)
        layout.addWidget(self.predictandApplyButton, 6, 0, 1, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 10)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        
        widg.setLayout(layout)
        #widg.setStyleSheet("""QWidget {border: 1px solid red}""")
        widg.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.dataPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        targetSelectLayout.addWidget(widg)
        targetSelectLayout.addWidget(self.dataPlot)
        widg = QtWidgets.QWidget()
        widg.setLayout(targetSelectLayout)
        self.workflowWidget.addTab(widg, "FORECAST<br>TARGET", "resources/GraphicalResources/icons/target-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ===================================================================================================================
        ### Layout the predictor selector widget ###
        # Create the icon on the left side of the screen
        predictorWidget = QtWidgets.QWidget()

        # Setup the initial items
        predictorScrollableArea = QtWidgets.QScrollArea()
        predictorScrollableArea.setWidgetResizable(True)
        predictorLayout = QtWidgets.QVBoxLayout()
        predictorLayout.setContentsMargins(0, 0, 0, 0)

        # Create the initial dialog for the type of analysis
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Mode: <strong>')
        label.setFixedWidth(100)

        self.defaultPredictorButton = QtWidgets.QRadioButton("Default")
        self.defaultPredictorButton.setChecked(True)
        self.defaultPredictorButton.setFixedWidth(100)
        self.expertPredictorButton = QtWidgets.QRadioButton("Expert")
        self.expertPredictorButton.setFixedWidth(100)

        bgroup = QtWidgets.QButtonGroup()
        bgroup.addButton(self.defaultPredictorButton)
        bgroup.addButton(self.expertPredictorButton)
        bgroup.setExclusive(True)

        predictorModeLayout = QtWidgets.QHBoxLayout()
        predictorModeLayout.addWidget(label)
        predictorModeLayout.addWidget(self.defaultPredictorButton)
        predictorModeLayout.addWidget(self.expertPredictorButton)
        predictorModeLayout.setAlignment(QtCore.Qt.AlignLeft)

        gb = QtWidgets.QGroupBox("")
        gb.setLayout(predictorModeLayout)
        predictorLayout.addWidget(gb)

        # Space between the setup options and the tabs
        predictorLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        # Create the layout for the simple analysis
        self.layoutPredictorSimpleAnalysis = QtWidgets.QScrollArea()
        self.layoutPredictorSimpleAnalysis.setContentsMargins(15, 15, 15, 15)
        self.layoutPredictorSimpleAnalysis.setWidgetResizable(True)
        self.layoutPredictorSimpleAnalysis.setFrameShape(QtWidgets.QFrame.NoFrame)

        # Create the layout object for the expert analysis
        self.layoutPredictorExpertAnalysis = QtWidgets.QVBoxLayout()
        self.layoutPredictorExpertAnalysis.setContentsMargins(15, 15, 15, 15)

        ### Create the simple analysis tab ###
        # Fill the remaining area with the layout options
        self._createSimplePredictorLayout(self.layoutPredictorSimpleAnalysis)

        ### Create the layout data tab ###
        ## Create the initial scrollable area and layout ##
        # Create the scrollable area and set it to resizeable
        layoutDataSA = QtWidgets.QScrollArea()
        layoutDataSA.setWidgetResizable(True)

        # Create the initial box layout
        layoutData = QtWidgets.QHBoxLayout()

        ## Add the webmap object to the current layout ##
        self.webMapView = webMapView.webMapView()
        layoutData.addWidget(self.webMapView)

        ## Setup the DoubleList object ##
        # Create the doublelist
        self.layoutDataDoubleList = DoubleListMultipleInstance(self.parent.datasetTable,
                                                               '<strong style="font-size: 18px">Available Datasets<strong>',
                                                               '<strong style="font-size: 18px">Selected Datasets<strong>',
                                                               operations_dataframe=self.parent.datasetOperationsTable)

        # Connect the DoubleList with the dataset hmtl list to keep everything in sync. This will automatically
        # populate the DoubleList entries
        self.datasetList.updateSignalToExternal.connect(self.layoutDataDoubleList.update)

        # Connect the doublelists together. This will keep the selection in sync between the simple and expert modes
        self.layoutDataDoubleList.updatedLinkedList.connect(self.layoutSimpleDoubleList.updateLinkedDoubleLists)
        self.layoutSimpleDoubleList.updatedLinkedList.connect(self.layoutDataDoubleList.updateLinkedDoubleLists)

        # Link the expert doublelist to the model operations table. Since the double lists are linked together, linking
        # only one is sufficient to ensure the table is always up-to-date
        self.layoutDataDoubleList.updatedOutputList.connect(self.layoutDataDoubleList.updateLinkedOperationsTables)

        # todo: Update the positions on the map

        # Add the widget to the layout
        layoutData.addWidget(self.layoutDataDoubleList)

        ## Finalize the tab format ##
        # Wrap the layout as a widget to make it compatible with the SA layout
        layoutDataSA.setLayout(layoutData)


        ### Create the layout fill tab ###
        # Create the scrollable area
        layoutFillSA = QtWidgets.QScrollArea()
        layoutFillSA.setWidgetResizable(True)

        # Fill the remaining area with the layout options
        self._createDataFillLayout(layoutFillSA)


        ### Create the layout extend tab ###
        # Create the scrollable area
        layoutExtendSA = QtWidgets.QScrollArea()
        layoutExtendSA.setWidgetResizable(True)

        # Fill the remaining area with the layout options
        self._createDataExtendLayout(layoutExtendSA)


        ### Create the layout window tab ###
        # Create the scrollable area
        layoutWindowSA = QtWidgets.QScrollArea()
        layoutWindowSA.setWidgetResizable(True)

        # Fill the remaining area with the layout options
        self._createDataWindowLayout(layoutWindowSA)


        ### Add the subtabs into the tab widget ###
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(layoutDataSA, 'Data')
        tabWidget.addTab(layoutFillSA, 'Fill')
        tabWidget.addTab(layoutExtendSA, 'Extend')
        tabWidget.addTab(layoutWindowSA, 'Window')

        # Add to the expert layout
        self.layoutPredictorExpertAnalysis.addWidget(tabWidget)
        expertPredictorWidget = QtWidgets.QWidget()
        expertPredictorWidget.setLayout(self.layoutPredictorExpertAnalysis)

        # Create the stacked widget to handle to toggle between simple and expert analyses
        self.stackedPredictorWidget = QtWidgets.QStackedLayout()
        self.stackedPredictorWidget.addWidget(self.layoutPredictorSimpleAnalysis)
        self.stackedPredictorWidget.addWidget(expertPredictorWidget)

        self.stackedPredictorWidget.setCurrentIndex(0)
        self.defaultPredictorButton.clicked.connect(self.setPredictorDefaultStack)
        self.expertPredictorButton.clicked.connect(self.setPredictorExpertStack)
        
        stackedModePredictorWidget = QtWidgets.QWidget()
        stackedModePredictorWidget.setLayout(self.stackedPredictorWidget)

        predictorLayout.addWidget(stackedModePredictorWidget)
        predictorWidget.setLayout(predictorLayout)
        predictorScrollableArea.setWidget(predictorWidget)
        self.workflowWidget.addTab(predictorScrollableArea, "PREDICTORS", "resources/GraphicalResources/icons/bullseye-24px.svg",
                                   "#FFFFFF", iconSize=(66, 66))

        # ====================================================================================================================
        # Layout the Forecast Settings widget
        # Create the scrollable area
        SA = QtWidgets.QScrollArea()
        SA.setWidgetResizable(True)

        # Construct the layout object
        optionsLayout = self._createOptionsTabLayout()

        # Set the layout into the widget
        widg = QtWidgets.QWidget()
        widg.setLayout(optionsLayout)

        # Add the widget to the scrollable area
        SA.setWidget(widg)
        self.workflowWidget.addTab(SA, "OPTIONS", "resources/GraphicalResources/icons/tune-24px.svg", "#FFFFFF", iconSize=(66,66))


        # ====================================================================================================================
        ### Create the summary scrollabe area ###
        # Create the scrollable area
        summarySA = QtWidgets.QScrollArea()
        summarySA.setWidgetResizable(True)

        # Lay out the summary widget
        summaryWidget = QtWidgets.QWidget()

        # Create the horizontal layout widget
        summaryLayout = QtWidgets.QHBoxLayout()

        ### Setup the layout ###
        # Create the layout by calling to the setup function, returning a layout object
        self._createSummaryTabLayout(summaryLayout)

        ### Add the layout to the main window ###
        # Wrap the summary layout in the widget
        summaryWidget.setLayout(summaryLayout)

        # Wrap the scrollable area in a widget
        summarySA.setWidget(summaryWidget)

        self.workflowWidget.addTab(summarySA, "SUMMARY", "resources/GraphicalResources/icons/clipboard-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ====================================================================================================================
        ### Create the results scrollabe area ###
        # Create the scrollable area
        resultsSA = QtWidgets.QScrollArea()
        resultsSA.setWidgetResizable(True)

        # Setup the layout
        self._createResultsTabLayout(resultsSA)

        # Layout the results widget
        self.workflowWidget.addTab(resultsSA, "RESULTS", "resources/GraphicalResources/icons/run-24px.svg", "#FFFFFF", iconSize=(66,66))
        
        overallLayout.addWidget(self.workflowWidget)
        #overallLayout.addWidget(self.overallStackWidget)
        self.setLayout(overallLayout)

        # ====================================================================================================================
        # Create an update method for when the tab widget gets changed to refresh elements
        self.workflowWidget.currentChanged.connect(self._updateTabDependencies)


    def _createSimplePredictorLayout(self, predictorLayoutSimple):
        """
        Lays out the full simple predictor tab

        Parameters
        ----------
        predictorLayoutSimple: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the DoubleList selector object ##
        self.layoutSimpleDoubleList = DoubleListMultipleInstance(self.parent.datasetTable,
                                                                 '<strong style="font-size: 18px">Available Datasets<strong>',
                                                                 '<strong style="font-size: 18px">Selected Datasets<strong>')

        ## Connect row-change event on the output list to the aggregation options widget ##
        self.layoutSimpleDoubleList.listOutput.currentRowChanged.connect(self._updateSimpleLayoutAggregationOptions)

        # Connect the DoubleList with the dataset hmtl list to keep everything in sync. This will automatically
        # populate the DoubleList entries
        self.datasetList.updateSignalToExternal.connect(self.layoutSimpleDoubleList.update)

        ## Create the objects on the right side ##
        # Aggregation options widget
        self.layoutAggregationOptions = AggregationOptions(False, orientation='vertical')

        # Simple fill
        self.layoutSimpleFill = richTextDescriptionButton(self,
                                                          '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                                                              'Fill data',
                                                              'Automatically fill the selected time series using default properties'))
        # self.layoutSimpleFill2 = QtWidgets.QCheckBox("Fill data: Automatically fill the selected time series using default properties")
        # self.layoutSimpleFill2.setChecked(False)

        # Simple extend
        self.layoutSimpleExtend = richTextDescriptionButton(self,
                                                            '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                                                                'Extend data',
                                                                'Automatically extend the selected time series using default properties'))
        # self.layoutSimpleExtend2 = QtWidgets.QCheckBox("Extend data: Automatically extend the selected time series using default properties")
        # self.layoutSimpleExtend2.setChecked(False)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutSimpleClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutSimpleClearButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the clear function
        self.layoutSimpleClearButton.clicked.connect(self._applySimpleClear)
        # self.layoutSimpleClearButton.clicked.connect(self._updateSimpleSubtab)

        # Create the apply button
        self.layoutSimpleApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutSimpleApplyButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the apply function
        self.layoutSimpleApplyButton.clicked.connect(self._applySimpleOptions)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutSimpleClearButton)
        buttonLayout.addWidget(self.layoutSimpleApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)

        ## Add the widgets into the layout ##
        # Add the items into the horizontal spacer
        layoutSimple = QtWidgets.QHBoxLayout()
        layoutSimple.setContentsMargins(0, 0, 0, 0)
        layoutSimple.addWidget(self.layoutSimpleDoubleList, 2)
        layoutSimple.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        # Create the right side options layout
        layoutSimpleOptions = QtWidgets.QVBoxLayout()
        layoutSimpleOptions.setAlignment(QtCore.Qt.AlignTop)
        layoutSimpleOptions.addWidget(self.layoutAggregationOptions)
        layoutSimpleOptions.addWidget(self.layoutSimpleFill)
        layoutSimpleOptions.addWidget(self.layoutSimpleExtend)
        layoutSimpleOptions.addWidget(buttonLayoutWidget)

        # Wrap the right side layout in another widget
        layoutSimpleOptionsWidget = QtWidgets.QWidget()
        layoutSimpleOptionsWidget.setLayout(layoutSimpleOptions)

        # Add the right side to the simple layout
        layoutSimple.addWidget(layoutSimpleOptionsWidget, 1)

        # Set the items into the simple layout
        predictorLayoutSimple.setLayout(layoutSimple)


    def _updateSimpleLayoutAggregationOptions(self):
        if self.layoutSimpleDoubleList.listOutput.currentIndex().row() >= 0:
            # Get the current datasest index
            currentIndex = self.layoutSimpleDoubleList.listOutput.datasetTable.index[self.layoutSimpleDoubleList.listOutput.currentIndex().row()]

            # Get the current dataset and operations settings
            datasetInfo = self.fillList.datasetTable.loc[currentIndex]["DatasetName"] + " - " + \
                          self.fillList.datasetTable.loc[currentIndex]["DatasetParameter"] + " " + \
                          str(self.fillList.datasetTable.loc[currentIndex].name)
            accumMethod = str(self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])
            accumPeriod = str(self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'])
            predForcing = str(self.parent.datasetOperationsTable.loc[currentIndex]['ForcingFlag'])

            self.layoutAggregationOptions.aggLabel1.setText('<strong style="font-size: 18px">Selected Predictor: ' + datasetInfo + '<strong>')
            self.layoutAggregationOptions.aggLabel2.setText("     Accumulation Method: " + accumMethod)
            self.layoutAggregationOptions.aggLabel3.setText("     Accumulation Period: " + accumPeriod)
            self.layoutAggregationOptions.aggLabel4.setText("     Forced Flag: " + predForcing)

            # Set date selector range
            minT = parser.parse(str(np.sort(list(set(self.parent.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[0]))
            maxT = parser.parse(str(np.sort(list(set(self.parent.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))
            self.layoutAggregationOptions.periodStart.minimumDate = minT
            self.layoutAggregationOptions.periodStart.maximumDate = maxT
            self.layoutAggregationOptions.periodStart.setDate(minT)

            # Set aggregation option on UI
            if accumMethod == 'None':
                self.layoutAggregationOptions.aggLabel2.setStyleSheet("color : red")
            else: #set defined aggregation scheme
                self.layoutAggregationOptions.aggLabel2.setStyleSheet("color : green")
                defIdx = self.layoutAggregationOptions.predictorAggregationOptions.index(accumMethod)
                self.layoutAggregationOptions.radioButtons.button(defIdx).setChecked(True)

            # Set aggregation period on UI
            if accumPeriod == 'None':
                self.layoutAggregationOptions.aggLabel3.setStyleSheet("color : red")
            else: #set defined resampling period options
                self.layoutAggregationOptions.aggLabel3.setStyleSheet("color : green")
                predPeriodItems = accumPeriod.split("/") #R/1978-03-01/P1M/F12M
                self.layoutAggregationOptions.periodStart.setDate(parser.parse(predPeriodItems[1]))
                predPeriodPStep = str(predPeriodItems[2])[-1]
                a = self.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodPStep)
                self.layoutAggregationOptions.tStepChar.setCurrentIndex(self.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodPStep))
                predPeriodPNum = ''.join(map(str,[int(s) for s in predPeriodItems[2] if s.isdigit()]))
                self.layoutAggregationOptions.tStepInteger.setValue(int(predPeriodPNum))
                predPeriodFStep = str(predPeriodItems[3])[-1]
                self.layoutAggregationOptions.freqChar.setCurrentIndex(self.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodFStep))
                predPeriodFNum = ''.join(map(str,[int(s) for s in predPeriodItems[3] if s.isdigit()]))
                self.layoutAggregationOptions.freqInteger.setValue(int(predPeriodFNum))

            # Set forcing flag on UI
            if predForcing == 'None':
                self.layoutAggregationOptions.aggLabel4.setStyleSheet("color : red")
            else: #set defined forcing flag
                self.layoutAggregationOptions.aggLabel4.setStyleSheet("color : green")
                self.layoutAggregationOptions.predForceCheckBox.setChecked(predForcing == 'True')
        else:
            self.layoutAggregationOptions.aggLabel1.setText('<strong style="font-size: 18px">No Predictor Selected<strong>')
            self.layoutAggregationOptions.aggLabel2.setText("     Accumulation Method: NA")
            self.layoutAggregationOptions.aggLabel3.setText("     Accumulation Period: NA")
            self.layoutAggregationOptions.aggLabel4.setText("     Forced Flag: NA")

        self.layoutAggregationOptions.resamplingUpdate()


    def _createDataFillLayout(self, layoutFillSA):
        """
        Lays out the fill subtab in the expert predictor mode

        Parameters
        ----------
        layoutFillSA: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the selector list ##
        # Create a vertical layout
        layoutFillLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutFillLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Add the list
        self.fillList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.fillList.refreshDatasetListFromExtenal)
        layoutFillLeftLayout.addWidget(self.fillList)

        # Connect the list widget to the right panel to adjust the display
        self.fillList.currentRowChanged.connect(self._updateFillOptionsOnDataset)

        ## Create the right panel ##
        # Create the vertical layout
        layoutFillRightLayout = QtWidgets.QVBoxLayout()

        # Set the options available for filling the data
        fillOptions = ['None', 'Nearest', 'Linear', 'Quadratic', 'Cubic', 'Spline', 'Polynomial']

        # Create and add a dropdown selector with the available options
        layoutFillRightLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Fill Method<strong>'))

        self.layoutFillMethodSelector = QtWidgets.QComboBox()
        self.layoutFillMethodSelector.addItems(fillOptions)
        layoutFillRightLayout.addWidget(self.layoutFillMethodSelector)

        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        layoutFillRightLayout.addWidget(lineA)

        # Create the fill limit label
        self.layoutFillGapLimitLabel = QtWidgets.QLabel('Maximum Filled Gap')
        self.layoutFillGapLimitLabel.setVisible(False)
        self.layoutFillGapLimitLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        # Create the fill limit widget
        self.layoutFillGapLimit = QtWidgets.QLineEdit()
        self.layoutFillGapLimit.setPlaceholderText('30')
        self.layoutFillGapLimit.setVisible(False)
        self.layoutFillGapLimit.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Maximum)

        # Create the fill order widget label
        self.layoutFillOrderLabel = QtWidgets.QLabel('Fill order')
        self.layoutFillOrderLabel.setVisible(False)
        self.layoutFillOrderLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        # Create the fill order widget
        self.layoutFillOrder = QtWidgets.QComboBox()
        self.layoutFillOrder.addItems([str(x) for x in range(1, 11, 1)])
        self.layoutFillOrder.setVisible(False)
        self.layoutFillOrder.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Maximum)

        # Create the layout for the fill limit
        filledGapLayout = QtWidgets.QHBoxLayout()
        filledGapLayout.setAlignment(QtCore.Qt.AlignTop)
        filledGapLayout.addWidget(self.layoutFillGapLimitLabel)
        filledGapLayout.addWidget(self.layoutFillGapLimit)
        filledGapLayout.setContentsMargins(0, 0, 0, 0)

        # Create the layout for the fill order
        filledOrderLayout = QtWidgets.QHBoxLayout()
        filledOrderLayout.setAlignment(QtCore.Qt.AlignTop)
        filledOrderLayout.addWidget(self.layoutFillOrderLabel)
        filledOrderLayout.addWidget(self.layoutFillOrder)
        filledOrderLayout.setContentsMargins(0, 0, 0, 0)

        # Crate the widgets to wrap the conserved buttons
        filledGapLayoutWidget = QtWidgets.QWidget()
        filledGapLayoutWidget.setLayout(filledGapLayout)

        filledOrderLayoutWidget = QtWidgets.QWidget()
        filledOrderLayoutWidget.setLayout(filledOrderLayout)

        # Create a layout, widget for the conserved widgets and add to the right layout
        filledTopOptionsLayout = QtWidgets.QHBoxLayout()
        filledTopOptionsLayout.addWidget(filledGapLayoutWidget)
        filledTopOptionsLayout.addWidget(filledOrderLayoutWidget)
        filledTopOptionsLayout.setContentsMargins(0, 0, 0, 0)

        filledTopOptionsLayoutWidget = QtWidgets.QWidget()
        filledTopOptionsLayoutWidget.setLayout(filledTopOptionsLayout)
        layoutFillRightLayout.addWidget(filledTopOptionsLayoutWidget)

        # Adjust the layout of the widgets
        layoutFillRightLayout.setAlignment(QtCore.Qt.AlignTop)

        ### Create the nearest page ###
        nearestLayout = QtWidgets.QGridLayout()

        ### Create the linear page ###
        linearLayout = QtWidgets.QGridLayout()

        ### Create the quadratic page ###
        quadradicLayout = QtWidgets.QGridLayout()

        ### Create the cubic page ###
        cubicLayout = QtWidgets.QGridLayout()

        ### Create the polynomial page ###
        polyLayout = QtWidgets.QGridLayout()

        ### Create the stacked layout ###
        # Initialize the layout
        self.stackedFillLayout = QtWidgets.QStackedLayout()

        # Wrap it in a widget and set visibility to false. If this is not done, a small, annoying popup window will
        # be opened separate from the main window
        stackedWidget = QtWidgets.QWidget()
        stackedWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        stackedWidget.setLayout(self.stackedFillLayout)
        stackedWidget.setVisible(False)

        # Add each of the interpolation types to it
        nearestWidget = QtWidgets.QWidget()
        nearestWidget.setLayout(nearestLayout)
        nearestWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(nearestWidget)

        linearWidget = QtWidgets.QWidget()
        linearWidget.setLayout(linearLayout)
        linearWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(linearWidget)

        quadradicWidget = QtWidgets.QWidget()
        quadradicWidget.setLayout(quadradicLayout)
        quadradicWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(quadradicWidget)

        cubicWidget = QtWidgets.QWidget()
        cubicWidget.setLayout(cubicLayout)
        cubicWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(cubicWidget)

        splineWidget = QtWidgets.QWidget()
        splineWidget.setLayout(polyLayout)
        splineWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(splineWidget)

        # Add the stacked layout to the main layout
        layoutFillRightLayout.addWidget(stackedWidget)
        stackedWidget.setVisible(True)

        ### Create the plot that shows the result of the selection ###
        # Create the plot
        self.layoutFillPlot = DatasetTimeseriesPlots(None)
        self.layoutFillPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # Add it into the layout
        layoutFillRightLayout.addWidget(self.layoutFillPlot)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutFillClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutFillClearButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the clear function
        self.layoutFillClearButton.clicked.connect(self._applyFillClearToDataset)
        self.layoutFillClearButton.clicked.connect(self._updateFillSubtab)

        # Create the apply button
        self.layoutFillApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutFillApplyButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the apply function
        self.layoutFillApplyButton.clicked.connect(self._applyFillOptionsToDataset)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutFillClearButton)
        buttonLayout.addWidget(self.layoutFillApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)
        layoutFillRightLayout.addWidget(buttonLayoutWidget)

        ### Connect the stacked widget with the selection combo box ###
        self.layoutFillMethodSelector.currentIndexChanged.connect(self._updateFillSubtab)

        ### Connect the fill plot with the layout options ###
        # todo: build this

        ### Create the full layout ###
        layoutFill = QtWidgets.QHBoxLayout()

        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutFillLeftLayout)
        layoutFill.addWidget(leftWidget, 1)

        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutFillRightLayout)
        layoutFill.addWidget(rightWidget, 2)

        layoutFillSA.setLayout(layoutFill)

    def _createDataExtendLayout(self, layoutExtendSA):
        """
        Lays out the extend subtab in the expert predictor mode

        Parameters
        ----------
        layoutExtendSA: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the selector list ##
        # Create a vertical layout
        layoutExtendLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutExtendLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Connect and add the list
        self.extendList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.extendList.refreshDatasetListFromExtenal)
        layoutExtendLeftLayout.addWidget(self.extendList)

        # Connect the list widget to the right panel to adjust the display
        self.extendList.currentRowChanged.connect(self._updateExtendOptionsOnDataset)

        ## Create the right panel ##
        # Create the vertical layout
        layoutExtendRightLayout = QtWidgets.QVBoxLayout()

        # Set the options available for filling the data
        extendOptions = ['None', 'Fourier']

        # Create and add a dropdown selector with the available options
        layoutExtendRightLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Extend Method<strong>'))

        self.layoutExtendMethodSelector = QtWidgets.QComboBox()
        self.layoutExtendMethodSelector.addItems(extendOptions)
        layoutExtendRightLayout.addWidget(self.layoutExtendMethodSelector)

        # Connect the methods selector with the update function
        self.layoutExtendMethodSelector.currentIndexChanged.connect(self._updateExtendSubtab)

        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        layoutExtendRightLayout.addWidget(lineA)

        # Create the fill limit label
        self.layoutExtendDurationLabel = QtWidgets.QLabel('Extension Duration')
        self.layoutExtendDurationLabel.setVisible(False)

        # Create the fill limit widget
        self.layoutExtendDurationLimit = QtWidgets.QLineEdit()
        self.layoutExtendDurationLimit.setPlaceholderText('30')
        self.layoutExtendDurationLimit.setVisible(False)

        # Create the layout for the fill limit
        extendGapLayout = QtWidgets.QHBoxLayout()
        extendGapLayout.setAlignment(QtCore.Qt.AlignTop)
        extendGapLayout.setContentsMargins(0, 0, 0, 0)

        extendGapLayout.addWidget(self.layoutExtendDurationLabel, 1, QtCore.Qt.AlignLeft)
        extendGapLayout.addWidget(self.layoutExtendDurationLimit, 5, QtCore.Qt.AlignLeft)

        # Add the limit into the main page
        extendGapLayoutWidget = QtWidgets.QWidget()
        extendGapLayoutWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        extendGapLayoutWidget.setLayout(extendGapLayout)

        layoutExtendRightLayout.addWidget(extendGapLayoutWidget)

        # Adjust the layout of the widgets
        layoutExtendRightLayout.setAlignment(QtCore.Qt.AlignTop)

        ### Create the none page ###
        noneLayout = QtWidgets.QGridLayout()

        ### Create the fourier page ###
        fourierLayout = QtWidgets.QGridLayout()

        ### Create the stacked layout ###
        # Initialize the layout
        self.stackedExtendLayout = QtWidgets.QStackedLayout()

        # Wrap it in a widget and set visibility to false. If this is not done, a small, annoying popup window will
        # be opened separate from the main window
        stackedWidget = QtWidgets.QWidget()
        stackedWidget.setLayout(self.stackedExtendLayout)
        stackedWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)

        # Add each of the interpolation types to it, specifying how to scale with the screen
        noneWidget = QtWidgets.QWidget()
        noneWidget.setLayout(noneLayout)
        noneWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedExtendLayout.addWidget(noneWidget)

        fourierWidget = QtWidgets.QWidget()
        fourierWidget.setLayout(fourierLayout)
        fourierWidget.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.stackedExtendLayout.addWidget(fourierWidget)

        # Add the stacked layout to the main layout
        layoutExtendRightLayout.addWidget(stackedWidget)

        ### Connect the stacked widget with the selection combo box ###
        self.layoutExtendMethodSelector.currentIndexChanged.connect(self._updateExtendSubtab)

        ### Create the plot that shows the result of the selection ###
        # Create the plot
        self.layoutExtendPlot = DatasetTimeseriesPlots(None)
        self.layoutExtendPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # Add it into the layout
        layoutExtendRightLayout.addWidget(self.layoutExtendPlot)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutExtendClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutExtendClearButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the clear function
        self.layoutExtendClearButton.clicked.connect(self._applyExtendClearToDataset)
        self.layoutExtendClearButton.clicked.connect(self._updateExtendSubtab)

        # Create the apply button
        self.layoutExtendApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutExtendApplyButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the apply function
        self.layoutExtendApplyButton.clicked.connect(self._applyExtendOptionsToDataset)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutExtendClearButton)
        buttonLayout.addWidget(self.layoutExtendApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)
        layoutExtendRightLayout.addWidget(buttonLayoutWidget)

        ## Create the full layout ##
        # Create the horizontal layout
        layoutExtend = QtWidgets.QHBoxLayout()

        # Wrap the left layout in a widget and add to the layout
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutExtendLeftLayout)
        layoutExtend.addWidget(leftWidget, 1)

        # Wrap the right layout in a widget and add to the layout
        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutExtendRightLayout)
        layoutExtend.addWidget(rightWidget, 2)

        # Add the layout to the extend scrollable area
        layoutExtendSA.setLayout(layoutExtend)

    def _createDataWindowLayout(self, layoutWindowSA):
        """
        Lays out the windowing subtab in the expert predictor mode

        Parameters
        ----------
        layoutWindowSA: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the selector list ##
        # Create a vertical layout
        layoutWindowLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutWindowLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Connect and add the list
        self.windowList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.windowList.refreshDatasetListFromExtenal)
        layoutWindowLeftLayout.addWidget(self.windowList)

        ## Create the right panel ##
        # Create the layouts for subsequent use
        layoutWindowRightLayout = QtWidgets.QVBoxLayout()
        layoutWindowRightLayout.setContentsMargins(0, 0, 0, 0)

        layoutWindowRightGridLayout = QtWidgets.QGridLayout()
        layoutWindowRightGridLayout.setContentsMargins(0, 0, 0, 0)

        ### Setup the upper plot ###
        # Create a line/bar plot object
        dataPlot = TimeSeriesLineBarPlot()

        # Add some random data to test
        dataPlot.createBarPlotItem('test1', [0, 1, 2])
        dataPlot.createBarPlotItem('test2', [3, 4, 6])
        dataPlot.createBarPlotItem('test3', [7, 8, 9])

        # Add some random timeseries data
        # @@ These aren't referenced to the values, but to the positions ont eh cart
        dataPlot.createLinePlotItem('test4', [[0, 2], [2, 4], [4, 6]])

        # Set the bar categories
        dataPlot.setBarCategories(['1', '2', '3'])

        # Plot the data
        dataPlot.plot()

        # Add into the main layout
        layoutWindowRightGridLayout.addWidget(dataPlot.chartView, 0, 0, 1, 3)

        ### Create the date/lag widgets ###
        # todo: capture these values for each dataset on list change

        ## Create the start time widget ##
        # Create the label
        periodStartLabel = QtWidgets.QLabel('Start Date:')

        # Create the date widget
        self.periodStartWindowLayout = QtWidgets.QDateTimeEdit()
        self.periodStartWindowLayout.setDisplayFormat("MMMM d")
        self.periodStartWindowLayout.setCalendarPopup(True)
        self.periodStartWindowLayout.setMinimumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1))
        self.periodStartWindowLayout.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))

        # Add the widgets to the layout
        startLayout = QtWidgets.QHBoxLayout()
        startLayout.setAlignment(QtCore.Qt.AlignLeft)
        startLayout.addWidget(periodStartLabel, 1)
        startLayout.addWidget(self.periodStartWindowLayout, 2)

        startLayoutWidget = QtWidgets.QWidget()
        startLayoutWidget.setLayout(startLayout)

        layoutWindowRightGridLayout.addWidget(startLayoutWidget, 1, 0)

        ## Create the stop time widget ##
        # Create the label
        periodEndLabel = QtWidgets.QLabel('End Date:')

        # Create the date widget
        self.periodEndWindowLayout = QtWidgets.QDateTimeEdit()
        self.periodEndWindowLayout.setDisplayFormat("MMMM d")
        self.periodEndWindowLayout.setCalendarPopup(True)
        self.periodEndWindowLayout.setMinimumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1))
        self.periodEndWindowLayout.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))

        # Add the widgets to the layout
        stopLayout = QtWidgets.QHBoxLayout()
        stopLayout.setAlignment(QtCore.Qt.AlignLeft)
        stopLayout.addWidget(periodEndLabel, 1)
        stopLayout.addWidget(self.periodEndWindowLayout, 2)

        stopLayoutWidget = QtWidgets.QWidget()
        stopLayoutWidget.setLayout(stopLayout)
        layoutWindowRightGridLayout.addWidget(stopLayoutWidget, 1, 1)

        ## Create the lag box widget ##
        # Create the label
        extendGapLabel = QtWidgets.QLabel('Lag Length')
        # extendGapLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Create the widget
        self.layoutWindowLagLimit = QtWidgets.QTextEdit()
        self.layoutWindowLagLimit.setPlaceholderText('30')
        self.layoutWindowLagLimit.setFixedHeight(25)
        # self.layoutWindowLagLimit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Add the widgets to the layout
        lagLayout = QtWidgets.QHBoxLayout()
        lagLayout.setAlignment(QtCore.Qt.AlignLeft)
        lagLayout.addWidget(extendGapLabel, 1)
        lagLayout.addWidget(self.layoutWindowLagLimit, 2)

        lagLayoutWidget = QtWidgets.QWidget()
        lagLayoutWidget.setLayout(lagLayout)
        layoutWindowRightGridLayout.addWidget(lagLayoutWidget, 1, 2)

        ### Add the aggregation options ###
        # Create the widget
        self.layoutWindowAggregationGroup = AggregationOptions(False, orientation='horizontal')

        # Add it into the page
        layoutWindowRightGridLayout.addWidget(self.layoutWindowAggregationGroup, 2, 0)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutWindowClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutWindowClearButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the clear function
        self.layoutWindowClearButton.clicked.connect(self._applyWindowClearToDataset)
        self.layoutWindowClearButton.clicked.connect(self._updateWindowSubtab)

        # Create the apply button
        self.layoutWindowApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutWindowApplyButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        # Link the button to the apply function
        self.layoutWindowApplyButton.clicked.connect(self._applyWindowOptionsToDataset)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutWindowClearButton)
        buttonLayout.addWidget(self.layoutWindowApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)

        ## Create the full layout ##
        # Add the items to the right layout
        rightGridWidget = QtWidgets.QWidget()
        rightGridWidget.setLayout(layoutWindowRightGridLayout)
        layoutWindowRightLayout.addWidget(rightGridWidget)

        layoutWindowRightLayout.addWidget(buttonLayoutWidget)

        # Create the horizontal layout
        layoutWindow = QtWidgets.QHBoxLayout()

        # Wrap the left layout in a widget and add to the layout
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutWindowLeftLayout)
        layoutWindow.addWidget(leftWidget, 1)

        # Wrap the Right layout in a widget and add to the layout
        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutWindowRightLayout)
        layoutWindow.addWidget(rightWidget, 2)

        # Add the layout to the extend scrollable area
        layoutWindowSA.setLayout(layoutWindow)

    def _createOptionsTabLayout(self):
        """
        Lays out the options tab

        Parameters
        ----------
        None.

        Returns
        -------
        layoutMain: QT layout object
            Object containing all layout information to be placed in the widgets tab

        """

        # Create the page master layout
        layoutMain = QtWidgets.QVBoxLayout()
        layoutMain.setContentsMargins(0, 0, 0, 0)

        # Create the description text for the page
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">How should PyForecast build and evaluate models?</strong>')
        layoutMain.addWidget(label)

        # Forecast Issue Date
        # Model Training Period

        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Select options below or choose the default options<strong>')
        layoutMain.addWidget(label)
        self.defButton = QtWidgets.QRadioButton("Choose Defaults")
        self.defButton.setChecked(True)
        self.expertButton = QtWidgets.QRadioButton("I'm an expert! Let me choose")
        bgroup = QtWidgets.QButtonGroup()
        gb = QtWidgets.QGroupBox("")
        bgroup.addButton(self.defButton)
        bgroup.addButton(self.expertButton)
        bgroup.setExclusive(True)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(self.defButton)
        layout2.addWidget(self.expertButton)
        gb.setLayout(layout2)
        layoutMain.addWidget(gb)

        ### Setup the preprocessing algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Preprocessing Algorithms</strong>')
        layoutMain.addWidget(label)
        layoutMain.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsPreprocessorLayout = QtWidgets.QGridLayout()
        optionsPreprocessorLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsPreprocessor = []
        numPreProcessors = len(self.parent.preProcessors.keys())
        for i in range(int(numPreProcessors / 3) + 1 if numPreProcessors % 3 != 0 else int(numPreProcessors / 3)):
            for j in range(3):
                if (i * 3) + j < numPreProcessors:
                    prKey = list((self.parent.preProcessors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                        self.parent.preProcessors[prKey]['name'], self.parent.preProcessors[prKey]['description'])
                    button = richTextDescriptionButton(self, regrText)
                    button.setObjectName(str(prKey))

                    # Add the button to the layout and the tracking list
                    optionsPreprocessorLayout.addWidget(button, i, j, 1, 1)
                    self.optionsPreprocessor.append(button)

        layoutMain.addLayout(optionsPreprocessorLayout)

        ### Setup the regression algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Regression Algorithms</strong>')
        layoutMain.addWidget(label)
        layoutMain.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsRegressionLayout = QtWidgets.QGridLayout()
        optionsRegressionLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsRegression = []
        numRegressionModels = len(self.parent.regressors.keys())
        for i in range(int(numRegressionModels / 3) + 1 if numRegressionModels % 3 != 0 else int(numRegressionModels / 3)):
            for j in range(3):
                if (i * 3) + j < numRegressionModels:
                    regrKey = list((self.parent.regressors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                        self.parent.regressors[regrKey]['name'], self.parent.regressors[regrKey]['description'])
                    button = richTextDescriptionButton(self, regrText)
                    button.setObjectName(str(regrKey))

                    # Add the button to the layout and the tracking list
                    optionsRegressionLayout.addWidget(button, i, j, 1, 1)
                    self.optionsRegression.append(button)

        layoutMain.addLayout(optionsRegressionLayout)

        ### Setup the model selection algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Selection Algorithms</strong>')
        layoutMain.addWidget(label)
        layoutMain.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsSelectionLayout = QtWidgets.QGridLayout()
        optionsSelectionLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsSelection = []
        numFeatSelectors = len(self.parent.featureSelectors.keys())
        for i in range(int(numFeatSelectors / 3) + 1 if numFeatSelectors % 3 != 0 else int(numFeatSelectors / 3)):
            for j in range(3):
                if (i * 3) + j < numFeatSelectors:
                    regrKey = list((self.parent.featureSelectors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                        self.parent.featureSelectors[regrKey]['name'],
                        self.parent.featureSelectors[regrKey]['description'])
                    button = richTextDescriptionButton(self, regrText)
                    button.setObjectName(str(regrKey))

                    # Add the button to the layout and the holding list
                    optionsSelectionLayout.addWidget(button, i, j, 1, 1)
                    self.optionsSelection.append(button)

        layoutMain.addLayout(optionsSelectionLayout)

        ### Setup the model scoring algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Scoring</strong>')
        layoutMain.addWidget(label)
        layoutMain.addWidget(QtWidgets.QLabel("Select one or more scoring parameters (used to rank models):"))

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsScoringLayout = QtWidgets.QGridLayout()
        optionsScoringLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsScoring = []
        numScorers = len(self.parent.scorers['info'].keys())
        for i in range(int(numScorers / 3) + 1 if numScorers % 3 != 0 else int(numScorers / 3)):
            # layout2 = QtWidgets.QHBoxLayout()
            # layout2.setContentsMargins(1,1,1,1)
            for j in range(3):
                if (i * 3) + j < numScorers:
                    nameKey = list((self.parent.scorers['info'].keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color:darkcyan">{2}</strong><br>{0}'.format(
                        self.parent.scorers['info'][nameKey]['NAME'], self.parent.scorers['info'][nameKey]['WEBSITE'],
                        self.parent.scorers['info'][nameKey]['HTML'])
                    button = richTextDescriptionButton(self, regrText)
                    button.setObjectName(str(nameKey))

                    # Add the button to the layout and the holding list
                    optionsScoringLayout.addWidget(button, i, j, 1, 1)
                    self.optionsScoring.append(button)

        layoutMain.addLayout(optionsScoringLayout)

        # items = (layout.itemAt(i) for i in range(layout.count()))
        # print(items)
        # for w in items:
        #     w.ResizeEvent()

        # layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Multiple Linear Regression</strong><br>Ordinary Least Squares'))
        # layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Principal Components Regression</strong><br>Ordinary Least Squares'))
        # layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Z-Score Regression</strong><br>Ordinary Least Squares'))

        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(100, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        return layoutMain

    def _createSummaryTabLayout(self, mainLayout):
        """
        Lays out the summary tab

        Parameters
        ----------
        None.

        Returns
        -------
        layoutMain: QT layout object
            Object containing all layout information to be placed in the widgets tab

        """

        ### Create the left side dataset summary table ###
        # Create a vertical layout
        listLayout = QtWidgets.QVBoxLayout()
        #listLayout.setContentsMargins(2, 2, 2, 2)
        listLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Model Training Period<strong>'))
        self.summaryLayoutLabel1 = QtWidgets.QLabel('     Period: None')
        listLayout.addWidget(self.summaryLayoutLabel1)
        listLayout.addWidget(QtWidgets.QLabel(''))
        listLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Predictand<strong>'))
        self.summaryLayoutLabel2 = QtWidgets.QLabel('     Predictand: None')
        self.summaryLayoutLabel3 = QtWidgets.QLabel('     Predictand Period: None')
        self.summaryLayoutLabel4 = QtWidgets.QLabel('     Predictand Method: None')
        listLayout.addWidget(self.summaryLayoutLabel2)
        listLayout.addWidget(self.summaryLayoutLabel3)
        listLayout.addWidget(self.summaryLayoutLabel4)
        listLayout.addWidget(QtWidgets.QLabel(''))
        listLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Predictors<strong>'))

        # Create the list widget
        self.summaryListWidget = SpreadSheetViewOperations(self.parent.datasetTable, self.parent.datasetOperationsTable,
                                                           parent=self)

        # Connect the summary list to change with the operations table
        listLayout.addWidget(self.summaryListWidget)
        listLayout.addItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

        # Force the background color to prevent bleed through of the SA color in the headings
        listLayoutWidget = QtWidgets.QWidget()
        listLayoutWidget.setLayout(listLayout)
        #listLayoutWidget.setStyleSheet("background-color:white;")

        # Add to the layout
        mainLayout.addWidget(listLayoutWidget)

        ### Create the right side of the pane ###
        ## Create a vertical layout ##
        summaryRightLayout = QtWidgets.QVBoxLayout()

        ## Layout the preprocessors grid ##
        # Create the label
        preprocessorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Preprocessors</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(preprocessorLabelWidget)

        # Create the grid layout
        preprocessorLayout = QtWidgets.QGridLayout()

        # Loop and fill the preprocessor options
        numPreProcessors = len(self.parent.preProcessors.keys())
        counter = 0
        for i in range(int(numPreProcessors/3) + 1 if numPreProcessors%3 != 0 else int(numPreProcessors/3)):
            for j in range(3):
                if (i*3)+j < numPreProcessors:
                    prKey = list((self.parent.preProcessors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong>'.format(self.parent.preProcessors[prKey]['name'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    preprocessorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsPreprocessor[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_exteral)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        preprocessorLayoutWidget = QtWidgets.QWidget()
        preprocessorLayoutWidget.setLayout(preprocessorLayout)
        summaryRightLayout.addWidget(preprocessorLayoutWidget)

        ## Layout the regressors grid ##
        # Create the label
        regressorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Regressors</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(regressorLabelWidget)

        # Create the grid layout
        regressorLayout = QtWidgets.QGridLayout()

        # Loop and fill the preprocessor options
        numRegressors = len(self.parent.regressors.keys())
        counter = 0
        for i in range(int(numRegressors / 3) + 1 if numRegressors % 3 != 0 else int(numRegressors / 3)):
            for j in range(3):
                if (i * 3) + j < numRegressors:
                    prKey = list((self.parent.regressors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.regressors[prKey]['name'], '')

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    regressorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsRegression[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_exteral)
                    counter += 1


        # Wrap the layout in a widget and add to the layout
        regressorLayoutWidget = QtWidgets.QWidget()
        regressorLayoutWidget.setLayout(regressorLayout)
        summaryRightLayout.addWidget(regressorLayoutWidget)

        ## Layout the feature selectors grid ##
        # Create the label
        selectorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Feature Selectors</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(selectorLabelWidget)

        # Create the grid layout
        selectorLayout = QtWidgets.QGridLayout()

        # Loop and fill the preprocessor options
        numSelector = len(self.parent.featureSelectors.keys())
        counter = 0
        for i in range(int(numSelector / 3) + 1 if numSelector % 3 != 0 else int(numSelector / 3)):
            for j in range(3):
                if (i * 3) + j < numSelector:
                    prKey = list((self.parent.featureSelectors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong>'.format(self.parent.featureSelectors[prKey]['name'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    selectorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsSelection[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_exteral)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        selectorLayoutWidget = QtWidgets.QWidget()
        selectorLayoutWidget.setLayout(selectorLayout)
        summaryRightLayout.addWidget(selectorLayoutWidget)

        ## Layout the feature selectors grid ##
        # Create the label
        scoringLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Model Scoring</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(scoringLabelWidget)

        # Create the grid layout
        scoringLayout = QtWidgets.QGridLayout()

        # Loop and fill the preprocessor options
        numScorers = len(self.parent.scorers['info'].keys())
        counter = 0
        for i in range(int(numScorers/3) + 1 if numScorers%3 != 0 else int(numScorers/3)):
            for j in range(3):
                if (i*3)+j < numScorers:
                    nameKey = list((self.parent.scorers['info'].keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color:darkcyan">{0}</strong>'.format(self.parent.scorers['info'][nameKey]['NAME'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add to the layout object
                    scoringLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsScoring[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_exteral)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        scoringLayoutWidget = QtWidgets.QWidget()
        scoringLayoutWidget.setLayout(scoringLayout)
        summaryRightLayout.addWidget(scoringLayoutWidget)

        ## Set a horizontal break line ##
        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        summaryRightLayout.addWidget(lineA)

        ## Create and add the activation buttons ##
        # Create the clear button
        self.summaryClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.summaryClearButton.setMaximumSize(125, 65)

        # Connect the clear button to its action function
        self.summaryClearButton.clicked.connect(self._applySummaryClear)

        # Create the start button
        self.summaryStartButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Start</strong>')
        self.summaryStartButton.setMaximumSize(125, 65)

        # Connect the start button to its action function
        self.summaryStartButton.clicked.connect(self._applySummaryStart)

        # Create an horizontal layout, aligned to the right
        summaryButtonsLayout = QtWidgets.QHBoxLayout()
        summaryButtonsLayout.setAlignment(QtCore.Qt.AlignRight)

        summaryButtonsLayout.addWidget(self.summaryClearButton)
        summaryButtonsLayout.addWidget(self.summaryStartButton)

        # Wrap the layout as a widget and add to the main layout
        summaryButtonsLayoutWidget = QtWidgets.QWidget()
        summaryButtonsLayoutWidget.setLayout(summaryButtonsLayout)
        summaryRightLayout.addWidget(summaryButtonsLayoutWidget)

        ## Add the summary right pane to the summary layout ##
        # Create the widget to wrap the layout
        rightLayoutWidget = QtWidgets.QWidget()
        rightLayoutWidget.setLayout(summaryRightLayout)

        # Add the widget to the main layout
        mainLayout.addWidget(rightLayoutWidget)

    def _createResultsTabLayout(self, resultSA):
        """
        Lays out the results tab

        Parameters
        ----------
        None.

        Returns
        -------
        resultSA: QT scrollable area


        """

        ### Create the left side dataset summary table ###
        # Create a vertical layout
        leftLayout = QtWidgets.QVBoxLayout()

        # Create the preprocessing list
        resultPreprocessingLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Preprocessors<strong>')
        leftLayout.addWidget(resultPreprocessingLabel)

        resultPreprocessorsList = QtWidgets.QListWidget()
        leftLayout.addWidget(resultPreprocessorsList)

        # Create the regression list
        resultsRegressorsLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Regressors<strong>')
        leftLayout.addWidget(resultsRegressorsLabel)

        resultsRegressorsList = QtWidgets.QListWidget()
        leftLayout.addWidget(resultsRegressorsList)

        # Create the selection list
        resultsSelectorsLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Selectors<strong>')
        leftLayout.addWidget(resultsSelectorsLabel)

        resultsSelectorsList = QtWidgets.QListWidget()
        leftLayout.addWidget(resultsSelectorsList)

        ### Create the right side items ###
        ## Create the initial layouts ##
        rightLayout = QtWidgets.QVBoxLayout()

        rightLayoutHorizontal = QtWidgets.QHBoxLayout()
        rightLayoutHorizontal.setContentsMargins(0, 0, 0, 0)

        rightLayoutVertical = QtWidgets.QVBoxLayout()
        rightLayoutVertical.setContentsMargins(0, 0, 0, 0)

        ## Create the main left observed/forecast plot ##
        self.resultsObservedForecstPlot = QtWidgets.QTableWidget()

        ## Create the upper right inflow/year plot ##
        self.resultsInflowYearPlot = QtWidgets.QTableWidget()

        ## Create the lower right residual/year plot ##
        self.resultsResidualYearPlot = QtWidgets.QTableWidget()

        ## Create the table to show the metrics ##
        self.resultsMetricTable = QtWidgets.QTableWidget()

        ## Add items into the layouts ##
        # Add the subplots to the vertical layout
        rightLayoutVertical.addWidget(self.resultsInflowYearPlot)
        rightLayoutVertical.addWidget(self.resultsResidualYearPlot)

        # Wrap the vertical layout as a widget 
        rightLayoutVerticalWidget = QtWidgets.QWidget()
        rightLayoutVerticalWidget.setLayout(rightLayoutVertical)

        # Add items to the horizontal layout
        rightLayoutHorizontal.addWidget(self.resultsObservedForecstPlot)
        rightLayoutHorizontal.addWidget(rightLayoutVerticalWidget)

        # Wrap the horizontal layout as a widget
        rightLayoutHorizontalWidget = QtWidgets.QWidget()
        rightLayoutHorizontalWidget.setLayout(rightLayoutHorizontal)

        # Add items into the main right layout
        rightLayout.addWidget(rightLayoutHorizontalWidget)
        rightLayout.addWidget(self.resultsMetricTable)

        ### Add the items into the layout ###
        # Create the horizontal layout
        layoutMain = QtWidgets.QHBoxLayout()

        ## Add the left layout ##
        # Promote the layout to a widget
        leftLayoutWidget = QtWidgets.QWidget()
        leftLayoutWidget.setLayout(leftLayout)

        # Add it to the layout
        layoutMain.addWidget(leftLayoutWidget, 1)

        ## Add the right layout ##
        # Promote the right layout to a widget
        rightLayoutWidget = QtWidgets.QWidget()
        rightLayoutWidget.setLayout(rightLayout)

        # Add it into the layout
        layoutMain.addWidget(rightLayoutWidget, 2)

        ## Add into the scrollable area ##
        layoutMainWidget = QtWidgets.QWidget()
        layoutMainWidget.setLayout(layoutMain)
        resultSA.setWidget(layoutMainWidget)

    def setPredictorDefaultStack(self):
        self.stackedPredictorWidget.setCurrentIndex(0)

    def setPredictorExpertStack(self):
        self.stackedPredictorWidget.setCurrentIndex(1)

    def _applySimpleOptions(self):
        """
        Applies the attributes from the simple predictor page into the dataset operations table

        """
        # todo: write this function when the aggregation group is stable

        # Clear the button click
        self.layoutSimpleApplyButton.setChecked(False)

        # Get the current datasest index
        rowIdx = self.layoutSimpleDoubleList.listOutput.currentIndex().row()

        if rowIdx >= 0:

            currentIndex = self.layoutSimpleDoubleList.listOutput.datasetTable.index[rowIdx]

            # Apply selected options
            self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = self.layoutAggregationOptions.selectedAggOption
            self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = self.layoutAggregationOptions.periodStart.dateTime().toString("yyyy-MM-dd")
            self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = (parser.parse(str(np.sort(list(set(self.parent.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))).strftime("%Y-%m-%d")
            self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = self.layoutAggregationOptions.selectedAggPeriod
            self.parent.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = str(self.layoutAggregationOptions.predForceCheckBox.checkState() == 2)

            # Extract the fill limit
            # try:
            #     fillLimit = int(self.layoutFillGapLimit.toPlainText())
            # except:
            #     fillLimit = None
            #
            # # Get the method to be utilized
            # fillMethod = self.layoutFillMethodSelector.currentText()
            #
            # # Set the values
            # self.parent.datasetOperationsTable.loc[currentIndex]['FillMethod'] = fillMethod
            # self.parent.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = fillLimit
            #

        self._updateSimpleLayoutAggregationOptions()


    def _applySimpleClear(self):
        """
        Clears the fill attributes of a predictor

        """

        # Drop all rows in the dataset operations table
        self.parent.datasetOperationsTable.drop(self.parent.datasetOperationsTable.index, inplace=True)

        # Reset the output table
        self.layoutSimpleDoubleList.resetOutputItems()

        # Clear the checkboxes
        self.layoutSimpleExtend.updateToUnchecked()
        self.layoutSimpleFill.updateToUnchecked()

        # Clear the aggregation options
        # todo: Add this functionality

        ### Reset the button state ###
        self.layoutSimpleClearButton.setChecked(False)

    def _updateFillSubtab(self):
        """
        Updates the state of the fill subtab methods pane based on the method selector

        """

        ### Update the widget pane ###
        # Switch the stacked widgets
        self.stackedFillLayout.setCurrentIndex(self.layoutFillMethodSelector.currentIndex())

        # Update the gap limit visibility
        if self.layoutFillMethodSelector.currentIndex() > 0:
            self.layoutFillGapLimitLabel.setVisible(True)
            self.layoutFillGapLimit.setVisible(True)
        else:
            self.layoutFillGapLimitLabel.setVisible(False)
            self.layoutFillGapLimit.setVisible(False)

        if self.layoutFillMethodSelector.currentIndex() >= 5:
            self.layoutFillOrderLabel.setVisible(True)
            self.layoutFillOrder.setVisible(True)
        else:
            self.layoutFillOrderLabel.setVisible(False)
            self.layoutFillOrder.setVisible(False)

    def _updateFillOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Get the current datasest index
        currentIndex = self.fillList.datasetTable.index[self.fillList.currentIndex().row()]

        ### Update the widgets with dataset information ###
        # Get the options for the item
        fillMethod = self.parent.datasetOperationsTable.loc[currentIndex]['FillMethod']
        fillGap = self.parent.datasetOperationsTable.loc[currentIndex]['FillMaximumGap']
        fillOrder = self.parent.datasetOperationsTable.loc[currentIndex]['FillOrder']
        # If needed, can extract more information based on the fill method here

        # Get the options for the selector and stack
        fillOptionsIndex = [x for x in range(self.layoutFillMethodSelector.count()) if self.layoutFillMethodSelector.itemText(x) == fillMethod]
        if fillOptionsIndex:
            fillOptionsIndex = fillOptionsIndex[0]
        else:
            fillOptionsIndex = 0

        # Get the fill order index
        fillOrderIndex = [x for x in range(self.layoutFillOrder.count()) if self.layoutFillOrder.itemText(x) == str(fillOrder)]
        if fillOrderIndex:
            fillOrderIndex = fillOrderIndex[0]
        else:
            fillOrderIndex = 0

        # Set the values into the widgets
        self.stackedFillLayout.setCurrentIndex(fillOptionsIndex)
        self.layoutFillMethodSelector.setCurrentIndex(fillOptionsIndex)
        self.layoutFillOrder.setCurrentIndex(fillOrderIndex)

        # Set the values into the widgets
        # Correct this issue
        self.layoutFillGapLimit.setText(str(fillGap))

        ### Update the plot with the dataset and interpolation ###
        self._updateFillPlot(currentIndex, fillMethod, fillGap, fillOrder)

    def _applyFillOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Extract the fill limit
        try:
            fillLimit = int(self.layoutFillGapLimit.text())
        except:
            fillLimit = None

        # Get the method to be utilized
        fillMethod = self.layoutFillMethodSelector.currentText()

        # Get the order
        fillOrder = int(self.layoutFillOrder.currentText())

        # Get the current dataset
        currentIndex = self.fillList.datasetTable.index[self.fillList.currentIndex().row()]

        # Set the values
        self.parent.datasetOperationsTable.loc[currentIndex]['FillMethod'] = fillMethod
        self.parent.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = fillLimit
        self.parent.datasetOperationsTable.loc[currentIndex]['FillOrder'] = fillOrder

        # Clear the button click
        self.layoutFillApplyButton.setChecked(False)

        # Update the plot on the tab
        self._updateFillPlot(currentIndex, fillMethod, fillLimit, fillOrder)


    def _applyFillClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.fillList.datasetTable.index[self.fillList.currentIndex().row()]

        # Set the values
        self.parent.datasetOperationsTable.loc[currentIndex]['FillMethod'] = None
        self.parent.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = None
        self.parent.datasetOperationsTable.loc[currentIndex]['FillOrder'] = None

        # Clear the button click
        self.layoutFillClearButton.setChecked(False)

        # Switch the stacked widgets
        self.layoutFillMethodSelector.setCurrentIndex(0)
        self._updateFillSubtab()

    def _updateFillPlot(self, currentIndex, fillMethod, fillLimit, fillOrder):
        """
        Updates the plot on the fill subtab

        Parameters
        ----------
        currentIndex: pandas index
            Index which specifies the active dataset
        fillMethod: str
            Fill method specified to fill the gaps
        fillLimit: int
            Maximum size of gap to fill via interpolation
        fillOrder: int
            Order of the fill method, if applicable

        """

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        sourceData = self.parent.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.parent.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        if fillMethod is not None and fillMethod != 'None':
            # Fill the data with the applied operation
            filledData = fill_missing(sourceData, fillMethod.lower(), fillLimit, order=fillOrder)

            # Promote and set the status of the filled data
            fillData = pd.DataFrame(filledData)
            fillData['Status'] = 'Filled'
            fillData.set_index(['Status'], append=True, inplace=True)

            # Promote and set the status of the source data
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'
            sourceData.set_index(['Status'], append=True, inplace=True)

            # Stack it together with the existing data
            sourceData = pd.concat([fillData, sourceData]).sort_index()

        else:
            # No filled data is present. Promote back to a dataframe and add the plotting label
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'

            # Convert to a multiinstance table
            sourceData.set_index(['Status'], append=True, inplace=True)

        ## Plot the source dataset ##
        self.layoutFillPlot.updateData(sourceData, 'Status', sourceUnits)
        self.layoutFillPlot.displayDatasets()

    def _updateExtendSubtab(self):
        """
        Updates the state of the extend subtab methods pane based on the method selector

        """

        # Switch the stacked widgets
        self.stackedExtendLayout.setCurrentIndex(self.layoutExtendMethodSelector.currentIndex())

        # Update the gap limit visibility
        if self.layoutExtendMethodSelector.currentIndex() > 0:
            self.layoutExtendDurationLabel.setVisible(True)
            self.layoutExtendDurationLimit.setVisible(True)
        else:
            self.layoutExtendDurationLabel.setVisible(False)
            self.layoutExtendDurationLimit.setVisible(False)

    def _updateExtendOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Get the current datasest index
        currentIndex = self.extendList.datasetTable.index[self.extendList.currentIndex().row()]

        # Get the options for the item
        extendMethod = self.parent.datasetOperationsTable.loc[currentIndex]['ExtendMethod']
        extendDuration = self.parent.datasetOperationsTable.loc[currentIndex]['ExtendDuration']
        # If needed, can extract more information based on the fill method here

        # # Get the options for the selector and stack
        extendOptionsIndex = [x for x in range(self.layoutExtendMethodSelector.count()) if self.layoutExtendMethodSelector.itemText(x) == extendMethod]
        if extendOptionsIndex:
            extendOptionsIndex = extendOptionsIndex[0]
        else:
            extendOptionsIndex = 0

        self.stackedExtendLayout.setCurrentIndex(extendOptionsIndex)
        self.layoutExtendMethodSelector.setCurrentIndex(extendOptionsIndex)

        # Set the values into the widgets
        # Correct this issue
        self.layoutExtendDurationLimit.setText(str(extendDuration))

        # Update the plot on the tab
        self._updateExtendPlot(currentIndex, extendMethod, extendDuration)

    def _applyExtendOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Extract the fill limit
        try:
            extendLimit = int(self.layoutExtendDurationLimit.text())
        except:
            extendLimit = None

        # Get the method to be utilized
        extendMethod = self.layoutExtendMethodSelector.currentText()

        # Get the current dataset
        currentIndex = self.extendList.datasetTable.index[self.extendList.currentIndex().row()]

        # Set the values
        self.parent.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = extendMethod
        self.parent.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = extendLimit

        # Clear the button click
        self.layoutExtendApplyButton.setChecked(False)

        # Update the plot on the tab
        self._updateExtendPlot(currentIndex, extendMethod, extendLimit)

    def _applyExtendClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.extendList.datasetTable.index[self.extendList.currentIndex().row()]

        # Set the values
        self.parent.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = None
        self.parent.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = None

        # Clear the button click
        self.layoutFillClearButton.setChecked(False)

        # # Switch the stacked widgets
        self.layoutExtendMethodSelector.setCurrentIndex(0)
        self._updateExtendSubtab()

    def _updateExtendPlot(self, currentIndex, extendMethod, extendLimit):
        """
        Updates the plot on the extend subtab

        Parameters
        ----------
        currentIndex: pandas index
            Index which specifies the active dataset
        extendMethod: str
            Fill method specified to extend the series
        extendLimit: int
            Extension period

        """

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        sourceData = self.parent.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.parent.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        extendMethod = None
        if extendMethod is not None and extendMethod != 'None':
            # Fill the data with the applied operation
            filledData = fill_missing(sourceData, extendMethod.lower(), extendLimit, order=None)

            # Promote and set the status of the filled data
            fillData = pd.DataFrame(filledData)
            fillData['Status'] = 'Filled'
            fillData.set_index(['Status'], append=True, inplace=True)

            # Promote and set the status of the source data
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'
            sourceData.set_index(['Status'], append=True, inplace=True)

            # Stack it together with the existing data
            sourceData = pd.concat([fillData, sourceData]).sort_index()

        else:
            # No filled data is present. Promote back to a dataframe and add the plotting label
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'

            # Convert to a multiinstance table
            sourceData.set_index(['Status'], append=True, inplace=True)

        ## Plot the source dataset ##
        self.layoutExtendPlot.updateData(sourceData, 'Status', sourceUnits)
        self.layoutExtendPlot.displayDatasets()


    def _updateWindowSubtab(self):
        """
        Updates the state of the extend subtab methods pane based on the method selector

        """
        # todo: build this when the aggregation group is stable

        # Switch the stacked widgets
        # self.stackedExtendLayout.setCurrentIndex(self.layoutExtendMethodSelector.currentIndex())
        #
        # # Update the gap limit visibility
        # if self.layoutExtendMethodSelector.currentIndex() > 0:
        #     self.layoutExtendDurationLabel.setVisible(True)
        #     self.layoutExtendDurationLimit.setVisible(True)
        # else:
        #     self.layoutExtendDurationLabel.setVisible(False)
        #     self.layoutExtendDurationLimit.setVisible(False)
        pass

    def _updateWindowOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """
        # todo: build this function when the aggregation function is stable

        # Get the current datasest index
        # currentIndex = self.extendList.datasetTable.index[self.extendList.currentIndex().row()]
        #
        # # Get the options for the item
        # extendMethod = self.parent.datasetOperationsTable.loc[currentIndex]['ExtendMethod']
        # extendDuration = self.parent.datasetOperationsTable.loc[currentIndex]['ExtendDuration']
        # # If needed, can extract more information based on the fill method here
        #
        # # # Get the options for the selector and stack
        # extendOptionsIndex = [x for x in range(self.layoutExtendMethodSelector.count()) if self.layoutExtendMethodSelector.itemText(x) == extendMethod]
        # if extendOptionsIndex:
        #     extendOptionsIndex = extendOptionsIndex[0]
        # else:
        #     extendOptionsIndex = 0
        #
        # self.stackedExtendLayout.setCurrentIndex(extendOptionsIndex)
        # self.layoutExtendMethodSelector.setCurrentIndex(extendOptionsIndex)
        #
        # # Set the values into the widgets
        # # Correct this issue
        # self.layoutExtendDurationLimit.setText(str(extendDuration))
        pass

    def _applyWindowOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """
        # todo: build this function when the aggregation widget is stable

        # Extract the fill limit
        # try:
        #     extendLimit = int(self.layoutExtendDurationLimit.toPlainText())
        # except:
        #     extendLimit = None
        #
        # # Get the method to be utilized
        # extendMethod = self.layoutExtendMethodSelector.currentText()
        #
        # # Get the current dataset
        # currentIndex = self.extendList.datasetTable.index[self.extendList.currentIndex().row()]
        #
        # # Set the values
        # self.parent.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = extendMethod
        # self.parent.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = extendLimit
        #
        # # Clear the button click
        # self.layoutExtendApplyButton.setChecked(False)
        pass

    def _applyWindowClearToDataset(self):
        """
        Clears the window attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.extendList.datasetTable.index[self.extendList.currentIndex().row()]

        # Set the values
        self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = None
        self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = None
        self.parent.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = None

        # Clear the button click
        self.layouWindowClearButton.setChecked(False)


    def _applySummaryClear(self):
        """
        Clear/reset all dataset and analysis options within the application

        """

        ### Reset the dataset operations table ###
        # Drop all rows in the table
        self.parent.datasetOperationsTable.drop(self.parent.datasetOperationsTable.index, inplace=True)

        # Update the table display elements
        self.summaryListWidget.model().loadDataIntoModel(self.parent.datasetTable, self.parent.datasetOperationsTable)

        ### Reset all processing options ###
        # Reset the preprocessing operations
        for x in self.optionsPreprocessor:
            x.updateToUnchecked()

        # Reset the regression options
        for x in self.optionsRegression:
            x.updateToUnchecked()

        # Reset the selection options
        for x in self.optionsSelection:
            x.updateToUnchecked()

        # Reset the scoring operations
        for x in self.optionsScoring:
            x.updateToUnchecked()

        ### Reset the button state ###
        self.summaryClearButton.setChecked(False)

        ### Emit change to the doublelist object ###
        self.layoutSimpleDoubleList.resetOutputItems()

    def _applySummaryStart(self):
        """
        Start the regression analysis using the specified settings

        """

        ### Reset the button state ###
        self.summaryStartButton.setChecked(False)

        ### Check all required options are defined ###
        # Check required self.modelRunsTable entries are defined

        ### Populate self.modelRunsTable ###
        # Pre-processors
        preProcList = []
        for preProc in self.optionsPreprocessor:
            if preProc.isChecked():
                preProcList.append(preProc.objectName())

        self.parent.modelRunsTable.loc[0]['Preprocessors'] = preProcList

        # Regression algorithms
        regAlgs = []
        for regAlg in self.optionsRegression:
            if regAlg.isChecked():
                regAlgs.append(regAlg.objectName())

        self.parent.modelRunsTable.loc[0]['RegressionTypes'] = regAlgs

        # Feature selection algorithms
        selAlgs = []
        for selAlg in self.optionsSelection:
            if selAlg.isChecked():
                selAlgs.append(selAlg.objectName())

        self.parent.modelRunsTable.loc[0]['FeatureSelectionTypes'] = selAlgs

        # Scoring parameters
        scoreParams = []
        for scoreParam in self.optionsScoring:
            if scoreParam.isChecked():
                scoreParams.append(scoreParam.objectName())

        self.parent.modelRunsTable.loc[0]['ScoringParameters'] = scoreParams

        ### Apply operations to datasets ###

        ### Generate predictors ###

        ### Kick off the analysis ###
        print('Beginning regression calculations...')
        print('I am batman!')

    def applyPredictandAggregationOption(self):
        predictandData = self.targetSelect.currentData()
        predID = predictandData.name
        # Get Min dataset date
        minT = parser.parse(str(np.sort(list(set(self.parent.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[0]))
        maxT = parser.parse(str(np.sort(list(set(self.parent.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[-1]))
        selT = parser.parse(self.periodStart.dateTime().toString("yyyy-MM-ddThh:mm:ss.zzz"))
        if (parser.parse(str(minT.year) + '-'+str(selT.month)+ '-'+str(selT.day))<minT):
            startT = parser.parse(str(minT.year + 1) + '-' + str(selT.month) + '-' + str(selT.day))
        else:
            startT = parser.parse(str(minT.year) + '-' + str(selT.month) + '-' + str(selT.day))

        nDays = self.periodEnd.date().toJulianDay() - self.periodStart.date().toJulianDay() + 1 #dates inclusive
        periodString = "R/" + startT.strftime("%Y-%m-%d") + "/P" + str(nDays) + "D/F12M" #(e.g. R/1978-02-01/P1M/F1Y)
        #print("Predictand Entries for the self.modelRunsTable: ")
        #print("--Model Training Period: " + minT.strftime("%Y-%m-%d") + "/" + maxT.strftime("%Y-%m-%d"))
        #print("--Predictand ID: " + str(predID))
        #print("--Predictand Period: " + periodString)
        #print("--Predictand Method: " + self.methodCombo.currentData())
        if self.parent.modelRunsTable.shape[0] < 1:
            self.parent.modelRunsTable.loc[0] = [None] * self.parent.modelRunsTable.columns.shape[0]

        self.parent.modelRunsTable.loc[0]['ModelTrainingPeriod'] = minT.strftime("%Y-%m-%d") + "/" + maxT.strftime("%Y-%m-%d")
        self.parent.modelRunsTable.loc[0]['Predictand'] = predID
        self.parent.modelRunsTable.loc[0]['PredictandPeriod'] = periodString
        self.parent.modelRunsTable.loc[0]['PredictandMethod'] = self.methodCombo.currentData()


    def _updateTabDependencies(self, tabIndex):
        # todo: doc string

        ### Get the current index the widget has been changed to ###
        # currentIndex = self.workflowWidget.currentIndex()
        ##print(tabIndex)


        if tabIndex == 3:
            # Update the summary boxes
            ##print('@@ debug statement')
            # Update predictand options
            if self.parent.modelRunsTable.shape[0] < 1:
                self.summaryLayoutLabel1.setText('     Period: None')
                self.summaryLayoutLabel1.setStyleSheet("color : red")
                self.summaryLayoutLabel2.setText('     Predictand: None')
                self.summaryLayoutLabel2.setStyleSheet("color : red")
                self.summaryLayoutLabel3.setText('     Predictand Period: None')
                self.summaryLayoutLabel3.setStyleSheet("color : red")
                self.summaryLayoutLabel4.setText('     Predictand Method: None')
                self.summaryLayoutLabel4.setStyleSheet("color : red")
            else:
                selDataset = self.parent.datasetTable.loc[self.parent.modelRunsTable.loc[0]['Predictand']]
                selName = str(selDataset['DatasetName']) + ' (' + str(selDataset['DatasetAgency']) + ') ' + str(selDataset['DatasetParameter'])
                self.summaryLayoutLabel1.setText('     Period: ' + str(self.parent.modelRunsTable.loc[0]['ModelTrainingPeriod']))
                self.summaryLayoutLabel1.setStyleSheet("color : green")
                self.summaryLayoutLabel2.setText('     Predictand: ' + selName)
                self.summaryLayoutLabel2.setStyleSheet("color : green")
                self.summaryLayoutLabel3.setText('     Predictand Period: ' + str(self.parent.modelRunsTable.loc[0]['PredictandPeriod']))
                self.summaryLayoutLabel3.setStyleSheet("color : green")
                self.summaryLayoutLabel4.setText('     Predictand Method: ' + str(self.parent.modelRunsTable.loc[0]['PredictandMethod']))
                self.summaryLayoutLabel4.setStyleSheet("color : green")

            # Load predictors table
            self.summaryListWidget.model().loadDataIntoModel(self.parent.datasetTable, self.parent.datasetOperationsTable)

