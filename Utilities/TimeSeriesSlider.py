import pyqtgraph as pg
from Utilities import DateAxis

import pandas as pd
import numpy as np

class TimeSliderPlot(pg.PlotItem):


  def __init__(self, parent = None):

    self.parent = parent
    pg.PlotItem.__init__(self)
    self.setMenuEnabled(False)
    self.setMouseEnabled(x=False, y=False)

    b_axis = DateAxis.DateAxisItem(orientation='bottom')
    b_axis.attachToPlotItem(self)

    self.region = pg.LinearRegionItem(brush=pg.mkBrush(100, 100, 100, 50))
    self.region.setZValue(10)
    self.addItem(self.region)

  def updateViews(self):
    self.viewbox_axis_2.setGeometry(self.vb.sceneBoundingRect())
    self.viewbox_axis_2.linkedViewChanged(self.vb, self.viewbox_axis_2.XAxis)

  def plot(self, data, colors):
    if isinstance(data, pd.DataFrame):
      self.plot_dataframe(data, colors)
    if isinstance(data, list):
      self.plot_dataframe(pd.DataFrame([0],index=pd.DatetimeIndex([pd.to_datetime('2000-01-01')])), colors)
    
  def plot_dataframe(self, dataframe, colors):

    self.clear()
    
    # Convert the index into unix integer time
    x = dataframe.index.values
    
    if not isinstance(x[0], (int, np.integer)):
      x = (dataframe.index.astype(np.int64)//10**9).values
    
    # Plot the data
    for i, col in enumerate(dataframe.columns):
      pg.PlotItem.plot(self, x=x, y=dataframe[col].values, clear=True if i==0 else False, pen=pg.mkPen(colors[i]))


    self.setLimits(xMin=np.nanmin(x), xMax=np.nanmax(x), yMin=dataframe.min().min(), yMax=dataframe.max().max())
    self.setRange(xRange=(np.nanmin(x), np.nanmax(x)), yRange=(dataframe.min().min(), dataframe.max().max()))

    self.region.setRegion([np.nanmin(x), np.nanmax(x)])
    self.region.setBounds([np.nanmin(x), np.nanmax(x)])
    self.region.setZValue(-10)

    # Re-Add the region (it got deleted when we cleared ["self.clear()"])
    self.addItem(self.region)
  
  