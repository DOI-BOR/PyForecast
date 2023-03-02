from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent
import pyqtgraph as pg
from Utilities import RichTextDelegate, ToggleSwitch
from datetime import datetime
fcst_label = """
<span style="font-family: 'Courier New', 'Courier', 'Consolas', monospace">
FORECAST LEGEND: <br>
<span style="color:#cfb83a">{lc}</span> : &lt;30% of normal<br>
<span style="color:#00bb00">{mc}</span> : 30% - 70% of normal<br>
<span style="color:#cc0000">{hc}</span> : &gt;70% of normal<br>
</span>"""
class SavedModelsTab(QWidget):

  def __init__(self):

    QWidget.__init__(self)
    self.setUI()
    self.year_select.setMinimum(1900)
    cwt = datetime.now()
    self.year_select.setMaximum(cwt.year if cwt.month < 10 else cwt.year+1)
    self.year_select.setValue(self.year_select.maximum())

  def setUI(self):

    self.layout = QHBoxLayout()
    splitter = QSplitter()
    vlayout = QVBoxLayout()
    vlayout2 = QVBoxLayout()
    hlayout = QHBoxLayout()
    hlayout2 = QHBoxLayout()

    self.issue_combo = QComboBox()
    self.model_list = ModelList()
    self.year_select = QSpinBox()
    self.plot_select = ToggleSwitch.Switch(thumb_radius=11, track_radius=8)
    self.prob_plot = ProbabilityPlots()
    self._10_value = valueLabel()
    self._30_value = valueLabel()
    self._50_value = valueLabel()
    self._70_value = valueLabel()
    self._90_value = valueLabel()
    self.export_values_button = QPushButton('Show all exceedance values')

    vlayout.addWidget(QLabel("Issue Date"))
    vlayout.addWidget(self.issue_combo)
    vlayout.addWidget(self.model_list)
    vlayout.addWidget(QLabel(fcst_label.format(lc=u'\u25bc', mc=u'\u25a0', hc=u'\u25b2')))
    widg = QWidget()
    widg.setLayout(vlayout)
    splitter.addWidget(widg)

    h = QHBoxLayout()
    h.addStretch(1)
    h.addWidget(QLabel("Select Year to view"))
    h.addWidget(self.year_select)
    h.addWidget(QLabel('|   PDF View'))
    h.addWidget(self.plot_select)
    h.addWidget(QLabel("CDF View"))
    vlayout2.addLayout(h)
    vlayout2.addWidget(self.prob_plot)
    vlayout2.addWidget(QLabel('<strong>Forecast Exceedances</strong>', objectName='HeaderLabel'))
    hlayout.addWidget(QLabel('90%'))
    hlayout.addWidget(self._10_value)
    hlayout.addWidget(QLabel('70%'))
    hlayout.addWidget(self._30_value)
    hlayout.addWidget(QLabel('50%'))
    hlayout.addWidget(self._50_value)
    hlayout.addWidget(QLabel('30%'))
    hlayout.addWidget(self._70_value)
    hlayout.addWidget(QLabel('10%'))
    hlayout.addWidget(self._90_value)
    vlayout2.addLayout(hlayout)
    hlayout2.addWidget(self.export_values_button)
    hlayout2.addStretch(1)
    vlayout2.addLayout(hlayout2)
    widg = QWidget()
    widg.setLayout(vlayout2)
    splitter.addWidget(widg)
    self.layout.addWidget(splitter)
    self.setLayout(self.layout)


class ModelList(QListView):

  def __init__(self, app = None):
    
    QListView.__init__(self)
    self.app = app
    self.setMinimumWidth(300)
    self.setItemDelegate(RichTextDelegate.HTMLDelegate())
    self.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.customContextMenuRequested.connect(self.customMenu)

    self.generate_forecast_action = QAction('Generate Forecasts')
    self.generate_forecast_action.setStatusTip('Generate forecasts for using this model')
    self.open_action = QAction('Open model')
    self.open_action.setStatusTip("Opens the forecast model in a new window for viewing model parameters")
    self.remove_action = QAction("Remove model")
    self.remove_action.setStatusTip("Removes the selected model from the file")
    


  def customMenu(self, pos):
    globalpos = self.mapToGlobal(pos)
    menu = QMenu()
    
    menu.addAction(self.generate_forecast_action)
    menu.addAction(self.open_action)
    menu.addAction(self.remove_action)


    index = self.indexAt(pos)
    selected = self.selectedIndexes()

    if not index.isValid():
      self.generate_forecast_action.setEnabled(False)
      self.open_action.setEnabled(False)
      self.remove_action.setEnabled(False)
    elif len(selected) == 1:
      self.generate_forecast_action.setEnabled(True)
      self.open_action.setEnabled(True)
      self.remove_action.setEnabled(True)
    else:
      self.open_action.setEnabled(False)
      self.generate_forecast_action.setEnabled(True)
      self.remove_action.setEnabled(True)
    menu.exec_(globalpos)

class valueLabel(QLineEdit):
  def __init__(self):
    QLineEdit.__init__(self)
    self.setReadOnly(True)
    
  def setText(self, value, units):
    value = f'{value:.2f} {units}'
    QLineEdit.setText(self, value)

class ProbabilityPlots(pg.PlotWidget):
    def __init__(self):
      pg.PlotWidget.__init__(self)
      self.addLegend()
      self.showGrid(True,False,0.85)
      self.getAxis('bottom').setLabel('Target Value')
      self.hideAxis('left')
      
    def plot_data(self, x, y, color, width=1.5, label=None):
      i = self.plot(x, y, pen=pg.mkPen({'color':color, "width":width}), name=label, antialias=True)
      i.setZValue(30)
      
    def plot_vlines(self, values):

      # plot regions
      _10_90_roi = pg.LinearRegionItem(
        values=(values[0], values[-1]),
        brush=pg.mkBrush(pg.mkColor('#dedede')),
        movable=False
      )
      _10_90_roi.setZValue(0)
      self.addItem(_10_90_roi)
      
      for i, val in enumerate(values):

        item = pg.InfiniteLine(
          val, 
          pen=pg.mkPen({'color':'black', 'width':2}), 
          movable=False)

        self.addItem(item)
        label = f'<span style="margin:5px;font-size:large;background-color: white; border: 1px solid black; padding: 5px"><strong>{100-(10+20*i)}%</strong>: {val:.2f}</span>'
        textItem = pg.TextItem(
          html=label
        )
        textItem.setZValue(30)
        self.addItem(textItem)
        lr = item.boundingRect()
        pt1 = pg.Point(lr.left(), 0)
        pt2 = pg.Point(lr.right(), 0)
        pt = pt2 * (0.1+0.2*i) + pt1 * (1-(0.1+0.2*i))
        textItem.setPos(val, pt.x())
        
