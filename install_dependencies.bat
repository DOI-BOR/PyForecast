@ECHO OFF
ECHO.
ECHO.
ECHO.
ECHO Installing python libraries
ECHO.
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy -U
ECHO O
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org scipy -U
ECHO OO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests -U
ECHO OOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org zeep -U
ECHO OOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pandas -U
ECHO OOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sklearn -U
ECHO OOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org matplotlib -U
ECHO OOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -Iv PyQt5==5.9
ECHO OOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org datetime -U
ECHO OOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org PyQt5-tools -U
ECHO OOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org openpyxl -U
ECHO OOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org configparser -U
ECHO OOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org xlrd -U
ECHO OOOOOOOOOOOO
ECHO.
ECHO Press any key to exit
PAUSE
EXIT
