"""
Script Name:        main.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      Jan 1, 2019

Description:        NextFlow is a statistical modeling tool useful in predicting season 
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

Disclaimer:         This script, and the overall NextFlow Application have not been
                    reviewed for scientific rigor or accuracy. The resulting forecasts
                    and forecast equations generated from this program are not in any
                    way guarnateed to be reliable or accurate. 

"""

# Import Libraries
import sys
import warnings
warnings.filterwarnings('ignore')
import time
import argparse
import resources.application as application
from datetime import datetime
from PyQt5 import QtGui, QtWidgets, QtCore

if __name__ == '__main__':

    # Print out a welcom message
    print("""
    ===========================================================

    STARTING NextFlow SOFTWARE

    logs and print statements will be printed in this terminal

    ===========================================================

    """)

    # Begin loading the application
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('resources/GraphicalResources/icons/icon.ico'))

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
    sys.exit(app.exec_())