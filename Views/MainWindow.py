from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from . import DatasetsTab, DataTab, ModelingTab, SavedModelsTab

app = QApplication.instance()

class MainWindow(QMainWindow):

  def __init__(self):

    QMainWindow.__init__(self)

    # Main window properties
    self.setWindowTitle('PyForecast')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    # Initialize the Views
    self.DatasetsTab = DatasetsTab.DatasetsTab()
    self.DataTab = DataTab.DataTab()
    self.ModelingTab = ModelingTab.ModelingTab()
    self.SavedModelsTab = SavedModelsTab.SavedModelsTab()

    # Create the Tab Widget
    tab_widget = QTabWidget(self)
    tab_widget.addTab(self.DatasetsTab, 'Datasets')
    tab_widget.addTab(self.DataTab, 'Data')
    tab_widget.addTab(self.ModelingTab, 'Model Configurations')
    tab_widget.addTab(self.SavedModelsTab, 'Saved Forecasts')

    # Set up the status bar
    self.status_bar = self.statusBar()
    self.current_file_widg = QLabel('')
    self.current_file_widg.setTextFormat(Qt.RichText)
    self.status_bar.insertPermanentWidget(0, self.current_file_widg)
    self.status_bar.setSizeGripEnabled(False)
    
    # Set up the menu bar
    menu_bar = self.menuBar()
    
    file_menu = QMenu('File', self)

    self.new_option = QAction("New forecast (Ctrl-N)", self)
    self.new_option.setShortcut(QKeySequence("Ctrl+N"))
    self.new_option.setStatusTip('Create a new forecast from scratch')
    file_menu.addAction(self.new_option)

    self.file_open_option = QAction('Open file (Ctrl-O)', self)
    self.file_open_option.setShortcut(QKeySequence("Ctrl+O"))
    self.file_open_option.setStatusTip('Select and open a forecast file')
    file_menu.addAction(self.file_open_option)

    self.file_save_option = QAction('Save (Ctrl-S)', self)
    self.file_save_option.setShortcut(QKeySequence("Ctrl+S"))
    self.file_save_option.setStatusTip('Saves the current forecast file with the same filename')
    file_menu.addAction(self.file_save_option)

    self.file_save_as_option = QAction('Save as', self)
    self.file_save_as_option.setStatusTip('Saves the current forecast file with a new filename')
    file_menu.addAction(self.file_save_as_option)

    file_menu.addSeparator()

    self.export_option = QAction('Export to Excel', self)
    self.export_option.setStatusTip('Exports the current forecast file to an Excel spreadsheet')
    file_menu.addAction(self.export_option)

    file_menu.addSeparator()

    toggle_font_option = QMenu('Adjust font size', self)
    self.toggle_font_small = QAction('Small', self)
    self.toggle_font_small.setStatusTip('Changes the application font size to "small"')
    toggle_font_option.addAction(self.toggle_font_small)

    self.toggle_font_medium = QAction('Medium', self)
    self.toggle_font_medium.setStatusTip('Changes the application font size to "medium"')
    toggle_font_option.addAction(self.toggle_font_medium)

    self.toggle_font_large = QAction('Large', self)
    self.toggle_font_large.setStatusTip('Changes the application font size to "large"')
    toggle_font_option.addAction(self.toggle_font_large)

    file_menu.addMenu(toggle_font_option)

    self.edit_units_option = QAction('Edit application units', self)
    self.edit_units_option.setStatusTip('View, add, and edit the measurement units that PyForecast has access to')
    file_menu.addAction(self.edit_units_option)

    self.edit_settings_option = QAction('Edit application settings', self)
    self.edit_settings_option.setStatusTip('Edit the application-wide settings and configuration')
    file_menu.addAction(self.edit_settings_option)

    self.show_log_option = QAction('Show application log', self)
    self.show_log_option.setStatusTip('Open a textbox that views the application log')
    file_menu.addAction(self.show_log_option)

    file_menu.addSeparator()

    self.documentation_option = QAction('PyForecast documentation', self)
    self.documentation_option.setStatusTip('Opens the PyForecast documentation in a separate window')
    file_menu.addAction(self.documentation_option)

    self.check_updates_option = QAction('Check for updates', self)
    self.check_updates_option.setStatusTip('Check the github repository for any software updates')
    file_menu.addAction(self.check_updates_option)

    menu_bar.addMenu(file_menu)

    # Layout and show the Main Window
    self.setCentralWidget(tab_widget)

    width = min(app.config['window_width'], app.desktop().screenGeometry().width())
    height = min(app.config['window_height'], app.desktop().screenGeometry().height())
    self.resize(width, height)

    self.show()

  def resizeEvent(self, ev):
    s = ev.size()
    app.config['window_width'] = s.width()
    app.config['window_height'] = s.height()
    QMainWindow.resizeEvent(self, ev)

