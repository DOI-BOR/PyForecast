"""
Script Name:        StatisticalModelsTab.py

Description:        'StatisticalModelsTab.py' is a PyQt5 GUI for the NextFlow application. 
                    The GUI includes all the visual aspects of the Statistical Models Tab (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

"""
NOTES ---------------------

-Models should not be included if one of the predictors has less than 5% influence on overall runoff
-predictor significance tests
-predictor importance in overall model result table

"""

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from resources.GUI.CustomWidgets.PyQtGraphs import TimeSeriesSliderPlot
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetView
import  sys
import  os

class variableSpecWidget(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QGridLayout()
        self.icon = QtGui.QPixmap() # Need to initially fill with ?
        self.predictorSelect = QtWidgets.QComboBox()
        self.functionSelect = QtWidgets.QComboBox()
        self.windowEdit = QtWidgets.QSpinBox()
        self.windowUnitSelect = QtWidgets.QComboBox()
        self.periodEdit = QtWidgets.QSpinBox()
        self.periodUnitSelect = QtWidgets.QComboBox()
        
        layout.addWidget(self.icon, 0, 0, 4, 1)
        layout.addWidget(self.predictorSelect, 0, 1, 1, 2)
        layout.addWidget(self.functionSelect, 1, 1, 1, 2)
        layout.addWidget(self.windowEdit, 2, 1, 1, 1)
        layout.addWidget(self.windowUnitSelect, 2, 2, 1, 1)
        layout.addWidget(self.periodEdit, 3, 1, 1, 1)
        layout.addWidget(self.periodUnitSelect, 3, 2, 1, 1)


class StatisticalModelsTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        overallLayout = QtWidgets.QHBoxLayout()
        leftSectionLayout = QtWidgets.QVBoxLayout()

        targetHeader = QtWidgets.QLabel("Forecast Target")
        predictorsHeader = QtWidgets.QLabel("Predictors")
        targetWidget = QtWidgets.QWidget()


