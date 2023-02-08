from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPicture, QPainter
import pandas as pd
import numpy as np
from Utilities.HydrologyDateTimes import convert_to_water_year, current_water_year
from inspect import signature
from collections import OrderedDict
import pyqtgraph as pg
from Utilities import Scatterplot
from Views import ExceedanceViewer, ForecastExperimentalFeatures

app = QApplication.instance()

class readOnlyLineEdit(QLineEdit):
  def __init__(self):
    QLineEdit.__init__(self)
    self.setReadOnly(True)
  def setText(self, a0):
    QLineEdit.setText(self, a0)
    self.setCursorPosition(0)

class resizingTextEdit(QTextEdit):
  def __init__(self):
    QTextEdit.__init__(self)
    self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
  def setText(self, a0):
    QTextEdit.setText(self, a0)


class ForecastViewer(QDialog):

  def __init__(self, fcst_idx):

    QDialog.__init__(self)
    self.setWindowTitle('Forecast Viewer')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))
    self.fcst_idx = fcst_idx
    self.model = app.saved_models[fcst_idx.row()]
    self.regression_algorithm = app.regressors[self.model.regression_model](cross_validation = self.model.cross_validator)
    self.setUI2()
    self.setForecast()
    self.forecast_year_select.valueChanged.connect(self.plot_forecast_for_view)
    self.plot_forecast_for_view(self.forecast_year_select.value())
    self.view_exceedance_button.pressed.connect(self.open_exceedances)

  def open_exceedances(self):
    forecasts = self.model.forecasts
    year = self.forecast_year_select.value()
    if year in forecasts.forecasts.index.get_level_values(0):
      values = forecasts.forecasts.loc[(year), 'Value']
      e = ExceedanceViewer.ExceedanceViewer(values)
      e.exec()


  def plot_forecast_for_view(self, year):
    forecasts = self.model.forecasts

    if isinstance(self.model_plots_ft.sp.items[-1], RectItem):
      self.model_plots_ft.sp.removeItem(self.model_plots_ft.sp.items[-1])
    if isinstance(self.model_plots_ft.tp.items[-1], RectItem):
      self.model_plots_ft.tp.removeItem(self.model_plots_ft.tp.items[-1])
    

    if year in forecasts.forecasts.index.get_level_values(0):
      fcst = forecasts.get_10_30_50_70_90(year)
      scatterItem = RectItem((fcst[0], fcst[4]), (fcst[4], fcst[0]))
      self.model_plots_ft.sp.addItem(scatterItem)
      tsItem = RectItem((year-0.5, fcst[4]), (year+0.5, fcst[0]))
      self.model_plots_ft.tp.addItem(tsItem)
    else:
      fcst = [np.nan, np.nan, np.nan, np.nan, np.nan]
    
    
    self.forecast_10.setText(f'{fcst[0]:0.4g} {self.model.predictand.unit.id}')
    self.forecast_30.setText(f'{fcst[1]:0.4g} {self.model.predictand.unit.id}')
    self.forecast_50.setText(f'{fcst[2]:0.4g} {self.model.predictand.unit.id}')
    self.forecast_70.setText(f'{fcst[3]:0.4g} {self.model.predictand.unit.id}')
    self.forecast_90.setText(f'{fcst[4]:0.4g} {self.model.predictand.unit.id}')
    app.processEvents()

    return
  
  def view_resampled_data(self, idx=-1):
    return

  def setForecast(self):

    self.name_edit.setText(self.model.name)
    self.comment_edit.setText(self.model.comment)
    self.regression_line.setText(self.model.regression_model)
    self.cross_validation_line.setText(self.model.cross_validator)
    training_text = f'{self.model.training_period_start:%b %Y} - {self.model.training_period_end:%b %Y}'
    if len(self.model.training_exclude_dates)>0:
      datestr = ', '.join(list(map(str, self.model.training_exclude_dates)))
      training_text += f' excluding {datestr}'
    self.training_line.setText(training_text)
    self.issue_line.setText(self.model.issue_date.strftime('%B %d'))
    self.target_name_line.setText(self.model.predictand.dataset.__str__())
    self.target_parameter_line.setText(self.model.predictand.dataset.parameter)
    self.target_period_line.setText(self.model.predictand.__period_str__())
    self.target_aggregation_line.setText(self.model.predictand.agg_method)
    self.target_preprocessing_line.setText(self.model.predictand.preprocessing)
    self.target_name_line_2.setText(self.model.predictand.dataset.__str__())
    self.target_parameter_line_2.setText(self.model.predictand.dataset.parameter)
    self.target_period_line_2.setText(self.model.predictand.__period_str__())
    self.target_aggregation_line_2.setText(self.model.predictand.agg_method)
    self.target_preprocessing_line_2.setText(self.model.predictand.preprocessing)

    # PRedictors
    p_text = ''
    for i, predictor in enumerate(self.model.predictors):
      p_text += f'<li><strong>X{i+1}: {predictor.dataset.name}</strong><br>' + \
        f'{predictor.dataset.parameter} [{predictor.unit}]<br>' + \
        f'{predictor.__period_str__()} {predictor.agg_method}<br>' + \
        f'Pre-processing: {predictor.preprocessing}</li><br>'
    self.predictor_area.setHtml(f'<ul>{p_text}</ul>')

    # Fit the model
    df = pd.DataFrame()
    for predictor in self.model.predictors:
      df = pd.concat([df, predictor.data], axis=1)
    df = pd.concat([df, self.model.predictand.data], axis=1).sort_index()
    df = df.loc[convert_to_water_year(self.model.training_period_start):convert_to_water_year(self.model.training_period_end)].dropna()
    df = df.drop(self.model.training_exclude_dates, errors='ignore')
    years = list(df.index)
    x_data = df.values[:,:-1]
    predictand_data = df.values[:, -1]
    y_a = predictand_data

    y_p_cv, y_a_cv = self.regression_algorithm.cross_val_predict(x_data, predictand_data)
    y_p = self.regression_algorithm.predict(x_data)

    method = app.preprocessing_methods['INV_' + self.model.predictand.preprocessing]
    if len(signature(method).parameters)>1:
      y_p_cv = method(y_p_cv,**self.model.predictand.params)
      y_a_cv = method(y_a_cv,**self.model.predictand.params)
      y_p = method(y_p,**self.model.predictand.params)
      y_a = method(y_a,**self.model.predictand.params)
    else:
      y_p_cv = method(y_p_cv)
      y_a_cv = method(y_a_cv)
      y_p = method(y_p)
      y_a = method(y_a)

    self.regression_algorithm.update_params()

    for key, widg in self.model_params.items():
      item = self.regression_algorithm.exposed_params[key]
      if isinstance(item, list) or isinstance(item, np.ndarray):
        t = '\n'.join([f'{i+1}: {val:.5g}' for i, val in enumerate(item)])
      elif isinstance(item, dict) or isinstance(item, OrderedDict):
        t = ''
        for key2, item2 in item.items():
          t += f'{key2}: {item2}\n'
      else:
        t = f'{item:.5g}'
      widg.setText(t)

    for key, widg in self.scorers.items():
      scorer = app.scorers[key]
      widg.setText(f'{scorer(y_p, y_a):.5g}')
    
    self.model_plots.plot_model_data(y_a, y_p, years, units=self.model.predictand.unit.id)
    self.model_plots_ft.plot_model_data(y_a, y_p, years, units=self.model.predictand.unit.id)

    col_names = ['Year', 'Actual', 'Model Fit', 'Error', 'Forecast']
    self.model_fit_table.setColumnCount(5)
    
    self.model_fit_table.setHorizontalHeaderLabels(col_names)

    self.data = []
    for i in range(len(years)):
      year = years[i]
      actual = y_a[i]
      predicted = y_p[i]
      error = actual - predicted
      forecast = self.model.forecasts.get_10_50_90(year)
      if np.isnan(forecast[1]):
        forecast = '-'
      else:
        forecast = f'{forecast[1]:0.5g} ({forecast[0]:0.4g} - {forecast[2]:0.4g})'
      self.data.append([str(year), f'{actual:0.5g}', f'{predicted:0.5g}', f'{error:0.5g}', forecast])

    for year in sorted(list(set(self.model.forecasts.forecasts.index.get_level_values(0)))):
      if year not in years:
        forecast =  self.model.forecasts.get_10_50_90(year)
        if np.isnan(forecast[1]):
          forecast = '-'
        else:
          forecast = f'{forecast[1]:0.5g} ({forecast[0]:0.4g} - {forecast[2]:0.4g})'

        self.data.append([str(year), '-', '-', '-', forecast])
    self.model_fit_table.setRowCount(len(self.data))
    for i in range(len(self.data)):

      for j, col in enumerate(col_names):
        item = QTableWidgetItem(self.data[i][j])
        self.model_fit_table.setItem(i, j, item)



  def setUI2(self):

    self.tw = QTabWidget()

    overviewTab = QWidget()
    targetPredictorsTab = QWidget()
    forecastsTab = QWidget()
    self.experimentalTab = ForecastExperimentalFeatures.ExperimentalFeatures()

    self.tw.addTab(overviewTab, 'Overview')
    self.tw.addTab(targetPredictorsTab, 'Target and Predictors')
    self.tw.addTab(forecastsTab, 'Forecasts')
    self.tw.addTab(self.experimentalTab, 'Experimental')

    ll = QVBoxLayout()
    ll.addWidget(self.tw)
    self.setLayout(ll)

    # OVERVIEW TAB

    layout = QGridLayout()

    self.save_button = QPushButton('Save Changes')

    self.name_edit = QLineEdit()
    self.comment_edit = resizingTextEdit()
    self.regression_line = readOnlyLineEdit()
    self.cross_validation_line = readOnlyLineEdit()
    self.training_line = readOnlyLineEdit()
    self.issue_line = readOnlyLineEdit()

    self.target_name_line = readOnlyLineEdit()
    self.target_period_line = readOnlyLineEdit()
    self.target_aggregation_line = readOnlyLineEdit()
    self.target_preprocessing_line = readOnlyLineEdit()
    self.target_parameter_line = readOnlyLineEdit()

    self.scorers = {}
    for scorer in app.scorers.keys():
      self.scorers[scorer] = readOnlyLineEdit()

    self.model_plots = ModelPlots()

    layout.addWidget(QLabel("Model Overview", objectName="HeaderLabel"), 0, 0, 1, 2)
    flayout = QFormLayout()
    flayout.addRow('Name', self.name_edit)
    flayout.addRow('Comments', self.comment_edit)
    flayout.addRow('Regression Algorithm', self.regression_line)
    flayout.addRow('Cross Validation', self.cross_validation_line)
    flayout.addRow('Training Data', self.training_line)
    flayout.addRow('Issue Date', self.issue_line)
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)
    flayout.addRow(frame)
    flayout.addRow(QLabel('Target Info'))
    flayout.addRow(QLabel("Dataset"), self.target_name_line)
    flayout.addRow(QLabel("Parameter"), self.target_parameter_line)
    flayout.addRow(QLabel("Period"), self.target_period_line)
    flayout.addRow(QLabel("Aggregation"), self.target_aggregation_line)
    flayout.addRow(QLabel("Preprocessing"), self.target_preprocessing_line)
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)
    flayout.addRow(frame)

    flayout.addRow(QLabel("Model Score"))
    for scorer, widg in self.scorers.items():
      flayout.addRow(scorer, widg)

    layout.addLayout(flayout, 1, 0, 1, 1)
    layout.addWidget(self.model_plots, 1, 1, 1, 1)
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(self.save_button)
    layout.addLayout(hlayout, 2, 0, 1, 2)

    overviewTab.setLayout(layout)

    # TARGET AND PREDICTOR TAB
    self.target_name_line_2 = readOnlyLineEdit()
    self.target_period_line_2 = readOnlyLineEdit()
    self.target_aggregation_line_2 = readOnlyLineEdit()
    self.target_preprocessing_line_2 = readOnlyLineEdit()
    self.target_parameter_line_2 = readOnlyLineEdit()
    self.target_view_data_button = QPushButton('View Data')

    self.predictor_area = QTextEdit()

    self.model_params = {}
    for param in self.regression_algorithm.exposed_params.keys():
      self.model_params[param] = resizingTextEdit()
      self.model_params[param].setReadOnly(True)

    layout2 = QGridLayout()
    layout2.addWidget(QLabel("Forecast Target and Predictors", objectName='HeaderLabel'), 0, 0, 1, 2)
    flayout2 = QFormLayout()
    flayout2.addRow(QLabel('Target Info'))
    flayout2.addRow(QLabel("Dataset"), self.target_name_line_2)
    flayout2.addRow(QLabel("Parameter"), self.target_parameter_line_2)
    flayout2.addRow(QLabel("Period"), self.target_period_line_2)
    flayout2.addRow(QLabel("Aggregation"), self.target_aggregation_line_2)
    flayout2.addRow(QLabel("Preprocessing"), self.target_preprocessing_line_2)
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setLineWidth(2)
    flayout2.addRow(frame)
    flayout2.addRow(QLabel("Model Parameters"))
    for param, widg in self.model_params.items():
      flayout2.addRow(param, widg)
    layout2.addLayout(flayout2, 1, 0)
    vlayout2 = QVBoxLayout()
    vlayout2.addWidget(QLabel("Predictors"))
    vlayout2.addWidget(self.predictor_area)
    layout2.addLayout(vlayout2, 1, 1)
    targetPredictorsTab.setLayout(layout2)

    # FORECASTS TAB
    self.model_fit_table = QTableWidget() 
    self.model_fit_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.model_fit_table.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.model_plots_ft = ModelPlots()
    self.view_exceedance_button = QPushButton("View Forecast Exceedance")
    self.forecast_year_select = QSpinBox()
    self.forecast_year_select.setMinimum(1900)
    self.forecast_year_select.setMaximum(current_water_year())
    self.forecast_year_select.setValue(current_water_year())
    self.forecast_10 = QLineEdit()
    self.forecast_10.setReadOnly(True)
    self.forecast_30 = QLineEdit()
    self.forecast_30.setReadOnly(True)
    self.forecast_50 = QLineEdit()
    self.forecast_50.setReadOnly(True)
    self.forecast_70 = QLineEdit()
    self.forecast_70.setReadOnly(True)
    self.forecast_90 = QLineEdit()
    self.forecast_90.setReadOnly(True)

    layout3 = QHBoxLayout()
    splitter = QSplitter(Qt.Horizontal)
    vboxLayout = QVBoxLayout()
    vboxLayout.addWidget(QLabel("Model Fit Information"))
    vboxLayout.addWidget(self.model_fit_table)
    w = QWidget()
    w.setLayout(vboxLayout)
    splitter.addWidget(w)
    vlayout = QVBoxLayout()
    vlayout.addWidget(QLabel("Forecasts"))
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(QLabel('Select Forecast Year'))
    hlayout.addWidget(self.forecast_year_select)
    vlayout.addLayout(hlayout)
    vlayout.addWidget(self.model_plots_ft)
    hlayout = QHBoxLayout()
    hlayout.addWidget(QLabel("90% : "))
    hlayout.addWidget(self.forecast_10)
    hlayout.addWidget(QLabel("70% : "))
    hlayout.addWidget(self.forecast_30)
    hlayout.addWidget(QLabel("50% : "))
    hlayout.addWidget(self.forecast_50)
    hlayout.addWidget(QLabel("30% : "))
    hlayout.addWidget(self.forecast_70)
    hlayout.addWidget(QLabel("10% : "))
    hlayout.addWidget(self.forecast_90)
    vlayout.addLayout(hlayout)
    hlayout = QHBoxLayout()
    hlayout.addWidget(self.view_exceedance_button)
    hlayout.addStretch(1)
    vlayout.addLayout(hlayout)
    w2 = QWidget()
    w2.setLayout(vlayout)
    splitter.addWidget(w2)
    layout3.addWidget(splitter)

    forecastsTab.setLayout(layout3)









class ModelPlots(pg.GraphicsLayoutWidget):

  def __init__(self):
    pg.GraphicsLayoutWidget.__init__(self)
    self.sp = Scatterplot.ScatterPlot()
    self.ep = Scatterplot.ScatterPlot()
    self.tp = Scatterplot.ScatterPlot2(line=True)
    [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(4)]
    self.addItem(self.sp, row=0, col=0, rowspan=2)
    self.addItem(self.ep, row=2, col=0)
    self.addItem(self.tp, row=3, col=0)

    self.sp.sp.sigHovered.connect(lambda points, ev: self.hoverConnect(points, ev, 'sp'))
    self.ep.sp.sigHovered.connect(lambda points, ev: self.hoverConnect(points, ev, 'ep'))
    self.tp.sp.sigHovered.connect(lambda points, ev: self.hoverConnect(points, ev, 'tp1'))
    self.tp.sp2.sigHovered.connect(lambda points, ev: self.hoverConnect(points, ev, 'tp2'))

  def hoverConnect(self, points, ev, plot):

    
    if plot == 'ep':
      old = self.sp.sp.data['hovered']
      old = old & self.tp.sp.data['hovered']
      old = old & self.tp.sp2.data['hovered']
      new = points.data['hovered']

      self.sp.sp.data['sourceRect'][old^new] = 0
      self.sp.sp.data['hovered'] = new
      self.sp.sp.updateSpots()
      self.tp.sp.data['sourceRect'][old^new] = 0
      self.tp.sp.data['hovered'] = new
      self.tp.sp.updateSpots()
      self.tp.sp2.data['sourceRect'][old^new] = 0
      self.tp.sp2.data['hovered'] = new
      self.tp.sp2.updateSpots()

    elif plot == 'tp1':
      old = self.ep.sp.data['hovered']
      old = old & self.sp.sp.data['hovered']
      old = old & self.tp.sp2.data['hovered']
      new = points.data['hovered']

      self.ep.sp.data['sourceRect'][old^new] = 0
      self.ep.sp.data['hovered'] = new
      self.ep.sp.updateSpots()
      self.sp.sp.data['sourceRect'][old^new] = 0
      self.sp.sp.data['hovered'] = new
      self.sp.sp.updateSpots()
      self.tp.sp2.data['sourceRect'][old^new] = 0
      self.tp.sp2.data['hovered'] = new
      self.tp.sp2.updateSpots()
    
    elif plot == 'tp2':
      old = self.ep.sp.data['hovered']
      old = old & self.sp.sp.data['hovered']
      old = old & self.tp.sp.data['hovered']
      new = points.data['hovered']

      self.ep.sp.data['sourceRect'][old^new] = 0
      self.ep.sp.data['hovered'] = new
      self.ep.sp.updateSpots()
      self.sp.sp.data['sourceRect'][old^new] = 0
      self.sp.sp.data['hovered'] = new
      self.sp.sp.updateSpots()
      self.tp.sp.data['sourceRect'][old^new] = 0
      self.tp.sp.data['hovered'] = new
      self.tp.sp.updateSpots()

    else:
      old = self.ep.sp.data['hovered']
      old = old & self.tp.sp.data['hovered']
      old = old & self.tp.sp2.data['hovered']
      new = points.data['hovered']

      self.ep.sp.data['sourceRect'][old^new] = 0
      self.ep.sp.data['hovered'] = new
      self.ep.sp.updateSpots()
      self.tp.sp.data['sourceRect'][old^new] = 0
      self.tp.sp.data['hovered'] = new
      self.tp.sp.updateSpots()
      self.tp.sp2.data['sourceRect'][old^new] = 0
      self.tp.sp2.data['hovered'] = new
      self.tp.sp2.updateSpots()
  
  def plot_model_data(self, actual, predicted, years, units=None):
    rg = max(actual) - min(actual)
    x = [min(actual)-rg/5, max(actual) + rg/5]
    y = x
    
    self.sp.plot_data(x=actual, y=predicted, data=years)
    self.sp.setLabel('bottom', f'Actual ({units})')
    self.sp.setLabel('left', f'Predicted ({units})')
       
    self.sp.plot(x, y, pen=pg.mkPen({'color':'#FF0000', "width":2.5}))

    self.ep.plot_data(x=years, y=actual-predicted)
    self.ep.setLabel('left', f'Actual - Predicted ({units})')

    self.ep.plot([years[0]-1, years[-1]+1], [0, 0],  pen=pg.mkPen({'color':'#FF0000', "width":2.5}))
    self.ep.setRange(xRange=(years[0]-1, years[-1]+1), yRange=(-1.1*np.max(np.abs(actual-predicted)),1.1*np.max(np.abs(actual-predicted))))

    self.tp.plot_data(x=years, y=actual,y2=predicted, name='Actual', name2='Predicted')
    self.tp.setLabel('left', f'Forecast [{units}]')

    #self.tp.setRange(xRange=(years[0]-1, years[-1]+1), yRange=(0.9*min(min(predicted), min(actual)),1.1*max(max(predicted), max(actual))))

# class RectItem(pg.QtGui.QGraphicsRectItem):
#     def __init__(self, topLeft, bottomRight):
#         width = bottomRight[0] - topLeft[0]
#         height = topLeft[1] - bottomRight[1]
#         pg.QtGui.QGraphicsRectItem.__init__(self, topLeft[0], topLeft[1], width, height)
#         self.setPos(topLeft[0], topLeft[1])
#         self.setZValue(30)
#         self.setPen(pg.mkPen('k'))
#         self.setBrush(pg.mkBrush('r'))

class RectItem(pg.GraphicsObject):
    def __init__(self, topLeft, bottomRight):
        pg.GraphicsObject.__init__(self)
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.setZValue(8)
        self.generatePicture()
    
    def generatePicture(self):
        ## pre-computing a QPicture object allows paint() to run much more quickly, 
        ## rather than re-drawing the shapes every time.
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('k'))
        w = (self.bottomRight[0] - self.topLeft[0])
        h = (self.bottomRight[1]- self.topLeft[1])
        p.setBrush(pg.mkBrush('#ff221188'))
        p.drawRect(QRectF(self.topLeft[0], self.topLeft[1], w, h))
        p.end()
    
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    
    def boundingRect(self):
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QRectF(self.picture.boundingRect())

        

