import sys
from cx_Freeze import setup, Executable

# exclude unneeded packages. More could be added. Has to be changed for
# other programs.
build_exe_options = {"excludes": ["scipy.spatial.cKDTree"],
                     "includes": ["matplotlib","numpy","scipy","sklearn","requests","zeep","pandas","PyQt5","datetime","configparser"],
                     "include_files": ["Resources"],
                     "optimize": 2,
                     }

setup(
    name = "PyForecast" ,
    version = "1.0" ,
    description = "PyForecast Software Application" ,
    options = {"build_exe": build_exe_options},
    #executables = [Executable("Resources/application.py")]#, base="Win32GUI")]
    executables = [Executable("PyForecast.py", base="Win32GUI")]
)