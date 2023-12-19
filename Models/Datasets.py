"""
Datasets.py

Datasets.py stores the classes that contain and display information 
about the daily-resolution datasets in the forecast file.

A "Dataset" is a class that stores the metadata about a dataset (e.g. name,
id, agency, file_path, etc), as well as the daily time series data for that
dataset (in this case, a pandas series object containing the data.)

"Datasets" is a QAbstractListModel that stores multiple datasets and 
displays those datasets in lists and drop-down views.
"""


from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from Models.Units import Unit
from uuid import uuid4
import pandas as pd

# Get the global application
app = QApplication.instance()

# Rich Text for Rich-Text formatted listviews
DATASET_LIST_RICH_TEXT = """
  <style>
  
  .big {{
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
  table {{
    margin-top: 4px;
  }}
  
  </style>
  <table cellpadding="2" cellspacing="0" width="100%" border="0">
  <tr><td colspan="2" class="big">{name2}</td></tr><hr>
  <tr><td width="120" class="bold">ID:</td><td>{external_id}</td></tr>
  <tr><td width="120" class="bold">Agency:</td><td>{agency}</td></tr>
  <tr><td width="120" class="bold">Parameter:</td><td>{parameter}</td></tr>
  <tr><td width="120" class="bold">Unit:</td><td>{display_unit.name}</td></tr>
  </table>
 
  
"""

def color(dataset):
  """Assigns a color to a dataset depending on the dataset agency"""

  if dataset.agency == 'USGS':
    return 'green'
  elif 'USBR' in dataset.agency:
    return 'blue'
  elif 'NRCS' in dataset.agency:
    return 'purple'
  else:
    return 'red'


class Dataset:
  """Dataset Class

  This class stores the metadata and time-series data for a dataset in the 
  forecast file. 

  Class Members:
  "is_file_import" (`bool`) : Dictates whether PyForecast should try to load 
                              this data from a file, as opposed to a dataloader
  "file_path" (`string`) :    contains the file path to the CSV that contains 
                              time series data for this dataset.

  Class Variables:
  "guid" : simple UUID4 that uniquely identifies this dataset
  "external_id" : the ID associated with this location used in external API's
                  (e.g. a USGS stream gage ID)
  "agency": The agency that maintains the data for this dataset
  "name": The dataset's display name
  "parameter" : the parameter for this dataset ('e.g. streamflow)
  "param_code" : the code used by external API's for this parameter (e.g. 00060
                 for USGS streamflow)
  "raw_unit" : An instance of a `Unit` that correlates to the data unit that gets
               downloaded from the API or flat file
  "display_unit": an instance of a `Unit` that is the unit displayed and used 
                  in the forecasts.
  "data" : A pandas Series object containing the data for this dataset.

  """
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
  
  def raw_convert(self):

    scale, offset = self.raw_unit.convert_to(self.display_unit)
    self.data = self.data*scale + offset
    

  def convert_to(self, new_unit):
    """
    Converts the dataset's unit to a new unit.
    """

    scale, offset = self.display_unit.convert_to(new_unit)
    self.data = self.data*scale + offset
    self.display_unit = new_unit


  def __condensed_form__(self):
    """
    Creates a condensed string containing information about the dataset
    """
    id = f'{f"{self.external_id:8.8}" if len(self.external_id)<=8 else f"{self.external_id:5.5}"+ "..."}'
    name = f'{f"{self.name:30.30}" if len(self.name)<=30 else f"{self.name:27.27}"+ "..."}'
    param = f'{f"{self.parameter:13.13}" if len(self.parameter)<=13 else f"{self.parameter:10.10}"+ "..."}'
    return " ".join(f'{id}: {name} | {param}'.split())


  def __rich_text__(self):
    """
    Creates rich text containing info about the dataset, used in displays like
    ListViews.
    """
    self.name2 = ''
    counter = 0
    for n in self.name:
      if n == ' ' and counter > 24:
        counter = 0
        self.name2 += '<br>'
      else:
        self.name2 += n
        counter += 1
    
    self.name2 = self.name2.title()
    
    self.name2 = f'<span style="color:{color(self)}">' + self.name2 + '</span>'

    return DATASET_LIST_RICH_TEXT.format(**self.__dict__)


  def __export_form__(self):
    """
    Another condensed form of the dataset, used in exported outputs
    """
    return f'{self.external_id}: {self.name} - {self.parameter}'
  

  def __str__(self):
    """
    Simple string Representation of the dataset
    """
    return f"{self.external_id}: {self.name}"


  def __repr__(self):
    """
    String used to represent the dataset in the terminal console.
    """
    return f'<Dataset {self.guid} name={self.name} parameter={self.parameter}/>'
  

  def __eq__(self, comp_dataset):
    """
    Checks for equality between this dataset and another dataset
    based on ID, name, parameter, and param_code
    """
    if comp_dataset.external_id == self.external_id:
      if comp_dataset.name == self.name:
        if comp_dataset.param_code == self.param_code:
          if comp_dataset.parameter == self.parameter:
            return True
    return False


class Datasets(QAbstractListModel):

  """
  Datasets Class

  This class is a subclass of a QT5.QAbstractListModel which
  stores Dataset objects in a structured model that can 
  be directly accessed by QT5 views such as listviews or 
  tableviews.
  """

  # Define model roles
  id_role = Qt.UserRole + 1 # Returns the dataset GUID
  obj_role = Qt.UserRole + 2 # Returns the dataset object
  rich_text_role = Qt.UserRole + 3

  def __init__(self):

    QAbstractListModel.__init__(self)
    self.datasets = [] # Stores datasets in an internal list

    return

  def columnCount(self, parent):
    """Returns the number of model columns"""
    return 2


  def clear(self):
    """Clears all datasets from the model and re-initializes the model"""
    self.datasets = []
    QAbstractListModel.__init__(self)
    

  def data(self, index, role=Qt.DisplayRole):
    """Retrieves data from the model, given an index and role"""
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

    return QVariant()
    

  def rowCount(self, parent=QModelIndex()):
    """Returns the number of datasets in the model"""
    return len(self.datasets)
  
  
  def roleNames(self):
    """Returns names for each role in the model"""
    return {
      self.id_role : b'id',
      self.obj_role: b'object',
      self.rich_text_role : b'rich_text'
    }
  

  def get_dataset_by_name_and_parameter(self, name, param):
    """retrieves a dataset from the model that matches the given name and parameter"""
    for dataset in self.datasets:
      if dataset.name.upper() == name.upper():
        if dataset.parameter.upper() in param.upper():
          return dataset


  def get_dataset_by_guid(self, guid):
    """Retrieves a dataset from the model that matches the given UUID"""
    for dataset in self.datasets:
      if dataset.guid == guid:
        return dataset
      

  def update_dataset_by_guid(self, guid, new_dataset):
    """Changes the dataset for the given UUID to the new dataset provided"""
    for i, dataset in enumerate(self.datasets):
      if dataset.guid == guid:
        self.datasets[i] = new_dataset
        self.dataChanged.emit(self.index(i), self.index(i))
        print(f'Updated Dataset: {new_dataset}')
        return

  def update_dataset_display_units(self, dataset, new_units):
    dataset_idx = self.datasets.index(dataset)
    self.datasets[dataset_idx].convert_to(new_units)
    self.dataChanged.emit(self.index(dataset_idx), self.index(dataset_idx))

  def add_dataset(self, *args, **kwargs):
    """
    add_dataset adds a new dataset to the model. all "kwargs" are 
    passed to the Dataset Object before the dataset is added.
    """
    
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
    """remove_dataset removes a dataset from the model given certain
    arguments. 

    if 'guid' is given as a kwarg: removes the dataset with that guid
    if the first argument is a dataset, removes that dataset from the model
    if the first argument is an integer, removes that index from the model.

    """

    if 'guid' in kwargs:
      dataset = self.get_dataset_by_guid(kwargs['guid'])
      self.remove_dataset(dataset)
      return

    if isinstance(args[0], Dataset):

      dataset = args[0]
      idx = self.datasets.index(dataset)
      self.beginRemoveRows(QModelIndex(), idx, idx)
      dataset = self.datasets.pop(idx)
      self.removeRow(idx)  
      self.endRemoveRows()
      print(f'Removed Dataset: {dataset}')
    
    elif isinstance(args[0], int):
      
      idx = args[0]
      self.beginRemoveRows(QModelIndex(), idx, idx)
      dataset = self.datasets.pop(idx)
      self.removeRow(idx) 
      self.endRemoveRows()
      print(f'Removed Dataset: {dataset}')
  
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))    
    

    return
  

  def clear_all(self):
    j=0
    for i in range(len(self.datasets)):
      dataset = self.datasets[i-j]
      self.remove_dataset(dataset)
      j+=1
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))

  

  # Convienence Functions 
  def __getitem__(self, index):
    return self.datasets[index]

  def __setitem__(self, index, **kwargs):
    self.datasets[index] = Dataset(**kwargs)

  def __len__(self):
    return len(self.datasets)
  
  def __contains__(self, dataset):
    return (dataset in self.datasets)