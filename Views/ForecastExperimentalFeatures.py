from PyQt5.QtWidgets import *

app = QApplication.instance()

class ExperimentalFeatures(QWidget):

  def __init__(self):

    QWidget.__init__(self)
    self.setUI()

  def setUI(self):

    layout = QVBoxLayout()
    self.tabWidget = QTabWidget()
    layout.addWidget(self.tabWidget)

    forecastUpdateTab = QWidget()
    self.tabWidget.addTab(forecastUpdateTab, 'Update Forecast')

    disaggTab = QWidget()
    self.tabWidget.addTab(disaggTab, 'Forecast Disaggregation')



    self.setLayout(layout)
