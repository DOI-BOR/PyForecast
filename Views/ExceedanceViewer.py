from PyQt5.QtWidgets import *

app = QApplication.instance()

class ExceedanceViewer(QDialog):

  def __init__(self, exceedances):

    self.exceedances = exceedances
    QDialog.__init__(self)
    self.setUI()

    for i, (ex, val) in enumerate(self.exceedances.iteritems()):

      idxItem = QTableWidgetItem(f'{int(100*(1-ex))}%')
      valItem = QTableWidgetItem(f'{val:0.4g}')
      self.excTable.setItem(i, 0, idxItem)
      self.excTable.setItem(i, 1, valItem)


  def setUI(self):

    layout = QVBoxLayout()
    self.excTable = QTableWidget()
    self.excTable.setRowCount(99)
    self.excTable.setColumnCount(2)
    self.excTable.setHorizontalHeaderLabels(['Exceedance', 'Forecast'])
    layout.addWidget(self.excTable)
    self.setLayout(layout)
    self.setMinimumSize(500,500)
