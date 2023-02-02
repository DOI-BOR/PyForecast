from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QCoreApplication, QUrl
from Views import UnitsEditor, SettingsDialog, AppLogViewer
from Utilities import ExcelExporter, Updater, FileLoaderSaver
import os

# Get the global application
app = QApplication.instance()

class MainWindowModelView:
  """The MainWindowModelView object controls all the 'File Menu' functionality,
  connecting the file menu and it's various dialogs to the application variables
  such as app.config, app.units.
  """

  def __init__(self):
    """Constructor"""

    # Reference to the main window GUI
    self.mw = app.gui
    
    # Connect events from the file-menu
    self.mw.new_option.triggered.connect(self.NewFile)
    self.mw.file_open_option.triggered.connect(self.OpenFile)
    self.mw.file_save_option.triggered.connect(self.SaveFile)
    self.mw.file_save_as_option.triggered.connect(self.SaveFileAs)
    self.mw.export_option.triggered.connect(self.ExportFile)
    self.mw.toggle_font_small.triggered.connect(lambda x: self.ChangeFont('small'))
    self.mw.toggle_font_medium.triggered.connect(lambda x: self.ChangeFont('medium'))
    self.mw.toggle_font_large.triggered.connect(lambda x: self.ChangeFont('large'))
    self.mw.edit_units_option.triggered.connect(self.EditUnits)
    self.mw.edit_settings_option.triggered.connect(self.EditApplicationSettings)
    self.mw.documentation_option.triggered.connect(self.OpenDocs)
    self.mw.check_updates_option.triggered.connect(self.UpdateCheck)
    self.mw.show_log_option.triggered.connect(self.ShowLog)

    # initialize the application font-size from the configuration file
    self.ChangeFont(app.config['application_font_size'])
    
    # Set the current file name in the status bar
    app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')


  def NewFile(self, _):
    """Prompts the user if they want to save the current file, and opens a new 
    file (using the default new file name). Clears all the application models and
    top level widgets.
    """

    ret = QMessageBox.question(app.gui, 'Save changes?', f"You're about to open a new file. \n\nSave changes to:\n{app.current_file}?")
    if ret == QMessageBox.Yes:
      self.SaveFile()
    
    # Clear all the models
    self.clear_models()

    app.current_file = app.config['last_dir']+ '/' + app.config['new_filename']
    app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')

    # Redraw the entire app
    for w in app.topLevelWidgets():
      w.update()
    QCoreApplication.processEvents()

    return

  
  def OpenFile(self, _, filename=None):
    """Opens the filename specified by 'filename', or if 'filename' is none, opens
    the file specified by the user from the QFileDialog.
    """

    # Open a QFIleDialog if the there is no filename specified
    if not filename:
      filename, _ = QFileDialog.getOpenFileName(app.gui, "Open Forecast", app.config['last_dir'], '*.fcst')

    # Ensure that the file is a pyforecast file
    if '.fcst' in str(filename):
      
      # Clear any existing data in the application
      self.clear_models()

      # Open the file and use the file-loader function to read the data into the application
      with open(str(filename), 'rb') as read_file:
        FileLoaderSaver.load_file(read_file)

      # Update the application configuration and current file name
      app.current_file = filename
      app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')
      app.config['last_dir'] = os.path.dirname(app.current_file)
      print(f"Successfully opened the file: {app.current_file}")

    return 


  def SaveFile(self, _=None):
    """Saves the forecast to the forecast file (set in app.current_file)"""

    # If the filename is the 'default' file name from app.config, we should
    # ask the user if they want to specify a file name first.
    if os.path.basename(app.current_file) == app.config['new_filename']:
      if not _:
        self.SaveFileAs(None)
        return

    # Save the file using the file-loader-saver module
    with open(app.current_file, 'wb') as write_file:
      FileLoaderSaver.save_to_file(write_file)

    # Update the application with the file name and update the config.
    app.gui.status_bar.showMessage(f'File [{app.current_file}] saved successfully!', 3000)
    app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')
    app.config['last_dir'] = os.path.dirname(app.current_file)
    print(f"Successfully saved the file: {app.current_file}")

    return


  def SaveFileAs(self, _):
    """ Prompts the user with a QFIleDialog for a filename, then uses the 
    SaveFile function to save the file.
    """

    # Get a file name using the QFileDialog
    filename, _ = QFileDialog.getSaveFileName(app.gui, "Open Forecast", app.config['last_dir'], '*.fcst')

    # Check that filename is valid
    if filename != '':

      # Set the current file name in the app and save the file
      app.current_file = filename
      self.SaveFile(0)

    return


  def clear_models(self):
    """Clears the application models.
    """

    app.datasets.clear_all()
    app.model_configurations.clear_all()
    app.saved_models.clear_all()

    return


  def ExportFile(self, _):
    """Exports the forecast file to an excel spreadsheet using the ExcelExporter Module
    """

    # Create an instance of the ExcelExporter writer
    writer = ExcelExporter.Exporter()

    # Update the status bar
    app.gui.status_bar.showMessage('Exporting to Excel...')
    app.processEvents()

    # Export the file
    fn = writer.export()

    # Update the status bar
    app.gui.status_bar.showMessage('')
    app.processEvents()

    # Prompt the user to see if they want to open the excel file
    ret = QMessageBox.question(app.gui, 'Export successful', f'Successfully exported the file to:\n\n{fn}\n\nOpen the file?')
    if ret == QMessageBox.Yes:
      os.system(f'start EXCEL.EXE "{fn}"')
      app.gui.status_bar.showMessage('Opening excel file...', 3000)
    
    return


  def ChangeFont(self, size):
    """Changes the application wide font size and modifies the configuration file"""

    # Change the configuration file
    app.config['application_font_size'] = size
    
    # Set the application stylesheet based on the selected size
    if size == 'small':
     
      app.setStyleSheet(app.styleSheet()+'QWidget {font-size:9pt; font-family:"Arial"} QWidget#HeaderLabel {font-size:12pt} ')

    elif size == 'medium':

      app.setStyleSheet(app.styleSheet()+'QWidget {font-size:13pt; font-family:"Arial"} QWidget#HeaderLabel {font-size:16pt}')

    elif size == 'large':

      app.setStyleSheet(app.styleSheet()+'QWidget {font-size:15pt; font-family:"Arial"} QWidget#HeaderLabel {font-size:18pt}')

    return


  def EditUnits(self, _):
    """Opens the Unit Editor Dialog """
    
    u = UnitsEditor.UnitsEditor()

    return


  def EditApplicationSettings(self, _):
    """Opens the Application Settings Dialog"""

    s = SettingsDialog.SettingsDialog()
    s.exec()

    return


  def ShowLog(self, _):
    """Opens the log viewer dialog"""

    self.log_view = AppLogViewer.LogViewer()
    self.log_view.show()

    return


  def OpenDocs(self, _):
    """Opens the Github documentation page for V5"""

    QDesktopServices.openUrl(QUrl('https://github.com/usbr/PyForecast/tree/PyForecastV5#pyforecast-version-5-'))
    
    return


  def UpdateCheck(self, _):
    """Opens the update check dialog box"""
    
    self.updater = Updater.UpdaterDialog()
    self.updater.exec()

    return