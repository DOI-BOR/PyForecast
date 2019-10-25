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
rmdir /s /q "pyforecast"
cd..
echo.

:: Run pyinstaller to create a new build
echo Running PyInstaller...
pyinstaller pyforecast.py
echo.

:: Copy required files 
echo Copying Python modules...
xcopy /s /y env\Lib\site-packages dist\pyforecast
echo Copying PyForecast resources...
xcopy /s /y Resources dist\pyforecast\Resources\
echo.
