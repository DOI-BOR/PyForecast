import uuid
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pandas as pd
import numpy as np
import pickle
from Models.ModelConfigurations import ResampledDataset
from datetime import datetime

# Get the global application
app = QApplication.instance()

RICH_TEXT = """<style>
  .title {{
    font-size: small;
    background-color: #e0e0e0;
    font-weight: bold;
    border: 1px solid black;
    padding: 5px
  }}
  .big {{
    font-size: large;
  }}
  .high {{
    background-color: skyblue
  }}
  .normal {{
    background-color: aquamarine
  }}
  .low {{
    background-color: pink
  }}
  .border_right {{
    border-right: 1px solid black;
  }}
  body {{
    font-family: arial;
    font-weight: bold;
  }}
  span {{
    margin: 5px
  }}
  table {{
    margin: 0px;
    padding: 3px;
  }}
</style>
<table width="100%" border="0">
  <tr><td colspan="2" class="title">Name</td></tr>
  <tr><td colspan="2" class="big">{name}</td></tr>
  <tr><td colspan="2" class="title">Recent Forecasts</td></tr>
  {fcst_text}
</table>
"""

class Model:

  def __init__(self, **kwargs):

    self.regression_model = None
    self.cross_validator = None
    self.predictors = None
    self.predictand = None
    self.training_period_start = None
    self.training_period_end = None
    self.training_exclude_dates = []
    self.issue_date = None
    self.name = ""
    self.comment = ""
    self.forecasts = ForecastList(self)

    # Load in all args and kwargs into the dataset definition
    self.guid = str(uuid.uuid4())
    self.__dict__.update(**kwargs)

    
    

    return
  
  def __rich_text__(self):
    if self.forecasts.forecasts.empty:
      fcsts = [('-', "<td class='big'>no forecasts yet...</td>"),('','<td></td>'),('','<td></td>')]
    else:
      fcsts = [('-', "<td class='big'>no forecasts yet...</td>"),('','<td></td>'),('','<td></td>')]
      years = list(self.forecasts.forecasts.index.get_level_values(0).unique())
      years.sort()
      years.reverse()
      for i, year in enumerate(years[:3]):
        _10,_50,_90 = self.forecasts.get_10_50_90(year)
        low, normal, high = np.quantile(self.predictand.data.values, [0.3, 0.5, 0.7])
        if not _50:
          sym = "<td class='big'>Unable to generate forecast for this year...</td>"
        else:
          sym = f"<td class='big'>{_50:.2f} {self.predictand.unit.id}"
          if _50 <= low:
            sym += f" <span class='low'>&nbsp;({int(100*_50/normal)}% of normal)&nbsp;</span></td>"
          elif _50 >= high:
            sym += f" <span class='high'>&nbsp;({int(100*_50/normal)}% of normal)&nbsp;</span></td>"
          else:
            sym += f" <span class='normal'>&nbsp;({int(100*_50/normal)}% of normal)&nbsp;</span></td>"
        fcsts[i]=(year, sym)
      self.normal = normal

    fcst_text = ''
    for fcst in fcsts:
      if fcst[0] != "":
        fcst_text += f"<tr><td class='big border_right'>{fcst[0]}</td>{fcst[1]}</tr>"


    content = RICH_TEXT.format(fcst_text = fcst_text, **self.__dict__)

    return content

class ForecastList(object):

  def __init__(self, model = None):
 
    self.forecasts = pd.DataFrame(
      index=pd.MultiIndex(
        levels=[[],[]],
        codes=[[],[]],
        names=['Year', 'Exceedence']
      ),
      columns=['Value']
    )


  def set_forecasts_1_99(self, year, values):
    idx = [(year, round(i,4)) for i in np.arange(0.01, 1, 0.0025)]
    data = pd.DataFrame(
      index = pd.MultiIndex.from_tuples(idx, names=('Year', 'Exceedence')),
      columns = ['Value'],
      data = values
    )
    self.forecasts = pd.concat([self.forecasts, data])
    self.forecasts = self.forecasts[~self.forecasts.index.duplicated(keep='last')]
    self.forecasts.sort_index(inplace=True)

  def get_10_50_90(self, year):
    if year in self.forecasts.index.get_level_values(0):
      values = self.forecasts.loc[(year), 'Value']
      if values.empty:
        return np.nan, np.nan, np.nan
      if 0.1 in values.index and 0.9 in values.index and 0.5 in values.index:
        return float(values.loc[0.1]),float(values.loc[0.5]),float(values.loc[0.9])
      else:
        q = np.quantile(values, [0.1, 0.5, 0.9])
        return q[0],q[1],q[2]
    else:
      return np.nan, np.nan, np.nan
  
  def get_10_30_50_70_90(self, year):
    if year in self.forecasts.index.get_level_values(0):
      values = self.forecasts.loc[(year), 'Value']
      if values.empty:
        return np.nan, np.nan, np.nan, np.nan, np.nan
      if 0.1 in values.index and 0.3 in values.index and 0.9 in values.index and 0.5 in values.index and 0.7 in values.index:
        return float(values.loc[0.1]),float(values.loc[0.3]),float(values.loc[0.5]),float(values.loc[0.7]),float(values.loc[0.9])
      else:
        q = np.quantile(values, [0.1, 0.3, 0.5, 0.7, 0.9])
        return q[0],q[1],q[2], q[3], q[4]
    else:
      return np.nan, np.nan, np.nan

class SavedModelList(QAbstractListModel):
  
  dataRole = Qt.UserRole + 1
  filterRole = Qt.UserRole + 2
  richTextRole = Qt.UserRole + 3

  def __init__(self):
    QAbstractListModel.__init__(self)
    self.saved_models = []

  def rowCount(self, parent=QModelIndex):
    return len(self.saved_models)
  
  def list_forecast_years(self):
    years = []
    for m in self.saved_models:
      y = list(set(m.forecasts.forecasts.index.get_level_values(0)))
      years = years + y
    years.sort()
    return list(set(years))
  
  def data(self, index=QModelIndex(), role=Qt.DisplayRole):
    if index.isValid():
      model = self.saved_models[index.row()]
      
      if role == self.dataRole:
        return model
      if role == self.filterRole:
        return model.issue_date.strftime("%B %d")
      if role == Qt.DisplayRole:
        return model.guid
      if role == self.richTextRole:
        return model.__rich_text__()
    return QVariant()
  
  def save_to_file(self, f):
    pickle.dump(len(self), f, 4)
    for i in range(len(self)):
      model = self.saved_models[i]
      pickle.dump(model.guid, f, 4)
      pickle.dump(model.regression_model, f, 4)
      pickle.dump(model.cross_validator, f, 4)
      pickle.dump(len(model.predictors), f, 4)
      for p in model.predictors:
        pickle.dump(p, f, 4)
      pickle.dump(model.predictand, f, 4)
      pickle.dump(model.training_period_start, f, 4)
      pickle.dump(model.training_period_end, f, 4)
      pickle.dump(model.training_exclude_dates, f, 4)
      pickle.dump(model.issue_date, f, 4)
      pickle.dump(model.name, f, 4)
      pickle.dump(model.comment, f, 4)
      pickle.dump(model.forecasts.forecasts, f, 4)
    return

  def load_from_file(self, f):
    num_models = pickle.load(f)
    for i in range(num_models):
      guid = pickle.load(f)
      regression_model = pickle.load(f)
      cross_validator = pickle.load(f)
      num_predictors = pickle.load(f)
      predictor_pool = []
      for j in range(num_predictors):
        p = pickle.load(f)
        p.dataset_guid = p.dataset.guid
        del p.dataset
        p = ResampledDataset(**p.__dict__)
        predictor_pool.append(p)
      
      predictand = pickle.load(f)
      predictand.dataset_guid = predictand.dataset.guid
      del predictand.dataset
      predictand = ResampledDataset(**predictand.__dict__)
      training_period_start = pickle.load(f)
      training_period_end = pickle.load(f)
      training_exclude_dates = pickle.load(f)
      issue_date = pickle.load(f)
      name = pickle.load(f)
      comment = pickle.load(f)
      forecasts = pickle.load(f)
      model = Model(
        regression_model = regression_model,
        cross_validator = cross_validator,
        predictors = predictor_pool,
        predictand = predictand,
        training_period_start = training_period_start,
        training_period_end = training_period_end,
        training_exclude_dates = training_exclude_dates,
        issue_date = issue_date,
        name = name,
        comment = comment,
        guid = guid
      )
      model.forecasts.forecasts = forecasts
      self.append(model)
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))
    app.SMMV.update_combo_box(None, None)
    return

  def add_model(self, **kwargs):
    model = Model(**kwargs)
    self.append(model)

  def remove_model(self, idx):

    
    if isinstance(idx, int):
      self.beginRemoveRows(QModelIndex(), idx, idx)
      model = self.saved_models.pop(idx)
      self.removeRow(idx)  
      self.endRemoveRows()
      
    elif isinstance(idx, Model):
      idx = self.saved_models.index(idx)
      self.beginRemoveRows(QModelIndex(), idx, idx)
      model = self.saved_models.pop(idx)
      self.removeRow(idx)  
      self.endRemoveRows()

    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))
    app.SMMV.update_combo_box(None, None)
  

  def clear_all(self):
    
    j=0
    for i in range(len(self.saved_models)):
      sm = self.saved_models[i-j]
      self.remove_model(sm)
      j+=1
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))
    app.SMMV.update_combo_box(None, None)

  def append(self, model):
    self.insertRow(self.rowCount())
    self.saved_models.append(model)
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))
    app.SMMV.update_combo_box(None, None)
  
  def insertRows(self, position, rows, parent=QModelIndex()):
    self.beginInsertRows(parent, position, position+rows-1)
    self.endInsertRows()
    return True

  def __len__(self):
    return len(self.saved_models)
  def __getitem__(self, idx):
    return self.saved_models[idx]
  def __setitem__(self, idx, data):
    self.saved_models[idx] = data


