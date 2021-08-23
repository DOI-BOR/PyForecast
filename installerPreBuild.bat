@echo off
echo ------------------------------------------------
echo This script contains the required processes that
echo need to be completed before the installer can be
echo built by InnoSetup.
echo.  
echo POC: jrocha@usbr.gov
echo.   
echo ------------------------------------------------

:: Delete the old directory containing the last build
echo Deleting old build directory...
cd dist
rmdir /s /q "main"
cd..
echo.

:: Run pyinstaller to create a new build
echo Running PyInstaller...
pyinstaller main.py
echo.

:: Copy required files 
echo Copying Python modules...
robocopy venv\Lib\site-packages dist\main /E /XC /XN /XO /NFL /XD __pycache__ *-info tests
echo Copying PyForecast resources...
robocopy resources dist\main\resources\ /E /XC /XN /XO /NFL /XD __pycache__
echo.
