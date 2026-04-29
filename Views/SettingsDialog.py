from datetime import datetime

from PySide6.QtCore import QStringListModel, QDate
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QLabel, QFrame,
                               QHBoxLayout, QPushButton, QVBoxLayout)

from Utilities.ZzQWidgets import ZzQDateEdit, ZzQComboBox, ZzQSpinBox, ZzQDoubleSpinBox

# Get the global application
app = QApplication.instance()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle('PyForecast Settings')
        self.setWindowIcon(app.icon)

        self.download_start_setting = ZzQDateEdit()
        self.download_start_setting.setStatusTip(
            'Choosing the "Download All" button will download data from this '
            'date until now')
        self.download_start_setting.setDisplayFormat('yyyy-MMM-d')
        self.download_recent_lookback_setting = ZzQSpinBox()
        self.download_recent_lookback_setting.setStatusTip(
            'Choosing the "Download Recent" button will download data from the '
            'datasets last datapoint minus this many days')
        self.download_recent_lookback_setting.setSuffix(' Days')
        self.model_training_duration_setting = ZzQSpinBox()
        self.model_training_duration_setting.setSuffix(' Years')
        self.default_cross_validation_setting = ZzQComboBox()
        self.default_cross_validation_setting.setModel(
            QStringListModel(app.cross_validation.keys()))
        self.default_feature_selection = ZzQComboBox()
        self.default_feature_selection.setModel(
            QStringListModel(app.feature_selection.keys()))
        self.brute_force_under_setting = ZzQSpinBox()
        self.brute_force_under_setting.setSuffix(' Predictors')
        self.search_time_limit_setting = ZzQSpinBox()
        self.search_time_limit_setting.setSuffix(' Minutes')
        self.max_pc_modes_setting = ZzQDoubleSpinBox()
        self.max_pc_modes_setting.setMinimum(0.5)
        self.max_pc_modes_setting.setMaximum(0.99)

        layout = QFormLayout()
        layout.setVerticalSpacing(4)
        layout.addRow(QLabel("<strong>Download Settings</strong>"))
        layout.addRow(
            '    Default Download Start Date',
            self.download_start_setting
        )
        layout.addRow(
            '    Number of days to look back for recent data edits',
            self.download_recent_lookback_setting
        )

        layout.addRow(QLabel('<strong>Model Configuration</strong>'))
        layout.addRow(
            '    Default training period for new models',
            self.model_training_duration_setting
        )
        layout.addRow(
            '    Default cross-validation for models',
            self.default_cross_validation_setting
        )
        layout.addRow(
            '    Default feature selection algorithm',
            self.default_feature_selection
        )
        layout.addRow(
            '    Maximum number of predictors to brute force search',
            self.brute_force_under_setting
        )
        layout.addRow(
            '    Maximum time per regressor to search for models',
            self.search_time_limit_setting
        )
        layout.addRow(
            '    Maximum cumulative importance for Princ. Comp. retention?',
            self.max_pc_modes_setting
        )

        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        vstretch = QVBoxLayout()
        vstretch.addStretch(1)
        layout.addItem(vstretch)
        layout.addRow(hline)

        layout2 = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.cancel_button = QPushButton('Cancel')
        layout2.addStretch(1)
        layout2.addWidget(self.save_button)
        layout2.addWidget(self.cancel_button)
        layout2.setSpacing(4)
        layout.addItem(layout2)

        self.setLayout(layout)

        self.save_button.pressed.connect(self.save_settings)
        self.cancel_button.pressed.connect(self.cancel_settings)

        self.load_settings()

    def save_settings(self):
        self.store_settings()
        self.close()

    def cancel_settings(self):
        self.close()

    def load_settings(self):
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

    def store_settings(self):
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
