from PyQt5 import QtWidgets, QtCore
from datetime import datetime
from resources.modules.Miscellaneous import  loggingAndErrors

class preferencesDialog(QtWidgets.QDialog):
    """
    """
    def __init__(self):
        super(preferencesDialog, self).__init__()
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.categorySelector = QtWidgets.QListWidget()
        self.categorySelector.setFixedWidth(75)
        self.categorySelector.addItems(["General","Plotting","Statistics"])
        self.categorySelector.currentTextChanged.connect(self.changePrefWindow)
        self.setupGeneralTab()
        self.setupPlottingTab()
        self.setupStatisticsTab()
        self.setCurrentPreferences()
        
        self.mainLayout.addWidget(self.categorySelector)
        self.mainLayout.addWidget(self.generalTab)
        self.setLayout(self.mainLayout)
        self.setWindowTitle('Application Preferences')

        self.currentSelection = 'General'

        self.exec_()
        return
    
    def changePrefWindow(self, newWindow):
        """
        """
        if newWindow == self.currentSelection:
            return
        
        if self.currentSelection == 'General':
            widg = self.generalTab
        if self.currentSelection == 'Plotting':
            widg = self.plottingTab
        if self.currentSelection == 'Statistics':
            widg = self.statisticsTab

        if newWindow == "General":
            self.currentSelection = 'General'
            self.generalTab.setVisible(True)
            self.mainLayout.replaceWidget(widg, self.generalTab)
            widg.setVisible(False)
            self.update()

        if newWindow == 'Plotting':
            self.currentSelection = 'Plotting'
            self.plottingTab.setVisible(True)
            self.mainLayout.replaceWidget(widg, self.plottingTab)
            widg.setVisible(False)
            self.update()
        
        if newWindow == 'Statistics':
            self.currentSelection = 'Statistics'
            self.statisticsTab.setVisible(True)
            self.mainLayout.replaceWidget(widg, self.statisticsTab)
            widg.setVisible(False)
            self.update()


    def setCurrentPreferences(self):
        """
        """
        return
    
    def setupGeneralTab(self):
        """
        """
        self.generalTab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()

        self.appDatetimeSelector = QtWidgets.QDateEdit()
        self.appDatetimeSelector.setDisplayFormat("yyyy-MM-dd")
        self.appDatetimeSelector.setCalendarPopup(True)
        today = datetime.now()
        self.appDatetimeSelector.setMaximumDate(QtCore.QDate(today.year, today.month, today.day))
        self.appDatetimeSelector.setDate(QtCore.QDate(today.year, today.month, today.day))
        layout.addRow(QtWidgets.QLabel("Set Application Date"), self.appDatetimeSelector)

        self.generalTab.setLayout(layout)

        return

    def setupPlottingTab(self):
        """
        """
        self.plottingTab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()

        return
    
    def setupStatisticsTab(self):
        """
        """
        self.statisticsTab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Stats"))
        self.statisticsTab.setLayout(layout)
        return