from PyQt5.QtWidgets import *
from datetime import datetime
import os

app = QApplication.instance()

class ExceedanceViewer(QDialog):

  def __init__(self, exceedances):

    self.exceedances = exceedances
    QDialog.__init__(self)
    self.setUI()
    self.excButton.pressed.connect(self.open_in_excel)

    for i, (ex, val) in enumerate(self.exceedances.items()):

      idxItem = QTableWidgetItem(f'{(100*(1-ex)):0.2f}%')
      valItem = QTableWidgetItem(f'{val:0.4g}')
      self.excTable.setItem(i, 0, idxItem)
      self.excTable.setItem(i, 1, valItem)

  def open_in_excel(self):
    fname = app.base_dir + f'/UserData/{datetime.now():%Y%b%d_%H%M%S}_EXCEED.csv'

    self.exceedances.to_csv(fname)
    os.system(f"start EXCEL.EXE {fname}")

  def setUI(self):

    layout = QVBoxLayout()
    self.excTable = QTableWidget()
    self.excButton = QPushButton('Open in Excel')
    self.excTable.setRowCount(len(self.exceedances))
    self.excTable.setColumnCount(2)
    self.excTable.setHorizontalHeaderLabels(['Exceedance', 'Forecast'])
    layout.addWidget(self.excTable)
    layout.addWidget(self.excButton)
    self.setLayout(layout)
    self.setMinimumSize(500,500)

