from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets, QtGui
import sys


# Define a custom Web Map widget using MapBox
class WebMap(QtWebEngineWidgets.QWebEnginePage):
    # Create a signal to emit console messages from Javascript
    java_msg_signal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):

        # Initialize the web map with HUC8 boundaries and water features
        QtWebEngineWidgets.QWebEnginePage.__init__(self)

        
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            print('opening url')
            QtGui.QDesktopServices.openUrl(url)    
            return False
        else: 
            return True

    # Override the 'javaScriptConsoleMessage' function to send console messages to a signal/slot
    def javaScriptConsoleMessage(self, lvl, msg, line, source):

        if lvl != 0:
            return

        # Split the recieved message by commas into a list and emit it through to the reciever.
        msg_list = msg.split('|')
        self.java_msg_signal.emit(msg_list)

class Window(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.initUI(self)

    def initUI(self, Window):

        self.w = QtWidgets.QWidget()
        self.w.box = QtWidgets.QHBoxLayout()
        self.webview = QtWebEngineWidgets.QWebEngineView()
        self.webview.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webpage = WebMap()
        self.webpage.java_msg_signal.connect(self.onNewData)
        url = QtCore.QUrl.fromLocalFile(r'C:\Users\KFoley\Documents\testing\11-15-17_fcstTool\Release040118\Resources\WebResources\WebMap.html')
        self.webview.setPage(self.webpage)
        self.webview.load(url)
        self.w.box.addWidget(self.webview)
        self.w.setLayout(self.w.box)
        self.setCentralWidget(self.w)

        self.show()
    
    def onNewData(self,data):
        print(data)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())