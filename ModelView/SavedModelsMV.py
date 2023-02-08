from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime
import pandas as pd
import numpy as np
from Utilities.HydrologyDateTimes import convert_to_water_year
from Utilities.ColorCycler import ColorCycler
from Views import ForecastViewer, ExceedanceViewer
from scipy.interpolate import InterpolatedUnivariateSpline
from inspect import signature

app = QApplication.instance()


class SavedModelsModelView:

  def __init__(self):

    self.sm = app.gui.SavedModelsTab
    self.grouped = pd.DataFrame([])
    self.forecast_proxy_model = QSortFilterProxyModel()
    self.forecast_proxy_model.setSourceModel(app.saved_models)
    self.forecast_proxy_model.setFilterRole(Qt.UserRole + 2)
    self.sm.model_list.setModel(self.forecast_proxy_model)
    app.saved_models.dataChanged.connect(self.update_combo_box)
    self.sm.issue_combo.currentIndexChanged.connect(self.change_dates)
    self.issue_dates = []
    self.sm.model_list.remove_action.triggered.connect(self.remove_model)
    self.sm.model_list.generate_forecast_action.triggered.connect(self.gen_forecast)
    self.sm.model_list.open_action.triggered.connect(self.open_model)
    self.sm.model_list.doubleClicked.connect(self.open_model)
    self.sm.model_list.selectionModel().selectionChanged.connect(self.plot_forecast)
    self.sm.year_select.valueChanged.connect(lambda i: self.plot_forecast(None,None))
    self.sm.export_values_button.pressed.connect(self.view_exceedances)
  
  def view_exceedances(self):
    if not self.grouped.empty:
      e = ExceedanceViewer.ExceedanceViewer(self.grouped)
      e.exec()

  
  def open_model(self, _=None):
    selection = self.sm.model_list.selectionModel().selectedRows()[0]
    real_idx = self.forecast_proxy_model.mapToSource(selection)
    f = ForecastViewer.ForecastViewer(real_idx)
    f.exec()
    return
  
  def plot_forecast(self, new_selection, _):
    selection = self.sm.model_list.selectionModel().selectedRows()
    real_idx = [self.forecast_proxy_model.mapToSource(i) for i in selection]
    year = self.sm.year_select.value()
    df = pd.DataFrame()
    self.sm.prob_plot.clear()
    cc = ColorCycler()
    for idx in real_idx:
      model = app.saved_models[idx.row()]
      self.sm.prob_plot.setLabel('bottom', f'{model.predictand.dataset.parameter} [{model.predictand.unit.id}]')
      if year in model.forecasts.forecasts.index.get_level_values(0):
        values = model.forecasts.forecasts.loc[(year, slice(None))]
        df = pd.concat([df, values], axis=1)
        values = values['Value']
        spl = InterpolatedUnivariateSpline(values.values, list(values.index), k=2)
        xs = np.linspace(values.min(), values.max(), 1000)
        spl_d = spl.derivative()
        self.sm.prob_plot.plot_data(xs, spl_d(xs), color=cc.next(), label=model.name)        

    grouped = df.mean(axis=1)
    if not grouped.empty:
      if len(real_idx)>1:
        spl = InterpolatedUnivariateSpline(grouped.values, list(grouped.index), k=2)
        xs = np.linspace(grouped.min(), grouped.max(), 1000)
        spl_d = spl.derivative()
        self.sm.prob_plot.plot_data(xs, spl_d(xs), color=cc.next(), width=3, label='Combined')
      self.grouped = grouped
      vals = grouped.loc[[0.1,0.3,0.5,0.7,0.9]].values
      self.sm._10_value.setText(vals[0], model.predictand.unit.id)
      self.sm._30_value.setText(vals[1], model.predictand.unit.id)
      self.sm._50_value.setText(vals[2], model.predictand.unit.id)
      self.sm._70_value.setText(vals[3], model.predictand.unit.id)
      self.sm._90_value.setText(vals[4], model.predictand.unit.id)
      self.sm.prob_plot.plot_vlines(vals)
        
      


  def gen_forecast(self):
    idx = self.sm.model_list.selectionModel().selectedRows()
    real_idx = [self.forecast_proxy_model.mapToSource(i) for i in idx]
    
    self.gen_for_dialog = genModelDialog(real_idx)
    self.gen_for_dialog.last_year.connect(self.sm.year_select.setValue)
    self.gen_for_dialog.finished.connect(lambda _: self.plot_forecast(None,None))
    self.gen_for_dialog.exec()

  def remove_model(self):
    idx = self.sm.model_list.selectionModel().selectedRows()
    real_idxs = [self.forecast_proxy_model.mapToSource(i) for i in idx]
    
    for i, idx_ in enumerate(real_idxs):
      app.saved_models.remove_model(idx_.row()-i)
  
  def change_dates(self, row):
    if row>=0:
      currentData = self.sm.issue_combo.currentData()
      if currentData:
        self.forecast_proxy_model.setFilterFixedString(currentData.strftime('%B %d'))
      else:
        print()


  def update_combo_box(self, idx0, idx1):
    current_text = self.sm.issue_combo.currentText()
    self.issue_dates = []
    self.sm.issue_combo.clear()
    for model in app.saved_models.saved_models:
      if model.issue_date not in self.issue_dates:
        self.issue_dates.append(model.issue_date)
    self.issue_dates = list(set(self.issue_dates))
    if len(self.issue_dates)==0:
      return
    if not self.issue_dates[0]:
      return
    self.issue_dates.sort()
    for d in self.issue_dates:
      self.sm.issue_combo.addItem(d.strftime('%B %d'), d)
    if current_text != '':
      if datetime.strptime(current_text, '%B %d') in self.issue_dates:
        self.sm.issue_combo.setCurrentText(current_text)
    self.change_dates(0)




class genModelDialog(QDialog):
  last_year = pyqtSignal(int)
  def __init__(self, idx_list):

    QDialog.__init__(self)
    self.setUI()
    self.idx_list = list(set(idx_list))
    self.gen_button.pressed.connect(self.generate_forecasts)
    self.prog_bar.setMaximum(100)
    self.year_ = 2000
    self.setMinimumWidth(500)

  def resample_all_data(self, model):
    self.log_box.appendPlainText(' -> regenerating predictor data')
    app.processEvents()
    for predictor in model.predictors:
      predictor.resample()
    model.predictand.resample()

  def parse_years(self, input):
    output = []
    years = input.split(',')
    for year in years:
      if '-' in year:
        low, high = year.split('-')
        output = output + list(range(int(low), int(high)+1))
      else:
        output.append(int(year))
    output.sort()
    return output

  def generate_forecasts(self):

    fcst_years = self.parse_years(self.year_input.text())
    self.year_ = fcst_years[-1]
    total = len(self.idx_list)*len(fcst_years)
    inc = 100/total

    for i, idx in enumerate(self.idx_list):
      
      
      model = app.saved_models[idx.row()]
      self.log_box.appendPlainText('----------------------------------------------')
      self.log_box.appendPlainText(f'Generating forecasts for model: {model.name}')
      app.processEvents()
      self.resample_all_data(model)

      for fcst_year in fcst_years:
        self.log_box.appendPlainText(f'   -> Generating forecasts for year: {fcst_year}')
      
        
        self.prog_bar.setValue(self.prog_bar.value()+inc/2)
        app.processEvents()
        
        regression_algorithm = app.regressors[model.regression_model](cross_validation = model.cross_validator)
        df = pd.DataFrame()
        for predictor in model.predictors:
          df = pd.concat([df, predictor.data], axis=1)
        df = pd.concat([df, model.predictand.data], axis=1).sort_index()
        x_fcst_year = df.loc[fcst_year]
        x_fcst_year = x_fcst_year.iloc[:-1].values
        df = df.loc[convert_to_water_year(model.training_period_start):convert_to_water_year(model.training_period_end)].dropna()
        df = df.drop(model.training_exclude_dates, errors='ignore')

        # Dont train on the year we're trying to forecast
        if fcst_year in df.index:
          df = df.drop(fcst_year)

        x_data = df.values[:,:-1]
        predictand_data = df.values[:, -1]

        n = x_data.shape[0] # num samples
        n_bootstraps = 100
        bootstrap_predictions, validation_residuals = np.empty(n_bootstraps), []
        
        for b in range(n_bootstraps):
          if b==50:
            self.prog_bar.setValue(self.prog_bar.value()+inc/2)
            app.processEvents()
          train_idxs = np.random.choice(range(n), size=n, replace=True)
          val_idxs = np.array([idx for idx in range(n) if idx not in train_idxs])
          _, _ = regression_algorithm.cross_val_predict(x_data[train_idxs, :], predictand_data[train_idxs])
          preds = regression_algorithm.predict(x_data[val_idxs])
          validation_residuals.append(predictand_data[val_idxs]-preds)
          bootstrap_predictions[b] = regression_algorithm.predict(x_fcst_year)
        bootstrap_predictions -= np.mean(bootstrap_predictions)
        validation_residuals = np.concatenate(validation_residuals)

        _, _ = regression_algorithm.cross_val_predict(x_data, predictand_data)
        predictions = regression_algorithm.predict(x_data)
        forecast = regression_algorithm.predict(x_fcst_year)
        train_residuals = predictand_data - predictions

        validation_residuals = np.percentile(validation_residuals, q=np.arange(100), method='linear')
        train_residuals = np.percentile(train_residuals, q=np.arange(100), method='linear')

        no_information_error = np.mean(np.abs(np.random.permutation(predictand_data) - np.random.permutation(predictions)))
        generalisation = np.abs(validation_residuals.mean() - train_residuals.mean())
        no_information_val = np.abs(no_information_error - train_residuals)
        relative_overfitting_rate = np.mean(generalisation / no_information_val)
        weight = .632 / (1 - .368 * relative_overfitting_rate)
        residuals = (1 - weight) * train_residuals + weight * validation_residuals
        C = np.array([m + o for m in bootstrap_predictions for o in residuals])
        qs = list(range(1, 100, 1))
        percentiles = np.percentile(C, q = qs) + forecast
        

        method = app.preprocessing_methods['INV_' + model.predictand.preprocessing]
        if len(signature(method).parameters)>1:
          percentiles = method(percentiles,**model.predictand.params)
         
        else:
          percentiles = method(percentiles)
          
        
        model.forecasts.set_forecasts_1_99(fcst_year, percentiles)
        app.processEvents()

    self.finish()

  def finish(self):
    self.last_year.emit(self.year_)
    self.done(0)

  def setUI(self):

    layout = QVBoxLayout()

    self.setWindowTitle('Generate Forecasts')

    self.gen_button = QPushButton("Generate Forecasts")
    self.year_input = QLineEdit()
    self.prog_bar = QProgressBar()
    self.year_input.setPlaceholderText('e.g. "2023" or "2011-2014" or "2003, 2004, 2006"')
    self.log_box = QPlainTextEdit(objectName='monospace')

    layout.addWidget(QLabel('What years should we forecast?'))
    layout.addWidget(self.year_input)
    layout.addWidget(self.prog_bar)
    layout.addWidget(self.log_box)
    layout.addWidget(self.gen_button)

    self.setLayout(layout)