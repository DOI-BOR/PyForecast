from Plots.Common import pg, CurveItem, ScatterItem, TimeSeriesLegend, takeClosest
from Utilities.ColorCycler import ColorCycler
from Utilities import DateAxis
import pandas as pd
import numpy as np
from PyQt5.QtCore import QPoint

class Plot(pg.GraphicsLayoutWidget):

  def __init__(self):

    pg.GraphicsLayoutWidget.__init__(self)
    
    # Initialize the upper and lower plots
    self.upper_plot = self.addPlot(row=0, col=0, rowspan=8, colspan=1)
    self.upper_plot.setMenuEnabled(False)

    self.lower_plot = self.addPlot(row=8, col=0, rowspan=1, colspan=1)
    self.lower_plot.setMenuEnabled(False)
    self.lower_plot.setMouseEnabled(x=False, y=False)

    # Set up Axes
    self.upper_x_axis = DateAxis.DateAxisItem(orientation='bottom')
    self.upper_x_axis.attachToPlotItem(self.upper_plot)
    self.lower_x_axis = DateAxis.DateAxisItem(orientation='bottom')
    self.lower_x_axis.attachToPlotItem(self.lower_plot)

    # Set up draggable slider region
    self.region = pg.LinearRegionItem(brush=pg.mkBrush(100, 100, 100, 50))
    self.region.setZValue(10)
    self.lower_plot.addItem(self.region)

    # Intialize the data items
    color_cycler = ColorCycler()
    
    self.upper_items_crv = [CurveItem(color_cycler.next()) for i in range(50)]
    self.lower_items_crv = [CurveItem(c.color) for c in self.upper_items_crv]
    self.crv_hover_points = [ScatterItem(c.color) for c in self.upper_items_crv]
    self.upper_items_sct = [ScatterItem(color_cycler.next()) for i in range(50)]
    self.lower_items_sct = [ScatterItem(s.color) for s in self.upper_items_sct]

    # SET MINIMUM ROW SIZE FOR ROWS
    _ = [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]

    # Legend
    self.legend = TimeSeriesLegend(size=None, offset=(30,30))
    self.legend.setParentItem(self.upper_plot.vb)


    self.region.sigRegionChanged.connect(self.updatePlot)
    self.upper_plot.sigRangeChanged.connect(self.updateRegion)
    self.upper_plot.scene().sigMouseMoved.connect(self.mouseMoved)

    self.legend_strings = []
    self.axis_label = ''

    return
  
  def updatePlot(self):

    self.region.setZValue(10)
    newRegion = self.region.getRegion()
    if not any(np.isinf(newRegion)):
        self.upper_plot.setXRange(*self.region.getRegion(), padding=0)
        for i in range(len(self.upper_plot.items)):
          self.upper_plot.items[i].viewRangeChanged()
          
    return

  def updateRegion(self, window, viewRange):

    self.region.setZValue(10)
    self.region.setRegion(viewRange[0])
    for i in range(len(self.upper_plot.items)):
      self.upper_plot.items[i].viewRangeChanged()

    return
  
  
  def mouseMoved(self,event):

    pos = QPoint(int(event.x()), int(event.y()))
    mouse_point = self.upper_plot.vb.mapSceneToView(pos)
    x_ = mouse_point.x()
    idx = int(x_ - x_%86400)
    h_cnt = 0

    for i, item in enumerate(self.upper_plot.listDataItems()):

      if item in self.crv_hover_points:
        continue

      if isinstance(item, ScatterItem):
        
        x_data, y_data = item.getData()
        mask = ~np.isnan(y_data)
        x_data = x_data[mask]
        y_data = y_data[mask]
        closest_x, closest_idx = takeClosest(x_data, idx)
        y = y_data[closest_idx]
        self.legend.items[i-h_cnt][1].setText(item.name().replace('-----', f'<span style="color:red">{y:,.2f}</span>'.replace('nan', '-----')))

      else:

        closest_x, closest_idx = takeClosest(item.getData()[0], idx)
        y = item.getData()[1][closest_idx]
        self.legend.items[i-h_cnt][1].setText(item.name().replace('-----', f'<span style="color:red">{y:,.2f}</span>'.replace('nan', '-----')))
        if item in self.upper_items_crv:
          if not np.isnan(closest_x):
            if not np.isnan(y):
              self.crv_hover_points[h_cnt].setData(x=[closest_x], y=[y])
          h_cnt += 1
  
  def clear_all(self):

    self.legend.clear()

    self.upper_plot.clear()
    self.lower_plot.clear()
    
    self.legend_strings = []
    self.axis_label = ''

    for i in range(len(self.upper_items_crv)):
      self.upper_items_crv[i].clear()
      self.lower_items_sct[i].clear()
      self.upper_items_sct[i].clear()
      self.lower_items_crv[i].clear()
  
  def plot(self, datasets = []):

    self.clear_all()

    min_x = np.inf
    max_x = -1*np.inf
    units = []

    for i, dataset in enumerate(datasets):

      units.append(dataset.display_unit.id)

      # Convert to display_unit
      scale, offset = dataset.raw_unit.convert_to(dataset.display_unit)
      data = dataset.data*scale + offset

      # trim to first valid index
      f_v_i = data.first_valid_index()
      if f_v_i is None:
        continue

      x_vals = ((data.index.astype('int64'))/10**9).values
      y_vals = data.values.flatten()
      name = f'{dataset.name} ----- [{dataset.display_unit.id}]'

      nan_cnt = data.loc[f_v_i:].isna().sum()
      if isinstance(nan_cnt, pd.Series):
        nan_cnt = nan_cnt.iloc[0]

      # Check to see if we need a scatter plot item instead of a line item.
      if int(nan_cnt) > 0.75*len(data.loc[f_v_i:]):

        self.upper_items_sct[i].setData(x = x_vals, y = y_vals, name=name)
        self.lower_items_sct[i].setData(x = x_vals, y = y_vals)
        self.upper_plot.addItem(self.upper_items_sct[i])
        self.lower_plot.addItem(self.lower_items_sct[i])
        self.legend.addItem(self.upper_items_sct[i], name)

      else:

        self.upper_items_crv[i].setData(x = x_vals, y = y_vals, name=name)
        self.lower_items_crv[i].setData(x = x_vals, y = y_vals)
        self.upper_plot.addItem(self.upper_items_crv[i])
        self.lower_plot.addItem(self.lower_items_crv[i])
        self.legend.addItem(self.upper_items_crv[i], name)
        self.upper_plot.addItem(self.crv_hover_points[i])

      min_x = min(np.nanmin(x_vals), min_x)
      max_x = max(np.nanmax(x_vals), max_x)

    self.region.setRegion([min_x, max_x])
    self.region.setBounds([min_x, max_x])
    self.lower_plot.addItem(self.region)
    self.upper_plot.autoRange()
    self.lower_plot.autoRange()
    self.upper_plot.getAxis('left').setLabel(' '.join(list(set(units))), **{'font-weight':'bold', 'font-size':'x-large', 'font-family':'Arial'})
    self.upper_plot.getAxis('left').setGrid(185)
    self.upper_plot.getAxis('left').setZValue(-1)
    self.upper_plot.getAxis('bottom').setGrid(185)
    self.upper_plot.getAxis('bottom').setZValue(-1)
      