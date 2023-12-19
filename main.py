from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QT_VERSION_STR, QEvent, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from Utilities.JsonHooks import DatetimeParser
from time import time
import traceback
import os
import atexit
import sys
import json
import ctypes



class Logger(QObject):
  """This is a simple logger class that redirects print statements and 
  error messages to the file 'app_log.txt'. It also prints those
  messages to the terminal.
  """

  new_log_message = pyqtSignal(str)
  base_dir = os.path.dirname(__file__)

  def __init__(self):
    """Constructor method
    """

    QObject.__init__(self)

    # Open the log file and redirect stdout to a variable
    self.terminal = sys.stdout
    self.log = open(self.base_dir+'/app_log.txt', 'w', encoding='utf-8')

    # Close the file on application exit
    atexit.register(self.cleanup)
    
    self.write('Starting PyForecast')

  def logger_excepthook(self, excType, excValue, tb, logger=None):
    s = list(traceback.format_tb(sys.last_traceback))
    for ss in s:
      self.write(ss)
    self.write(f"Uncaught exception: {excType}: {excValue} \n \n {tb}")

  def write(self, msg):
    """Writes the message (message redirected from print(...)) to the 
    log file and also prints it to the terminal
    """

    # Write print messages to the log file and the terminal
    if msg:

      # Ensure that the message is printable
      if msg != '' and msg.isprintable():

        # Split up messages longer than seventy characters into multiple lines
        if len(msg) > 80:
          c = 0
          while c < len(msg):
            c += 80
            if c == 80:
              m = f"[ {time():.2f} ] \t{msg:80.80}\t·\n"
            else:
              m = f"                 \t{msg[c-80:c]:80.80}\t·\n"
            self.terminal.write(m)
            self.log.write(m)
            self.new_log_message.emit(m)
        else:
          msg = f"[ {time():.2f} ] \t{msg:80.80}\t·\n"
          self.terminal.write(msg)
          self.log.write(msg)
          self.new_log_message.emit(msg)

  def cleanup(self):
    """Closes the log file and writes an exit statement
    """

    # Exit message and close log file
    self.write("Exiting PyForecast")
    self.log.close()
  
  def flush(self):
    
    # This function is needed for logger to function.
    pass


class PyForecast(QApplication):
  """The main application for PyForecast. Extends the QApplication class
  and contains a number of application wide members including configuration
  settings, stylesheets, version number, current user and filename,
  as well as all the models, and regression methods."""

  new_log_message = pyqtSignal() # Void signal emitted when a new message is added to the log
  base_dir = os.path.dirname(__file__) # path to folder where the PyForecast.EXE file lives

  def __init__(self, *args, **kwargs):
    """Constructor
    
    :arguments
      file (`str`) - filename to open with the application
    """

    # redirect stdout to log
    self.logger = Logger()
    sys.stdout = self.logger
    sys.excepthook = self.logger.logger_excepthook
    
    # System-specific settings. Sets Windows scaling
    # settings for High-DPI displays
    pyversion = sys.version_info
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    QApplication.setHighDpiScaleFactorRoundingPolicy(
      Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Delete all temporary files on exit
    atexit.register(self.delete_temp_files)

    # Initialize the application. Reads the version file,
    # the current user, the stylesheet, and initializes the application
    self.setAttribute(Qt.AA_ShareOpenGLContexts)
    self.log_message = ''
    self.current_user = os.getlogin()
    self.pid = os.getpid()
    QApplication.__init__(self, *args)
    self.installEventFilter(self)
    sys.stdout.new_log_message.connect(self.append_log_message)
    with open(self.base_dir + '/Resources/Stylesheets/application_style.qss', 'r') as stylesheet:
      self.setStyleSheet(self.styleSheet() + (stylesheet.read()))

    # Print out the various versions of installed software
    print(f'Using Python Version       {pyversion.major}.{pyversion.minor}.{pyversion.micro}')
    print(f"Using Qt Version           {QT_VERSION_STR}")
    with open('VERSION.TXT', 'r') as readfile:
      self.PYCAST_VERSION = readfile.read().strip()
      print(f"Using PyForecast Version   {self.PYCAST_VERSION}")
    
    # Windows specific commands to properly identify PyCast and show it's icon in the taskbar
    myappid = f'USBR.PyForecast.{self.PYCAST_VERSION}'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    self.setWindowIcon(QIcon(self.base_dir + '/Resources/Icons/AppIcon.ico'))

    # Read the application configuration and load into the application
    with open(self.base_dir + '/settings.conf', 'r') as config_file:
      self.config = json.load(config_file, object_hook=DatetimeParser)
    atexit.register(self.write_config)

    # Set up the current file name
    self.current_file = self.config['last_dir']+ '/' \
       + self.config['new_filename']
    
    # Initialize the Core Models
    from Models import Datasets, ModelConfigurations, SavedModels, Units
    self.units = Units.Units()
    self.datasets = Datasets.Datasets()
    self.model_configurations = ModelConfigurations.ModelConfigurations()
    self.saved_models = SavedModels.SavedModelList()

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

    # Initialize the Views
    from Views import MainWindow
    self.gui = MainWindow.MainWindow(show=kwargs.get('show', True))

    # Instanitate the View Models
    from ModelView import MainWindowMV, DatasetMV
    from ModelView import DataTabMV, ModelConfigurationMV, SavedModelsMV
    self.MWMV = MainWindowMV.MainWindowModelView()
    self.DMV = DatasetMV.DatasetModelView()
    self.DTMV = DataTabMV.DataModelView()
    self.MTMV = ModelConfigurationMV.ModelConfigurationModelView()
    self.SMMV = SavedModelsMV.SavedModelsModelView()

    # Open the file if there is one
    if "file" in kwargs:
      self.MWMV.OpenFile(None, filename=kwargs['file'])

  def write_config(self):

    # Copy the contents of the application 
    # configuration into the config file
    with open(self.base_dir + '/settings.conf', 'w') as configfile:
      json.dump(self.config, configfile, indent=4, default=str)
  
  def delete_temp_files(self):

    # delete all temporary files from the current directory
    for fn in os.listdir():
      if 'temp_' in fn and '.xlsx' in fn:
        os.remove(fn)

  def append_log_message(self, msg):
    
    # Appends the new log message to the application log-variable and updates
    # The gui log-dialog (if it's open).
    self.log_message += msg
    self.new_log_message.emit()
    

  def eventFilter(self, object, event):

    if isinstance(object, QComboBox) and event.type() == QEvent.Wheel:
      return True
    elif isinstance(object, QDateEdit) and event.type() == QEvent.Wheel:
      return True
    else:
      return QApplication.eventFilter(self, object, event)
  


if __name__ == '__main__':


  # Create the application
  app = PyForecast(sys.argv)

  # TODO: Argparser for runtime options, such as file

  # Run the application
  sys.exit(app.exec_())
