from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from Models.Units import Unit
from Resources import Dataloaders
from uuid import uuid4
import pandas as pd
import pickle

# Get the global application
app = QApplication.instance()

# Rich Text for Rich-Text formatted listviews
DATASET_LIST_RICH_TEXT = """
  <style>
  .light {{
    font-size:8pt;
    color: gray;
    font-weight:100;
  }}
  .big {{
    color: #0e67a9;
    font-weight: bold;
    font-size:large;
  }}
  .bold {{
    font-weight: bold;
  }}
  table td {{
    overflow: hidden;
    display: inline-block;
    whitespace: nowrap;
    font-size:medium;
  }}
  
  </style>
  <div width="100%" class="big">{name}</div>
  <table cellpadding="2" cellspacing="0" width="100%" border="0">
  <tr><td width="120" class="bold">ID:</td><td>{external_id}</td></tr>
  <tr><td width="120" class="bold">Agency:</td><td>{agency}</td></tr>
  <tr><td width="120" class="bold">Parameter:</td><td>{parameter}</td></tr>
  <tr><td width="120" class="bold">Unit:</td><td>{display_unit.name}</td></tr>
  </table>
  <div width="100%" class="light" align="right">{guid}</div>
 
  
""".replace('\n', '')

class Dataset:

  is_file_import = False
  file_path = ""
    
  def __init__(self, **kwargs):

    # Dataset parameters
    self.guid = str(uuid4())
    self.external_id = ''
    self.agency = ''
    self.name = ''
    self.parameter = ''
    self.param_code = ''
    self.dataloader = None
    self.raw_unit = Unit()
    self.display_unit = Unit()
    self.data = pd.Series(index=pd.DatetimeIndex([]), name=self.guid, dtype=float)
    
    # Load in all args and kwargs into the dataset definition
    self.__dict__.update(**kwargs)
    
    return

  def convert_to(self, new_unit):

    scale, offset = self.display_unit.convert_to(new_unit)
    self.data = self.data*scale + offset
    self.display_unit = new_unit

  def __condensed_form__(self):
    id = f'{f"{self.external_id:8.8}" if len(self.external_id)<=8 else f"{self.external_id:5.5}"+ "..."}'
    name = f'{f"{self.name:30.30}" if len(self.name)<=30 else f"{self.name:27.27}"+ "..."}'
    param = f'{f"{self.parameter:13.13}" if len(self.parameter)<=13 else f"{self.parameter:10.10}"+ "..."}'
    return " ".join(f'{id}: {name} | {param}'.split())

  def __rich_text__(self):
    return DATASET_LIST_RICH_TEXT.format(**self.__dict__)

  def __export_form__(self):
    return f'{self.external_id}: {self.name} - {self.parameter}'
  
  def __str__(self):
    return f"{self.external_id}: {self.name}"

  def __repr__(self):
    return f'<Dataset {self.guid} name={self.name} parameter={self.parameter}/>'
  
  def __eq__(self, comp_dataset):
    if comp_dataset.external_id == self.external_id:
      if comp_dataset.name == self.name:
        if comp_dataset.param_code == self.param_code:
          if comp_dataset.parameter == self.parameter:
            return True
    return False


class Datasets(QAbstractListModel):

  # Define model roles
  id_role = Qt.UserRole + 1 # Returns the dataset GUID
  obj_role = Qt.UserRole + 2 # Returns the dataset object
  rich_text_role = Qt.UserRole + 3

  def __init__(self):

    QAbstractListModel.__init__(self)
    self.datasets = []

    return

  def columnCount(self, parent):
    return 2

  def clear(self):

    self.datasets = []
    QAbstractListModel.__init__(self)
    
  def data(self, index, role=Qt.DisplayRole):

    row = index.row()
    dataset = self.datasets[row]
    if role == self.id_role:
      return dataset.guid
    if role == self.obj_role:
      return dataset
    if role == Qt.DisplayRole:
      return dataset.__condensed_form__()
    if role == self.rich_text_role:
      return dataset.__rich_text__()

    return
    
  def rowCount(self, parent=QModelIndex()):
    return len(self.datasets)
  
  def roleNames(self):
    return {
      self.id_role : b'id',
      self.obj_role: b'object',
      self.rich_text_role : b'rich_text'
    }

  def get_dataset_by_guid(self, guid):

    for dataset in self.datasets:
      if dataset.guid == guid:
        return dataset

  def update_dataset_by_guid(self, guid, new_dataset):

    for i, dataset in enumerate(self.datasets):
      if dataset.guid == guid:
        self.datasets[i] = new_dataset
        self.dataChanged.emit(self.index(i), self.index(i))
        print(f'Updated Dataset: {new_dataset}')
        return


  def add_dataset(self, *args, **kwargs):

    if not 'raw_unit' in kwargs:

      kwargs['raw_unit'] = app.units.get_unit('-')
      kwargs['display_unit'] = app.units.get_unit('-')
    
    

    if not 'dataloader' in kwargs:
      kwargs['dataloader'] = app.dataloaders['-']['CLASS']()
      
    dataset = Dataset(**kwargs)
    if dataset in self.datasets:
      return None
    self.datasets.append(dataset)
    self.insertRow(self.rowCount())
    
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))  
    print(f'Added dataset: {dataset}')
    return dataset

  def remove_dataset(self, *args, **kwargs):

    if 'guid' in kwargs:
      dataset = self.get_dataset_by_guid(kwargs['guid'])
      self.remove_dataset(dataset)
      return

    if isinstance(args[0], Dataset):

      dataset = args[0]
      idx = self.datasets.index(dataset)
      dataset = self.datasets.pop(idx)
      self.removeRow(idx)  
      print(f'Removed Dataset: {dataset}')
    
    elif isinstance(args[0], int):
      
      idx = args[0]
      dataset = self.datasets.pop(idx)
      self.removeRow(idx) 
      print(f'Removed Dataset: {dataset}')
  
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))    
    

    return
  
  def clear_all(self):
    for dataset in self.datasets:
      self.remove_dataset(dataset)
    self.dataChanged.emit(self.index(0), self.index(0))

  

  def __getitem__(self, index):
    return self.datasets[index]

  def __setitem__(self, index, **kwargs):
    self.datasets[index] = Dataset(**kwargs)

  def __len__(self):
    return len(self.datasets)
  
  def __contains__(self, dataset):
    return (dataset in self.datasets)