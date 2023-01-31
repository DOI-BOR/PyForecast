from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel, QDate
from PyQt5.QtGui import QIcon
from datetime import datetime

# Get the global application
app = QApplication.instance()

class SettingsDialog(QDialog):
  def __init__(self):

    QDialog.__init__(self)
    self.setWindowTitle('Application Settings')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    self.download_start_setting = QDateEdit()
    self.download_start_setting.setStatusTip('Choosing the "Download All" button will download data from this date until now')
    self.download_start_setting.setDisplayFormat('yyyy-MMM-d')
    self.download_recent_lookback_setting = QSpinBox()
    self.download_recent_lookback_setting.setStatusTip('Choosing the "Download Recent" button will download data from the datasets last datapoint minus this many days')
    self.download_recent_lookback_setting.setSuffix(' Days')
    self.model_training_duration_setting = QSpinBox()
    self.model_training_duration_setting.setSuffix(' Years')
    self.default_cross_validation_setting = QComboBox()
    self.default_cross_validation_setting.setModel(QStringListModel(list(app.cross_validation.keys())))
    self.default_feature_selection = QComboBox()
    self.default_feature_selection.setModel(QStringListModel(list(app.feature_selection.keys())))
    self.brute_force_under_setting = QSpinBox()
    self.brute_force_under_setting.setSuffix(' Predictors')
    self.search_time_limit_setting = QSpinBox()
    self.search_time_limit_setting.setSuffix(' Minutes')

    layout = QFormLayout()
    layout.addRow(QLabel("<strong>Download Settings</strong>"))
    layout.addRow('Default Download Start Date', self.download_start_setting)
    layout.addRow('Number of days to look back for recent data edits', self.download_recent_lookback_setting)

    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)

    layout.addRow(QLabel('<strong>Model Configuration</strong>'))
    layout.addRow('Default training period for new models', self.model_training_duration_setting)
    layout.addRow('Default cross-validation for models', self.default_cross_validation_setting)
    layout.addRow('Default feature selection algorithm',self.default_feature_selection)
    layout.addRow('Maximum number of predictors to brute force search', self.brute_force_under_setting)
    layout.addRow('Maximum time per regressor to search for models', self.search_time_limit_setting)

    self.setLayout(layout)

    self.setSettings()

  def closeEvent(self, a0):
    self.storeSettings()
    QDialog.closeEvent(self, a0)
  
  def setSettings(self):

    self.download_start_setting.setDate(QDate(app.config['default_data_download_start']))
    self.download_recent_lookback_setting.setValue(app.config['default_recent_data_lookback'])
    self.model_training_duration_setting.setValue(app.config['default_model_training_duration'])
    self.default_cross_validation_setting.setCurrentText(app.config['default_cross_validation'])
    self.default_feature_selection.setCurrentText(app.config['default_feature_selector'])
    self.brute_force_under_setting.setValue(app.config['brute_force_under_no'])
    self.search_time_limit_setting.setValue(app.config['model_search_time_limit'])

  def storeSettings(self):

    date = self.download_start_setting.date().toPyDate()
    app.config['default_data_download_start'] = datetime(date.year, date.month, date.day)
    app.config['default_recent_data_lookback'] = self.download_recent_lookback_setting.value()
    app.config['default_model_training_duration'] = self.model_training_duration_setting.value()
    app.config['default_cross_validation'] = self.default_cross_validation_setting.currentText()
    app.config['default_feature_selector'] = self.default_feature_selection.currentText()
    app.config['brute_force_under_no'] = self.brute_force_under_setting.value()
    app.config['model_search_time_limit'] = self.search_time_limit_setting.value()


    pass


