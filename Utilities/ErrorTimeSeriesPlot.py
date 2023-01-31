import pyqtgraph as pg
from Utilities import PlotUtils
import pandas as pd
import numpy as np
from PyQt5.QtCore import *

class ErrorPlot(pg.PlotItem):

  def __init__(self):

    pg.PlotItem.__init__(self, enableMenu=False)
    return

  def plot(self, x, y, data = None):

    self.clear()
    self.sp = pg.BarGraphItem()
    self.sp.setData(
      x=x,
      y=y,
      symbol='h',
      pxMode=True,
      size=14,
      hoverable=True if data else False,
      tip = self.tooltip 
    )
    self.addItem(self.sp)
  
  def tooltip(self, x, y, data):
    if self.sp.opts['hoverable']:
      return f'{data}: ({x:.2f}, {y:.2f})'
    else:
      return ''