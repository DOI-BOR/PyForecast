from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter
import pyqtgraph as pg
from Utilities import RichTextDelegate, ToggleSwitch
from datetime import datetime

app = QApplication.instance()

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
    self.splitter = QSplitter()
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
    self.widg = QWidget()
    self.widg.setLayout(vlayout)
    self.splitter.addWidget(self.widg)

    h = QHBoxLayout()
    h.addStretch(1)
    h.addWidget(QLabel("<strong>Select Year to view</strong>"))
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
    self.splitter.addWidget(widg)
    self.layout.addWidget(self.splitter)
    self.setLayout(self.layout)

    self.splitter.splitterMoved.connect(lambda pos, idx: self.updateListSize())
  
  def updateListSize(self):
    app.saved_models.dataChanged.emit(app.saved_models.index(0), app.saved_models.index(app.saved_models.rowCount()))
    app.gui.SavedModelsTab.widg.update()


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
    
  def paintEvent(self, e):
    QListView.paintEvent(self, e)
    if (self.model()) and (self.model().rowCount(self.rootIndex()) > 0):
      return
    painter = QPainter(self.viewport())
    painter.drawText(self.rect(), Qt.AlignCenter, 'No saved models in this forecast file')
    painter.end()

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
    
    def reframe_to_min_max_normal(self, min_, max_, normal):
      self.setXRange(min_, max_, padding=0.1)
      item0 = pg.InfiniteLine(
        normal,
        pen=pg.mkPen({'color':'blue', 'width':4}),
        movable=False
      )
      self.addItem(item0)
      item1 = pg.InfiniteLine(
        min_,
        pen=pg.mkPen({'color':'red', 'width':4}),
        movable=False
      )
      self.addItem(item1)
      item2 = pg.InfiniteLine(
        max_,
        pen=pg.mkPen({'color':'red', 'width':4}),
        movable=False
      )
      self.addItem(item2)
      label0 = f'<span style="margin:5px;font-size:large;background-color: white; border: 1px solid black; padding: 5px"><strong>P.O.R. Median</strong>: {normal:.2f}</span>'
      textItem0 = pg.TextItem(
          html=label0,
          angle=90
        )
      textItem0.setZValue(30)
      self.addItem(textItem0)
      vr = self.getPlotItem().viewRange()
      textItem0.setPos(normal,0)

      label1 = f'<span style="margin:5px;font-size:large;background-color: white; border: 1px solid black; padding: 5px"><strong>P.O.R. Min</strong>: {min_:.2f}</span>'

      textItem1 = pg.TextItem(
          html=label1,
          angle=90
        )
      textItem1.setZValue(30)
      self.addItem(textItem1)
      textItem1.setPos(min_, 0)

      label2 = f'<span style="margin:5px;font-size:large;background-color: white; border: 1px solid black; padding: 5px"><strong>P.O.R. Max</strong>: {max_:.2f}</span>'

      textItem2 = pg.TextItem(
          html=label2,
          angle=90
        )
      textItem2.setZValue(30)
      self.addItem(textItem2)
      textItem2.setPos(max_, 0)

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
        
