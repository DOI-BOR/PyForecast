from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel,QDate, Qt, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QIcon
from datetime import datetime
from Views import PredictorView, RegressorView, ResampledDataViewer, GenModelDialog
from Models.ModelConfigurations import ResampledDataset, Regressor
import Utilities.HydrologyDateTimes as hdt
from copy import deepcopy

app = QApplication.instance()

class MethodFilterModel(QSortFilterProxyModel):

  def __init__(self):
    QSortFilterProxyModel.__init__(self)
    self.filterString = None
    
  def setFilterString(self, dataset):
    
    self.dataset = dataset
    text = dataset.display_unit.type
    self.filterString = text.lower()
    self.invalidateFilter()
    
  def filterAcceptsRow(self, sourceRow, sourceParent = QModelIndex()):
    idx = self.sourceModel().index(sourceRow)
    source_method = self.sourceModel().data(idx, Qt.DisplayRole)
    if self.filterString == 'flow':
      if self.dataset.display_unit.id == 'cfs':
        if 'MCM' in source_method:
          return False
      elif self.dataset.display_unit.id == 'cms':
        if 'KAF' in source_method:
          return False
      return True
    else:
      if 'MCM' in source_method or 'KAF' in source_method:
        return False
      else:
        return True

class UnitFilterModel(QSortFilterProxyModel):

  def __init__(self):
    QSortFilterProxyModel.__init__(self)
    self.filterString = 'length'
    self.dataset = None
    self.method = ''

  def setFilterString(self, dataset, method):
    self.method = method
    self.dataset = dataset
    text = dataset.display_unit.type
    self.filterString = text.lower()
    self.invalidateFilter()
    
  def filterAcceptsRow(self, sourceRow, sourceParent = QModelIndex()):
    idx = self.sourceModel().index(sourceRow, 5)
    source_unit_type = self.sourceModel().data(idx, Qt.DisplayRole)
    idx2 = self.sourceModel().index(sourceRow, 0)
    source_unit_id = self.sourceModel().data(idx2, Qt.DisplayRole)
    
    if 'MCM' in self.method:
      if source_unit_id.value() == 'mcm':
        return True
      else:
        return False
    elif 'KAF' in self.method:
      if source_unit_id.value() == 'kaf':
        return True
      else:
        return False
    else:
      if source_unit_type.value() == self.filterString:
        return True
      else:
        return False

class ModelConfigurationModelView:

  def __init__(self):

    self.mt = app.gui.ModelingTab
    self.ce = self.mt.config_editor

    # set the models
    self.mt.config_list.setModel(app.model_configurations)
    self.method_model = QStringListModel(list(app.agg_methods.keys()))
    self.filter_method_model = MethodFilterModel()
    self.filter_method_model.setSourceModel(self.method_model)
    self.filter_units_model = UnitFilterModel()
    self.filter_units_model.setSourceModel(app.units)


    # COnnect views with models
    self.mt.config_editor.predictand_method_field.setModel(self.filter_method_model)
    self.mt.config_editor.predictand_preprocessing_field.setModel(QStringListModel(list(filter(lambda x: not x.startswith('INV_'),app.preprocessing_methods.keys()))))
    self.mt.config_editor.predictand_field.setModel(app.datasets)
    
    self.mt.config_editor.predictand_unit_field.setModel(self.filter_units_model)
    self.mt.config_editor.predictand_unit_field.setModelColumn(6)
    self.mt.add_conf_button.pressed.connect(self.new_configuration)
    self.mt.config_list.add_action.triggered.connect(self.new_configuration)
    self.mt.config_list.selectionModel().currentChanged.connect(lambda sel, desel: self.set_configuration(sel.row()))
    self.mt.config_editor.save_button.pressed.connect(self.store_configuration)
    self.mt.config_editor.predictor_add_button.pressed.connect(self.open_predictor_view)
    self.mt.config_editor.regressor_add_button.pressed.connect(self.open_regressor_view)
    self.mt.config_editor.view_predictand_data_button.pressed.connect(lambda: self.open_view_data(-1))
    self.mt.config_editor.view_predictor_data_button.pressed.connect(lambda: self.open_view_data(None))
    self.mt.config_editor.run_button.pressed.connect(self.gen_button_pressed)
    self.mt.config_editor.predictand_field.currentIndexChanged.connect(lambda idx: self.update_predictand_info(idx, 'predictand'))
    self.mt.config_editor.predictand_method_field.currentIndexChanged.connect(lambda idx: self.update_predictand_info(idx, 'method'))
    #self.mt.config_editor.predictand_method_field.currentTextChanged.connect(lambda text: self.mt.config_editor.predictand_unit_field.setCurrentText(app.units.get_unit('kaf').__list_form__()) if 'KAF' in text else None)
    #self.mt.config_editor.predictand_method_field.currentTextChanged.connect(lambda text: self.mt.config_editor.predictand_unit_field.setCurrentText(app.units.get_unit('mcm').__list_form__()) if 'MCM' in text else None)
    self.mt.config_list.remove_action.triggered.connect(self.delete_conf)
    self.mt.config_list.duplicate_action.triggered.connect(self.duplicate_conf)

    self.mt.config_editor.setEnabled(False)


  def delete_conf(self, _):
    idx = self.mt.config_list.selectionModel().currentIndex().row()
    conf = app.model_configurations[idx]
    app.model_configurations.remove_configuration(conf)

  def duplicate_conf(self, _):
    rowcount = app.model_configurations.rowCount()
    idx = self.mt.config_list.selectionModel().currentIndex().row()
    conf = app.model_configurations[idx]
    
    
    app.model_configurations.add_configuration(
      name = f'{conf.name} - Copy',
      comment = f'Created by user: {app.current_user} at {datetime.now():%Y-%m-%d %H:%M:%S}',
      training_start_date = conf.training_start_date,
      training_end_date = conf.training_end_date,
      training_exclude_dates = conf.training_exclude_dates,
      issue_date = conf.issue_date,
      predictand = ResampledDataset(
        dataset_guid = conf.predictand.dataset().guid,
        unit =  conf.predictand.unit,
        agg_method = conf.predictand.agg_method,
        preprocessing =  conf.predictand.preprocessing,
        period_start =  conf.predictand.period_start,
        period_end =  conf.predictand.period_end
      )
    )
    new_conf = app.model_configurations[rowcount]
    for predictor in conf.predictor_pool:
      
      new_conf.predictor_pool.add_predictor(
        ResampledDataset(
          dataset_guid = predictor.dataset().guid,
          unit = predictor.unit,
          agg_method=predictor.agg_method,
          preprocessing = predictor.preprocessing,
          period_start = predictor.period_start,
          period_end = predictor.period_end
        )
      )
    for regressor in conf.regressors:
      new_conf.regressors.add_regressor(
        Regressor(
          regression_model = regressor.regression_model,
          cross_validation = regressor.cross_validation,
          feature_selection = regressor.feature_selection,
          scoring_metric = regressor.scoring_metric
        )
      )
    app.model_configurations[rowcount] = new_conf
    self.mt.config_list.setCurrentIndex(app.model_configurations.index(rowcount))

  def new_configuration(self, checked=None):

    # Ensure that we have at least one dataset in the file
    if len(app.datasets) < 1:
      msg = QMessageBox.information(self.mt, 'Not enough data', 'You must add at least one dataset to create a new configuration')
      return
    rowcount = app.model_configurations.rowCount()
    app.model_configurations.add_configuration(
      name = f'NewConfiguration{rowcount}',
      comment = f'Created by user: {app.current_user} at {datetime.now():%Y-%m-%d %H:%M:%S}',
      training_start_date = datetime(hdt.current_water_year()-30, 10, 1),
      training_end_date = datetime(hdt.current_water_year()-1, 9, 30),
      issue_date = datetime(hdt.current_water_year(),10,1),
      predictand = ResampledDataset(
        dataset_guid = app.datasets[0].guid,
        unit = app.datasets[0].display_unit,
        agg_method = list(app.agg_methods.keys())[0],
        preprocessing = list(app.preprocessing_methods.keys())[0],
        period_start = datetime(2000, 4,1),
        period_end = datetime(2000,7,31)
      )
    )
    self.mt.config_list.setCurrentIndex(app.model_configurations.index(rowcount))

  def set_configuration(self, configuration_idx):
    self.ce.clear()
    configuration = app.model_configurations[configuration_idx]
    self.ce.summary_field.setText(configuration.__simple_target_string__())
    self.ce.name_field.setText(configuration.name)
    issue_date = QDate(configuration.issue_date)
    training_start_date = QDate(configuration.training_start_date)
    training_end_date = QDate(configuration.training_end_date)
    self.ce.issue_date_field.setDate(issue_date)
    self.ce.training_start_field.setDate(training_start_date)
    self.ce.training_end_field.setDate(training_end_date)
    if len(configuration.training_exclude_dates)>0:
      self.ce.exclude_check.setChecked(True)
      self.ce.exclude_years_field.setText(', '.join(configuration.training_exclude_dates))
    self.ce.comment_field.setText(configuration.comment)

    # Set the predictand
    self.ce.predictand_field.setCurrentText(configuration.predictand.dataset().__condensed_form__())
    self.ce.predictand_preprocessing_field.setCurrentText(configuration.predictand.preprocessing)
    self.ce.predictand_method_field.setCurrentText(configuration.predictand.agg_method)
    self.ce.predictand_period_start_field.setDate(QDate(configuration.predictand.period_start))
    self.ce.predictand_period_end_field.setDate(QDate(configuration.predictand.period_end))
    self.ce.predictand_unit_field.setCurrentText(configuration.predictand.unit.__list_form__())

    # Set the predictors
    pl = self.ce.predictor_list
    pl.setModel(configuration.predictor_pool)
    pl.resizeColumnsToContents()
    pl.horizontalHeader().setStretchLastSection(True)
    self.ce.predictor_count.setText(f'There are <strong>{len(configuration.predictor_pool)}</strong> predictors in this configuration')

    # Set the regressors
    r = self.ce.regressor_list
    r.setModel(configuration.regressors)
    r.resizeColumnsToContents()
    r.horizontalHeader().setStretchLastSection(True)
    self.ce.regressor_count.setText(f'There are <strong>{len(configuration.regressors)}</strong> regressors in this configuration')

    configuration.predictor_pool.dataChanged.connect(lambda idx1,idx2: self.ce.predictor_list.resizeColumnsToContents())
    configuration.predictor_pool.dataChanged.connect(lambda idx1,idx2: self.ce.predictor_list.horizontalHeader().setStretchLastSection(True))
    configuration.predictor_pool.dataChanged.connect(lambda idx1,idx2: self.ce.predictor_count.setText(f'There are <strong>{len(configuration.predictor_pool)}</strong> predictors in this configuration'))

    configuration.regressors.dataChanged.connect(lambda idx1,idx2: self.ce.regressor_list.resizeColumnsToContents())
    configuration.regressors.dataChanged.connect(lambda idx1,idx2: self.ce.regressor_list.horizontalHeader().setStretchLastSection(True))
    configuration.regressors.dataChanged.connect(lambda idx1,idx2: self.ce.regressor_count.setText(f'There are <strong>{len(configuration.regressors)}</strong> regressors in this configuration'))


    self.ce.setEnabled(True)
    self.ce.deselect_all()

  def update_predictand_info(self, idx, type_):
    dataset = app.datasets[self.ce.predictand_field.currentIndex()]

    if type_ == 'predictand':
      self.filter_method_model.setFilterString(dataset)
      self.filter_units_model.setFilterString(dataset, self.ce.predictand_method_field.currentText())
      self.ce.predictand_unit_field.setCurrentText(dataset.display_unit.__list_form__())
    elif type_ == 'method':
      method = self.ce.predictand_method_field.currentText()
      self.filter_units_model.setFilterString(dataset, method)
      if not ('MCM' in method) and not ('KAF' in method):
        self.ce.predictand_unit_field.setCurrentText(dataset.display_unit.__list_form__())
    else:
      return


  def store_configuration(self, configuration_idx=None):
    if not configuration_idx:
      configuration_idx = self.mt.config_list.selectionModel().selectedRows()[0].row()
    config = app.model_configurations[configuration_idx]

    # Store the metadata
    config.name = self.ce.name_field.text()
    config.comment = self.ce.comment_field.toPlainText()
    config.issue_date = self.ce.issue_date_field.date().toPyDate()
    config.training_start_date = self.ce.training_start_field.date().toPyDate()
    config.training_end_date = self.ce.training_end_field.date().toPyDate()
    if self.ce.exclude_check.isChecked():
      config.training_exclude_dates = list(map(lambda y: int(y.strip()), self.ce.exclude_years_field.text().split(',')))
    else:
      config.training_exclude_dates = []
    
    # Predictand
    idx = self.ce.predictand_field.currentIndex()
    config.predictand.dataset_guid = app.datasets.data(app.datasets.index(idx), Qt.UserRole+2).guid
    config.predictand.preprocessing = self.ce.predictand_preprocessing_field.currentText()
    config.predictand.agg_method = self.ce.predictand_method_field.currentText()
    config.predictand.period_start = self.ce.predictand_period_start_field.date().toPyDate()
    config.predictand.period_end = self.ce.predictand_period_end_field.date().toPyDate()
    idx = self.ce.predictand_unit_field.currentIndex()
    idx = self.filter_units_model.mapToSource(self.filter_units_model.index(idx, 0))
    config.predictand.unit = app.units[idx.row()]

    app.model_configurations[configuration_idx] = config
    self.ce.summary_field.setText(config.__simple_target_string__())

  def gen_button_pressed(self):
    
    configuration_idx = self.mt.config_list.selectionModel().selectedRows()[0].row()
    config = app.model_configurations[configuration_idx]
    mv = GenModelDialog.GenModelDialog(config)
    

  def open_view_data(self, dataset_idx=None):
    
    self.store_configuration()
    configuration_idx = self.mt.config_list.selectionModel().selectedRows()[0].row()

    if not dataset_idx:
      sel = self.ce.predictor_list.selectionModel().currentIndex()
      if sel.isValid:
        dataset_idx = sel.row()
      else:
        dataset_idx = 0
    dv = ResampledDataViewer.DataViewer(configuration_idx, dataset_idx)
    dv.exec()
  

  def open_predictor_view(self):
    conf = self.mt.config_list.selectionModel().currentIndex().row()
    conf_id = app.model_configurations[conf].guid
    pv = PredictorView.PredictorView(app, conf_id)
    pv.exec()

  def open_regressor_view(self):
    conf = self.mt.config_list.selectionModel().currentIndex().row()
    conf_id = app.model_configurations[conf].guid
    pv = RegressorView.RegressorView(conf_id)
    pv.exec()

