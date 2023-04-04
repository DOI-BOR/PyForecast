import pyqtgraph as pg
from Utilities import DateAxis, PlotUtils
import pandas as pd
import numpy as np
from PyQt5.QtCore import *
from itertools import combinations

class TimeSeriesPlot(pg.PlotItem):

  def __init__(self, parent = None, datetimeAxis=True):

    self.parent = parent
    pg.PlotItem.__init__(self)
    self.no_dots = True
    self.no_hover = True
    self.no_legend = True

    self.setMenuEnabled(False)
    if datetimeAxis:
      b_axis = DateAxis.DateAxisItem(orientation='bottom')
      b_axis.attachToPlotItem(self)
      b_axis.setZValue(0)

    self.showAxis("right")
    self.viewbox_axis_2 = pg.ViewBox()
    self.parent.scene().addItem(self.viewbox_axis_2)
    self.getAxis("right").linkToView(self.viewbox_axis_2)
    self.viewbox_axis_2.setXLink(self)

    self.getAxis('right').setZValue(0)
    self.getAxis('left').setZValue(0)
    
    self.legend = PlotUtils.TimeSeriesLegend(size=None, offset=(30,30))
    self.legend.setParentItem(self.vb)
    self.showGrid(True, True, 0.85)

    self.plot_assignments = []
    self.hoverPoints = []    

    self.updateViews()
    self.vb.sigResized.connect(self.updateViews)
    self.parent.scene().sigMouseMoved.connect(self.mouseMoved)



  def mouseMoved(self,event):
    if self.no_hover:
      return
    pos = QPoint(int(event.x()), int(event.y()))
    mouse_point = self.vb.mapSceneToView(pos)
    x_ = mouse_point.x()
    idx = int(x_ - x_%86400)
    legend_count = 0

    for i,(item, pa) in enumerate(self.plot_assignments):
      hoverpoint = self.hoverPoints[i]
      
      closest_x, closest_idx = PlotUtils.takeClosest(item.getData()[0], idx)
      y = item.getData()[1][closest_idx]
      if np.isnan(closest_x) or np.isnan(y):
        hoverpoint.setData(x=[], y=[])
      else:
        hoverpoint.setData(x=[closest_x], y=[y])

      self.legend.items[i][1].setText(f'{item.opts["name"]} <strong>{y:.2f}</strong>')
    


  def updateViews(self):
    self.viewbox_axis_2.setGeometry(self.vb.sceneBoundingRect())
    self.viewbox_axis_2.linkedViewChanged(self.vb, self.viewbox_axis_2.XAxis)

  def plot(self, data, colors, **kwargs):

    if isinstance(data, list):
      data = pd.DataFrame([0], index=pd.DatetimeIndex([pd.to_datetime('1970-01-01')]))

    if 'unit_list' in kwargs:
      self.unit_list = kwargs['unit_list']
    else:
      self.unit_list = ['-']*len(data.columns)

    if 'no_legend' in kwargs:
      self.no_legend = True
    else:
      self.no_legend = False

    if 'no_dots' in kwargs:
      self.no_dots = True
    else:
      self.no_dots = False

    if 'no_hover' in kwargs:
      self.no_hover = True
    else:
      self.no_hover = False
    if 'trace_width' in kwargs:
      self.trace_width = True
    else:
      self.trace_width = False

    self.plot_dataframe(data, colors)

    
  def plot_dataframe(self, dataframe, colors):
    self.clear()
    self.plot_assignments = []
    self.viewbox_axis_2.clear()
    # Convert the index into unix integer time
    
    if dataframe.empty:
      dataframe.loc[pd.to_datetime('2000-10-01')] = [0]*len(dataframe.columns)
    x = dataframe.index.values
    if not isinstance(x[0], (int, np.integer)):
      x = (dataframe.index.astype(np.int64)//10**9).values
    
    condensed = PlotUtils.condenseUnits([u for u in self.unit_list])

    self.setLimits(xMin=np.nanmin(x), xMax=np.nanmax(x), yMin=dataframe.min().min(), yMax=dataframe.max().max())
    self.setRange(xRange=(np.nanmin(x), np.nanmax(x)), yRange=(dataframe.min().min(), dataframe.max().max()))

    self.hoverPoints = []    

    # Plot the data
    for i, col in enumerate(dataframe.columns):

      y = dataframe[col]
      if len(y.dropna()) < 300 and not self.no_dots:
        marker = 'o'
      else:
        marker = None
      markerPen = pg.mkPen(colors[i])
      markerBrush = pg.mkBrush(colors[i])
      if not self.no_hover:
        point = pg.ScatterPlotItem(symbol='o', brush=markerBrush, pen = markerPen, size=10, pxMode=True)
        self.hoverPoints.append(point)

      if PlotUtils.sameUnits(self.unit_list[i], condensed[0])[0]:
        if self.no_legend:
          curve = pg.PlotDataItem(x=x, y=y.values, symbol=marker, symbolBrush=markerBrush, symbolPen = markerPen, pen=pg.mkPen(colors[i], width=1.5 if not self.trace_width else 0.5), connect='finite', stepMode='left')
        else:
          curve = pg.PlotDataItem(x=x, y=y.values, symbol=marker, symbolBrush=markerBrush, symbolPen = markerPen, name=col, pen=pg.mkPen(colors[i], width=1.5 if not self.trace_width else 0.5), connect='finite', stepMode='left')
        curve.setZValue(10)
        self.plot_assignments.append((curve, 0))
        self.addItem(curve)
        self.addItem(point)
        
        #pg.PlotItem.plot(self, x=x, y=dataframe[col].values, name=col, clear=True if i==0 else False, pen=pg.mkPen(colors[i]), connect='finite')
      else:
        if self.no_legend:
          curve = pg.PlotDataItem(x=x, y=y.values, symbol=marker, symbolBrush=markerBrush, symbolPen = markerPen, pen=pg.mkPen(colors[i], width=1.5 if not self.trace_width else 0.5), connect='finite', stepMode='left')
        else:
          curve = pg.PlotDataItem(x=x, y=y.values, symbol=marker, symbolBrush=markerBrush, symbolPen = markerPen, name=col, pen=pg.mkPen(colors[i], width=1.5 if not self.trace_width else 0.5), connect='finite', stepMode='left')
        curve.setZValue(10)
        self.viewbox_axis_2.addItem(curve)
        self.plot_assignments.append((curve, 1))
        if not self.no_legend:
          self.legend.addItem(curve, col)
        self.viewbox_axis_2.addItem(point)
        #pg.PlotItem.plot(self.viewbox_axis_2, x=x, y=dataframe[col].values, name=col, clear=True if i==0 else False, pen=pg.mkPen(colors[i]), connect='finite')
    
    self.getAxis('left').setLabel(condensed[0])
    self.getAxis('right').setLabel(' '.join(condensed[1:]))
