"""
Script Name:        PyForecast.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      Apr 2, 2018

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
                    'Resources.application.py' for the main processing and GUI functionality.

Disclaimer:         This script, and the overall PyForecast Application have not been
                    reviewed for scientific rigor or accuracy. The resulting forecasts
                    and forecast equations generated from this program are not in any
                    way guarnateed to be reliable or accurate. 

"""

if __name__ == '__main__':

    # Import libraries and the application
    import sys
    import time
    from PyQt5 import QtGui, QtWidgets, QtCore
    import Resources.application as application
    import argparse
    from datetime import datetime

    # Begin loading the application
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('Resources/Fonts_Icons_Images/icon.ico'))

    # Parse arguemnts
    parser = argparse.ArgumentParser()
    parser.add_argument('--splash','-s',help='Open program with splash screen',type=str, default='True')
    parser.add_argument('--customdate', '-c', help='Trick PyForecast into thinking the current date is the user-defined date.', type=str, default=datetime.strftime(datetime.now(), '%Y-%m-%d'))
    
    args = parser.parse_args()

    no_splash = args.splash
    customdate = args.customdate

    # Start up a splash screen while the application loads. (If 'no-splash' isn't specified)
    if no_splash == "True":
        splash_pic = QtGui.QPixmap('Resources/Fonts_Icons_Images/splash.png')
        splash = QtWidgets.QSplashScreen(splash_pic, QtCore.Qt.WindowStaysOnTopHint)
        splashFont = QtGui.QFont()
        splashFont.setPixelSize(14)
        splash.setFont(splashFont)
        splash.show()
        splash.showMessage("Loading resources...", QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom, QtCore.Qt.black)
        time.sleep(1)

    # Open the loaded application and close the splash screen
    mw = application.mainWindow(customdate)
    if no_splash == 'True':
        splash.finish(mw)
    sys.exit(app.exec_())