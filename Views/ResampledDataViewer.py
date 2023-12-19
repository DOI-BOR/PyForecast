from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from Utilities.TimeSeriesPlot import TimeSeriesPlot
from Utilities import ColorCycler, HydrologyDateTimes
import numpy as np
from Plots.ResampledDataViewer import Plot

app = QApplication.instance()

class DataViewer(QDialog):

  def __init__(self, configuration_idx = None, dataset_idx = None):

    QDialog.__init__(self)
    self.configuration = app.model_configurations[configuration_idx]
    if dataset_idx == -1:
      self.dataset = self.configuration.predictand
    else:
      self.dataset = self.configuration.predictor_pool[dataset_idx]

    self.datasets = [self.configuration.predictand] + [p for p in self.configuration.predictor_pool.predictors]
    
    self.setUi()
    self.setData(self.dataset)
    self.data_plot.plot(self.dataset, self.configuration.predictand)
    
    self.combo_select.setCurrentText(self.dataset.__list_form__())
    self.load_button.pressed.connect(self.combo_changed)

    

  def combo_changed(self):
    idx = self.combo_select.currentIndex()
    self.dataset = self.datasets[idx]
    self.setData(self.dataset)
    self.data_plot.plot(self.dataset, self.configuration.predictand)
    

  def setUi(self):

    self.setWindowTitle('Dataset Viewer')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))

    layout = QGridLayout()

    self.load_button = QPushButton('Load')
    self.load_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    self.combo_select = QComboBox()
    self.combo_select.setModel(QStringListModel([d.__list_form__() for d in self.datasets]))
    self.data_grid = QTableWidget()
    
    self.data_plot = Plot()
    
    layout.addWidget(self.combo_select, 0, 0, 1, 3)
    layout.addWidget(self.load_button, 0, 3, 1, 1)
    splitter = QSplitter()
    splitter.addWidget(self.data_plot)
    splitter.addWidget(self.data_grid)
    layout.addWidget(splitter, 1, 0, 1, 5)

    self.setLayout(layout)
  
  def setData(self, dataset):
    
    dataset.resample()
    dataset.data = dataset.data.loc[HydrologyDateTimes.convert_to_water_year(self.configuration.training_start_date):HydrologyDateTimes.convert_to_water_year(self.configuration.training_end_date)]
    self.data_grid.setRowCount(len(dataset.data))
    self.data_grid.setColumnCount(2)
    self.data_grid.setHorizontalHeaderLabels(['Water Year', 'Value'])
    for r, (year, value) in enumerate(dataset.data.items()):
      yearItem = QTableWidgetItem(f'{year}')
      valItem = QTableWidgetItem(f'{value:.2f}')
      self.data_grid.setItem(r, 0, yearItem)
      self.data_grid.setItem(r, 1, valItem)

