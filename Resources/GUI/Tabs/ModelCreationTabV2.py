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
import pandas as pd


class hoverLabel(QtWidgets.QLabel):
    """
    This is the label that is used on the left hand side of the tab
    to change between the model creation sub-pages. It subclasses
    a regular QLabel, but add's hover and click functionality.

    Unfortunately, we have to style this label in this
    function and cannot style it in the application
    stylesheet.
    """
    changeTabSignal = QtCore.pyqtSignal(int)

    def __init__(self, text, objectName, idx):
        QtWidgets.QLabel.__init__(self, text = text, objectName = objectName)
        self.selectedTab = False
        self.idx = idx
    
    def mousePressEvent(self, event):
        QtWidgets.QLabel.mousePressEvent(self, event)
        self.onSelect()

    def onSelect(self):
        self.selectedTab = True
        self.changeTabSignal.emit(self.idx)
        self.setStyleSheet("""
        QLabel {border-left: 3px solid white; color: white}
        """)

    def onDeselect(self):
        self.selectedTab = False
        self.setStyleSheet("""
        QLabel {border-left: 3px solid #4e4e4e; color: #d8d8d8}
        """)

    def enterEvent(self, event):
        if not self.selectedTab:
            self.setStyleSheet("""
            QLabel {border-left: 3px solid #4e4e4e; color: white}
            """)
    def leaveEvent(self, event):
        if not self.selectedTab:
            self.setStyleSheet("""
            QLabel {border-left: 3px solid #4e4e4e; color: #d8d8d8}
            """)


class ModelCreationTab(QtWidgets.QWidget):
    """
    This is the overall tab layout. 
    """

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        
        self.parent = parent

        # Set up the overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        overallLayout.setContentsMargins(0,0,0,0)
        overallLayout.setSpacing(0)
        targetSelectLayout = QtWidgets.QGridLayout()
        predictorLayout = QtWidgets.QVBoxLayout()
        optionsLayout = QtWidgets.QVBoxLayout()
        summaryLayout = QtWidgets.QVBoxLayout()
        workflowLayout = QtWidgets.QVBoxLayout()

        # Left Side workflow Widget
        self.workflowWidget = QtWidgets.QWidget()
        workflowLayout.setContentsMargins(0,0,0,0)
        workflowLayout.setSpacing(0)
        self.targetWidgetButton = hoverLabel('<p style="font-size: 20px; margin:0px; padding: 0px;">Specify</p>FORECAST TARGET', objectName='workflowLabel', idx = 0)
        self.targetWidgetButton.setTextFormat(QtCore.Qt.RichText)
        self.targetWidgetButton.onSelect()
        workflowLayout.addWidget(self.targetWidgetButton)
        self.predictorWidgetButton = hoverLabel('<p style="font-size: 20px; margin:0px; padding: 0px;">Select</p>PREDICTORS', objectName='workflowLabel', idx = 1)
        self.predictorWidgetButton.setTextFormat(QtCore.Qt.RichText)
        workflowLayout.addWidget(self.predictorWidgetButton)
        self.optionsWidgetButton = hoverLabel('<p style="font-size: 20px; margin:0px; padding: 0px;">Set</p>FORECAST OPTIONS', objectName='workflowLabel', idx = 2)
        self.optionsWidgetButton.setTextFormat(QtCore.Qt.RichText)
        workflowLayout.addWidget(self.optionsWidgetButton)
        self.summaryWidgetButton = hoverLabel('<p style="font-size: 20px; margin:0px; padding: 0px;">Summary</p>BUILD MODELS', objectName='workflowLabel', idx = 3)
        self.summaryWidgetButton.setTextFormat(QtCore.Qt.RichText)
        workflowLayout.addWidget(self.summaryWidgetButton)
        self.buttons = [self.targetWidgetButton, self.predictorWidgetButton, self.optionsWidgetButton, self.summaryWidgetButton]
        self.workflowWidget.setLayout(workflowLayout)

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
        self.customMethodSpecEdit.setPlaceholderText("Define a custom python function here. The variable 'x' represents the periodic dataset. E.g. np.nanstd(x)")
        layout.addWidget(self.customMethodSpecEdit)
        self.customMethodSpecEdit.hide()
        
        widg.setLayout(layout)
        targetSelectLayout.addWidget(widg, 0, 0, 1, 1)
        targetSelectLayout.addWidget(self.dataPlot, 1, 0, 1, 1)
        overallLayout.addWidget(self.workflowWidget)
        overallLayout.addLayout(targetSelectLayout)
        self.setLayout(overallLayout)

    