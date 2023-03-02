from PyQt5.QtWidgets import *
from Utilities import TimeSeriesPlot, ColorCycler
import pyqtgraph as pg

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
    self.tabWidget.addTab(forecastUpdateTab, 'Forecast Sandbox')

    disaggTab = QWidget()
    self.tabWidget.addTab(disaggTab, 'Forecast Disaggregation')

    self.disagg_year_select = QSpinBox()
    self.disagg_start_edit = QDateEdit()
    self.disagg_start_edit.setDisplayFormat('MMMM dd')
    self.disagg_end_edit = QDateEdit()
    self.disagg_end_edit.setDisplayFormat('MMMM dd')
    self.disagg_start_btn = QPushButton('Disaggregate')
    self.disagg_table_view_btn = QPushButton('Export to Excel')
    self.disagg_plot_view = DataViewer()

    dlayout = QVBoxLayout()
    h = QHBoxLayout()
    h.addStretch(1)
    h.addWidget(QLabel('Which Year to Disaggregate'))
    h.addWidget(self.disagg_year_select)
    h.addWidget(QLabel('      Start Date'))
    h.addWidget(self.disagg_start_edit)
    h.addWidget(QLabel(' End Date'))
    h.addWidget(self.disagg_end_edit)
    h.addWidget(QLabel('      '))
    h.addWidget(self.disagg_table_view_btn)
    h.addWidget(QLabel('      '))
    h.addWidget(self.disagg_start_btn)
    dlayout.addLayout(h)

    dlayout.addWidget(self.disagg_plot_view)
    disaggTab.setLayout(dlayout)

    self.setLayout(layout)
    


class DataViewer(pg.GraphicsLayoutWidget):

  def __init__(self):

    pg.GraphicsLayoutWidget.__init__(self)
    self.color_cycler = ColorCycler.ColorCycler()
    self.setMinimumWidth(500)

    # initialize the plots
    self.timeseriesplot = TimeSeriesPlot.TimeSeriesPlot(self)
    self.addItem(self.timeseriesplot, row=0, col=0)

    return
  
  def plot(self, dataframe, **kwargs):
    colors = [self.color_cycler.next() for i in dataframe.columns]
    self.timeseriesplot.plot(dataframe, colors, **kwargs)
  
  def clear_all(self):
    colors = [self.color_cycler.next()]
    self.timeseriesplot.plot([[],[]],colors)
