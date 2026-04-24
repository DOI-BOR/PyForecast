import numpy as np
import pandas as pd
import pyqtgraph as pg

from Utilities import DateAxis


class TimeSliderPlot(pg.PlotItem):

    def __init__(self, parent, **kwargs):

        super().__init__(parent, **kwargs)
        self.setMenuEnabled(False)
        self.getViewBox().setMouseEnabled(x=False, y=False)

        b_axis = DateAxis.DateAxisItem(orientation='bottom')
        b_axis.attachToPlotItem(self)

        self.region = pg.LinearRegionItem(brush=pg.mkBrush(100, 100, 100, 30))
        self.region.setZValue(10)
        self.addItem(self.region)

    def updateViews(self):
        self.getViewBox().setGeometry(self.vb.sceneBoundingRect())
        self.getViewBox().linkedViewChanged(self.vb, self.getViewBox().XAxis)

    def plot(self, data, colors):
        if isinstance(data, pd.DataFrame):
            self.plot_dataframe(data, colors)
        if isinstance(data, list):
            self.plot_dataframe(pd.DataFrame([0], index=pd.DatetimeIndex(
                [pd.to_datetime('2000-01-01')])), colors)

    def plot_dataframe(self, dataframe, colors):

        self.clear()

        # Convert the index into unix integer time
        x = dataframe.index.values

        if not isinstance(x[0], (int, np.integer)):
            x = (dataframe.index.astype(np.int64) // 10 ** 9).values

        # Plot the data
        for i, col in enumerate(dataframe.columns):
            pg.PlotItem.plot(
                self,
                x=x,
                y=dataframe[col].values,
                clear=True if i == 0 else False,
                pen=pg.mkPen(colors[i])
            )

        self.getViewBox().setLimits(
            xMin=np.nanmin(x),
            xMax=np.nanmax(x),
            yMin=dataframe.min().min(),
            yMax=dataframe.max().max()
        )
        self.getViewBox().setRange(
            xRange=(np.nanmin(x), np.nanmax(x)),
            yRange=(dataframe.min().min(), dataframe.max().max())
        )

        self.region.setRegion([np.nanmin(x), np.nanmax(x)])
        self.region.setBounds([np.nanmin(x), np.nanmax(x)])
        self.region.setZValue(-10)

        # Re-Add the region (it got deleted when we cleared ["self.clear()"])
        self.addItem(self.region)
