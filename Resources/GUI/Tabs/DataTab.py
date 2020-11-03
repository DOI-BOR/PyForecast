"""
Script Name:        DataTab.py

Description:        'DataTab.py' is a PyQt5 GUI for the PyForecast application. 
                    The GUI includes all the visual aspects of the Data Tab (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetListHTMLFormatted
from resources.GUI.CustomWidgets import SVGIcon, customTabs
from resources.GUI.CustomWidgets.PyQtGraphs import DataTabPlots
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetView
import  sys
import  os
from datetime import datetime

class DataTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, objectName = 'tabPage')
        self.parent = parent

        # Initialize the Layouts
        overallLayout = QtWidgets.QHBoxLayout()
        overallLayout.setContentsMargins(0,0,0,0)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        leftPaneLayout = QtWidgets.QVBoxLayout()
        downUpdateBoxLayout = QtWidgets.QFormLayout()

        # Build the download/update box
        title = QtWidgets.QLabel('<b style="font-size: 17px">Download/Update Data</b>')
        self.startYearInput = QtWidgets.QSpinBox()
        self.startYearInput.setMinimum(1900)
        self.startYearInput.setMaximum(datetime.now().year + 1 if datetime.now().month >= 10 else datetime.now().year)
        self.startYearInput.setValue(self.startYearInput.maximum() - 30)
        self.endYearInput = QtWidgets.QSpinBox()
        self.endYearInput.setMinimum(1900)
        self.endYearInput.setMaximum(datetime.now().year + 1 if datetime.now().month >= 10 else datetime.now().year)
        self.endYearInput.setValue(self.endYearInput.maximum())

        self.downloadOptionsGroupBox = QtWidgets.QGroupBox("Retrieval Option")
        self.freshDownloadOption = QtWidgets.QRadioButton("Download all data")
        self.updateOption = QtWidgets.QRadioButton("Update with new data")
        self.freshDownloadOption.setChecked(True)

        icon = SVGIcon.SVGIcon(os.path.abspath("resources/graphicalResources/icons/get_app-24px.svg"), "#333333")
        self.downloadButton = QtWidgets.QPushButton(icon, "Retrieve Data")
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.hide()
        self.statusBar = QtWidgets.QLabel("") # Maybe change this to a textEdit
        self.statusBar.hide()

        downUpdateBoxLayout.addRow(title)
        downUpdateBoxLayout.addRow(QtWidgets.QLabel("Start Year"), self.startYearInput)
        downUpdateBoxLayout.addRow(QtWidgets.QLabel("End Year"), self.endYearInput)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.freshDownloadOption)
        vbox.addWidget(self.updateOption)
        self.downloadOptionsGroupBox.setLayout(vbox)
        downUpdateBoxLayout.addRow(self.downloadOptionsGroupBox)
        downUpdateBoxLayout.addRow(self.downloadButton)
        downUpdateBoxLayout.addRow(self.progressBar)
        downUpdateBoxLayout.addRow(self.statusBar)

        # Initialize other widgets
        # self.datasetList = DatasetList_HTML_Formatted(self, datasetTable = self.parent.datasetTable, HTML_formatting = "", addButtons = False )
        self.datasetList = DatasetListHTMLFormatted(self, datasetTable=self.parent.datasetTable, addButtons=False)
        self.plot = DataTabPlots(self)
        self.spreadsheet = SpreadSheetView(self)

        # Create a stackedWidget to store the plots and spreadsheet
        self.stackWidget = customTabs.EnhancedTabWidget(self, "above", "vertical", True, True, True)

        #self.stackWidget = QtWidgets.QTabWidget(objectName = 'datasetTabPane')
        #self.stackWidget.setTabPosition(QtWidgets.QTabWidget.East)
        #self.stackWidget.setIconSize(QtCore.QSize(25,25))
        #icon = SVGIcon.SVGIcon(os.path.abspath("resources/graphicalResources/icons/chart_areaspline-24px.svg"), '#FFFFFF', 270, (100,100))
        #self.stackWidget.addTab(self.plot, icon, "")
        #icon = SVGIcon.SVGIcon(os.path.abspath("resources/graphicalResources/icons/border_all-24px.svg"), '#FFFFFF', 270, (100,100))
        #self.stackWidget.addTab(self.spreadsheet, icon, "")
        #self.stackWidget.setCurrentIndex(0)

        self.stackWidget.addTab(self.plot, "GRAPH", "resources/GraphicalResources/icons/chart_areaspline-24px.svg", "#FFFFFF", iconSize=(25,25))
        self.stackWidget.addTab(self.spreadsheet, "TABLE", "resources/GraphicalResources/icons/border_all-24px.svg", "#FFFFFF", iconSize=(25,25))

        # Configuration Widget
        widg = QtWidgets.QWidget()
        self.stackWidget.addTab(widg, "CONFIGURE", "resources/graphicalResources/icons/settings-24px.svg", "#FFFFFF", iconSize=(20,20) )


        # Build the overall page
        widgetLeft = QtWidgets.QWidget()
        leftPaneLayout.addLayout(downUpdateBoxLayout)
        leftPaneLayout.addWidget(self.datasetList)
        leftPaneLayout.setContentsMargins(0,0,0,0)
        widgetLeft.setMaximumWidth(330)
        widgetLeft.setLayout(leftPaneLayout)
        widgetRight = QtWidgets.QWidget()
        rightSideLayout = QtWidgets.QVBoxLayout()
        rightSideLayout.setContentsMargins(0,0,0,0)
        rightSideLayout.addWidget(self.stackWidget)
        widgetRight.setLayout(rightSideLayout)
        splitter.addWidget(widgetLeft)
        splitter.addWidget(widgetRight)
        overallLayout.addWidget(splitter)
        
        
        self.setLayout(overallLayout)

    def switchView(self):
        
        if self.stackWidget.currentIndex() == 0:
            self.stackWidget.setCurrentIndex(1)
            self.switchViewButton.setText("View Plots")
        else:
            self.stackWidget.setCurrentIndex(0)
            self.switchViewButton.setText("View Spreadsheet")


if __name__ == '__main__':
    print(os.listdir())
    app = QtWidgets.QApplication(sys.argv)
    widg = DataTab()
    widg.show()
    sys.exit(app.exec_())


