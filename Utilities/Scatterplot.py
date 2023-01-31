import pyqtgraph as pg
from Utilities import PlotUtils
import pandas as pd
import numpy as np
from PyQt5.QtCore import *

class ScatterPlot(pg.PlotItem):

  def __init__(self, line=False):

    pg.PlotItem.__init__(self, enableMenu=False)
    self.sp = pg.ScatterPlotItem()
    self.line = line
    if self.line:
      self.lineItem = pg.PlotCurveItem()
    self.showGrid(True, True, 0.85)
    return

  def plot_data(self, x, y, data = None, name=None):

    self.clear()

    self.sp.setData(
      x=x,
      y=y,
      data = data,
      symbol='o',
      pxMode=True,
      pen=pg.mkPen({'color':'#000000'}),
      brush=pg.mkBrush(pg.mkColor('#00FF33')),
      size=10,
      hoverable=True,
      tip = self.tooltip,
      hoverPen = pg.mkPen('r', width=3),
      hoverBrush = pg.mkBrush('b'),
      hoverSize=12,
      name = name
    )
    self.sp.setZValue(10)

    self.addItem(self.sp)

    
  
  def tooltip(self, x, y, data):

    if self.sp.opts['hoverable']:
      if data:
        return f'{data}: ({x:.2f}, {y:.2f})'
      else:
        return f'{x}: {y:.2f}'
    else:
      return ''

class ScatterPlot2(pg.PlotItem):

  def __init__(self, line = False):
    pg.PlotItem.__init__(self, enableMenu=False)
    self.sp = pg.ScatterPlotItem()
    self.sp2 = pg.ScatterPlotItem()
    self.line = line
    if self.line:
      self.lineItem = pg.PlotCurveItem()
      self.lineItem2 = pg.PlotCurveItem()
    self.showGrid(True, True, 0.85)
    return
  

  def plot_data(self, x, y, y2, data = None, data2 = None, name=None, name2 = None):

    self.clear()
    self.addLegend(offset=(5,5), brush=pg.mkBrush('#FFFFFF'))

    self.sp.setData(
      x=x,
      y=y,
      data = data,
      symbol='o',
      pxMode=True,
      pen=pg.mkPen({'color':'#000000'}),
      brush=pg.mkBrush(pg.mkColor('#00FF33')),
      size=10,
      hoverable=True,
      tip = self.tooltip,
      hoverPen = pg.mkPen('r', width=3),
      hoverBrush = pg.mkBrush('b'),
      hoverSize=12,
      name = name
    )
    self.sp.setZValue(10)

    self.addItem(self.sp)

    self.sp2.setData(
      x=x,
      y=y2,
      data = data2,
      symbol='o',
      pxMode=True,
      pen=pg.mkPen({'color':'#000000'}),
      brush=pg.mkBrush(pg.mkColor('#883A33')),
      size=10,
      hoverable=True,
      tip = self.tooltip,
      hoverPen = pg.mkPen('r', width=3),
      hoverBrush = pg.mkBrush('b'),
      hoverSize=12,
      name = name2
    )
    self.sp2.setZValue(10)

    self.addItem(self.sp2)
  
    if self.line:
      self.lineItem.setData(
        x=x,
        y=y,
        pen=pg.mkPen({'color':'#000000'})
      )
      self.lineItem2.setData(
        x=x,
        y=y2,
        pen=pg.mkPen({'color':'#000000'})
      )
      self.lineItem.setZValue(5)
      self.lineItem2.setZValue(5)
      self.addItem(self.lineItem)
      self.addItem(self.lineItem2)

  def tooltip(self, x, y, data):

    
    return ''