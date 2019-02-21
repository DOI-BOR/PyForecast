import sys
from cx_Freeze import setup, Executable

setup(
    name = "PyForecast" ,
    version = "1.0" ,
    description = "PyForecast Software Application" ,
    options = {"build_exe": {
        #'packages': ["atomicwrites","attr","backports","dateutil","et_xmlfile","jinja2","lxml","markupsafe","matplotlib","more_itertools","numpy","openpyxl","pandas","pkg_resources","pluggy","py","PyQt5","pytz","scipy","setuptools","sqlalchemy","xlrd"],
        'include_files': ['Resources'],
        #'include_msvcr': True
    }},
    executables = [Executable("Resources/application.py", base="Win32GUI")]
)