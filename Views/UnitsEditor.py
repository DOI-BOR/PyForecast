from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIcon
from copy import deepcopy

# Get the global application
app = QApplication.instance()

class UnitsEditor(QDialog):
  
  def __init__(self):

    QDialog.__init__(self)
    self.setWindowTitle('Edit PyForecast Units')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    self.old_units = deepcopy(app.units.units)

    self.units_table = QTableView(self)
    self.units_table.setModel(app.units)
    self.units_table.horizontalHeader().setStretchLastSection(True)
    self.units_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.units_table.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.units_table.setSelectionMode(QAbstractItemView.SingleSelection)
    self.units_table.setContextMenuPolicy(Qt.ActionsContextMenu)
    self.units_table.setColumnHidden(6, True)
    
    self.remove_action = QAction('Remove Unit')
    self.units_table.addAction(self.remove_action)
    self.remove_action.triggered.connect(self.remove_unit)

    

    layout = QVBoxLayout()
    layout.addWidget(self.units_table, 10)

    layout.addWidget(QLabel('Add new unit'))
    layout3 = QHBoxLayout()
    layout3.addWidget(QLabel('ID'))
    self.new_id_edit = QLineEdit(self)
    layout3.addWidget(self.new_id_edit)
    layout3.addWidget(QLabel('Name'))
    self.name_edit = QLineEdit(self)
    layout3.addWidget(self.name_edit)
    layout3.addWidget(QLabel('SI Unit'))
    self.si_unit_edit = QLineEdit(self)
    layout3.addWidget(self.si_unit_edit)
    layout3.addWidget(QLabel('SI Scale'))
    self.scale_edit = QLineEdit(self)
    layout3.addWidget(self.scale_edit)
    layout3.addWidget(QLabel('SI Offset'))
    self.off_edit = QLineEdit(self)
    layout3.addWidget(self.off_edit)
    self.type_edit = QLineEdit(self)
    layout3.addWidget(QLabel('Type'))
    layout3.addWidget(self.type_edit)
    self.new_button = QPushButton('Add')
    layout3.addWidget(self.new_button)
    layout.addLayout(layout3)


    hline = QFrame()
    hline.setFrameShape(QFrame.HLine)
    layout.addWidget(hline)

    layout2 = QHBoxLayout()
    self.save_button = QPushButton('Save')
    self.cancel_button = QPushButton('Cancel') 
    layout2.addWidget(self.save_button)
    layout2.addWidget(self.cancel_button)
    layout2.addStretch(1)
    layout.addLayout(layout2, 1)

    self.setLayout(layout)

    self.new_button.pressed.connect(self.add_unit)
    self.save_button.pressed.connect(self.save_list)
    self.cancel_button.pressed.connect(self.cancel_list)

    # Validators
    dval = QDoubleValidator(self)
    self.scale_edit.setValidator(dval)
    self.off_edit.setValidator(dval)
    self.scale_edit.setText('1.0')
    self.off_edit.setText('0.0')
    

    self.exec()

  def closeEvent(self, event):

    new = [u.id for u in app.units.units]
    if new != [u.id for u in self.old_units]:
      ret = QMessageBox.question(self, 'Unsaved Changes', 'You have made changes to the units list. Save those changes?')
      if ret == QMessageBox.Yes:
        QDialog.closeEvent(self,event)
      else:
        self.cancel_list()
    else:
      QDialog.closeEvent(self,event)

  def save_list(self):

    self.old_units = app.units.units
    self.close()
  
  def cancel_list(self):

    for unit in app.units.units:
      if unit.id in [u.id for u in self.old_units]:
        continue
      else:
        app.units.remove_unit(unit)
    self.close()

  def remove_unit(self, _):

    selected_idx = set([i.row() for i in self.units_table.selectedIndexes()])
    if len(selected_idx) > 0:
      idx = selected_idx.pop()
    app.units.remove_unit(idx)
  
  def add_unit(self):

    id = self.new_id_edit.text()
    name = self.name_edit.text()
    si_id = self.si_unit_edit.text()
    si_scale = float(self.scale_edit.text())
    offset = float(self.off_edit.text())
    type=self.type_edit.text()

    app.units.add_unit(True, id=id, name=name, si_id=si_id, si_scale=si_scale, si_offset=offset, type=type)
    self.new_id_edit.clear()
    self.name_edit.clear()
    self.si_unit_edit.clear()
    self.scale_edit.setText('1.0')
    self.off_edit.setText('0.0')
    

