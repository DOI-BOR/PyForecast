from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QDesktopServices, QColor
from PyQt5.QtCore import QCoreApplication, QUrl, Qt
from Views import UnitsEditor, SettingsDialog, AppLogViewer
from Utilities import ExcelExporter, Updater, FileLoaderSaver
import pickle
import os
from pyqtspinner import WaitingSpinner
import urllib.request

# Get the global application
app = QApplication.instance()

class MainWindowModelView:

  def __init__(self):

    self.mw = app.gui
    
    # Connect events 
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

    self.ChangeFont(app.config['application_font_size'])
    
    app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')


  def NewFile(self, _):

    ret = QMessageBox.question(app.gui, 'Save changes?', f"You're about to open a new file. \n\nSave changes to:\n{app.current_file}?")
    if ret == QMessageBox.Yes:
      self.SaveFile()
    
    # Clear all the models
    app.datasets.clear()

    app.current_file = app.config['last_dir']+ '/' + app.config['new_filename']
    app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')

    # Redraw the entire app
    for w in app.topLevelWidgets():
      w.update()
    QCoreApplication.processEvents()


    return
  
  def OpenFile(self, _, filename=None):

    if not filename:
      filename, _ = QFileDialog.getOpenFileName(app.gui, "Open Forecast", app.config['last_dir'], '*.fcst')

    if '.fcst' in str(filename):
      
      self.clear_models()

      with open(str(filename), 'rb') as read_file:
        FileLoaderSaver.load_file(read_file)
        #version = pickle.load(read_file)
        #app.datasets.load_from_file(read_file)
        #app.model_configurations.load_from_file(read_file)
        #app.saved_models.load_from_file(read_file)

      app.current_file = filename
      app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')
      app.config['last_dir'] = os.path.dirname(app.current_file)
      print(f"Successfully opened the file: {app.current_file}")

    return 

  def SaveFile(self, _=None):

    if os.path.basename(app.current_file) == app.config['new_filename']:
      if not _:
        self.SaveFileAs(None)
        return

    with open(app.current_file, 'wb') as write_file:
      FileLoaderSaver.save_to_file(write_file)
      # Save the version number
      #pickle.dump(app.PYCAST_VERSION, write_file, 4)
      #pickle.dump(app.datasets.datasets, write_file, 4)
      #app.model_configurations.save_to_file(write_file)
      #app.saved_models.save_to_file(write_file)

    app.gui.status_bar.showMessage(f'File [{app.current_file}] saved successfully!', 3000)
    app.gui.current_file_widg.setText(f'<strong>File</strong>: {app.current_file}   ')
    app.config['last_dir'] = os.path.dirname(app.current_file)
    print(f"Successfully saved the file: {app.current_file}")
    return

  def SaveFileAs(self, _):

    filename, _ = QFileDialog.getSaveFileName(app.gui, "Open Forecast", app.config['last_dir'], '*.fcst')

    if filename != '':

      app.current_file = filename
      self.SaveFile(0)

    return

  def clear_models(self):
    app.datasets.clear_all()
    app.model_configurations.clear_all()
    app.saved_models.clear_all()

  def ExportFile(self, _):

    writer = ExcelExporter.Exporter()
    app.gui.status_bar.showMessage('Exporting to Excel...')
    app.processEvents()
    fn = writer.export()
    app.gui.status_bar.showMessage('')
    app.processEvents()
    ret = QMessageBox.question(app.gui, 'Export successful', f'Successfully exported the file to:\n\n{fn}\n\nOpen the file?')
    if ret == QMessageBox.Yes:
      os.system(f'start EXCEL.EXE "{fn}"')
      app.gui.status_bar.showMessage('Opening excel file...', 3000)
    return

  def ChangeFont(self, size):
    app.config['application_font_size'] = size
    if size == 'small':
      #font = QFont('Arial', 9)
      #app.setFont(font)
      app.setStyleSheet(app.styleSheet()+'QWidget {font-size:9pt; font-family:"Arial"} QWidget#HeaderLabel {font-size:12pt} ')
    elif size == 'medium':
      #font = QFont('Arial', 13)
      #elf.app.setFont(font)
      app.setStyleSheet(app.styleSheet()+'QWidget {font-size:13pt; font-family:"Arial"} QWidget#HeaderLabel {font-size:16pt}')
    else:
      #font = QFont('Arial', 15)
      #app.setFont(font)
      app.setStyleSheet(app.styleSheet()+'QWidget {font-size:15pt; font-family:"Arial"} QWidget#HeaderLabel {font-size:18pt}')

    return

  def EditUnits(self, _):
    u = UnitsEditor.UnitsEditor()
    return

  def EditApplicationSettings(self, _):
    s = SettingsDialog.SettingsDialog()
    s.exec()

  def ShowLog(self, _):
    self.log_view = AppLogViewer.LogViewer()
    self.log_view.show()

  def OpenDocs(self, _):

    QDesktopServices.openUrl(QUrl('https://github.com/usbr/PyForecast/wiki'))
    
    return

  def UpdateCheck(self, _):
    
    self.updater = Updater.UpdaterDialog()
    self.updater.exec()