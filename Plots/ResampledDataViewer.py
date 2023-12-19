from Plots.Common import pg, BarItem, ScatterItem, CurveItem
from Utilities.ColorCycler import ColorCycler
from Utilities import DateAxis
import pandas as pd
import numpy as np
from scipy.stats import linregress
from PyQt5.QtCore import QPoint


class Plot(pg.GraphicsLayoutWidget):

    
    def __init__(self):

        pg.GraphicsLayoutWidget.__init__(self)
        
        # Initialize the upper and lower plots
        self.upper_plot = self.addPlot(row=0, col=0, rowspan=3, colspan=2)
        self.upper_plot.setMenuEnabled(False)
        self.upper_plot.setTitle('<strong>Data</strong>')
        self.upper_plot.getAxis('left').setLabel('Value')
        self.upper_plot.getAxis('bottom').setLabel('Year')

        self.lower_plot = self.addPlot(row=3, col=0, rowspan=6, colspan=1)
        self.lower_plot.setMenuEnabled(False)
        self.lower_plot.setMouseEnabled(x=False, y=False)
        self.lower_plot.setTitle('<strong>Correlation w/ Forecast Target</strong>')
        self.lower_plot.getAxis('left').setLabel('Fcst Target')
        self.lower_plot.getAxis('bottom').setLabel('Dataset')

        self.lower_label = self.addLabel(text='No dataset selected', row=3, col=1, rowspan=6, colspan=1)

        # SET MINIMUM ROW SIZE FOR ROWS
        _ = [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]

        # Intialize the data items
        color_cycler = ColorCycler()

        # Data items
        self.upper_items_bar = BarItem(color_cycler.next(), x=[1], height=[1], width=0.9)
        self.lower_items_sct = ScatterItem(color_cycler.col, hoverable=False)
        self.lower_items_line = CurveItem(color_cycler.col, fillLevel=None)

    def clear_all(self):
        
        self.upper_plot.clear()
        self.lower_plot.clear()
        
        return

    def plot(self, dataset, target_dataset):
    
        self.clear_all()
        
        # Compute statistics between the target and the dataset
        common_idx = dataset.data.index.intersection(target_dataset.data.index)
        data_1 = dataset.data.loc[common_idx]
        data_2 = target_dataset.data.loc[common_idx]
        stats = linregress(data_1.values.flatten(), data_2.values.flatten())
        statsLine_y = [stats.slope*min(data_1) + stats.intercept, stats.slope*max(data_1) + stats.intercept]
        statsLine_x = [min(data_1), max(data_1)]


        self.upper_items_bar.setOpts(**{
            'x':data_1.index,
            'height':data_1.values.flatten()
        })

        self.lower_items_sct.setData(x=data_1.values.flatten(), y=data_2.values.flatten())
        self.lower_items_line.setData(x=statsLine_x, y=statsLine_y)

        self.upper_plot.addItem(self.upper_items_bar)
        self.lower_plot.addItem(self.lower_items_sct)
        self.lower_plot.addItem(self.lower_items_line)

        if stats.pvalue > 0.05:
            flavor_text = "It is probable that there is <strong>no</strong><br> correlation between these 2 datasets."
        elif stats.rvalue > 0.7:
            flavor_text = "There is a definite correlation<br> between these 2 datasets."
        else:
            flavor_text = "There may be a weak correlation<br> between these 2 datasets.<br> It may be non-linear."

        self.lower_label.setText(f"""
        <div style="font-family:Arial">
            <span style="font-weight:bold">Correlation Stats</span><br>
            <span style="font-weight:bold">R2:</span> {stats.rvalue:0.2f}<br>
            <span style="font-weight:bold">P-val:</span> {stats.pvalue:0.2f}<br>
            {flavor_text}
        </div> """)
    
        return


