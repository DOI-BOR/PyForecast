from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QIcon
import pyqtgraph as pg
import numpy as np
from datetime import datetime
from Models.SavedModels import Model
from Utilities.Scatterplot import ScatterPlot
from Utilities.ModelGenerator import ModelGenerator
import pandas as pd
from Utilities.HydrologyDateTimes import convert_to_water_year
from jinja2 import Environment, FileSystemLoader
from inspect import signature

app = QApplication.instance()


class PossibleModels(QAbstractTableModel):

  def __init__(self, scorers=None):

    QAbstractTableModel.__init__(self)
    self.models = []
    self.scorers=scorers
  
  def headerData(self, section, orientation, role):
    if role == Qt.DisplayRole:
      if section == 0 and orientation == Qt.Horizontal:
        return 'Algorithm'
      if section == 1 and orientation == Qt.Horizontal:
        return 'Genome'
      if section > 1 and orientation == Qt.Horizontal:
        return f'Score ({self.scorers[section-2]})'
    return QVariant()

  def data(self, index, role):
    model = self.models[index.row()]
    if role == Qt.DisplayRole:
      if index.column() == 0:
        r = model.regressor
        return QVariant(f'{r.regression_model} / {r.scoring_metric}')
      if index.column() == 1:
        return QVariant(''.join([u'\u25cf' if b else u'\u25cc' for b in model.genome]))
      if index.column() > 1:
        if model.scorer == self.scorers[index.column()-2]:
          return QVariant(f'{model.score:0.6g}')
        else:
          return QVariant('-')


    if role == Qt.UserRole + 1:
      if index.column() == 0:
        return self.data(index, role=Qt.DisplayRole)
      if index.column() == 1:
        return QVariant(sum(v<<i for i, v in enumerate(self.models[index.row()].genome[::-1])))
      if index.column() > 1:
        if model.scorer == self.scorers[index.column()-2]:
          return QVariant(model.score)
        else:
          return QVariant(np.nan)
    return QVariant()

  def rowCount(self, parent=QModelIndex()):
    return len(self)

  def columnCount(self, parent=QModelIndex()):
    return 2 + len(self.scorers)

  def append(self, model):
    self.models.append(model)
    self.insertRow(len(self)-1)
    
  def insertRows(self, position, rows, parent=QModelIndex()):
    self.beginInsertRows(parent, position, position+rows-1)
    self.endInsertRows()
    return True

  def refresh(self):
    
    self.dataChanged.emit(self.index(0,0), self.index(len(self)-1, self.columnCount()))
    app.processEvents()

  def __len__(self):
    return len(self.models)

  def __getitem__(self, index):
    return self.models[index]

class FilterTable(QSortFilterProxyModel):

  def __init__(self):

    QSortFilterProxyModel.__init__(self)
    self.setSortRole(Qt.UserRole + 1)
  
  def lessThan(self, left, right):
    if left.column() == right.column():
      left_data = left.data(Qt.UserRole + 1)
      right_data = right.data(Qt.UserRole + 1)
      return left_data < right_data
    return QSortFilterProxyModel.lessThan(self, left, right)



class GenModelDialog(QDialog):

  def __init__(self, config=None):

    QDialog.__init__(self)
    self.setUI()
    self.config = config

    # Get unique scorers
    scorers = []
    for r in self.config.regressors.regressors:
      if r.scoring_metric not in scorers:
        scorers.append(r.scoring_metric)

    self.possible_models = PossibleModels(scorers=scorers)
    self.model_list_p = FilterTable()
    self.model_list_p.setSourceModel(self.possible_models)
    self.model_list.setModel(self.model_list_p)
    self.model_list.setSortingEnabled(True)
    self.model_list.selectionModel().currentRowChanged.connect(self.set_model)

    self.mg = ModelGenerator(self.config)
    self.mg.updateTextSignal.connect(self.prog_text.setText)
    self.mg.updateProgSignal.connect(self.model_progress_bar.setValue)
    self.mg.newModelSignal.connect(self.possible_models.append)
    self.mg.updateTextSignal.connect(lambda x: app.processEvents())
    self.mg.updateProgSignal.connect(lambda x: app.processEvents())
    
    self.mg.finished.connect(self.model_search_finished)

    self.save_button.pressed.connect(self.save_model)

    self.mg.start()
    
    self.exec()
  
  def closeEvent(self, ev):
    self.mg.stop()
    QDialog.closeEvent(self, ev)

    
  def model_search_finished(self):
    print("Finished model search")
    self.model_progress_bar.setValue(100)
    self.possible_models.refresh()
    self.model_progress_bar.setFormat('100%')
    self.model_list.resizeColumnsToContents()
    

  def save_model(self):
    row = self.model_list.selectionModel().selectedIndexes()[0]
    row = self.model_list_p.mapToSource(row)
    model = self.possible_models[row.row()]
    saved_model = Model(
      regression_model = model.regression_model,
      cross_validator = model.cross_validator,
      predictors = model.predictors,
      predictand = model.predictand,
      training_period_start = model.training_period_start,
      training_period_end = model.training_period_end,
      training_exclude_dates = model.training_exclude_dates,
      issue_date = model.issue_date,
      name = model.name if model.name != '' else f'NewModel{len(app.saved_models)}',
      comment = model.comment if model.comment != '' else f'Saved by {app.current_user} on {datetime.now():%Y-%b-%d %H:%M}'
    )
    app.saved_models.append(saved_model)

  def setUI(self):


    self.setWindowTitle('Generated Models')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    self.status_bar = QStatusBar(objectName='monospace')
    self.model_list = QTableView()
    self.model_list.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.model_list.setSelectionMode(QAbstractItemView.SingleSelection)
    self.model_plots = ModelPlots()
    self.model_info = QTextEdit()
    self.model_info.setReadOnly(True)
    self.model_info.setMinimumWidth(400)
    self.prog_text = QLabel(objectName='monospace')
    self.model_progress_bar = QProgressBar()
    self.model_progress_bar.setFormat("Finding models...")
    self.model_progress_bar.setMaximum(100)
    self.save_button = QPushButton('Save Model')

    layout = QVBoxLayout()
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(self.save_button)

    layout.addLayout(hlayout)

    splitter = QSplitter()
    splitter.addWidget(self.model_plots)
    splitter.addWidget(self.model_info)

    layout.addWidget(splitter)

    layout.addWidget(self.model_list)
    layout.addWidget(self.status_bar)

    self.status_bar.addWidget(self.model_progress_bar, 1)
    self.status_bar.addWidget(self.prog_text)
    self.status_bar.setSizeGripEnabled(False)

    self.setLayout(layout)

  def set_model(self, new_row, _):
    row = self.model_list_p.mapToSource(new_row)
    model = self.possible_models[row.row()]
    regression_algorithm = app.regressors[model.regression_model](cross_validation = model.cross_validation)
    df = pd.DataFrame()
    for predictor in model.predictors:
      df = pd.concat([df, predictor.data], axis=1)
    df = pd.concat([df, model.predictand.data], axis=1).sort_index()
    df = df.loc[convert_to_water_year(self.config.training_start_date):convert_to_water_year(self.config.training_end_date)].dropna()
    df = df.drop(self.config.training_exclude_dates, errors='ignore')
    years = list(df.index)
    x_data = df.values[:,:-1]
    predictand_data = df.values[:, -1]
    y_a = predictand_data

    y_p_cv, y_a_cv = regression_algorithm.cross_val_predict(x_data, predictand_data)
    y_p = regression_algorithm.predict(x_data)

    method = app.preprocessing_methods['INV_' + model.predictand.preprocessing]
    if len(signature(method).parameters)>1:
      y_p_cv = method(y_p_cv,**model.predictand.params)
      y_a_cv = method(y_a_cv,**model.predictand.params)
      y_p = method(y_p,**model.predictand.params)
      y_a = method(y_a,**model.predictand.params)
    else:
      y_p_cv = method(y_p_cv)
      y_a_cv = method(y_a_cv)
      y_p = method(y_p)
      y_a = method(y_a)

    scores = []
    for metric, func in app.scorers.items():
      if metric == model.regressor.scoring_metric:
        scores.append((metric+' Cross Validated', model.score))
        scores.append((metric, func(y_p, y_a)))
      else:
        scores.append((metric+' Cross Validated', func(y_p_cv, y_a_cv)))
        scores.append((metric, func(y_p, y_a)))

    regression_algorithm.update_params()
    param_dict = regression_algorithm.exposed_params

    self.model_plots.plot_model_data(y_a, y_p, years, units=model.predictand.unit.id)
    environment = Environment(loader=FileSystemLoader(app.base_dir + '/Resources/templates/'))
    template = environment.get_template("PossibleModelTemplate.html")
    content = template.render(
      model = model,
      genome =  ''.join([u'\u25cf' if b else u'\u25cc' for b in model.genome]),
      scores=scores,
      param_dict = param_dict
    )
    self.model_info.setHtml(content)
  
class ModelPlots(pg.GraphicsLayoutWidget):

  def __init__(self):
    pg.GraphicsLayoutWidget.__init__(self)
    self.sp = ScatterPlot()
    self.ep = ScatterPlot()
    [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(3)]
    self.addItem(self.sp, row=0, col=0, rowspan=2)
    self.addItem(self.ep, row=2, col=0)

    self.sp.sp.sigHovered.connect(lambda points, ev: self.hoverConnect(points, ev, 'sp'))
    self.ep.sp.sigHovered.connect(lambda points, ev: self.hoverConnect(points, ev, 'ep'))

  def hoverConnect(self, points, ev, plot):

    
    if plot == 'ep':
      old = self.sp.sp.data['hovered']
      new = points.data['hovered']

      self.sp.sp.data['sourceRect'][old^new] = 0
      self.sp.sp.data['hovered'] = new
      self.sp.sp.updateSpots()
    else:
      old = self.ep.sp.data['hovered']
      new = points.data['hovered']

      self.ep.sp.data['sourceRect'][old^new] = 0
      self.ep.sp.data['hovered'] = new
      self.ep.sp.updateSpots()
    

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

if __name__ == '__main__':
  import sys
  app = QApplication(sys.argv)
  t = GenModelDialog()
  t.show()
  sys.exit(app.exec_())