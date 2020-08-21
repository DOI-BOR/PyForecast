@ECHO OFF
ECHO.
ECHO.
ECHO.
ECHO Installing python libraries
ECHO.
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org numpy -U --user
ECHO O
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org scipy -U --user
ECHO OO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org requests -U --user
ECHO OOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org zeep -U --user
ECHO OOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pandas -U --user
ECHO OOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org scikit-learn -U --user
ECHO OOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org matplotlib -U --user
ECHO OOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -Iv PyQt5==5.9.2 --user
ECHO OOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org datetime -U --user
ECHO OOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org openpyxl -U --user
ECHO OOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org configparser -U --user
ECHO OOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org xlrd -U --user
ECHO OOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org staty -U --user
ECHO OOOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyqtgraph -U --user
ECHO OOOOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org geojson -U --user
ECHO OOOOOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fuzzywuzzy -U --user
ECHO OOOOOOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org bitarray -U --user
ECHO OOOOOOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org statsmodels -U --user
ECHO OOOOOOOOOOOOOOOOO
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -Iv pyqtchart==5.9.2 --user
ECHO OOOOOOOOOOOOOOOOOO
ECHO.
ECHO Press any key to exit
PAUSE
EXIT
