"""
Script Name:        DataTab.py

Description:        'DataTab.py' is a PyQt5 GUI for the NextFlow application. 
                    The GUI includes all the visual aspects of the Data Tab (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetList_HTML_Formatted
from resources.GUI.CustomWidgets.PyQtGraphs import DataTabPlots
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetView
import  sys
import  os
from datetime import datetime

class DataTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self)
        self.parent = parent

        # Initialize the Layouts
        overallLayout = QtWidgets.QHBoxLayout()
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

        self.downloadButton = QtWidgets.QPushButton("Retrieve Data")
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
        self.datasetList = DatasetList_HTML_Formatted(self, datasetTable = self.parent.datasetTable, HTML_formatting = "", addButtons = False )
        self.plot = DataTabPlots(self)
        self.spreadsheet = SpreadSheetView(self)

        # Create a stackedWidget to store the plots and spreadsheet
        self.stackWidget = QtWidgets.QStackedWidget()
        self.stackWidget.addWidget(self.plot)
        self.stackWidget.addWidget(self.spreadsheet)
        self.stackWidget.setCurrentIndex(0)

        # Switch Button
        self.switchViewButton = QtWidgets.QPushButton("View Spreadsheet")
        self.switchViewButton.pressed.connect(self.switchView)
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addSpacerItem(QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Minimum))
        buttonLayout.addWidget(self.switchViewButton)

        # Build the overall page
        widgetLeft = QtWidgets.QWidget()
        leftPaneLayout.addLayout(downUpdateBoxLayout)
        leftPaneLayout.addWidget(self.datasetList)
        widgetLeft.setMaximumWidth(330)
        widgetLeft.setLayout(leftPaneLayout)
        widgetRight = QtWidgets.QWidget()
        rightSideLayout = QtWidgets.QVBoxLayout()
        rightSideLayout.addWidget(self.stackWidget)
        rightSideLayout.addLayout(buttonLayout)
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


