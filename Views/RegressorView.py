from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QStringListModel
from PyQt5.QtGui import QIcon
from pandas import DateOffset
from Models.ModelConfigurations import Regressor

app = QApplication.instance()

class RegressorView(QDialog):

  def __init__(self, selected_configuration = None):

    QDialog.__init__(self)
    self.selected_configuration = selected_configuration
    self.configuration = app.model_configurations.get_by_id(self.selected_configuration)
    self.current_idx = -1
    self.setUI()
    self.regressor_select.setModel(QStringListModel(list(app.regressors.keys())))
    self.scoring_metric.setModel(QStringListModel(list(app.scorers.keys())))
    self.regressor_grid.setModel(self.configuration.regressors)
    self.new_button.pressed.connect(self.add_regressor)
    self.delete_button.pressed.connect(self.delRegressor)
    self.delete_all_button.pressed.connect(self.delete_all)
    self.regressor_save_btn.pressed.connect(self.saveRegressor)
  
    self.delete_all_button.pressed.connect(self.delete_all)
    self.configuration.regressors.dataChanged.connect(lambda idx1,idx2: self.regressor_grid.resizeColumnsToContents())
    self.regressor_grid.selectionModel().currentChanged.connect(lambda new, old: self.setRegressor(new.row()))


  def delete_all(self):
    for i in range(len(self.configuration.regressors)):
      rc = self.configuration.regressors.rowCount()
      self.configuration.regressors.delete_regressor(rc-1)

  def add_regressor(self):
    regressor = Regressor(
      regression_model = list(app.regressors.keys())[0],
      cross_validation = app.config['default_cross_validation'],
      feature_selection = app.config['default_feature_selector'],
      scoring_metric = list(app.scorers.keys())[0],
    )
    self.configuration.regressors.add_regressor(regressor)

  def setUI(self):

    self.setWindowTitle('Regressors')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    self.delete_all_button = QPushButton('Delete All')
    self.delete_button = QPushButton("Delete Selected")
    self.regressor_grid = QTableView()     
    self.regressor_grid.setSelectionBehavior(QAbstractItemView.SelectRows)

    self.regressor_grid.horizontalHeader().setVisible(True)
    self.new_button = QPushButton("Add new Regressor")

    self.regressor_select = QComboBox()
    self.scoring_metric = QComboBox()

    self.regressor_save_btn = QPushButton("Save")
    

    self.regressor_widg = QFrame()
    self.regressor_widg.setFrameStyle(QFrame.Box)
    self.regressor_widg.setLineWidth(2)
    qlayout = QFormLayout()
    qlayout.addRow(QLabel("Edit Regressor"))
    qlayout.addRow("Regressor Algorithm", self.regressor_select)
    qlayout.addRow("Regressor Scoring Metric", self.scoring_metric)
    l = QHBoxLayout()
    l.addStretch(1)
    l.addWidget(self.regressor_save_btn)
    qlayout.addRow(l)
    

    self.regressor_widg.setLayout(qlayout)
    self.regressor_widg.setEnabled(False)
    

    layout = QGridLayout()
    layout.addWidget(self.new_button, 0, 2, 1, 1)
    layout.addWidget(self.delete_button, 0, 3, 1, 1)
    layout.addWidget(self.delete_all_button, 0, 4, 1, 1)
    layout.addWidget(self.regressor_grid, 1,0,1,5)
    layout.addWidget(self.regressor_widg, 2, 0, 1, 5)
    
    self.setLayout(layout)

  def delRegressor(self):
    idx = self.regressor_grid.selectionModel().currentIndex().row()
    self.configuration.regressors.delete_regressor(idx)

  def saveRegressor(self):
    idx = self.current_idx
    regressor = self.configuration.regressors[idx]

    regressor.regression_model = self.regressor_select.currentText()
    regressor.scoring_metric = self.scoring_metric.currentText()
    self.configuration.regressors[idx] = regressor

  def setRegressor(self, idx):
    regressor = self.configuration.regressors[idx]
    self.current_idx = idx
    self.regressor_select.setCurrentText(regressor.regression_model)
    self.scoring_metric.setCurrentText(regressor.scoring_metric)
    self.regressor_widg.setEnabled(True)
    

