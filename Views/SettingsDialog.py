from datetime import datetime

from PySide6.QtCore import QStringListModel, QDate
from PySide6.QtWidgets import (QApplication, QDialog, QSpinBox,
                               QDoubleSpinBox, QFormLayout, QLabel, QFrame)

from Utilities.ZzQWidgets import ZzQDateEdit, ZzQComboBox

# Get the global application
app = QApplication.instance()


class SettingsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle('Application Settings')
        self.setWindowIcon(app.icon)

        self.download_start_setting = ZzQDateEdit()
        self.download_start_setting.setStatusTip(
            'Choosing the "Download All" button will download data from this '
            'date until now')
        self.download_start_setting.setDisplayFormat('yyyy-MMM-d')
        self.download_recent_lookback_setting = QSpinBox()
        self.download_recent_lookback_setting.setStatusTip(
            'Choosing the "Download Recent" button will download data from the '
            'datasets last datapoint minus this many days')
        self.download_recent_lookback_setting.setSuffix(' Days')
        self.model_training_duration_setting = QSpinBox()
        self.model_training_duration_setting.setSuffix(' Years')
        self.default_cross_validation_setting = ZzQComboBox()
        self.default_cross_validation_setting.setModel(
            QStringListModel(list(app.cross_validation.keys())))
        self.default_feature_selection = ZzQComboBox()
        self.default_feature_selection.setModel(
            QStringListModel(list(app.feature_selection.keys())))
        self.brute_force_under_setting = QSpinBox()
        self.brute_force_under_setting.setSuffix(' Predictors')
        self.search_time_limit_setting = QSpinBox()
        self.search_time_limit_setting.setSuffix(' Minutes')
        self.max_pc_modes_setting = QDoubleSpinBox()
        self.max_pc_modes_setting.setMinimum(0.5)
        self.max_pc_modes_setting.setMaximum(0.99)

        layout = QFormLayout()
        layout.addRow(QLabel("<strong>Download Settings</strong>"))
        layout.addRow('Default Download Start Date', self.download_start_setting)
        layout.addRow('Number of days to look back for recent data edits',
                      self.download_recent_lookback_setting)

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.HLine)
        frame.setLineWidth(2)

        layout.addRow(QLabel('<strong>Model Configuration</strong>'))
        layout.addRow('Default training period for new models',
                      self.model_training_duration_setting)
        layout.addRow('Default cross-validation for models',
                      self.default_cross_validation_setting)
        layout.addRow('Default feature selection algorithm',
                      self.default_feature_selection)
        layout.addRow('Maximum number of predictors to brute force search',
                      self.brute_force_under_setting)
        layout.addRow('Maximum time per regressor to search for models',
                      self.search_time_limit_setting)
        layout.addRow('Maximum cumulative importance for Princ. Comp. retention?',
                      self.max_pc_modes_setting)
        self.setLayout(layout)

        self.setSettings()

    def closeEvent(self, event):
        self.storeSettings()
        event.accept()

    def setSettings(self):
        self.download_start_setting.setDate(
            QDate(app.settings['default_data_download_start']))
        self.download_recent_lookback_setting.setValue(
            app.settings['default_recent_data_lookback'])
        self.model_training_duration_setting.setValue(
            app.settings['default_model_training_duration'])
        self.default_cross_validation_setting.setCurrentText(
            app.settings['default_cross_validation'])
        self.default_feature_selection.setCurrentText(
            app.settings['default_feature_selector'])
        self.brute_force_under_setting.setValue(
            app.settings['brute_force_under_no'])
        self.search_time_limit_setting.setValue(
            app.settings['model_search_time_limit'])
        self.max_pc_modes_setting.setValue(
            app.settings['max_pc_mode_variance'])

    def storeSettings(self):
        date = self.download_start_setting.date().toPython()
        app.settings['default_data_download_start'] = (
            datetime(date.year, date.month, date.day))
        app.settings['default_recent_data_lookback'] = (
            self.download_recent_lookback_setting.value())
        app.settings['default_model_training_duration'] = (
            self.model_training_duration_setting.value())
        app.settings['default_cross_validation'] = (
            self.default_cross_validation_setting.currentText())
        app.settings['default_feature_selector'] = (
            self.default_feature_selection.currentText())
        app.settings['brute_force_under_no'] = (
            self.brute_force_under_setting.value())
        app.settings['model_search_time_limit'] = (
            self.search_time_limit_setting.value())
        app.settings['max_pc_mode_variance'] = (
            self.max_pc_modes_setting.value())
