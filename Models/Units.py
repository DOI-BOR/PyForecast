"""
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication

# Get the global application
app = QApplication.instance()


class Unit:
  """ The Unit class contains a description of a single unit, including its 
  id, name, and its association with the SI base unit. 
  """

  def __init__(self, **kwargs):
    """Constructor

    args:
      id (`str`) - short name for the unt (e.g. 'ft')
      name (`str`) - longer name for the unit (e.g. 'feet')
      si_id (`str`) - SI unit for which this unit corresponds (e.g. 'm')
      si_scale (`float`) - scale factor to convert this unit to SI
      si_offset (`float`) - offset to add after scale applied to get to SI value
      type (`str`) - type of physical dimension (e.g. 'length')
    """

    # Instantiate the unit based on constructor arguments
    self.id = ''
    self.name = ''
    self.si_id = ''
    self.si_scale = 1
    self.si_offset = 0
    self.type = 'none'

    self.__dict__.update(**kwargs)

    if not self.si_id:
      self.si_id = self.id
      self.si_scale = 1
      self.si_offset = 0
      self.type = 'none'
    
    return

  def convert_to(self, new_unit):
    """returns a scale and multiplier for converting to the new unit
    """
    if new_unit.si_id != self.si_id:
      raise Exception(f"Error: impossible to convert {self} to {new_unit}")

    return   self.si_scale/new_unit.si_scale, \
            (self.si_offset - new_unit.si_offset) / new_unit.si_scale

  def to_dict(self):
    return {
      'id':self.id, 'name':self.name, 'si_id':self.si_id, 
      'si_scale':self.si_scale, 'si_offset':self.si_offset
    }
  
  def __eq__(self, other_unit):
    return other_unit.id == self.id

  def __str__(self):
    return self.id
  
  def __list_form__(self):
    return f'({self.type}) {self.id} - {self.name}'
  
  def __repr__(self):
    return f'<Unit id="{self.id}", name={self.name}, si_id="{self.si_id}", ' \
       + f'si_scale={self.si_scale:.5f}, si_offset={self.si_offset:.5f}/> '


class Units(QAbstractTableModel):
  """ the Units class stores a list of units currently in the
  application. It extends the QAbstractTableModel to provide a model
  for QTableViews and QComboBox's where necessary.
  """

  def __init__(self):
    """Constructor"""

    # Instantiate the QAbstractTableModel and create a list 
    # data structure to store the application units
    QAbstractTableModel.__init__(self)

    self.units = []
    self.attrs = ['id', 'name', 'si_id', 'si_scale', 'si_offset', 'type']
    
    # Load the units from the application configuration into 
    # the units list. 
    for unit in app.config['default_units']:
      self.add_unit(False, **unit)
    for unit in app.config['user_units']:
      self.add_unit(False, **unit)


  def data(self, index, role):
    """ Gets information for a specific unit in the units list
    corresponding to the index and role provided.
    """
    
    # Check that the index is valid. Note that a col == 6 returns
    # the combo-box string associated with the unit
    row = index.row()
    col = index.column()
    if not index.isValid():
      if col != 6:
        return
    if row >= self.rowCount():
      return QVariant()

    # Get the unit associated with the row
    unit = self.units[row]

    # Return the combo-box string if col == 6
    if col == 6 and role == Qt.DisplayRole:
      return unit.__list_form__()

    # return the data as requested.
    if role == Qt.UserRole + 1:
      return unit
    if role == Qt.DisplayRole:
      return QVariant(getattr(unit, self.attrs[col]))
    
  # Row count returns the number of units in the list
  def rowCount(self, index=QModelIndex()):
    return len(self.units)

  # column count returns 7 columns
  def columnCount(self, index=QModelIndex()):
    return 7

  # returns the header data for views that require a header
  def headerData(self, section, orientation, role):
    if role == Qt.DisplayRole:
      if orientation == Qt.Horizontal:
        return [
          'ID', 'Name', 'Associated SI Unit',
          'SI Scale', 'SI Offset', 'Type',''][section]
      else:
        return str(section+1)

  def add_unit(self, user_added, **kwargs):
    """
    Adds the unit defined by **kwargs to the 
    unit list and updates the model and any associated views
    """

    new_unit = Unit(**kwargs)

    # Check if unit already in list
    if any(unit for unit in self.units if unit.id == new_unit.id):
      print(f"unit {new_unit} already exists")
      return

    # Add new unit to list
    self.units.append(new_unit)
    
    # generate an entry in the config if the unit is a user-defined unit
    if user_added:
      app.config['user_units'].append(new_unit.to_dict())
    
    # Update any views
    self.dataChanged.emit(self.index(0,0), self.index(self.rowCount(), 6))

    return

  def remove_unit(self, *args):
    """Removes the unit from the unit-list and updates
    any views.
    """

    if isinstance(args[0], Unit):

      unit = args[0]
      idx = self.units.index(unit)
      unit = self.units.pop(idx)

    elif isinstance(args[0], int):

      idx = args[0]
      unit = self.units.pop(idx)
    
    for i, user_unit in enumerate(app.config['user_units']):
      if unit.id == user_unit['id']:
        removed_unit = app.config['user_units'].pop(i)
    
    self.dataChanged.emit(self.index(0,0), self.index(self.rowCount(), 6))

    return

  def get_units_by_si(self, si_unit):
    """Returns the units (`list`) associated with the si-unit (`str`) provided"""
    results = []
    for unit in self.units:
      if unit.si_id == si_unit:
        results.append(unit)
    return results

  def get_unit(self, unit_id):
    """returns the unit specified by the unit-id (`str`) provided"""
    for unit in self.units:
      if unit.id == unit_id:
        return unit
    return None

  # Magic functions
  def __setitme__(self, index, unit):
    self.units[index] = unit
    self.dataChanged.emit(self.index(0,0), self.index(self.rowCount(), 6))

  def __getitem__(self, index):
    return self.units[index]

  def __len__(self):
    return len(self.units)
