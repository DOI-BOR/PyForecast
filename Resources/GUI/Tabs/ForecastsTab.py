"""
Script Name:        ForecastsTab.py

Description:      
"""

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetList_HTML_Formatted
from resources.GUI.CustomWidgets import SVGIcon, customTabs

class ForecastsTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self)

        self.parent = parent

        # Overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        