from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QFont, QAction, QIcon
from PySide6.QtWidgets import (QMainWindow, QApplication, QTabWidget, QLabel,
                               QMenu)

from . import DatasetsTab, DataTab, ModelingTab, SavedModelsTab

app = QApplication.instance()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):

        QMainWindow.__init__(self, *args)

        # Main window properties
        self.setWindowTitle(f'PyForecast v{app.PYCAST_VERSION}')
        self.setWindowIcon(app.icon)

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
        self.current_file_widg = QLabel()
        f = self.current_file_widg.font()
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 110.)
        self.current_file_widg.setFont(f)
        self.current_file_widg.setTextFormat(Qt.TextFormat.RichText)
        self.status_bar.insertPermanentWidget(0, self.current_file_widg)
        self.status_bar.setSizeGripEnabled(False)

        # Set up the menu bar
        menu_bar = self.menuBar()

        # Set up the File menu
        file_menu = QMenu('File', self)

        self.new_option = QAction("New", self)
        self.new_option.setShortcut('Ctrl+N')
        self.new_option.setStatusTip('Create a new forecast from scratch')
        self.new_option.setIcon(QIcon.fromTheme('document-new'))
        file_menu.addAction(self.new_option)

        self.file_open_option = QAction('Open', self)
        self.file_open_option.setShortcut('Ctrl+O')
        self.file_open_option.setStatusTip('Select and open a forecast file')
        self.file_open_option.setIcon(QIcon.fromTheme('document-open'))
        file_menu.addAction(self.file_open_option)

        self.file_save_option = QAction('Save', self)
        self.file_save_option.setShortcut('Ctrl+S')
        self.file_save_option.setStatusTip(
            'Saves the current forecast file with the same filename')
        self.file_save_option.setIcon(QIcon.fromTheme('document-save'))
        file_menu.addAction(self.file_save_option)

        self.file_save_as_option = QAction('Save As', self)
        self.file_save_as_option.setShortcut('Ctrl+Shift+S')
        self.file_save_as_option.setStatusTip(
            'Saves the current forecast file with a new filename')
        self.file_save_as_option.setIcon(QIcon.fromTheme('document-save-as'))
        file_menu.addAction(self.file_save_as_option)

        file_menu.addSeparator()

        self.export_option = QAction('Export to Excel', self)
        self.export_option.setStatusTip(
            'Exports the current forecast file to an Excel spreadsheet')
        self.export_option.setIcon(QIcon.fromTheme('application-x-executable'))
        file_menu.addAction(self.export_option)

        # Set up the View menu
        view_menu = QMenu('View', self)

        toggle_font_option = QMenu('Adjust font size', self, toolTipsVisible=True)
        toggle_font_option.setStatusTip('Changes the application font size')
        toggle_font_option.setIcon(QIcon.fromTheme('preferences-desktop-font'))
        self.toggle_font_small = QAction('Small', self)
        self.toggle_font_small.setStatusTip(
            'Changes the application font size to "small"')
        toggle_font_option.addAction(self.toggle_font_small)

        self.toggle_font_medium = QAction('Medium', self)
        self.toggle_font_medium.setStatusTip(
            'Changes the application font size to "medium"')
        toggle_font_option.addAction(self.toggle_font_medium)

        self.toggle_font_large = QAction('Large', self)
        self.toggle_font_large.setStatusTip(
            'Changes the application font size to "large"')
        toggle_font_option.addAction(self.toggle_font_large)

        view_menu.addMenu(toggle_font_option)

        self.show_log_option = QAction('Show application log', self)
        self.show_log_option.setStatusTip(
            'Open a textbox that views the application log')
        self.show_log_option.setIcon(QIcon.fromTheme('system-file-manager'))
        view_menu.addAction(self.show_log_option)

        # Set up the Settings menu
        settings_menu = QMenu('Settings', self)

        self.edit_units_option = QAction('Edit application units', self)
        self.edit_units_option.setStatusTip(
            'View, add, and edit the measurement units that PyForecast has access to')
        self.edit_units_option.setIcon(QIcon.fromTheme('applications-system'))
        settings_menu.addAction(self.edit_units_option)

        self.edit_settings_option = QAction('Edit application settings', self)
        self.edit_settings_option.setStatusTip(
            'Edit the application-wide settings and configuration')
        self.edit_settings_option.setIcon(QIcon.fromTheme('applications-system'))
        settings_menu.addAction(self.edit_settings_option)

        # Set up the Tools menu
        tools_menu = QMenu('Tools', self)

        self.reload_points_option = QAction('Reload Point Datasets', self)
        self.reload_points_option.setStatusTip(
            'Add new point datasets that PyForecast has access to')
        self.reload_points_option.setIcon(QIcon.fromTheme('view-refresh'))
        tools_menu.addAction(self.reload_points_option)

        # Set up the Help menu
        help_menu = QMenu('Help', self)

        self.documentation_option = QAction('PyForecast documentation', self)
        self.documentation_option.setStatusTip(
            'Opens the PyForecast documentation in a separate window')
        self.documentation_option.setIcon(QIcon.fromTheme('system-help'))
        help_menu.addAction(self.documentation_option)

        self.check_updates_option = QAction('Check for updates', self)
        self.check_updates_option.setStatusTip(
            'Check the github repository for any software updates')
        self.check_updates_option.setIcon(QIcon.fromTheme('system-software-update'))
        help_menu.addAction(self.check_updates_option)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(view_menu)
        menu_bar.addMenu(settings_menu)
        menu_bar.addMenu(tools_menu)
        menu_bar.addMenu(help_menu)

        # Layout and show the Main Window
        self.setCentralWidget(tab_widget)

        user_screen_size = QGuiApplication.primaryScreen().size()
        width = min(app.settings['window_width'], user_screen_size.width())
        height = min(app.settings['window_height'], user_screen_size.height())

        rec = self.size()
        if kwargs.get('show'):
            if (width >= 0.95 * rec.width()) or (height >= 0.95 * rec.height()):
                self.showMaximized()
            else:
                self.resize(width, height)
                self.show()

    def resizeEvent(self, event):
        s = event.size()
        app.settings['window_width'] = s.width()
        app.settings['window_height'] = s.height()
        super().resizeEvent(event)

    def closeEvent(self, event):
        app.removeEventFilter(self)

        print('Exiting PyForecast')

        # close app windows if they are open
        if app.MWMV.log_view:
            app.MWMV.log_view.close()

        # delete all temporary files from the current directory
        app.delete_temp_files()

        # write out settings
        app.write_settings()

        # cleanup logging messages
        app.logger.cleanup()

        # accept closeEvent passing it to Qt
        event.accept()
