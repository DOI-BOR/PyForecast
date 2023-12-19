from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QStringListModel, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QIcon
from Utilities.ToolTipLabel import ToolTipLabel
from copy import deepcopy
from operator import attrgetter

app = QApplication.instance()

class UnitFilterModel(QSortFilterProxyModel):

  def __init__(self):
    QSortFilterProxyModel.__init__(self)
    self.filterString = 'length'
  def setFilterString(self, text):
    self.filterString = text.lower()
    self.invalidateFilter()
  def filterAcceptsRow(self, sourceRow, sourceParent = QModelIndex()):
    idx = self.sourceModel().index(sourceRow, 5)
    source_unit_type = self.sourceModel().data(idx, Qt.DisplayRole)
    
    if source_unit_type.value() == self.filterString:
      return True
    else:
      return False

class DatasetViewer(QDialog):

  def __init__(self, app=None, dataset_guid=None, new=False):

    QDialog.__init__(self)
    self.setWindowTitle('View Dataset')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))
    self.app = app
    self.guid = dataset_guid
    self.new = new

    # Create the fields
    self.guid_field_readonly = QLineEdit()
    self.guid_field_readonly.setReadOnly(True)
    self.guid_field_readonly.setEnabled(False)
    self.external_id_field = QLineEdit()
    self.name_field = QLineEdit()
    self.agency_field = QLineEdit()
    self.parameter_field = QLineEdit()
    self.param_code_field = QLineEdit()
    self.unit_field = QComboBox()
    self.unit_field.setModel(self.app.units)
    self.unit_field.setModelColumn(6)
    self.display_unit_field = QComboBox()
    self.unitFilterModel = UnitFilterModel()
    self.unitFilterModel.setSourceModel(app.units)
    self.display_unit_field.setModel(self.unitFilterModel)
    self.display_unit_field.setModelColumn(6)
    self.dataloader_field = QComboBox()
    self.dataloader_field.setModel(QStringListModel(list(self.app.dataloaders.keys())))

    self.unit_field.currentIndexChanged.connect(self.updateUnits)

    # Create the hidden fields
    self.is_file_import = QCheckBox()
    self.file_path = QLineEdit()
    self.file_path.setReadOnly(True)
    self.file_path.setEnabled(False)
    self.file_select_button = QPushButton(self.style().standardIcon(QStyle.SP_DirIcon),'')
    self.file_select_button.setEnabled(False)
    self.file_validation_label = QLabel()

    # Save/cancel buttons
    self.save_button = QPushButton('Save')
    self.cancel_button = QPushButton('Cancel')

    # Set up the form
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    layout = QVBoxLayout()
    label = QLabel('<strong>Dataset Description</strong>')
    
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    layout.addWidget(line)
    layout2 = QFormLayout()
    layout2.setLabelAlignment(Qt.AlignRight)
    layout2.addRow(ToolTipLabel('GUID', 'Internal identifier for this dataset'), self.guid_field_readonly)
    layout2.addRow(ToolTipLabel('ID', "This dataset's <strong>ID</strong>. Dataloaders use this to find and download data"), self.external_id_field)
    layout2.addRow('Name', self.name_field)
    layout2.addRow('Agency', self.agency_field)
    layout2.addRow('Parameter', self.parameter_field)
    layout2.addRow(ToolTipLabel('Parameter Code', 'This code is used by dataloaders when downloading data'), self.param_code_field)
    layout2.addRow(ToolTipLabel('Raw Units', 'Data is returned from the dataloader in this unit'), self.unit_field)
    layout2.addRow(ToolTipLabel('Display Units', 'PyForecast converts the raw units to this unit for display and processing'), self.display_unit_field)
    layout2.addRow('Dataloader', self.dataloader_field)
    line2 = QFrame()
    line2.setFrameShape(QFrame.HLine)
    layout2.addWidget(line2)
    layout2.addRow(ToolTipLabel('Flat-file source?', "Check this box if you're importing data from a file"), self.is_file_import)
    layout3 = QHBoxLayout()
    layout3.addWidget(self.file_path)
    layout3.addWidget(self.file_select_button)
    layout2.addRow('File path',layout3)
    layout.addLayout(layout2)
    line3 = QFrame()
    line3.setFrameShape(QFrame.HLine)
    layout.addWidget(line3)
    layout4 = QHBoxLayout()
    layout4.addWidget(self.save_button)
    layout4.addWidget(self.cancel_button)
    layout4.addStretch(1)
    layout.addLayout(layout4)
    
    self.is_file_import.toggled.connect(lambda c: self.file_import_toggled(c))
    self.save_button.pressed.connect(self.save_dataset)
    self.cancel_button.pressed.connect(self.cancel_button_pressed)
    self.file_select_button.pressed.connect(self.file_select)

    self.setLayout(layout)

    # Load the dataset
    self.load_dataset()

    self.exec_()

  def updateUnits(self, idx):
    new_unit = app.units[idx]
    self.unitFilterModel.setFilterString(new_unit.type)

  def file_select(self):
    fn, _filter = QFileDialog.getOpenFileName(self, 'Select Flat File', self.app.config['last_dir'], 'Flat-File Files (*.csv  *.xlsx)')
    if fn:
      if fn != '':
        self.file_path.setText(fn)

  def file_import_toggled(self, checkstate):

    if checkstate:
      self.file_path.setEnabled(True)
      self.file_select_button.setEnabled(True)
      self.dataloader_field.setCurrentText('Flat File Import')
    else:
      self.file_path.clear()
      self.file_path.setEnabled(False)
      self.file_select_button.setEnabled(False)
      self.dataloader_field.setCurrentText('')
  
  def gather_dataset(self):
    dataset = deepcopy(self.dataset)
    dataset.external_id = self.external_id_field.text().strip()
    dataset.name = self.name_field.text().strip()
    dataset.agency = self.agency_field.text().strip()
    dataset.parameter = self.parameter_field.text().strip()
    dataset.param_code = self.param_code_field.text().strip()
    dataset.raw_unit = self.unit_field.currentData(Qt.UserRole + 1)
    dataset.display_unit = self.display_unit_field.currentData(Qt.UserRole + 1)
    dataset.dataloader = self.app.dataloaders[self.dataloader_field.currentText()]['CLASS']()
    dataset.is_file_import = self.is_file_import.isChecked()
    if dataset.is_file_import:
      dataset.dataloader = self.app.dataloaders['Flat File Import']['CLASS']()
      dataset.file_path = self.file_path.text().strip()
    return dataset

  def checkDataset(self, new_dataset):
    
    attrs = ['external_id', 'name', 'agency', 'parameter', 'param_code', 'raw_unit.id', 'display_unit.id', 'dataloader.NAME', 'file_path', 'is_file_import']
    diffs = []
    for attr in attrs:
      old = attrgetter(attr)(self.old_dataset)
      new = attrgetter(attr)(new_dataset)
      if old != new:
        diffs.append((attr, old, new))
    if len(diffs) > 0:
      diff_string = ',\n'.join([f'{a[0]}: "{a[1]}" -> "{a[2]}"' for a in diffs])
      ret = QMessageBox.question(self, 'Unsaved Changes', f"You have made changes to the dataset. Changes include:\n\n{diff_string}\n\nSave those changes?")
      return ret
    else:
      return QMessageBox.No

  def closeEvent(self, event):
    if event.spontaneous():
      d = self.gather_dataset()
      ret = self.checkDataset(d)
      if ret == QMessageBox.Yes:
        self.save_dataset()
      else:
        if self.new:
          self.app.datasets.remove_dataset(guid = self.dataset.guid)
        self.close()
        #QWidget.closeEvent(self, event)
    else:
      if self.new:
        self.app.datasets.remove_dataset(guid = self.dataset.guid)
      self.close()
      #QWidget.closeEvent(self, event)
    

  def save_dataset(self):

    self.dataset = self.gather_dataset()
    
    self.old_dataset = self.dataset

    self.app.datasets.update_dataset_by_guid(self.dataset.guid, self.dataset)
    self.new = False
    self.close()
  

  def cancel_button_pressed(self):
    self.dataset = self.old_dataset
    if self.new:
      self.app.datasets.remove_dataset(guid = self.dataset.guid)
    self.close()
  

  def load_dataset(self):

    self.dataset = self.app.datasets.get_dataset_by_guid(self.guid)
    self.old_dataset = deepcopy(self.dataset)

    if self.dataset:
      self.guid_field_readonly.setText(self.dataset.guid)
      self.external_id_field.setText(self.dataset.external_id)
      self.name_field.setText(self.dataset.name)
      self.agency_field.setText(self.dataset.agency)
      self.parameter_field.setText(self.dataset.parameter)
      self.param_code_field.setText(self.dataset.param_code)
      unit = self.dataset.raw_unit
      display_unit = self.dataset.display_unit
      idx = self.app.units.units.index(unit)
      self.unit_field.setCurrentIndex(idx)
      self.unitFilterModel.setFilterString(unit.type)
      self.display_unit_field.setCurrentText(display_unit.__list_form__())
      self.dataloader_field.setCurrentText(self.dataset.dataloader.NAME)
      if self.dataset.is_file_import:
        self.is_file_import.toggle()
        self.file_path.setText(self.dataset.file_path)

if __name__ == '__main__':
  import sys
  app = QApplication(sys.argv)
  mw = DatasetViewer(app)
  mw.show()
  sys.exit(app.exec())