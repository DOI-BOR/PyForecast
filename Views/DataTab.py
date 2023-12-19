from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtGui
from Utilities import RichTextDelegate, ColorCycler, TimeSeriesPlot, TimeSeriesSlider
import pyqtgraph as pg
import numpy as np
from Plots import DataTab as DTP

# Initial PyQt Setup
pg.setConfigOption('background', pg.mkColor('#f7f7f7'))
pg.setConfigOption('foreground', pg.mkColor('#292929'))

app = QApplication.instance()

class DataTab(QWidget):

  def __init__(self):

    QWidget.__init__(self)

    self.data_all_button = QPushButton('Download all data')
    self.data_all_button.setStatusTip(f'Downloads all the data for all datasets in the forecast file (from {app.config["default_data_download_start"]:%Y-%m-%d} until now)')
    self.data_update_button = QPushButton('Download recent data')
    self.data_update_button.setStatusTip(f'Downloads only recent data for all datasets in the forecast file')
    self.edit_data_excel_button = QPushButton('Edit data in excel')
    self.edit_data_excel_button.setStatusTip('Open the selected datasets for editing in Excel')

    # Create the dataset list
    self.dataset_list = SelectedDatasetList()

    # Create the data viewer
    self.data_viewer = DTP.Plot()#DataViewer()

    # Layout the Tab
    layout = QHBoxLayout()
    self.splitter = QSplitter()
    layout2 = QVBoxLayout()
    layout2.addWidget(self.data_all_button)
    layout2.addWidget(self.data_update_button)
    layout2.addWidget(self.dataset_list)
    layout2.addWidget(self.edit_data_excel_button)
    self.w = QWidget()
    self.w.setLayout(layout2)
    self.splitter.addWidget(self.w)
    self.splitter.addWidget(self.data_viewer)
    layout.addWidget(self.splitter)
    self.setLayout(layout)

    self.splitter.splitterMoved.connect(lambda pos, idx: self.updateListSize())
  
  def updateListSize(self):
    app.datasets.dataChanged.emit(app.datasets.index(0), app.datasets.index(app.datasets.rowCount()))
    app.gui.DataTab.w.update()
    app.gui.DataTab.dataset_list.update()

class DataViewer(pg.GraphicsLayoutWidget):

  def __init__(self):

    pg.GraphicsLayoutWidget.__init__(self)
    self.color_cycler = ColorCycler.ColorCycler()
    self.setMinimumWidth(500)

    # SET MINIMUM ROW SIZE FOR ROWS
    [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]

    # initialize the plots
    self.timeseriesplot = TimeSeriesPlot.TimeSeriesPlot(self)
    self.timesliderplot = TimeSeriesSlider.TimeSliderPlot(self)

    self.addItem(self.timeseriesplot, row=0, col=0, rowspan=7)
    self.addItem(self.timesliderplot, row=7, col=0, rowspan=2)

    self.timesliderplot.region.sigRegionChanged.connect(self.updatePlot)
    self.timeseriesplot.sigRangeChanged.connect(self.updateRegion)

    return
  
  def updatePlot(self):

    self.timesliderplot.region.setZValue(10)
    newRegion = self.timesliderplot.region.getRegion()
    if not any(np.isinf(newRegion)):
        self.timeseriesplot.setXRange(*self.timesliderplot.region.getRegion(), padding=0)
        for i in range(len(self.timeseriesplot.items)):
          self.timeseriesplot.items[i].viewRangeChanged()
          
    return

  def updateRegion(self, window, viewRange):
    self.timesliderplot.region.setZValue(10)
    self.timesliderplot.region.setRegion(viewRange[0])
    for i in range(len(self.timeseriesplot.items)):
      self.timeseriesplot.items[i].viewRangeChanged()

    return

  
  def plot(self, dataframe, **kwargs):
    colors = [self.color_cycler.next() for i in dataframe.columns]
    self.timeseriesplot.plot(dataframe, colors, **kwargs)
    self.timesliderplot.plot(dataframe, colors)
  
  def clear_all(self):
    colors = [self.color_cycler.next()]
    self.timeseriesplot.plot([[],[]],colors)
    self.timesliderplot.plot([[],[]],colors)

class SelectedDatasetList(QListView):

  def __init__(self):
    
    QListView.__init__(self)
    self.setMinimumWidth(300)
    self.setItemDelegate(RichTextDelegate.HTMLDelegate())
    self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    self.download_all_one_shot_action = QAction('Download all data for selection')
    self.download_all_one_shot_action.setStatusTip('Downloads all the data for datasets in the selection')
    self.download_all_one_shot_action = QAction('Download all data for selection')
    self.download_all_one_shot_action.setStatusTip('Downloads all the data for datasets in the selection')

  def paintEvent(self, e):
    QListView.paintEvent(self, e)
    if (self.model()) and (self.model().rowCount(self.rootIndex()) > 0):
      return
    painter = QtGui.QPainter(self.viewport())
    painter.drawText(self.rect(), Qt.AlignCenter, 'No datasets in this forecast file')
    painter.end()

  def customMenu(self, pos):
    globalpos = self.mapToGlobal(pos)
    menu = QMenu()
    
    menu.addAction(self.download_all_one_shot_action)
    menu.addAction(self.download_recent_one_shot_action)

    index = self.indexAt(pos)
    selected = self.selectedIndexes()

    if not index.isValid():
      self.view_action.setEnabled(False)
      self.add_action.setEnabled(True)
      self.remove_action.setEnabled(False)
    elif len(selected)>1:
      self.view_action.setEnabled(False)
      self.remove_action.setEnabled(True)
      self.add_action.setEnabled(False)
    else:
      self.view_action.setEnabled(True)
      self.remove_action.setEnabled(True)
      self.add_action.setEnabled(False)
    menu.exec_(globalpos)