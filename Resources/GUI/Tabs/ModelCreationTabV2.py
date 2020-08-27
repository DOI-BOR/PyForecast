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
from resources.GUI.CustomWidgets.PyQtGraphs import ModelTabPlots, TimeSeriesLineBarPlot
from resources.GUI.CustomWidgets.customTabs import EnhancedTabWidget
from resources.GUI.CustomWidgets.richTextButtons import richTextButton, richTextButtonCheckbox, richTextDescriptionButton
from resources.GUI.WebMap import webMapView
# import pandas as pd


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
        predictandApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        predictandApplyButton.setMaximumSize(125, 50)
        layout.addWidget(predictandApplyButton, 6, 0, 1, 1)

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
        self.layoutPredictorSimpleAnalysis = QtWidgets.QHBoxLayout()
        self.layoutPredictorSimpleAnalysis.setContentsMargins(15, 15, 15, 15)

        # Create the layout object for the expert analysis
        self.layoutPredictorExpertAnalysis = QtWidgets.QVBoxLayout()
        self.layoutPredictorExpertAnalysis.setContentsMargins(15, 15, 15, 15)

        ### Create the simple analysis tab ###
        ## Create the initial scrollable area and layout ##
        predictorLayoutSimple = QtWidgets.QScrollArea()
        predictorLayoutSimple.setWidgetResizable(True)

        ## Create the DoubleList selector object ##
        self.layoutSimpleDoubleList = DoubleListMultipleInstance(self.parent.datasetTable,
                                                                 '<strong style="font-size: 18px">Available Datasets<strong>',
                                                                 '<strong style="font-size: 18px">Selected Datasets<strong>')

        # Connect the DoubleList with the dataset hmtl list to keep everything in sync. This will automatically
        # populate the DoubleList entries
        self.datasetList.updateSignalToExternal.connect(self.layoutSimpleDoubleList.update)

        ## Create the objects on the right side ##
        # Simple fill
        self.layoutSimpleFill = richTextDescriptionButton(self, '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format('Fill data',
                                               'Automatically fill the selected time series using default properties'))

        # Simple extend
        self.layoutSimpleExtend = richTextDescriptionButton(self, '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format('Extend data',
                                                 'Automatically extend the selected time series using default properties'))

        self.layoutAggregationOptions = AggregationOptions(False)


        ## Add the widgets into the layout ##
        # Add the items into the horizontal spacer
        layoutSimple = QtWidgets.QHBoxLayout()
        layoutSimple.setContentsMargins(0, 0, 0, 0)
        layoutSimple.addWidget(self.layoutSimpleDoubleList, 2)
        layoutSimple.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        # Create the right side options layout
        layoutSimpleOptions = QtWidgets.QVBoxLayout()
        layoutSimpleOptions.setAlignment(QtCore.Qt.AlignTop)
        layoutSimpleOptions.addWidget(self.layoutSimpleFill)
        layoutSimpleOptions.addWidget(self.layoutSimpleExtend)
        layoutSimpleOptions.addWidget(self.layoutAggregationOptions)

        # Wrap the right side layout in another widget
        layoutSimpleOptionsWidget = QtWidgets.QWidget()
        layoutSimpleOptionsWidget.setLayout(layoutSimpleOptions)

        # Add the right side to the simple layout
        layoutSimple.addWidget(layoutSimpleOptionsWidget, 1)

        # Wrap the layout in a widget
        layoutSimpleWidget = QtWidgets.QWidget()
        layoutSimpleWidget.setLayout(layoutSimple)

        # Set the items into the simple layout
        self.layoutPredictorSimpleAnalysis.addWidget(layoutSimpleWidget)
        simplePredictorWidget = QtWidgets.QWidget()
        simplePredictorWidget.setLayout(self.layoutPredictorSimpleAnalysis)


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
                                                               '<strong style="font-size: 18px">Selected Datasets<strong>')

        # Connect the DoubleList with the dataset hmtl list to keep everything in sync. This will automatically
        # populate the DoubleList entries
        self.datasetList.updateSignalToExternal.connect(self.layoutDataDoubleList.update)

        # Connect the doublelists together. This will keep the selection in sync between the simple and expert modes
        self.layoutDataDoubleList.updatedLinkedList.connect(self.layoutSimpleDoubleList.updateLinkedDoubleLists)
        self.layoutSimpleDoubleList.updatedLinkedList.connect(self.layoutDataDoubleList.updateLinkedDoubleLists)

        # todo: Update the positions on the map

        # Add the widget to the layout
        layoutData.addWidget(self.layoutDataDoubleList)

        ## Finalize the tab format ##
        # Wrap the layout as a widget to make it compatible with the SA layout
        layoutDataSA.setLayout(layoutData)


        ### Create the layout fill tab ###
        ## Create the scrollable area ##
        layoutFillSA = QtWidgets.QScrollArea()
        layoutFillSA.setWidgetResizable(True)

        ## Fill the remaining area with the layout options ##
        self._createDataFillLayout(layoutFillSA)

        ### Create the layout extend tab ###
        layoutExtendSA = QtWidgets.QScrollArea()
        layoutExtendSA.setWidgetResizable(True)

        ## Create the selector list ##
        # Create a vertical layout
        layoutExtendLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutExtendLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Connect and add the list
        self.extendList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.extendList.refreshDatasetListFromExtenal)
        layoutExtendLeftLayout.addWidget(self.extendList)

        ## Create the right panel ##
        # Create the vertical layout
        layoutExtendRightLayout = QtWidgets.QVBoxLayout()

        # Fill the remaining area with the layout options
        self._createDataExtendLayout(layoutExtendRightLayout)

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


        ### Create the layout window tab ###
        ## Create the scrollable area ##
        layoutWindowSA = QtWidgets.QScrollArea()
        layoutWindowSA.setWidgetResizable(True)

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
        # Create the vertical layout
        layoutWindowRightLayout = QtWidgets.QGridLayout()

        # Fill the remaining area with the layout options
        self._createDataWindowLayout(layoutWindowRightLayout)

        ## Create the full layout ##
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


        ### Add the tabs into the tab widget ###
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
        self.stackedPredictorWidget.addWidget(simplePredictorWidget)
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

        SA = QtWidgets.QScrollArea()
        SA.setWidgetResizable(True)
        widg = QtWidgets.QWidget()        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">How should PyForecast build and evaluate models?</strong>')
        layout.addWidget(label)

        # Forecast Issue Date
        # Model Training Period
        

        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Select options below or choose the default options<strong>')
        layout.addWidget(label)
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
        layout.addWidget(gb)
        

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Preprocessing Algorithms</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))
        
        numPreProcessors = len(self.parent.preProcessors.keys())
        layout2 = QtWidgets.QGridLayout()

        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numPreProcessors/3) + 1 if numPreProcessors%3 != 0 else int(numPreProcessors/3)):
            for j in range(3):
                if (i*3)+j < numPreProcessors:
                    prKey = list((self.parent.preProcessors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.preProcessors[prKey]['name'], self.parent.preProcessors[prKey]['description'])
                    layout2.addWidget(richTextDescriptionButton(self, regrText), i, j, 1, 1)
        layout.addLayout(layout2)

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Regression Algorithms</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))
        
        numRegressionModels = len(self.parent.regressors.keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numRegressionModels/3) + 1 if numRegressionModels%3 != 0 else int(numRegressionModels/3)):
            for j in range(3):
                if (i*3)+j < numRegressionModels:
                    regrKey = list((self.parent.regressors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.regressors[regrKey]['name'], self.parent.regressors[regrKey]['description'])
                    layout2.addWidget(richTextDescriptionButton(self, regrText), i, j, 1, 1)
        layout.addLayout(layout2)

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Selection Algorithms</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))
        
        numFeatSelectors = len(self.parent.featureSelectors.keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numFeatSelectors/3) + 1 if numFeatSelectors%3 != 0 else int(numFeatSelectors/3)):
            for j in range(3):
                if (i*3)+j < numFeatSelectors:
                    regrKey = list((self.parent.featureSelectors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.featureSelectors[regrKey]['name'], self.parent.featureSelectors[regrKey]['description'])
                    layout2.addWidget(richTextDescriptionButton(self, regrText), i, j, 1, 1)
        layout.addLayout(layout2)

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Scoring</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more scoring parameters (used to rank models):"))

        numScorers = len(self.parent.scorers['info'].keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numScorers/3) + 1 if numScorers%3 != 0 else int(numScorers/3)):
            #layout2 = QtWidgets.QHBoxLayout()
            #layout2.setContentsMargins(1,1,1,1)
            for j in range(3):
                if (i*3)+j < numScorers:
                    nameKey = list((self.parent.scorers['info'].keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color:darkcyan">{2}</strong><br>{0}'.format(self.parent.scorers['info'][nameKey]['NAME'], self.parent.scorers['info'][nameKey]['WEBSITE'], self.parent.scorers['info'][nameKey]['HTML'])
                    layout2.addWidget(richTextDescriptionButton(self, regrText), i, j, 1, 1)
        layout.addLayout(layout2)

        # items = (layout.itemAt(i) for i in range(layout.count()))
        # print(items)
        # for w in items:
        #     w.ResizeEvent()

        #layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Multiple Linear Regression</strong><br>Ordinary Least Squares'))
        #layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Principal Components Regression</strong><br>Ordinary Least Squares'))
        #layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Z-Score Regression</strong><br>Ordinary Least Squares'))
        
        layout.addSpacerItem(QtWidgets.QSpacerItem(100,100,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        widg.setLayout(layout)
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

        # Layout the results widget
        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "RESULTS", "resources/GraphicalResources/icons/run-24px.svg", "#FFFFFF", iconSize=(66,66))


        
        
        overallLayout.addWidget(self.workflowWidget)
        #overallLayout.addWidget(self.overallStackWidget)
        self.setLayout(overallLayout)

        # ====================================================================================================================
        # Create an update method for when the tab widget gets changed to refresh elements
        self.workflowWidget.currentChanged.connect(self._updateTabDependencies)


    def _createDataFillLayout(self, layoutFillSA):
        """
        Creates the layout of the fill subtab based on the options for each fill method

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

        # Create teh fill limit widget
        self.layoutFillGapLimit = QtWidgets.QTextEdit()
        self.layoutFillGapLimit.setPlaceholderText('30')
        self.layoutFillGapLimit.setFixedWidth(50)
        self.layoutFillGapLimit.setFixedHeight(25)
        self.layoutFillGapLimit.setVisible(False)

        # Create the layout for the fill limit
        filledGapLayout = QtWidgets.QHBoxLayout()
        filledGapLayout.setAlignment(QtCore.Qt.AlignTop)

        filledGapLayout.addWidget(self.layoutFillGapLimitLabel, 1, QtCore.Qt.AlignLeft)
        filledGapLayout.addWidget(self.layoutFillGapLimit, 5, QtCore.Qt.AlignLeft)

        # Add the limit into the main page
        filledGapLayoutWidget = QtWidgets.QWidget()
        filledGapLayoutWidget.setLayout(filledGapLayout)

        layoutFillRightLayout.addWidget(filledGapLayoutWidget)

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
        stackedWidget.setLayout(self.stackedFillLayout)
        stackedWidget.setVisible(False)

        # Add each of the interpolation types to it
        nearestWidget = QtWidgets.QWidget()
        nearestWidget.setLayout(nearestLayout)
        nearestWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.stackedFillLayout.addWidget(nearestWidget)

        linearWidget = QtWidgets.QWidget()
        linearWidget.setLayout(linearLayout)
        linearWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.stackedFillLayout.addWidget(linearWidget)

        quadradicWidget = QtWidgets.QWidget()
        quadradicWidget.setLayout(quadradicLayout)
        quadradicWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.stackedFillLayout.addWidget(quadradicWidget)

        cubicWidget = QtWidgets.QWidget()
        cubicWidget.setLayout(cubicLayout)
        cubicWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.stackedFillLayout.addWidget(cubicWidget)

        splineWidget = QtWidgets.QWidget()
        splineWidget.setLayout(polyLayout)
        splineWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.stackedFillLayout.addWidget(splineWidget)

        # Add the stacked layout to the main layout
        layoutFillRightLayout.addWidget(stackedWidget)
        stackedWidget.setVisible(True)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutFillClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutFillClearButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

        # Link the button to the clear function
        self.layoutFillClearButton.clicked.connect(self._applyFillClearToDataset)
        self.layoutFillClearButton.clicked.connect(self._updateFillSubtab)

        # Create the apply button
        self.layoutFillApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutFillApplyButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

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

        ### Create the full layout ###
        layoutFill = QtWidgets.QHBoxLayout()

        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutFillLeftLayout)
        layoutFill.addWidget(leftWidget, 1)

        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutFillRightLayout)
        layoutFill.addWidget(rightWidget, 2)

        layoutFillSA.setLayout(layoutFill)

    def _createDataExtendLayout(self, layoutMain):
        """
        Creates the layout of the fill subtab based on the options for each fill method

        """

        # Set the options available for filling the data
        extendOptions = ['None', 'Fourier']

        # Create and add a dropdown selector with the available options
        layoutMain.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Extend Method<strong>'))

        self.layoutExtendMethodSelector = QtWidgets.QComboBox()
        self.layoutExtendMethodSelector.addItems(extendOptions)
        layoutMain.addWidget(self.layoutExtendMethodSelector)

        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        layoutMain.addWidget(lineA)

        # Create the fill limit label
        extendGapLabel = QtWidgets.QLabel('Extension Duration')

        # Create the fill limit widget
        self.layoutExtendGapLimit = QtWidgets.QTextEdit()
        self.layoutExtendGapLimit.setPlaceholderText('30')
        self.layoutExtendGapLimit.setFixedWidth(50)
        self.layoutExtendGapLimit.setFixedHeight(25)

        # Create the layout for the fill limit
        extendGapLayout = QtWidgets.QHBoxLayout()
        extendGapLayout.setAlignment(QtCore.Qt.AlignTop)

        extendGapLayout.addWidget(extendGapLabel, 1, QtCore.Qt.AlignLeft)
        extendGapLayout.addWidget(self.layoutExtendGapLimit, 5, QtCore.Qt.AlignLeft)

        # Add the limit into the main page
        extendGapLayoutWidget = QtWidgets.QWidget()
        extendGapLayoutWidget.setLayout(extendGapLayout)

        layoutMain.addWidget(extendGapLayoutWidget)

        # Adjust the layout of the widgets
        layoutMain.setAlignment(QtCore.Qt.AlignTop)

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
        stackedWidget.setVisible(False)

        # Add each of the interpolation types to it
        noneWidget = QtWidgets.QWidget()
        noneWidget.setLayout(noneLayout)
        self.stackedExtendLayout.addWidget(noneWidget)

        fourierWidget = QtWidgets.QWidget()
        fourierWidget.setLayout(fourierLayout)
        self.stackedExtendLayout.addWidget(fourierWidget)

        # Add the stacked layout to the main layout
        layoutMain.addWidget(stackedWidget)

        ### Connect the stacked widget with the selection combo box ###
        self.layoutExtendMethodSelector.currentIndexChanged.connect(self._updateExtendSubtab)

    def _createDataWindowLayout(self, layoutMain):

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
        layoutMain.addWidget(dataPlot.chartView, 0, 0, 1, 3)

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

        layoutMain.addWidget(startLayoutWidget, 1, 0)

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
        layoutMain.addWidget(stopLayoutWidget, 1, 1)

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
        layoutMain.addWidget(lagLayoutWidget, 1, 2)

    def _createSummaryTabLayout(self, mainLayout):
        """


        """
        # todo: doc string

        ### Create the left side dataset summary table ###
        # Create the list widget
        summaryListWidget = QtWidgets.QListWidget()

        # Populate the widget with data
        # todo: add the linkage across the tables

        # Add to the layout
        mainLayout.addWidget(summaryListWidget)

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
        summaryClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        summaryClearButton.setMaximumSize(125, 65)

        # Create the start button
        summaryStartButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Start</strong>')
        summaryStartButton.setMaximumSize(125, 65)

        # Create an horizontal layout, aligned to the right
        summaryButtonsLayout = QtWidgets.QHBoxLayout()
        summaryButtonsLayout.setAlignment(QtCore.Qt.AlignRight)

        summaryButtonsLayout.addWidget(summaryClearButton)
        summaryButtonsLayout.addWidget(summaryStartButton)

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


    def setPredictorDefaultStack(self):
        self.stackedPredictorWidget.setCurrentIndex(0)

    def setPredictorExpertStack(self):
        self.stackedPredictorWidget.setCurrentIndex(1)

    def _updateFillSubtab(self):
        """
        Updates the state of the fill subtab methods pane based on the method selector

        """

        # Switch the stacked widgets
        self.stackedFillLayout.setCurrentIndex(self.layoutFillMethodSelector.currentIndex())

        # Update the gap limit visibility
        if self.layoutFillMethodSelector.currentIndex() > 0:
            self.layoutFillGapLimitLabel.setVisible(True)
            self.layoutFillGapLimit.setVisible(True)
        else:
            self.layoutFillGapLimitLabel.setVisible(False)
            self.layoutFillGapLimit.setVisible(False)

    def _updateFillOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Check that the fill options have been added into the table
        if 'FillMethod' not in self.parent.datasetTable.columns:
            self.__addFillOptionsToDatasetTable()

        # Get the current dataset
        currentIndex = self.fillList.currentIndex().row()
        currentInternalID = self.fillList.datasetTable.index[currentIndex]

        # Get the options for the item
        fillMethod = self.parent.datasetTable.at[currentInternalID, 'FillMethod']
        fillGap = self.parent.datasetTable.at[currentInternalID, 'FillMaximumGap']
        # If needed, can extract more information based on the fill method here

        # Get the options for the selector and stack
        fillOptionsIndex = [x for x in range(self.layoutFillMethodSelector.count()) if self.layoutFillMethodSelector.itemText(x) == fillMethod][0]
        self.stackedFillLayout.setCurrentIndex(fillOptionsIndex)
        self.layoutFillMethodSelector.setCurrentIndex(fillOptionsIndex)

        # Set the values into the widgets
        # Correct this issue
        self.layoutFillGapLimit.setText(str(fillGap))

    def _applyFillOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Check that the fill options have been added into the table
        if 'FillMethod' not in self.parent.datasetTable.columns:
            self.__addFillOptionsToDatasetTable()

        # Extract the fill limit
        try:
            fillLimit = int(self.layoutFillGapLimit.toPlainText())
        except:
            fillLimit = None

        # Get the method to be utilized
        fillMethod = self.layoutFillMethodSelector.currentText()

        # Get the current dataset
        currentIndex = self.fillList.currentIndex().row()
        currentInternalID = self.fillList.datasetTable.index[currentIndex]

        # Set the values
        self.parent.datasetTable.at[currentInternalID, 'FillMethod'] = fillMethod
        self.parent.datasetTable.at[currentInternalID, 'FillMaximumGap'] = fillLimit

        # Clear the button click
        self.layoutFillApplyButton.setChecked(False)

    def _applyFillClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        if 'FillMethod' not in self.parent.datasetTable.columns:
            self.__addFillOptionsToDatasetTable()

        # Get the current dataset
        currentIndex = self.fillList.currentIndex().row()
        currentInternalID = self.fillList.datasetTable.index[currentIndex]

        # Set the values
        self.parent.datasetOperationsTable.at[currentInternalID, 'FillMethod'] = 'None'
        self.parent.datasetOperationsTable.at[currentInternalID, 'FillMaximumGap'] = None

        # Clear the button click
        self.layoutFillClearButton.setChecked(False)

        # Switch the stacked widgets
        self.layoutFillMethodSelector.setCurrentIndex(0)
        self._updateFillSubtab()

    def _updateExtendSubtab(self):
        self.stackedExtendLayout.setCurrentIndex(self.layoutExtendMethodSelector.currentIndex())


    def _updateTabDependencies(self, tabIndex):
        # todo: doc string

        ### Get the current index the widget has been changed to ###
        # currentIndex = self.workflowWidget.currentIndex()
        ##print(tabIndex)


        if tabIndex == 3:
            # Update the summary boxes
            ##print('@@ debug statement')
            pass






