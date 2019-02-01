@ECHO OFF
ECHO.
ECHO.
ECHO.
ECHO Installing python libraries
ECHO.
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org numpy -U --user
ECHO O
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org scipy -U --user
ECHO OO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests -U --user
ECHO OOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org zeep -U --user
ECHO OOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pandas -U --user
ECHO OOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sklearn -U --user
ECHO OOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org matplotlib -U --user
ECHO OOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -Iv PyQt5==5.9.2 --user
ECHO OOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org datetime -U --user
ECHO OOOOOOOOO

ECHO OOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org openpyxl -U --user
ECHO OOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org configparser -U --user
ECHO OOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org xlrd -U --user
ECHO OOOOOOOOOOOO
ECHO.
ECHO Press any key to exit
PAUSE
EXIT
