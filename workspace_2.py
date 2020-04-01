
# Import Libraries
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import pandas as pd
from datetime import datetime
from bisect import bisect_left

# Set the widget options
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Create a custom legend for the Spaghetti Plots
class SpaghettiLegend(pg.LegendItem):

    def __init__(self, size = None, offset = None):
        
        # Instantiate the legend Item
        pg.LegendItem.__init__(self, size, offset)
    
    def addItem(self, item, name):

        # Instantiate a Label Item using the supplied Name
        label = pg.graphicsItems.LegendItem.LabelItem(name, justify='left')

        # Create the sample image to place next to the legend Item
        if isinstance(item, pg.graphicsItems.LegendItem.ItemSample):
            sample = item
            sample.setFixedWidth(20)
        else:
            sample = pg.graphicsItems.LegendItem.ItemSample(item)     
            sample.setFixedWidth(20)   

        # Add the item to the legend and update the size
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(label, row, 1)
        self.updateSize()
    
    def updateSize(self):

        if self.size is not None:
            return
            
        height = 0
        width = 0

        for sample, label in self.items:
            height += max(sample.boundingRect().height(), label.height()) + 3
            width = max(width, sample.boundingRect().width()+label.width())

        self.setGeometry(0, 0, width+60, height)


# Create a custom Legend for the Time Series Plots
class TimeSeriesLegend(pg.LegendItem):

    def __init__(self, size = None, offset = None):
        
        # Instantiate the legend Item
        pg.LegendItem.__init__(self, size, offset)
    
    def addItem(self, item, name):

        # Instantiate a Label Item using the supplied Name
        label = pg.graphicsItems.LegendItem.LabelItem(name, justify='left')

        # Create the sample image to place next to the legend Item
        if isinstance(item, pg.graphicsItems.LegendItem.ItemSample):
            sample = item
            sample.setFixedWidth(20)
        else:
            sample = pg.graphicsItems.LegendItem.ItemSample(item)     
            sample.setFixedWidth(20)   

        # Add the item to the legend and update the size
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(label, row, 1)
        self.updateSize()
    
    def updateSize(self):

        if self.size is not None:
            return
            
        height = 0
        width = 0

        for sample, label in self.items:
            height += max(sample.boundingRect().height(), label.height()) + 3
            width = max(width, sample.boundingRect().width()+label.width())

        self.setGeometry(0, 0, width+60, height)


# Create a special Axis to display below the Spaghetti plots
class SpaghettiAxis(pg.AxisItem):

    def __init__(self, *args, **kwargs):

        # Instantiate the axisItem
        pg.AxisItem.__init__(self, *args, **kwargs)
    
    def tickSpacing(self, minValue, maxValue, size):

        # Set the tick spacing based on the current zoom level
        spacing = max([1, int(0.1*(maxValue - minValue) + 22)])
        return [(spacing, 0), (spacing, 0)]
    
    def tickStrings(self, values, scale, spacing):
        
        # Set the tick strings to be in the format MMM-DD (e.g. JAN-23)
        values = [value + 273 if value < 92 else value - 91 for value in values]
        return [datetime.strptime('2010-{:03d}'.format(int(value)), '%Y-%j').strftime("%b-%d") for value in values]


# Create a special Axis to display below the Time Series Plots
class DateTimeAxis(pg.AxisItem):

    def __init__(self, *args, **kwargs):

        # Instantiate the axisItem
        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickSpacing(self, minValue, maxValue, size):

        # Set the tick spacing based on the current zoom level
        spacing = max([1, int(0.27*(maxValue - minValue) + 22)])
        return [(spacing, 0), (spacing, 0)]
    
    def tickStrings(self, values, scale, spacing):

        # Set the datetime display based on the zoom level
        if spacing > 7*365.24*86400:
            return [datetime.utcfromtimestamp(value).strftime('%Y-%m') for value in values]
        return [datetime.utcfromtimestamp(value).strftime('%Y-%m-%d') for value in values]


# Create a Graphics Layout Widget to display all the plots in one widget
class DataTabPlots(pg.GraphicsLayoutWidget):
    
    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent
        [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]
        
        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = self.parent.datasetTable
        self.dataTable = self.parent.dataTable

        # Create a color cyler
        self.colorCycler = [
            (255, 61, 0), 
            (255, 214, 0), 
            (0, 200, 83), 
            (255, 103, 32), 
            (0, 145, 234), 
            (170, 0, 255), 
            (141, 110, 99), 
            (198, 255, 0), 
            (29, 233, 182), 
            (136, 14, 79)
        ]

        # Instantiate the plots
        self.timeSeriesPlot = TimeSeriesLinePlot(self)
        self.timeSliderPlot = TimeSliderPlot(self)
        #self.spaghettiPlot = SpaghettiPlot(self)

        # Add the plots
        self.addItem(self.timeSeriesPlot, row=0, col=0, rowspan=6)
        self.addItem(self.timeSliderPlot, row=6, col=0, rowspan=2)
        #self.addItem(self.spaghettiPlot, row=9, col=0, rowspan=5)
    
        return
    
    def displayDatasets(self, datasets):
        
        # If there is more than one dataset, 
        self.timeSeriesPlot.displayDatasets(datasets)
        self.timeSliderPlot.displayDatasets(datasets)
        #self.spaghettiPlot.displayDatasets(datasets[0])

        return



# The Spaghetti Plot displays time series data as a layered spaghetti hydrograph.
class SpaghettiPlot(pg.PlotItem):

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self, axisItems={"bottom":SpaghettiAxis(orientation = "bottom")})
        self.parent = parent
        self.setMenuEnabled(False)

        # Set the Range and limits for the plot
        self.setXRange(1, 366, padding=0)
        self.setLimits(xMin=1, xMax=366)

        # Create 10 PlotCurveItems to work with
        self.items_ = [pg.PlotCurveItem(parent = self, pen = (*parent.colorCycler[i%10],150), antialias = True) for i in range(100)]

        return

    
    def displayDatasets(self, dataset):
        
        # Clear any existing datasets
        self.clear()

        # Process the Data
        data = self.parent.dataTable.loc[(slice(None), dataset), 'Value'].unstack()
        data['Year'] = [i.year if i.month < 10 else i.year + 1 for i in data.index]
        data['Day'] = [i.dayofyear - 273 if i.month >=10 else i.dayofyear+92 for i in data.index]
        self.yMin = float(data[dataset].min())
        self.yMax = float(data[dataset].max())
        data = data.pivot_table(values=dataset, index='Day', columns='Year')

        # Set the data for the i-th PlotCurveItem
        for i, year in enumerate(data.columns):

            self.items_[i].setData(list(data.index), list(data[year]))

            # Add the item to the plot
            self.addItem(self.items_[i])
        
        # Set the plot limits and current x range
        self.setLimits(

            xMin = 1,
            xMax = 366,
            yMin = self.yMin,
            yMax = self.yMax,

        )
        self.setXRange(1, 366, padding=0)

        # Show the grid
        self.showGrid(True, True, 0.85)

        return


# The Time slider plot displays a smaller version of the Period of Record data with a Time Slider Control overlay
class TimeSliderPlot(pg.PlotItem):

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self, axisItems={"bottom":DateTimeAxis(orientation = "bottom")})
        self.parent = parent
        self.setMenuEnabled(False)

        # Create 10 PlotCurveItems to work with
        self.items_ = [pg.PlotCurveItem(parent = self, pen = parent.colorCycler[i], antialias = True) for i in range(10)]

        # Create a slider region
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)

        # Instantiate Limits
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf
        
        # Make region interactive
        self.region.sigRegionChanged.connect(self.updatePlot)
        self.parent.timeSeriesPlot.sigRangeChanged.connect(self.updateRegion)

        # Add the slider region
        self.addItem(self.region)

        return

    
    # Changes the bounds of the Time Series Plot when the slider is moved
    def updatePlot(self):

        self.region.setZValue(10)
        self.parent.timeSeriesPlot.setXRange(*self.region.getRegion(), padding=0)
        [self.parent.timeSeriesPlot.items[i].viewRangeChanged() for i in range(len(self.parent.timeSeriesPlot.items))]

        return

    
    # Changes the bounds of the slider when the Time Series Plot is moved
    def updateRegion(self, window, viewRange):

        self.region.setZValue(10)
        self.region.setRegion(viewRange[0])
        [self.parent.timeSeriesPlot.items[i].viewRangeChanged() for i in range(len(self.parent.timeSeriesPlot.items))]

        return


    def displayDatasets(self, datasets):
        """
        datasets = [100103, 313011, ...]
        """
        
        # Clear any existing datasets
        self.clear()

        # Create a new item for each dataset
        for i, dataset in enumerate(datasets):

            # Get the Data
            x = np.array(self.parent.dataTable.loc[(slice(None), dataset), 'Value'].index.levels[0].astype('int64'))/1000000000 # Dates in seconds since epoch
            y = self.parent.dataTable.loc[(slice(None), dataset), 'Value'].values

            # Set new limits
            self.xMax = max(self.xMax, max(x))
            self.xMin = min(self.xMin, min(x))
            self.yMax = max(self.yMax, max(y))
            self.yMin = min(self.yMin, min(y))

            # Set the data for the i-th PlotCurveItem
            self.items_[i].setData(x, y)

            # Add the item to the plot
            self.addItem(self.items_[i])

        # Set the data limits and the current ranges and bounds
        self.setLimits(

            xMin = self.xMin,
            xMax = self.xMax,
            yMin = self.yMin,
            yMax = self.yMax,
            minXRange = self.xMax - self.xMin,
            minYRange = self.yMax - self.yMin

        )

        self.region.setRegion([self.xMin, self.xMax])
        self.region.setBounds([self.xMin, self.xMax])
        self.region.setZValue(-10)

        # Re-Add the region (it got deleted when we cleared ["self.clear()"])
        self.addItem(self.region)

        return


# Time Series Plot to display Time Series Data
class TimeSeriesLinePlot(pg.PlotItem):

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self, axisItems={"bottom":DateTimeAxis(orientation = "bottom")})
        self.parent = parent
        self.setMenuEnabled(False)

        # Instantiate Limits
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # Instantiate a legend
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # Add interaction
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)

        # Create 10 PlotCurveItems to work with
        self.items_ = [pg.PlotCurveItem(parent = self, pen = parent.colorCycler[i], antialias = True) for i in range(10)]
        self.circleItems_ = [pg.ScatterPlotItem(size=10, alpha=1, brush=parent.colorCycler[i]) for i in range(10)]

        return
    
    def mouseMoved(self, event):
        
        # Get the mouse position
        pos = QtCore.QPoint(event.x(), event.y())

        # Check that the overall widget actually contains the mouse point
        if self.sceneBoundingRect().contains(pos):

            # Get the mousepoint in relation to the plot
            mousePoint = self.vb.mapSceneToView(pos)
            x_ = mousePoint.x()
            y_ = mousePoint.y()

            # Round x value to the nearest date
            idx = int(x_ - x_%86400)
            ts = datetime.utcfromtimestamp(idx).strftime('%Y-%m-%d')

            # Iterate over the active items and display the data points in the legend
            for i, item in enumerate(self.items_):
                if i < len(self.datasets):

                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData==date)
                    yval = round(item.yData[idx2][0],2)
                    self.legend.items[i][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circleItems_[i].setData([date], [yval])
            
        


    def displayDatasets(self, datasets):
        """
        datasets = [100103, 313011, ...]
        """
        
        # Clear any existing datasets
        self.clear()

        # Keep track of current datasets
        self.datasets = datasets

        # Create a new item for each dataset
        for i, dataset in enumerate(datasets):

            # Get the Dataset Title
            d = self.parent.datasetTable.loc[dataset]
            title = d['DatasetName'] + ': ' + d['DatasetParameter']

            # Get the Data
            x = np.array(self.parent.dataTable.loc[(slice(None), dataset), 'Value'].index.levels[0].astype('int64'))/1000000000 # Dates in seconds since epoch
            y = self.parent.dataTable.loc[(slice(None), dataset), 'Value'].values

            # Set new limits
            self.xMax = max(self.xMax, max(x))
            self.xMin = min(self.xMin, min(x))
            self.yMax = max(self.yMax, max(y))
            self.yMin = min(self.yMin, min(y))

            # Set the data for the i-th PlotCurveItem
            self.items_[i].setData(x, y, name = title)
            self.items_[i].units = d['DatasetUnits']

            # Add the item to the plot
            self.addItem(self.items_[i])
            self.addItem(self.circleItems_[i])
        
        
        
        self.setLimits(

            xMin = self.xMin,
            xMax = self.xMax,
            yMin = self.yMin,
            yMax = self.yMax,
        
        )

        # Show the grid
        self.showGrid(True, True, 0.85)

        return





def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """

    # Gets the left-most closest number in the list
    pos = bisect_left(myList, myNumber)

    # Return the closest number
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before





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

    dates = pd.date_range('1999-10-01', '2001-09-30', freq='D')
    y1 = np.sin(0.5*np.array(range(len(dates)))) + np.random.randint(-4, 5)
    y2 = np.cos(0.2*np.array(range(len(dates))))

    for i in range(len(dates)):
        if i == 40:
            # Test case for NaNs
            mw.dataTable.loc[(dates[i], 100000), 'Value'] = np.nan
        else:
            mw.dataTable.loc[(dates[i], 100000), 'Value'] = y1[i]
        mw.dataTable.loc[(dates[i], 100001), 'Value'] = y2[i]

    dp = DataTabPlots(mw)
    mw.setCentralWidget(dp)
    dp.displayDatasets([100000, 100001])
    mw.show()
    sys.exit(app.exec_())

    