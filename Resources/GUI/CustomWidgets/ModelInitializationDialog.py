from PyQt5 import QtWidgets, QtCore, QtGui

class forecastTargetPage(QtWidgets.QWizardPage):
    """
    """

    def __init__(self, modelRunTableEntry = None):

        QtWidgets.QWizard.__init__(self)
        self.setTitle("Forecast Target")
        self.setSubTitle("Use the form below to tell PyForecast what data you are trying to forecast.")

        # Set the UI
        self.setUI()

        # Connectors
        self.periodStart.dateChanged.connect(self.periodEnd.setMinimumDate)
        self.periodEnd.dateChanged.connect(self.periodStart.setMaximumDate)
        self.periodStart.dateChanged.connect(self.updateSummaryLabel)

        # Initialize dates
        self.periodStart.setDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 4, 1))
        self.periodEnd.setDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 7, 31))


    def setUI(self):

        # Create Page UI
        vlayout = QtWidgets.QVBoxLayout()

        targetLabel = QtWidgets.QLabel("<strong>Forecast Target</strong>")
        self.targetDropDown = QtWidgets.QComboBox()
        vlayout.addWidget(targetLabel)
        vlayout.addWidget(self.targetDropDown)
        
        periodLabel = QtWidgets.QLabel("<strong>Forecast Period</strong>")
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
        vlayout.addWidget(periodLabel)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel("Period Start"))
        hlayout.addWidget(self.periodStart)
        vlayout.addLayout(hlayout)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel("Period End"))
        hlayout.addWidget(self.periodEnd)
        vlayout.addLayout(hlayout)

        methodLabel = QtWidgets.QLabel("<strong>Calculation</strong>")
        self.methodDropDown = QtWidgets.QComboBox()
        self.methodDropDown.addItems(["Average", "Accumulation", "Minimum", "Maximum"])
        vlayout.addWidget(methodLabel)
        vlayout.addWidget(self.methodDropDown)

        self.summaryLabel = QtWidgets.QLabel()

        self.setLayout(vlayout)

        return
    
    def updateSummaryLabel(self, dummy = None):

        

        return

class predictorsPage(QtWidgets.QWizardPage):
    """
    """

    def __init__(self, modelRunTableEntry = None):

        QtWidgets.QWizard.__init__(self)
        self.setTitle("Predictors")
        self.setSubTitle("Use the form below to tell PyForecast what predictors you want to consider.")

        return

class modelBuilderPage(QtWidgets.QWizardPage):
    """
    """

    def __init__(self, modelRunTableEntry = None):

        QtWidgets.QWizard.__init__(self)
        self.setTitle("Model Building Settings")
        self.setSubTitle("Use the form below to tell PyForecast how you want to generate models.")

        return

class ModelInitializationDialog(QtWidgets.QWizard):
    """
    """

    def __init__(self, parent = None, modelRunTableEntry = None, datasetTable = None):
        """
        """

        QtWidgets.QWizard.__init__(self)
        self.modelRunTableEntry = modelRunTableEntry
        self.datasetTable = datasetTable

        self.setUI()

        self.show()

        return

    def setUI(self):
        """
        """
        # Title
        self.setWindowTitle("Model Generation Settings")
        
        # Pages
        self.addPage(forecastTargetPage(self.modelRunTableEntry))
        self.addPage(predictorsPage(self.modelRunTableEntry))
        self.addPage(modelBuilderPage(self.modelRunTableEntry))

        # Pixmaps
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        #WatermarkPixmap = QtGui.QPixmap("resources/GraphicalResources/splash.png")
        #LogoPixmap = QtGui.QPixmap("resources/GraphicalResources/splash.png")
        #BannerPixmap = QtGui.QPixmap("resources/GraphicalResources/splash.png")
        #BackgroundPixmap = QtGui.QPixmap("resources/GraphicalResources/splash.png")
        #self.setPixmap(QtWidgets.QWizard.WatermarkPixmap, WatermarkPixmap)
        #self.setPixmap(QtWidgets.QWizard.LogoPixmap, LogoPixmap)
        #self.setPixmap(QtWidgets.QWizard.BannerPixmap, BannerPixmap)
        #self.setPixmap(QtWidgets.QWizard.BackgroundPixmap, BackgroundPixmap)


        return


    def printSummary(self):

        summaryText = ""

        return summaryText

if __name__ == '__main__':
    import sys
    import os
    import pandas as pd
    print(os.getcwd())
    app = QtWidgets.QApplication(sys.argv)
    widg = ModelInitializationDialog()

    sys.exit(app.exec_())