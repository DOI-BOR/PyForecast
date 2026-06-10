import argparse
import os
import sys
import logging
import ctypes
from pathlib import Path

from PySide6.QtCore import (qVersion, Signal, QObject, QFile, QTextStream,
                            QJsonDocument, Slot, Qt, QThreadPool)
from PySide6.QtGui import QIcon, QGuiApplication, QPixmap
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from PySide6.QtWidgets import QApplication

from Resources import resources
from Utilities.JsonHooks import DatetimeParser
from Utilities.LineWrappingFormatter import LineWrappingFormatter


class LogSignaler(QObject):
    """Emits log records safely across threads"""
    new_log_message = Signal(str)

class QSignalingHandler(logging.Handler):
    """Custom Python logging handler that bridges events to a QObject signal."""
    def __init__(self):
        super().__init__()
        self.signaler = LogSignaler()

    def emit(self, record):
        # Format the log record into a string
        msg = self.format(record)

        # Emit the message through the QObject signal
        self.signaler.new_log_message.emit(msg)


class PyForecast(QApplication):
    """The main application for PyForecast. Extends the QApplication class
    and contains a number of application wide members including configuration
    settings, stylesheets, version number, current user and filename."""

    # Path to folder where the PyForecast.exe file lives from PyInstaller or
    # the current Python code start location where main.py is
    base_dir = (
        Path(sys._MEIPASS)
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
        else Path(__file__).parent.absolute()
    )

    # icon used in the application
    icon = ''

    def __init__(self, *args, **kwargs):

        # Initialize the parent QApplication
        super().__init__(*args, **kwargs)

        # Manager for QThreads to run processes outside the main gui thread
        self.threadpool = QThreadPool()

        # Init Resources/resources.py
        resources.qInitResources()

        # Setup logging
        self.setup_logger()
        logging.info('Starting PyForecast')

        # Gets the current user
        self.current_user = os.getlogin()

        # Print out the various versions of installed software
        pyversion = sys.version_info
        self.PYTHON_VERSION = f'{pyversion.major}.{pyversion.minor}.{pyversion.micro}'
        file = QFile(':/version.txt')
        if file.open(QFile.OpenModeFlag.Text.ReadOnly):
            stream = QTextStream(file)
            self.PYCAST_VERSION = stream.readLine()
            file.close()
        logging.info(f'Using Python Version ... {self.PYTHON_VERSION}')
        logging.info(f'Using PySide Qt Version ... {qVersion()}')
        logging.info(f'Using PyForecast Version ... {self.PYCAST_VERSION}')

        # Setup Application information
        self.setApplicationName(f'PyForecast v{self.PYCAST_VERSION}')
        self.setApplicationVersion(self.PYCAST_VERSION)

        # Windows specific commands to properly identify PyForecast and
        # show its icon in the taskbar
        myappid = f'Reclamation.PyForecast.{self.PYCAST_VERSION}'
        if os.name == 'nt':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set application_style and window icon
        file = QFile(':/Stylesheets/application_style.qss')
        if file.open(QFile.OpenModeFlag.Text.ReadOnly):
            stream = QTextStream(file)
            self.setStyleSheet(self.styleSheet() + (stream.readAll()))
            file.close()
        self.icon = QIcon(QPixmap(':/Icons/AppIcon.ico'))
        self.setWindowIcon(self.icon)

        # Read the application configuration and load into the application
        file = QFile(':/settings.conf')
        if file.open(QFile.OpenModeFlag.Text.ReadOnly):
            self.settings = DatetimeParser(
                QJsonDocument.fromJson(file.readAll()).toVariant()
            )
            file.close()

        # Set up the current file name
        if self.settings is not None:
            self.current_file = Path().joinpath(
                self.settings['last_dir'],
                self.settings['new_filename']
            )

    def write_settings(self):
        # Copy the contents of the application configuration into the settings file
        file = QFile(':/settings.conf')
        if file.open(QFile.OpenModeFlag.Text.WriteOnly):
            fmt = QJsonDocument.JsonFormat.Indented
            file.write(QJsonDocument(self.settings).toJson(format=fmt))
            file.close()

    @staticmethod
    def delete_temp_files():

        # delete all temporary files from the current directory
        for fn in os.listdir():
            if 'temp_' in fn and '.xlsx' in fn:
                os.remove(fn)

    @Slot(str)
    def append_log_message(self, msg):

        # Appends the new log message to the application log-variable
        self.log_message += f'{msg}\n'

    def setup_logger(self):
        # String to load in AppLogViewer
        self.log_message = ''

        # Instantiate our signaling handler
        self.log_handler = QSignalingHandler()

        # Format log representation
        formatter = LineWrappingFormatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            "%I:%M:%S %p",
            width=120
        )
        self.log_handler.setFormatter(formatter)

        # Connect the QObject signal to the UI updater slot
        self.log_handler.signaler.new_log_message.connect(self.append_log_message)

        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(self.log_handler)

    def load_ui(self, **kwargs):
        '''
        :arguments
          file (`str`) - filename to open with the application
        '''

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

        # Bring gui to foreground, request OS focus
        self.gui.setWindowState(
            self.gui.windowState()
            & ~Qt.WindowState.WindowMinimized
            | Qt.WindowState.WindowActive
        )
        self.gui.raise_()
        self.gui.activateWindow()

        # Open the file if there is one
        if kwargs['file']:
            self.MWMV.OpenFile(None, filename=kwargs['file'])


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
    QApplication.setStyle('fusion')
    app = PyForecast(sys.argv)
    app.load_ui(file=params.file)

    # If app is running as a compiled bundle, close splash screen
    if getattr(sys, 'frozen', False):
        import pyi_splash
        pyi_splash.close()

    # Run the application
    sys.exit(app.exec())
