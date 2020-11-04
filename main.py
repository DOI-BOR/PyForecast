"""
Script Name:        main.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      Jan 1, 2019

Description:        PyForecast is a statistical modeling tool useful in predicting season 
                    inflows and streamflows. The tool collects meterological and hydrologic 
                    datasets, analyzes hundreds to thousands of predictor subsets, and returns 
                    well-performing statistical regressions between predictors and streamflows.

                    Data is collected from web services located at NOAA, RCC-ACIS, Reclamation, 
                    and USGS servers, and is stored locally on the user’s machine. Data can be 
                    updated with current values at any time, allowing the user to make current 
                    water-year forecasts using equations developed with the program.

                    After potential predictor datasets are downloaded and manipulated, the tool 
                    allows the user to develop statistically significant regression equations 
                    using multiple regression, principal components regression, and z-score 
                    regression. Equations are developed using a combination of paralleled 
                    sequential forward selection and cross validation.

                    This script is merely the entry point for the application. See
                    'resources.application.py' for the main processing and GUI functionality.

Disclaimer:         This script, and the overall PyForecast Application have not been
                    reviewed for scientific rigor or accuracy. The resulting forecasts
                    and forecast equations generated from this program are not in any
                    way guarnateed to be reliable or accurate. 

"""

# Import Libraries
import sys
import ctypes
import os
import warnings
warnings.filterwarnings('ignore')
import time
import argparse
from datetime import datetime
import traceback
from PyQt5 import QtGui, QtWidgets, QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QMessageBox


# Custom application style to make the tooltip behavior a bit more tolerable.
class PyForecastProxyStyle(QtWidgets.QProxyStyle):

    def __init__(self):
        QtWidgets.QProxyStyle.__init__(self)
    
    def styleHint(self, hint, option, widget, returnData):
        if hint == QtWidgets.QStyle.SH_ToolTip_WakeUpDelay:
            return 1400
        elif hint == QtWidgets.QStyle.SH_ToolTip_FallAsleepDelay:
            return 10
        else:
            return self.baseStyle().styleHint(hint, option, widget, returnData)

# Custom class to send all stdout and stderr to a log file instead of the console
class Logger(object):
    def __init__(self, filename = 'application_log.txt'):
        self.log = open(filename, 'w')
    def write(self, message):
        self.log.write(message)
    def flush(self):
        self.log.flush()


class ErrorApp:
    def raise_error(self):
        assert False


def showMessageBox(boxTitle, mainText, subText = None, detailText = None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(boxTitle)
    msg.setText(mainText)
    if subText is not None:
        msg.setInformativeText(subText)
    if detailText is not None:
        msg.setDetailedText(detailText)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    showMessageBox("FATAL ERROR",
                   "PyForecast has encountered a fatal error and needs to close. ",
                   "You may report this error to the developers with the information shown below.",
                   tb)
    print("-- ERROR --")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


if __name__ == '__main__':

    # Redirect all console and error messages to log file
    #sys.stdout = Logger()
    #sys.stderr = sys.stdout

    # Print out a welcome message
    print("""
    ===========================================================

    STARTING PyForecast SOFTWARE

    logs and print statements will be printed in this terminal

    ===========================================================

    """)

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # Query DPI Awareness (Windows 10 and 8)
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))

    # Set DPI Awareness  (Windows 10 and 8)
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    # the argument is the awareness level, which can be 0, 1 or 2:
    # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)

    # Set DPI Awareness  (Windows 7 and Vista)
    success = ctypes.windll.user32.SetProcessDPIAware()
    # behaviour on later OSes is undefined, although when I run it on my Windows 10 machine, it seems to work with effects identical to SetProcessDpiAwareness(1)


    # Begin loading the application
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('resources/GraphicalResources/icons/icon.ico'))
    app.style_ = PyForecastProxyStyle()
    app.setStyle(app.style_)
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)

    import resources.application as application

    # Parse arguemnts
    parser = argparse.ArgumentParser()
    parser.add_argument('--splash','-s',help='Open program with splash screen',type=str, default='True')
    
    args = parser.parse_args()

    no_splash = args.splash

    # Start up a splash screen while the application loads. (If 'no-splash' isn't specified)
    if no_splash == "True":
        splash_pic = QtGui.QPixmap('resources/GraphicalResources/splash.png')
        splash = QtWidgets.QSplashScreen(splash_pic, QtCore.Qt.WindowStaysOnTopHint)
        splashFont = QtGui.QFont()
        splashFont.setPixelSize(14)
        splash.setFont(splashFont)
        splash.show()
        time.sleep(1)

    # Open the loaded application and close the splash screen
    mw = application.mainWindow()
    if no_splash == 'True':
        splash.finish(mw)

    RUNFROMSOURCE = True
    if (RUNFROMSOURCE):
        sys.exit(app.exec_())
    else:
        sys.excepthook = excepthook
        e = ErrorApp()
        e.app = app
        ret = e.app.exec_()
        sys.exit(ret)

    #sys.exit(app.exec_())