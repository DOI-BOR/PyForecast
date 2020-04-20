"""
Script Name:        ForecastsTab.py

Description:      
"""
import sys
import os
sys.path.append(r"C:\Users\KFoley\Documents\NextFlow")

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from resources.GUI.CustomWidgets.forecastList_FormattedHTML import forecastList_HTML
from resources.GUI.CustomWidgets import SVGIcon, customTabs

class ForecastsTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self)

        self.parent = parent

        # Overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        overallLayout.setContentsMargins(0,0,0,0)

        # Right side tab widget
        tabWidget = customTabs.EnhancedTabWidget(self, "above", "vertical", eastTab=True, tint=True)
        aggPage = QtWidgets.QWidget()
        singlePage = QtWidgets.QWidget()
        configPage = QtWidgets.QWidget()
        tabWidget.addTab(aggPage, "COMPARE<br>FORECASTS", "resources/GraphicalResources/icons/chart_bellcurve-24px.svg", "#FFFFFF", iconSize=(25,25))
        tabWidget.addTab(singlePage, "FORECAST<br>DETAIL", "resources/GraphicalResources/icons/chart_scatter-24px.svg", "#FFFFFF", iconSize=(25,25))
        tabWidget.addTabBottom(configPage, "CONFIGURE", "resources/GraphicalResources/icons/settings-24px.svg", "#FFFFFF", iconSize=(20,20))
      
        forecastsPane = forecastList_HTML(self.parent)
        forecastsPane.setFixedWidth(300)
        forecastsPane.setContentsMargins(0,0,0,0)

        overallLayout.addWidget(forecastsPane)
        overallLayout.addWidget(tabWidget)


        # Set the widgets layout
        self.setLayout(overallLayout)
        self.setContentsMargins(0,0,0,0)

if __name__ == '__main__':
    
    app  = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QWidget()
    widg = ForecastsTab(mw)
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(widg)
    mw.setLayout(layout)
    mw.show()
    sys.exit(app.exec_())