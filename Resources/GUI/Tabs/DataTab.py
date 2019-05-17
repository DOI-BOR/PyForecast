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
from resources.GUI.CustomWidgets.PyQtGraphs import TimeSeriesSliderPlot
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetView
import  sys
import  os

class DataTab(QtWidgets.QWidget):
    """
    """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()
        porLabel = QtWidgets.QLabel("Period of Record:")
        self.porT1 = QtWidgets.QLineEdit()
        self.porT2 = QtWidgets.QLineEdit()
        self.porT2.setDisabled(True)
        self.porT1.setFixedWidth(50)
        self.porT2.setFixedWidth(50)
        self.downloadButton = QtWidgets.QPushButton("Download / Update")
        self.importButton = QtWidgets.QPushButton("Import")
        self.downloadProgressBar = QtWidgets.QProgressBar()
        self.downloadProgressBar.setRange(0, 100)
        self.downloadProgressBar.setFixedWidth(100)
        self.downloadProgressBar.hide()
        self.compositeButton = QtWidgets.QPushButton("Create Composite Dataset")
        hlayout.addWidget(porLabel)
        hlayout.addWidget(self.porT1)
        hlayout.addWidget(self.porT2)
        hlayout.addWidget(self.downloadButton)
        hlayout.addWidget(self.importButton)
        hlayout.addWidget(self.downloadProgressBar)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(500, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        hlayout.addWidget(self.compositeButton)
        layout.addLayout(hlayout)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.dataPlot = TimeSeriesSliderPlot()
        splitter.addWidget(self.dataPlot)

        self.table = SpreadSheetView()
        splitter.addWidget(self.table)

        layout.addWidget(splitter)

        self.setLayout(layout)

if __name__ == '__main__':
    print(os.listdir())
    app = QtWidgets.QApplication(sys.argv)
    widg = DataTab()
    widg.show()
    sys.exit(app.exec_())


