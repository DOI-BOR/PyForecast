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
from pathos.multiprocessing import ThreadingPool as Pool
from math import factorial

app = QApplication.instance()


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    
    window_size = np.abs(window_size)
    order = np.abs(order)
   
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

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
    self.sm.plot_select.clicked.connect(lambda b: self.plot_forecast(None, None))
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
  
  def plot_forecast(self, new_selection, _,):
    plot_type = 'pdf'
    if self.sm.plot_select.isChecked():
      plot_type = 'cdf'
    selection = self.sm.model_list.selectionModel().selectedRows()
    real_idx = [self.forecast_proxy_model.mapToSource(i) for i in selection]
    year = self.sm.year_select.value()
    df = None
    self.sm.prob_plot.clear()
    cc = ColorCycler()
    for idx in real_idx:
      model = app.saved_models[idx.row()]
      self.sm.prob_plot.setLabel('bottom', f'{model.predictand.dataset().parameter} [{model.predictand.unit.id}]')
      if year in model.forecasts.forecasts.index.get_level_values(0):
        values = model.forecasts.forecasts.loc[(year, slice(None))]
        if df is not None:
          df = pd.concat([df, values], axis=1)
        else:
          df = pd.concat([values], axis=1)
        values = values['Value']
        spl = InterpolatedUnivariateSpline(values.values, list(values.index), k=3)
        
        xs = np.linspace(values.min(), values.max(), 1000)
        spl_d = spl.derivative()
        if plot_type == 'pdf':
          ys = savitzky_golay(spl_d(xs), 63, 4, 0)
          self.sm.prob_plot.plot_data(xs, ys, color=cc.next(), label=model.name) 
        else:
          self.sm.prob_plot.plot_data(xs, spl(xs), color=cc.next(), label=model.name)       

    grouped = df.mean(axis=1)
    if not grouped.empty:
      if len(real_idx)>1:
        spl = InterpolatedUnivariateSpline(grouped.values, list(grouped.index), k=3)
        xs = np.linspace(grouped.min(), grouped.max(), 1000)
        spl_d = spl.derivative()
        if plot_type =='pdf':
          ys = savitzky_golay(spl_d(xs), 63, 4, 0)
          self.sm.prob_plot.plot_data(xs, ys, color=cc.next(), width=3, label='Combined')
        else:
          self.sm.prob_plot.plot_data(xs, spl(xs), color=cc.next(), width=3, label='Combined')
      self.grouped = grouped
      vals = grouped.loc[[0.1,0.3,0.5,0.7,0.9]].values
      self.sm._10_value.setText(vals[0], model.predictand.unit.id)
      self.sm._30_value.setText(vals[1], model.predictand.unit.id)
      self.sm._50_value.setText(vals[2], model.predictand.unit.id)
      self.sm._70_value.setText(vals[3], model.predictand.unit.id)
      self.sm._90_value.setText(vals[4], model.predictand.unit.id)
      self.sm.prob_plot.plot_vlines(vals)
    self.sm.prob_plot.reframe_to_min_max_normal(
      model.predictand.data.min(),
      model.predictand.data.max(),
      model.normal
    )
        
      


  def gen_forecast(self):
    idx = self.sm.model_list.selectionModel().selectedRows()
    real_idx = [self.forecast_proxy_model.mapToSource(i) for i in idx]
    
    self.gen_for_dialog = genModelDialog(real_idx)
    self.gen_for_dialog.last_year.connect(self.sm.year_select.setValue)
    self.gen_for_dialog.finished.connect(lambda _: self.plot_forecast(None,None))
    self.gen_for_dialog.finished.connect(lambda _: self.sm.updateListSize())
    self.gen_for_dialog.show()

  def remove_model(self):
    current_issue_date = self.sm.issue_combo.currentData()
    cidx = self.sm.issue_combo.currentIndex()

    idx = self.sm.model_list.selectionModel().selectedRows()
    real_idxs = [self.forecast_proxy_model.mapToSource(i) for i in idx]
    models = [app.saved_models[idx_.row()] for idx_ in real_idxs]
    
    for m in models:
      app.saved_models.remove_model(m)
    
    if current_issue_date in self.issue_dates:
        self.sm.issue_combo.setCurrentIndex(cidx)

  
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
    self.setModal(True)
    
    self.idx_list = list(set(idx_list))
    self.setUI()
    self.gen_button.pressed.connect(self.generate_forecasts)
    self.year_ = 2000
    self.setMinimumWidth(500)
  
  def closeEvent(self, a0):
    self.finish()
    QDialog.closeEvent(self, a0)

  def resample_all_data(self, model):
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

    for i in range(len(self.idx_list)):
      idx = self.idx_list[i]
      model = app.saved_models[idx.row()]
      app.processEvents()
      self.labels[i].setMessage('Resampling Data...')
      self.resample_all_data(model)
      for y, fcst_year in enumerate(fcst_years):
        self.labels[i].setMessage(f'Forecasting for year: {fcst_year}')
        
        regression_algorithm = app.regressors[model.regression_model](cross_validation = model.cross_validator)
        df = pd.DataFrame()
        for predictor in model.predictors:
          df = pd.concat([df, predictor.data], axis=1)
        df = pd.concat([df, model.predictand.data], axis=1).sort_index()
        if fcst_year not in df.index:
          msg = QMessageBox(self)
          msg.setIcon(QMessageBox.Warning)
          msg.setText('We do not have all the data yet for year: ' + str(fcst_year))
          msg.setWindowTitle('Error in Generating Forecast')
          msg.setStandardButtons(QMessageBox.Ok)
          
          retv= msg.exec()
          self.labels[i].setMessage(f'Could not forecast for year: {fcst_year} - Missing data')
          continue
        x_fcst_year = df.loc[[fcst_year]].iloc[0].iloc[:-1]
        if x_fcst_year.dropna().empty:
          msg = QMessageBox(self)
          msg.setIcon(QMessageBox.Warning)
          msg.setText('We do not have all the data yet for year: ' + str(fcst_year))
          msg.setWindowTitle('Error in Generating Forecast')
          msg.setStandardButtons(QMessageBox.Ok)
          
          retv= msg.exec()
          self.labels[i].setMessage(f'Could not forecast for year: {fcst_year} - Missing data')
          continue
        x_fcst_year = x_fcst_year.values
        df = df.loc[convert_to_water_year(model.training_period_start):convert_to_water_year(model.training_period_end)].dropna()
        df = df.drop(model.training_exclude_dates, errors='ignore')

        # Dont train on the year we're trying to forecast
        if fcst_year in df.index:
          df = df.drop(fcst_year)

        x_data = df.values[:,:-1]
        predictand_data = df.values[:, -1]

        n = x_data.shape[0] # num samples
        n_bootstraps = 300 # Must be a multiple of 10
        bootstrap_predictions, validation_residuals = np.empty(n_bootstraps), []
        
        for b in range(n_bootstraps):
          self.labels[i].setMessage(f'Year: {fcst_year} → Bootstrapping: {b+1:>4} / {n_bootstraps:>4}')
          total_prog = len(fcst_years)*n_bootstraps
          current_prog = b + (y*n_bootstraps)
          self.labels[i].setProgress(current_prog/total_prog)
          self.update()
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
        qs = np.arange(1,100,0.25)
        percentiles = np.percentile(C, q = qs) + forecast
        

        method = app.preprocessing_methods['INV_' + model.predictand.preprocessing]
        if len(signature(method).parameters)>1:
          percentiles = method(percentiles,**model.predictand.params)
          
        else:
          percentiles = method(percentiles)
        
        model.forecasts.set_forecasts_1_99(fcst_year, percentiles)
    self.last_year.emit(self.year_)
    self.finished.emit(1)
    app.processEvents()

  def finish(self):
    
    self.last_year.emit(self.year_)
    
    #self.finished.emit()
    self.done(0)

  def setUI(self):

    layout = QVBoxLayout()

    self.setWindowTitle('Generate Forecasts')

    self.labels = []


    self.gen_button = QPushButton("Generate Forecasts")
    self.year_input = QLineEdit()
    self.year_input.setPlaceholderText('e.g. "2023" or "2011-2014" or "2003, 2004, 2006"')
    
    self.scrollarea = QScrollArea()
    w = QWidget()
    l = QVBoxLayout()
    for i, idx in enumerate(self.idx_list):
      model = app.saved_models[idx.row()]
      label = ForecastGenLabel(model.name)
      self.labels.append(label)
      l.addWidget(label)
    w.setLayout(l)
    self.scrollarea.setWidget(w)
    self.scrollarea.setWidgetResizable(True)

    layout.addWidget(QLabel('What years should we forecast?'))
    layout.addWidget(self.year_input)
    layout.addWidget(self.scrollarea)
    layout.addWidget(self.gen_button)

    self.setLayout(layout)

class ForecastGenLabel(QLabel):
  
  def __init__(self, modelName):
    QLabel.__init__(self)
    self.setStyleSheet('border: 1px solid black')
    self.prog = 0.002
    self.setProgress(self.prog)
    self.modelName = modelName
    self.setText(f'<strong>{modelName}</strong><br>Ready to forecast')
  def setMessage(self, message):
    self.setText(f'<strong>{self.modelName}</strong><br>{message}') 
    self.update()
    app.processEvents()
  def setProgress(self, prog):
    if prog >= 1:
      prog = 0.999999
    if prog <= 0.002:
      prog = 0.002
    self.prog = prog
    self.setStyleSheet(f"""border: 1px solid black; padding: 10px;
    background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 #9deb9d, stop:{self.prog-0.001} #9deb9d, stop:{self.prog} white, stop:1 white)
    """)
    self.update()
    app.processEvents()
