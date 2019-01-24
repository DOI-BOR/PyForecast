"""
Script Name:        DocumentationGUI.py
Script Author:      Kevin Foley
Description:        Provides the GUI interface for viewing the 
                    documnetation web page.
"""


# Import libraries
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore, QtGui
import os

class DocumentationWindow(QtWidgets.QDialog):
    """
    This Dialog widget consists of a QWebEngineView. It loads the 'UserManual.html' file into 
    the webengineview when initialized.
    """

    def __init__(self):
        super(DocumentationWindow, self).__init__()

        mainLayout = QtWidgets.QVBoxLayout()
        self.mainWebPage = QtWebEngineWidgets.QWebEngineView(self)
        self.mainWebPage.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        #url = QtCore.QUrl.fromLocalFile(os.path.abspath('Resources/Documentation/UserManual.html'))
        self.page = WebBrowserPage(self)
        self.mainWebPage.setPage(self.page)
        #mainWebPage.load(url)
        mainLayout.addWidget(self.mainWebPage)

        self.setLayout(mainLayout)
        self.setWindowTitle("PyForecast Documentation")
        self.show()

# Define a custom Web Map widget using MapBox
class WebBrowserPage(QtWebEngineWidgets.QWebEnginePage):

    
    def __init__(self, parent=None):

        # Initialize the web map
        QtWebEngineWidgets.QWebEnginePage.__init__(self)
        print(os.getcwd())
        url = QtCore.QUrl.fromLocalFile(os.path.abspath('Resources/Documentation/UserManual.html'))
        self.load(url)

    # Override the 'acceptNavigationRequest' function to open href links in another browser
    def acceptNavigationRequest(self, url,  _type, isMainFrame):

        # Screen nvaigation requests for href links
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            print(url)
            if '.md' in str(url):
                return True
            QtGui.QDesktopServices.openUrl(url)    
            return False
        
        else: 
            return True


class VersionWindow(QtWidgets.QDialog):
    """
    This dialog widget displays the version information of the forecasting software 
    in a form layout. When initialized the widget reads the version information located
    'versionInfo.txt' in the documentation directory.
    """

    def __init__(self):
        super(VersionWindow, self).__init__()

        self.setStyleSheet("background-color: white; color: black;")

        mainLayout = QtWidgets.QGridLayout()
        rowCounter = 0

        # Read the version file
        with open("Resources/Documentation/versionInfo.txt", "r") as readFile:
            versionText = readFile.readlines()

        # Iterate through the version file lines and add a new label for each line
        for line in versionText:
            
            line = line.replace("\n", "")
            line = line.strip(' ')
            if line == '':
                continue
            if line[0] == '#':
                continue
            
            line = line.split(":")
            label = QtWidgets.QLabel(line[0].strip(' '))
            text = QtWidgets.QLineEdit()
            text.setReadOnly(True)
            text.setText(line[1].strip(' '))
            mainLayout.addWidget(label, rowCounter, 0)
            mainLayout.addWidget(text, rowCounter, 1)
            rowCounter += 1
        
        installLocationLabel = QtWidgets.QLabel("Installation Location")
        installLocation = QtWidgets.QLineEdit()
        installLocation.setMinimumWidth(200)
        installLocation.setReadOnly(True)
        installLocation.setText(os.getcwd())

        mainLayout.addWidget(installLocationLabel, rowCounter, 0)
        mainLayout.addWidget(installLocation, rowCounter, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("PyForecast Version")
        self.show()


        