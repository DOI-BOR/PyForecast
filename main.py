import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, qVersion, Signal, QObject
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from PySide6.QtWidgets import QApplication

from Utilities.JsonHooks import DatetimeParser


class Logger(QObject):
    """This is a simple logger class that redirects print statements and
    error messages to the file 'app_log.txt'. It also prints those
    messages to the terminal.
    """

    new_log_message = Signal(str)
    base_dir = Path(__file__).parent.absolute()

    def __init__(self, parent=None):
        """Constructor method """
        super().__init__(parent)

        # Open the log file and redirect stdout to a variable
        self.terminal = sys.stdout
        self.log = open(self.base_dir.joinpath('app_log.txt'), 'w', encoding='utf-8')

        self.write('Starting PyForecast')

    def logger_excepthook(self, etype, evalue, tb):
        s = list(traceback.format_tb(sys.last_traceback))
        for ss in s:
            self.write(ss)
        self.write(f"Uncaught exception: {etype}: {evalue} \n \n {tb}")

    def write(self, msg):
        """Writes the message (message redirected from print(...)) to the
        log file and also prints it to the terminal
        """

        # Write printable messages to the terminal
        if msg.isprintable():
            # Split up messages longer than 80 characters into multiple lines
            if len(msg) > 80:
                c = 0
                while c < len(msg):
                    c += 80
                    if c == 80:
                        m = f"[ {time.ctime()} ]{''.ljust(4)}{msg:<80.80}·\n"
                    else:
                        m = f"{''.rjust(32)}{msg[c - 80:c]:<80}·\n"
                    self.terminal.write(m)
                    self.log.write(m)
                    self.new_log_message.emit(m)
            else:
                msg = f"[ {time.ctime()} ]{''.ljust(4)}{msg:<80}·\n"
                self.terminal.write(msg)
                self.log.write(msg)
                self.new_log_message.emit(msg)

    def cleanup(self):
        # Close the log file and terminal
        self.terminal.close()
        self.log.close()

    def flush(self):
        # This function is needed for logger to function.
        pass


class PyForecast(QApplication):
    """The main application for PyForecast. Extends the QApplication class
    and contains a number of application wide members including configuration
    settings, stylesheets, version number, current user and filename,
    as well as all the models, and regression methods."""

    # Void signal emitted when a new message is added to the log
    new_log_message = Signal()

    # path to folder where the PyForecast.exe file lives
    base_dir = Path(__file__).parent.absolute()

    # icon used in the application
    icon = ''

    def __init__(self, *args, **kwargs):
        """Constructor

        :arguments
          file (`str`) - filename to open with the application
        """

        # Initialize the parent QApplication
        super().__init__(*args, **kwargs)

        # redirect stdout to log
        self.logger = Logger()
        sys.stdout = self.logger
        sys.excepthook = self.logger.logger_excepthook

        # Initialize the application. Reads the version file,
        # the current user, the stylesheet, and initializes the application
        self.log_message = ''
        self.current_user = os.getlogin()
        self.pid = os.getpid()
        sys.stdout.new_log_message.connect(self.append_log_message)
        stylesheet = self.base_dir.joinpath(
            'Resources', 'Stylesheets', 'application_style.qss')
        with open(stylesheet, 'r') as s:
            self.setStyleSheet(self.styleSheet() + (s.read()))

        # Print out the various versions of installed software
        pyversion = sys.version_info
        self.PYTHON_VERSION = f'{pyversion.major}.{pyversion.minor}.{pyversion.micro}'
        with open('version.txt', 'r') as readfile:
            self.PYCAST_VERSION = readfile.read().strip()
        print(f'{'Using Python Version'.ljust(50)}{self.PYTHON_VERSION:<10}')
        print(f'{'Using PySide Qt Version'.ljust(50)}{qVersion():<10}')
        print(f'{'Using PyForecast Version'.ljust(50)}{self.PYCAST_VERSION:<10}')

        # Setup Application information
        self.setApplicationName(f'PyForecast v{self.PYCAST_VERSION}')
        self.setApplicationVersion(self.PYCAST_VERSION)

        # Set window icon in the taskbar and any other windows
        self.icon= QIcon(
            str(self.base_dir.joinpath('Resources', 'Icons', 'AppIcon.ico')))
        self.setWindowIcon(self.icon)

        # Read the application configuration and load into the application
        with open(self.base_dir.joinpath('settings.conf'), 'r') as settings:
            settings = json.load(settings, object_hook=DatetimeParser)

        # Set up the current settings and file name
        self.settings = settings
        self.current_file = Path().joinpath(
            self.settings['last_dir'],
            self.settings['new_filename']
        )

        # Initialize the Core Models
        from Models import Datasets, ModelConfigurations, SavedModels, Units
        self.units = Units.Units(self)
        self.datasets = Datasets.Datasets(self)
        self.model_configurations = ModelConfigurations.ModelConfigurations(self)
        self.saved_models = SavedModels.SavedModelList(self)

        # Instantiate the Dataloaders
        from Resources import Dataloaders
        self.dataloaders = Dataloaders.DATALOADERS

        # Instantiate the aggregation methods
        from Resources import AggMethods
        self.agg_methods = AggMethods.METHODS

        # Instantiate the preprocessing methods
        from Resources import PreprocessingMethods
        self.preprocessing_methods = PreprocessingMethods.METHODS

        # instantiate the cross validation methods
        from Resources.CrossValidation import CROSS_VALIDATION
        self.cross_validation = CROSS_VALIDATION

        # Instantiate the feature selection methods
        from Resources.FeatureSelection import FEATURE_SEL
        self.feature_selection = FEATURE_SEL

        # Instantiate the model scoring methods
        from Resources.ScoringMetrics import SCORERS
        self.scorers = SCORERS

        # Istantiate the regressors
        from Resources.RegressionModels import REGRESSORS
        self.regressors = REGRESSORS

        # Initialize the MainWindow
        from Views import MainWindow
        self.gui = MainWindow.MainWindow()

        # Instanitate the View Models
        from ModelView import (MainWindowMV, DatasetMV, DataTabMV,
                               ModelConfigurationMV, SavedModelsMV)
        self.MWMV = MainWindowMV.MainWindowModelView()
        self.DMV = DatasetMV.DatasetModelView()
        self.DTMV = DataTabMV.DataModelView()
        self.MTMV = ModelConfigurationMV.ModelConfigurationModelView()
        self.SMMV = SavedModelsMV.SavedModelsModelView()

        # Show the MainWindow
        user_screen_size = QGuiApplication.primaryScreen().size()
        width = min(self.settings['window_width'], user_screen_size.width())
        height = min(self.settings['window_height'], user_screen_size.height())

        rec = self.gui.size()
        if (width >= 0.95 * rec.width()) or (height >= 0.95 * rec.height()):
            self.gui.showMaximized()
        else:
            self.gui.resize(width, height)
            self.gui.show()

        # Open the file if there is one
        if kwargs['file']:
            self.MWMV.OpenFile(None, filename=kwargs['file'])

    def write_settings(self):
        # Copy the contents of the application configuration into the settings file
        with open(self.base_dir.joinpath('settings.conf'), 'w') as settings:
            json.dump(self.settings, settings, indent=4, default=str)

    @staticmethod
    def delete_temp_files():

        # delete all temporary files from the current directory
        for fn in os.listdir():
            if 'temp_' in fn and '.xlsx' in fn:
                os.remove(fn)

    def append_log_message(self, msg):

        # Appends the new log message to the application log-variable and updates
        # The gui log-dialog (if it's open).
        self.log_message += msg
        self.new_log_message.emit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'PyForecast',
        description="PyForecast is a statistical modeling tool useful in predicting "
                    "monthly and seasonal inflows and streamflows."
    )
    parser.add_argument('-f', '--file',
                        help='Provide a file to immediately be opened by PyForecast')
    params = parser.parse_args()

    # Create the application
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Software)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = PyForecast(sys.argv, file=params.file)

    # Run the application
    sys.exit(app.exec())
