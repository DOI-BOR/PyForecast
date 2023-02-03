from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QStringListModel
from PyQt5.QtGui import QIcon
from pandas import DateOffset
from Models.ModelConfigurations import ResampledDataset
from Utilities.HydrologyDateTimes import water_year_start_date
app = QApplication.instance()
class PredictorView(QDialog):

  def __init__(self, app = None, selected_configuration = None):

    QDialog.__init__(self)
    self.selected_configuration = selected_configuration
    self.configuration = app.model_configurations.get_by_id(self.selected_configuration)
    self.current_idx = -1
    self.setUI()
    self.predictor_grid.setModel(self.configuration.predictor_pool)
    self.new_button.pressed.connect(self.new_predictor)
    self.delete_all_button.pressed.connect(self.delete_all)
    self.auto_gen_button.pressed.connect(self.autogen)
    self.configuration.predictor_pool.dataChanged.connect(lambda idx1,idx2: self.predictor_grid.resizeColumnsToContents())
    self.predictor_grid.selectionModel().currentChanged.connect(lambda new, old: self.setPredictor(new.row()))
    self.save_predictor_button.pressed.connect(self.savePredictor)
    self.delete_button.pressed.connect(self.delPredictor)

  def autogen(self):

    wys = water_year_start_date(self.configuration.issue_date)
    non_generated_predictors = []

    def boundByWaterYear(d):
      return max(d, wys)

    # Iterate over the datasets in the file
    for dataset in app.datasets.datasets:
      if dataset.raw_unit.type.lower() == 'flow':
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = False,
          agg_method = 'AVERAGE',
          period_start = boundByWaterYear(self.configuration.issue_date - DateOffset(months=3)),
          period_end = self.configuration.issue_date - DateOffset(days=1),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        continue
      elif dataset.raw_unit.type.lower() == 'temperature':
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = False,
          agg_method = 'AVERAGE',
          period_start = boundByWaterYear(self.configuration.issue_date - DateOffset(months=3)),
          period_end = self.configuration.issue_date - DateOffset(days=1),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        continue
      elif 'NOAA-CPC' in dataset.dataloader.NAME:
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = False,
          agg_method = 'AVERAGE',
          period_start = boundByWaterYear(self.configuration.issue_date - DateOffset(months=3)),
          period_end = self.configuration.issue_date - DateOffset(days=1),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        continue
      elif 'PRECIPITATION' in dataset.parameter.upper():
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = False,
          agg_method = 'ACCUMULATION',
          period_start = wys,
          period_end = self.configuration.issue_date - DateOffset(days=1),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = False,
          agg_method = 'ACCUMULATION',
          period_start = boundByWaterYear(self.configuration.issue_date - DateOffset(months=1)),
          period_end = self.configuration.issue_date - DateOffset(days=1),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        continue
      elif 'PDSI' in dataset.dataloader.NAME:
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = False,
          agg_method = 'AVERAGE',
          period_start = boundByWaterYear(self.configuration.issue_date - DateOffset(months=3)),
          period_end = self.configuration.issue_date - DateOffset(days=1),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        continue
      elif 'SNOW' in dataset.parameter.upper():
        predictor = ResampledDataset(
          dataset = dataset,
          forced = False,
          mustBePositive = True,
          agg_method = 'LAST',
          period_start = boundByWaterYear(self.configuration.issue_date - DateOffset(days=15)),
          period_end = self.configuration.issue_date - DateOffset(days=0),
          preprocessing = 'NONE'
        )
        self.configuration.predictor_pool.add_predictor(predictor)
        continue
      else:
        non_generated_predictors.append(dataset)

    if len(non_generated_predictors) > 0:
      s = '\n'.join([d.__repr__() for d in non_generated_predictors])
      ret = QMessageBox.information(self, 'Unsupported Datasets', f"The following datasets had no predictors genereated:\n\n {s}")

    return

  def delete_all(self):
    for i in range(len(self.configuration.predictor_pool)):
      rc = self.configuration.predictor_pool.rowCount()
      self.configuration.predictor_pool.delete_predictor(rc-1)

  def new_predictor(self):
    predictor = ResampledDataset(
      dataset=app.datasets[0],
      forced = False,
      mustBePositive = False,
      agg_method = list(app.agg_methods.keys())[0],
      preprocessing = list(app.preprocessing_methods.keys())[0],
      period_start = self.configuration.issue_date - DateOffset(days=1),
      period_end = self.configuration.issue_date - DateOffset(days=0),
    )
    self.configuration.predictor_pool.add_predictor(predictor)
    self.setPredictor(self.configuration.predictor_pool.rowCount()-1)
    return

  def clear_widg(self):
    return

  def setUI(self):

    self.setWindowTitle('Predictors')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    self.auto_gen_button = QPushButton("Auto Generate")
    self.auto_gen_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    self.delete_button = QPushButton('Delete Selected')
    self.delete_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    self.delete_all_button = QPushButton('Delete All')
    self.delete_all_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    self.predictor_grid = QTableView()     
    self.predictor_grid.horizontalHeader().setVisible(True)
    self.predictor_grid.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.predictor_grid.setSelectionMode(QAbstractItemView.SingleSelection)
    
    
    self.new_button = QPushButton("Add new predictor")
    self.new_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

    self.predictor_field = QComboBox()
    self.predictor_field.setModel(app.datasets)
    self.predictor_method_field = QComboBox()
    self.predictor_method_field.setModel(QStringListModel(list(app.agg_methods.keys())))
    self.predictor_period_start_field = QDateEdit()
    self.predictor_period_start_field.setDisplayFormat('MMM dd')
    self.predictor_period_end_field = QDateEdit()
    self.predictor_period_end_field.setDisplayFormat('MMM dd')
    self.predictor_preprocessing_field = QComboBox()  
    self.predictor_preprocessing_field.setModel(QStringListModel(list(app.preprocessing_methods.keys())))
    self.predictor_unit_field = QComboBox()
    self.predictor_unit_field.setModel(app.units)
    self.predictor_unit_field.setModelColumn(6)
    self.predictor_positive_box = QCheckBox()
    self.save_predictor_button = QPushButton("Save")
    self.predictor_force_box = QCheckBox()

    self.predictor_widg = QFrame()
    self.predictor_widg.setFrameStyle(QFrame.Box)
    self.predictor_widg.setLineWidth(2)
    qlayout = QFormLayout()
    qlayout.addRow(QLabel("Edit Predictor"))
    qlayout.addRow("Predictor Dataset", self.predictor_field)
    qlayout.addRow("Predictor Aggregation Method", self.predictor_method_field)
    hlayout = QHBoxLayout()
    hlayout.addWidget(QLabel('Aggregation Period'))
    hlayout.addStretch(1)
    hlayout.addWidget(self.predictor_period_start_field)
    hlayout.addWidget(QLabel('to'))
    hlayout.addWidget(self.predictor_period_end_field)
    qlayout.addRow(hlayout)
    qlayout.addRow("Predictor Preprocessing", self.predictor_preprocessing_field)
    qlayout.addRow("Predictor Unit", self.predictor_unit_field)
    qlayout.addRow("Enforce positive correlation between predictor and forecast target?", self.predictor_positive_box)
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    qlayout.addRow("Force predictor to be in all models?", self.predictor_force_box)
    hlayout.addWidget(self.save_predictor_button)
    qlayout.addRow(hlayout)

    self.predictor_widg.setLayout(qlayout)
    self.predictor_widg.setEnabled(False)
    

    layout = QGridLayout()
    layout.addWidget(self.auto_gen_button, 0, 0, 1, 1)
    layout.addWidget(self.new_button, 0, 2, 1, 1)
    layout.addWidget(self.delete_button, 0, 3, 1, 1)
    layout.addWidget(self.delete_all_button, 0, 4, 1, 1)
    layout.addWidget(self.predictor_grid, 1,0,1,5)
    layout.addWidget(self.predictor_widg, 2, 0, 1, 5)
    
    self.setLayout(layout)

  def delPredictor(self):
    idx = self.predictor_grid.selectionModel().currentIndex().row()
    self.configuration.predictor_pool.delete_predictor(idx)

  def savePredictor(self):
    
    self.predictor_widg.setEnabled(True)
    predictor = self.configuration.predictor_pool[self.current_idx]
    predictor.dataset = app.datasets[self.predictor_field.currentIndex()]
    predictor.agg_method = self.predictor_method_field.currentText()
    predictor.period_start = self.predictor_period_start_field.date().toPyDate()
    predictor.period_end = self.predictor_period_end_field.date().toPyDate()
    predictor.preprocessing = self.predictor_preprocessing_field.currentText()
    predictor.unit = app.units[self.predictor_unit_field.currentIndex()]
    predictor.forced = self.predictor_force_box.isChecked()
    predictor.mustBePositive = self.predictor_positive_box.isChecked()
    self.configuration.predictor_pool[self.current_idx] = predictor

  def setPredictor(self, idx):
    self.predictor_widg.setEnabled(True)
    self.current_idx = idx
    predictor = self.configuration.predictor_pool[idx]
    self.predictor_field.setCurrentText(predictor.dataset.__condensed_form__())
    self.predictor_method_field.setCurrentText(predictor.agg_method)
    self.predictor_period_start_field.setDate(QDate(predictor.period_start))
    self.predictor_period_end_field.setDate(QDate(predictor.period_end))
    self.predictor_preprocessing_field.setCurrentText(predictor.preprocessing)
    self.predictor_unit_field.setCurrentText(predictor.unit.__list_form__())
    self.predictor_positive_box.setChecked(predictor.mustBePositive)
    self.predictor_force_box.setChecked(predictor.forced)


if __name__ == '__main__':
  import sys
  app = QApplication(sys.argv)
  mw = PredictorView()
  mw.exec_()
  sys.exit(app.exec())