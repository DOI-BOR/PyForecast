
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import pandas as pd
from datetime import datetime
from bisect import bisect_left

class DataTabPlots(pg.GraphicsLayoutWidget):
    """
    """

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent
        
        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = self.parent.datasetTable
        self.dataTable = self.parent.dataTable

        # Instantiate the 2 plots
        self.timeSeriesPlot = TimeSeriesLinePlot(self)
        self.addItem(self.timeSeriesPlot)
    
        return

class SpaghettiPlot(pg.PlotItem):
    """
    """

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self)
        self.parent = parent

        return

class TimeSeriesLinePlot(pg.PlotItem):
    """
    """

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self)
        self.parent = parent

        # Create a color cyler
        colorCycler = ["#FF3D00", "#FFD600", "#00C853", "#FF6720", "#0091EA", "#AA00FF", "#8D6E63", "#C6FF00", "#1DE9B6", "#880E4F"]

        # Create 10 PlotCurveItems to work with
        self.items_ = [pg.PlotCurveItem(parent = self, pen = colorCycler[i], antialias = True) for i in range(10)]

        return

    def displayDatasets(self, datasets):
        """
        datasets = [100103, 313011, ...]
        """
        
        # Clear any existing datasets
        self.clear()

        # Create a new item for each dataset
        for i, dataset in enumerate(datasets):

            # Get the Dataset Title
            d = self.parent.datasetTable.loc[dataset]
            title = d['DatasetName'] + ': ' + d['DatasetParameter']

            # Get the Data
            x = list(self.parent.dataTable.loc[(slice(None), dataset), 'Value'].index.levels[0].astype('int64')) # Dates in seconds since epoch
            y = self.parent.dataTable.loc[(slice(None), dataset), 'Value'].values

            # Set the data for the i-th PlotCurveItem
            self.items_[i].setData(x, y)

            # Add the item to the plot
            self.addItem(self.items_[i])

        return

if __name__ == '__main__':

    import sys

    # Debugging dataset
    app = QtWidgets.QApplication(sys.argv)

    mw = QtWidgets.QMainWindow()
    
    mw.datasetTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR, ETC
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                "DatasetParameterCode",     # e.g. avgt
                'DatasetUnits',             # e.g. CFS
                
            ],
        ) 
    
    mw.datasetTable.loc[100000] = ["RESERVOIR", "GIBR", "Gibson Reservoir", "USBR", "Inflow", "in", 'cfs']
    mw.datasetTable.loc[100001] = ["STREAMGAGE", "0120332", "Sun River Near Augusta", "USGS", "Streamflow", "00060", 'cfs']

    mw.dataTable =  pd.DataFrame(
            index = pd.MultiIndex(
                levels=[[],[],],
                codes = [[],[],],
                names = [
                    'Datetime',             # E.g. 1998-10-23
                    'DatasetInternalID'     # E.g. 100302
                    ]
            ),
            columns = [
                "Value",                    # E.g. 12.3, Nan, 0.33
                "EditFlag"                  # E.g. True, False -> NOTE: NOT IMPLEMENTED
                ],
            dtype=float
        )
    mw.dataTable['EditFlag'] = mw.dataTable['EditFlag'].astype(bool)

    for date in pd.date_range('2000-10-01', '2001-01-01', freq='D'):
        mw.dataTable.loc[(date, 100000), 'Value'] = np.random.randint(100, 1000)
        mw.dataTable.loc[(date, 100001), 'Value'] = np.random.randint(700, 1000)

    
    dp = DataTabPlots(mw)
    mw.setCentralWidget(dp)
    dp.timeSeriesPlot.displayDatasets([100000, 100001])
    mw.show()
    sys.exit(app.exec_())

    
