@ECHO OFF
ECHO.
ECHO.
ECHO.
ECHO Installing python libraries
ECHO.
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy
ECHO O
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org scipy
ECHO OO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests
ECHO OOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org zeep
ECHO OOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pandas
ECHO OOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sklearn
ECHO OOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org matplotlib
ECHO OOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -Iv PyQt5==5.9
ECHO OOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org datetime
ECHO OOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org PyQt5-tools
ECHO OOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org openpyxl
ECHO OOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org configparser
ECHO OOOOOOOOOOO
ECHO.
ECHO Press any key to exit
PAUSE
EXIT
