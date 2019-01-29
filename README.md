[![Build status](https://ci.appveyor.com/api/projects/status/n5jktmnm4jqr37nm?svg=true)](https://ci.appveyor.com/project/usbr/pyforecast)

# PyForecast Forecasting Software
PyForecast is a statistical modeling tool useful in predicting season inflows and streamflows. The tool collects meterological and hydrologic datasets, analyzes hundreds to thousands of predictor subsets, and returns well-performing statistical regressions between predictors and streamflows. 

## Requirements
* Python 3.X with the following libraries installed
    * numpy
    * scipy
    * pandas
    * requests
    * zeep
    * sklearn
    * matplotlib
    * PyQt5 (MUST BE version 5.9)
    * datetime
    * openpyxl
    * xlrd

These packages can be installed automatically to your default python distribution by running the 'install_dependencies.bat' script. 

## Use
Run the software by running the 'run_PyForecast.bat' batch script. This will open the software along with a console window that will log any error messages. 
