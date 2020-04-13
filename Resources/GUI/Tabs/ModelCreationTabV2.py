"""
Script Name:    ModelCreationTabV2.py

Description:    Defines the layout for the Model Creation Tab. Includes all the sub-widgets
                for the stacked widget.
"""

# Import Libraries
from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui

from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetList_HTML_Formatted
from resources.GUI.CustomWidgets.PyQtGraphs import ModelTabPlots
from resources.GUI.CustomWidgets.customTabs import EnhancedTabWidget
import pandas as pd


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
        targetSelectLayout = QtWidgets.QGridLayout()
        predictorLayout = QtWidgets.QVBoxLayout()
        optionsLayout = QtWidgets.QVBoxLayout()
        summaryLayout = QtWidgets.QVBoxLayout()
        workflowLayout = QtWidgets.QVBoxLayout()


        self.workflowWidget = EnhancedTabWidget(self, 'above', 'vertical', True, False, True)


        # ===================================================================================================================

        # Layout the Target Selection Widget
        widg = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.dataPlot = ModelTabPlots(self, objectName='ModelTabPlot')
        self.dataPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.targetSelect = QtWidgets.QComboBox()
        self.datasetList = DatasetList_HTML_Formatted(self, datasetTable = self.parent.datasetTable, addButtons = False )
        self.targetSelect.setModel(self.datasetList.model())
        self.targetSelect.setView(self.datasetList)

        layout.addRow("Forecast Target", self.targetSelect)
        
        self.selectedItemDisplay = DatasetList_HTML_Formatted(self, addButtons = False, objectName = 'ModelTargetList')
        self.selectedItemDisplay.setFixedHeight(99)
        self.selectedItemDisplay.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        layout.addWidget(self.selectedItemDisplay)
        
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

        layout.addRow("Target Period (Start)", self.periodStart)
        layout.addRow("Target Period (End)", self.periodEnd)

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
        layout.addRow("Period Calculation", self.methodCombo)

        self.customMethodSpecEdit = QtWidgets.QLineEdit()
        self.customMethodSpecEdit.setPlaceholderText("Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        layout.addWidget(self.customMethodSpecEdit)
        self.customMethodSpecEdit.hide()
        
        widg.setLayout(layout)
        targetSelectLayout.addWidget(widg, 0, 0, 1, 1)
        targetSelectLayout.addWidget(self.dataPlot, 1, 0, 1, 1)
        widg = QtWidgets.QWidget()
        widg.setLayout(targetSelectLayout)
        self.workflowWidget.addTab(widg, "FORECAST<br>TARGET", "resources/GraphicalResources/icons/target-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ===================================================================================================================

        # Layout the predictor selector widget

        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "PREDICTORS", "resources/GraphicalResources/icons/bullseye-24px.svg", "#FFFFFF", iconSize=(66,66))
        
        
        # ====================================================================================================================

        # Layout the Forecast Settings widget
        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "OPTIONS", "resources/GraphicalResources/icons/tune-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ====================================================================================================================

        # Lay out the summary widget
        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "SUMMARY", "resources/GraphicalResources/icons/clipboard-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ====================================================================================================================

        # Layout the results widget
        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "RESULTS", "resources/GraphicalResources/icons/run-24px.svg", "#FFFFFF", iconSize=(66,66))


        
        
        overallLayout.addWidget(self.workflowWidget)
        #overallLayout.addWidget(self.overallStackWidget)
        self.setLayout(overallLayout)

    