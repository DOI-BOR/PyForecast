"""
Script Name:        NextFlowGUI.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      Apr 2, 2018

Description:        'NextFlowGUI.py' is a PyQt5 GUI for the NextFlow application. 
                    The GUI includes all the visual aspects of the application (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

import  sys
import  os
import  platform
import  ctypes
import  subprocess
from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from    resources.GUI.Tabs  import  DatasetsTab, DataTab, CreateForecastsTab

myappid = u'reclamation.NextFlow.2b'
if platform.system() == 'Windows':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class UI_MainWindow(object):
    """
    This Object class is used to describe the layout of the 
    FlowCast application. It lays out all the tabs and menubars in 
    the application and applies the overall stylesheet
    """


    def setUI(self):
        """
        Physically lays out the application.
        """
        # Window
        self.setWindowTitle("NextFlow - Untitled.fcst")
        self.setMinimumSize(QtCore.QSize(900,750))

        # Stylesheet
        self.setStyleSheet(open(os.path.abspath('resources/GUI/stylesheets/main.qss')).read())
        
        # Menu
        self.appMenu = MenuBar()
        self.setMenuBar(self.appMenu)

        # Tabs
        tabWidget = QtWidgets.QTabWidget()

        self.datasetTab = DatasetsTab.DatasetTab()
        tabWidget.addTab(self.datasetTab, "Datasets")

        self.dataTab = DataTab.DataTab()
        tabWidget.addTab(self.dataTab, "Data")

        #self.forecastsTab = CreateForecastsTab.CreateForecastsTab()
        #tabWidget.addTab(self.forecastsTab, "Create Forecasts")
        

        self.setCentralWidget(tabWidget)



class MenuBar(QtWidgets.QMenuBar):
    """
    This subclass of QMenuBar describes the layout of the FlowCast
    applicaiton's menubar. For the functionality of this menubar, 
    see the 'MenuBar' section of 'application.py'
    """
    def __init__(self, parent = None):
        """
        Initialization function for the MenuBar class. Physically
        lays out the MenuBar widget.

        Keyword Arguments:
        parent -- The parent widget of this menubar. Not used.
        """
        QtWidgets.QMenuBar.__init__(self)

        # File Menu
        self.fileMenu = self.addMenu("File")
        self.newAction = QtWidgets.QAction("New Forecast")
        self.saveAction = QtWidgets.QAction("&Save")
        self.saveAsAction = QtWidgets.QAction("Save As")
        self.openAction = QtWidgets.QAction("Open")
        self.excelAction = QtWidgets.QAction("To Excel")
        self.pdfAction = QtWidgets.QAction("To PDF")
        self.databaseAction = QtWidgets.QAction("To Database")
        self.exitAction = QtWidgets.QAction("Exit FlowCast")
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        exportMenu = self.fileMenu.addMenu("Export Forecast")
        exportMenu.addAction(self.excelAction)
        exportMenu.addAction(self.pdfAction)
        exportMenu.addAction(self.databaseAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        # Edit Menu
        self.editMenu = self.addMenu("Edit")
        self.preferencesAction = QtWidgets.QAction("Preferences")
        self.dataloaderAction = QtWidgets.QAction("Dataloaders")
        self.advancedOptionsAction = QtWidgets.QAction("Advanced Options")
        self.editMenu.addAction(self.preferencesAction)
        self.editMenu.addAction(self.dataloaderAction)
        self.editMenu.addAction(self.advancedOptionsAction)

        # About Menu
        self.aboutMenu = self.addMenu("About")
        self.documentationAction = QtWidgets.QAction("Documentation")
        self.versionAction = QtWidgets.QAction("Version Info")
        self.updateAction = QtWidgets.QAction("Check For Updates")
        self.aboutMenu.addAction(self.documentationAction)
        self.aboutMenu.addAction(self.versionAction)
        self.aboutMenu.addAction(self.updateAction)

        return
