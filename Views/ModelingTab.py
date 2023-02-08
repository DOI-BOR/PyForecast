from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import *
from Utilities import RichTextDelegate

class ModelingTab(QWidget):

  def __init__(self):

    QWidget.__init__(self)

    # Create the model configuration list
    self.add_conf_button = QPushButton('Add Configuration')
    self.add_conf_button.setStatusTip("Add a new configuration to this file. PyForecast uses configurations to search for viable models")
    self.config_list = ConfigurationList()

    # Create the configuration editor
    self.config_editor = ConfigurationEditor()

    # LAyout the tab
    layout = QHBoxLayout()
    widg = QWidget()
    vlayout = QGridLayout()
    vlayout.addWidget(self.add_conf_button, 0, 0, 1, 1)
    vlayout.addWidget(self.config_list, 1, 0, 1, 4)
    widg.setLayout(vlayout)
    splitter = QSplitter()
    splitter.addWidget(widg)
    splitter.addWidget(self.config_editor)
    layout.addWidget(splitter)
    self.setLayout(layout)
    
class ConfigurationList(QListView):

  def __init__(self):
    
    QListView.__init__(self)
    self.setMinimumWidth(300)
    self.setItemDelegate(RichTextDelegate.HTMLDelegate())
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.setSelectionMode(QAbstractItemView.SingleSelection)
    self.customContextMenuRequested.connect(self.customMenu)

    self.add_action = QAction('Add a new configuration')
    self.add_action.setStatusTip("Add a new configuration to this file. PyForecast uses configurations to search for viable models")
    self.duplicate_action = QAction("Duplicate selected configuration")
    self.duplicate_action.setStatusTip("Create a new configuration, duplicating the selected configuration")
    self.remove_action = QAction("Remove selected configuration")
    self.remove_action.setStatusTip("Removes the selected configuration from the file")


  def customMenu(self, pos):
    globalpos = self.mapToGlobal(pos)
    menu = QMenu()
    
    menu.addAction(self.add_action)
    menu.addAction(self.duplicate_action)
    menu.addAction(self.remove_action)

    index = self.indexAt(pos)
    selected = self.selectedIndexes()

    if not index.isValid():
      self.add_action.setEnabled(True)
      self.duplicate_action.setEnabled(False)
      self.remove_action.setEnabled(False)
    else:
      self.add_action.setEnabled(False)
      self.duplicate_action.setEnabled(True)
      self.remove_action.setEnabled(True)
    menu.exec_(globalpos)

class ConfigurationEditor(QWidget):

  def __init__(self):

    QWidget.__init__(self)
    sa = QScrollArea()
    widg = QWidget()
    self.save_button = QPushButton('Apply')
    self.run_button = QPushButton("Generate Models")
    olayout = QVBoxLayout()
    olayout.addWidget(sa)
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(self.save_button)
    hlayout.addWidget(self.run_button)
    olayout.addLayout(hlayout)
    self.setLayout(olayout)

    self.summary_field = QLabel()
    self.summary_field.setWordWrap(True)

    # Set up the fields
    self.name_field = QLineEdit()
    self.name_field.setStatusTip('Give this configuration a unique name')
    self.issue_date_field = QDateEdit()
    self.issue_date_field.setDisplayFormat('MMMM dd')
    self.issue_date_field.setStatusTip('What month and day will the forecasts from this model be issued')
    self.training_start_field = QDateEdit()
    self.training_start_field.setDisplayFormat('yyyy-MMM')
    self.training_start_field.setStatusTip('How much data will be used to train the models')
    self.training_end_field = QDateEdit()
    self.training_end_field.setDisplayFormat('yyyy-MMM')
    self.training_end_field.setStatusTip('How much data will be used to train the models')
    self.exclude_check = QCheckBox('Exclude dates from training?')
    self.exclude_check.setStatusTip('Should we exclude any dates from the training period?')
    self.exclude_years_field = QLineEdit()
    self.exclude_years_field.setStatusTip('Comma separated list of years to exclude (e.g. 2012,1990,2004)')
    self.exclude_years_field.setEnabled(False)
    self.exclude_check.toggled.connect(self.exclude_years_field.setEnabled)
    self.comment_field = QTextEdit()
    self.comment_field.setMinimumHeight(35)
    self.comment_field.setMaximumHeight(70)
    self.comment_field.setStatusTip('Add any comments for this configuration')

    self.predictand_field = QComboBox()
    self.predictand_method_field = QComboBox()  
    self.predictand_period_start_field = QDateEdit()
    self.predictand_period_start_field.setDisplayFormat('MMM dd')
    self.predictand_period_end_field = QDateEdit()
    self.predictand_period_end_field.setDisplayFormat('MMM dd')
    self.predictand_preprocessing_field = QComboBox()  
    self.predictand_unit_field = QComboBox()
    self.view_predictand_data_button = QPushButton('View/Edit Target Data')
    self.view_predictand_data_button.setStatusTip('Open the forecast target data in a new window for viewing/editing')
    
    self.predictor_list = QTableView()
    self.predictor_list.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.predictor_list.setSelectionMode(QAbstractItemView.SingleSelection)
    self.predictor_list.horizontalHeader().setVisible(True)
    self.predictor_count = QLabel('There are <strong>0</strong> predictors in this configuration')
    self.predictor_add_button = QPushButton('Add/Remove Predictors')
    self.predictor_add_button.setStatusTip('Open the Predictor Dialog to add or remove predictors')
    self.view_predictor_data_button = QPushButton("View/Edit Predictor Data")
    self.view_predictor_data_button.setStatusTip('Open the predictor data in a new window for viewing/editing')

    self.regressor_list = QTableView()
    self.regressor_list.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.regressor_list.setSelectionMode(QAbstractItemView.SingleSelection)
    self.regressor_list.horizontalHeader().setVisible(True)
    self.regressor_count = QLabel('There are <strong>0</strong> regressors in this configuration')
    self.regressor_add_button = QPushButton('Add/Remove Regressor')
    self.regressor_add_button.setStatusTip('Open the Regressor Dialog to add or remove regressors')
    

    # layout the form
    layout = QFormLayout()
    layout.addRow(QLabel('<strong>Model Information</strong>', objectName='HeaderLabel'))
    layout.addRow(self.summary_field)
    layout.addRow('Configuration Name', self.name_field)
    layout.addRow('Forecast Issue Date', self.issue_date_field)
    hlayout = QHBoxLayout()
    hlayout.addWidget(QLabel('Training Period'))
    hlayout.addStretch(1)
    hlayout.addWidget(self.training_start_field)
    hlayout.addWidget(QLabel('to'))
    hlayout.addWidget(self.training_end_field)
    layout.addRow(hlayout)
    hlayout = QHBoxLayout()
    hlayout.addWidget(self.exclude_check)
    hlayout.addStretch(1)
    hlayout.addWidget(self.exclude_years_field)
    layout.addRow(hlayout)
    layout.addRow('Model Comments', self.comment_field)
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)
    layout.addRow(frame)

    layout.addRow(QLabel('<strong>Forecast Target Information</strong>', objectName='HeaderLabel'))
    layout.addRow("Target Dataset", self.predictand_field)
    layout.addRow("Target Aggregation Method", self.predictand_method_field)
    hlayout = QHBoxLayout()
    hlayout.addWidget(QLabel('Aggregation Period'))
    hlayout.addStretch(1)
    hlayout.addWidget(self.predictand_period_start_field)
    hlayout.addWidget(QLabel('to'))
    hlayout.addWidget(self.predictand_period_end_field)
    layout.addRow(hlayout)
    layout.addRow("Target Preprocessing", self.predictand_preprocessing_field)
    layout.addRow("Target Unit", self.predictand_unit_field)
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(self.view_predictand_data_button)
    layout.addRow(hlayout)
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)
    layout.addRow(frame)

    layout.addRow(QLabel("<strong>Predictors</strong>", objectName='HeaderLabel'))
    hlayout = QHBoxLayout()
    hlayout.addWidget(self.predictor_count)
    hlayout.addStretch(1)
    hlayout.addWidget(self.view_predictor_data_button)
    hlayout.addWidget(self.predictor_add_button)
    layout.addRow(hlayout)
    layout.addRow(self.predictor_list)
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)
    layout.addRow(frame)

    layout.addRow(QLabel("<strong>Regressors</strong>", objectName='HeaderLabel'))
    hlayout = QHBoxLayout()
    hlayout.addWidget(self.regressor_count)
    hlayout.addStretch(1)
    hlayout.addWidget(self.regressor_add_button)
    layout.addRow(hlayout)
    layout.addRow(self.regressor_list)



    widg.setLayout(layout)
    sa.setWidget(widg)
    sa.setWidgetResizable(True)

  def deselect_all(self):
    for l in self.findChildren(QLineEdit):
      l.deselect()


  def clear(self):
    for l in self.findChildren(QLineEdit):
      l.clear()
    for d in self.findChildren(QTextEdit):
      d.clear()
    for c in self.findChildren(QComboBox):
      c.setCurrentIndex(0)
    for e in self.findChildren(QDateEdit):
      e.setDate(QDate(2000,1,1))
    for b in self.findChildren(QCheckBox):
      b.setChecked(False)
