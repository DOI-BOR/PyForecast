
# Import Libraries
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import importlib
from resources.GUI.CustomWidgets import PyQtGraphOverrides
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
from bisect import bisect_left

# Set the widget options
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
try:
    pg.setConfigOptions(useOpenGL = True)
except:
    print("not using OpenGL for plots.")


pg.PlotItem.clear = PyQtGraphOverrides.PLOTITEM_clear_
pg.InfiniteLine.setMouseHover = PyQtGraphOverrides.INFINITELINE_setMouseHover_
pg.InfiniteLine.mouseDragEvent = PyQtGraphOverrides.INFINITELINE_mouseDragEvent_

# NEEDS SOME WORK
#pg.LinearRegionItem.hoverEvent = PyQtGraphOverrides.LINEARREGION_hoverEvent_
#pg.LinearRegionItem.mouseDragEvent = PyQtGraphOverrides.LINEARREGION_mouseDragEvent_

EQUIVALENCY_LISTS = [
    ["INCHES", "INCH", "IN", "IN.", '"'],
    ['FEET', 'FOOT', 'FT', 'FT.', "'"],
    ['CFS', 'CUBIC FEET PER SECOND', 'FT3/S', 'FT3/SEC'],
    ['ACRE-FEET', 'AF', 'AC-FT', 'ACRE-FT'],
    ['KAF', 'THOUSAND ACRE-FEET', 'KAC-FT', 'THOUSAND ACRE-FT'],
    ['DEGREES', 'DEGF', 'DEG. FAHRENHEIT', 'DEGC', 'DEGREES FAHRENHEIT', 'DEGREES CELCIUS', 'DEG FAHRENHEIT', 'DEG CELCIUS', 'DEG. CELCIUS'],
    ['PERCENT', '%', 'PCT', 'PCT.'],
    ['UNITLESS'],
]



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

class DateTimeAxis_years(pg.AxisItem):

    def __init__(self, *args, **kwargs):

        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):

        return [datetime.utcfromtimestamp(value).strftime('%Y') for value in values]

# Create a graphics layout for the ModelTab graphs
class ModelTabPlots(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None, objectName = None):

        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.parent = parent

        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = self.parent.parent.datasetTable
        self.dataTable = self.parent.parent.dataTable

        self.plot = dataReductionPlot(self)

        self.addItem(self.plot, 0, 0)
    
    def clearPlots(self):
        """
        Clears the plots of any data
        """
        self.plot.clear()

        return

    def displayDatasets(self, datasets, period, method, customFunction):
        
        # If there is more than one dataset, 
        self.plot.displayDataset(datasets, period, method, customFunction)

        return

# Create a Graphics Layout Widget to display all the plots in one widget
class DataTabPlots(pg.GraphicsLayoutWidget):
    
    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent
        [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]
        
        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = self.parent.parent.datasetTable
        self.dataTable = self.parent.parent.dataTable

        # Create a color cyler
        self.colors = [
            (255, 61, 0), 
            (0, 145, 234),
            (255, 214, 0), 
            (0, 200, 83), 
            (255, 103, 32), 
            (170, 0, 255), 
            (141, 110, 99), 
            (198, 255, 0), 
            (29, 233, 182), 
            (136, 14, 79)
        ]
        self.penCycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brushCycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]

        # Instantiate the plots
        self.timeSeriesPlot = TimeSeriesLinePlot(parent=self)
        self.timeSliderPlot = TimeSliderPlot(self)
        #self.spaghettiPlot = SpaghettiPlot(self)

        # Add the plots
        self.addItem(self.timeSeriesPlot, row=0, col=0, rowspan=7)
        self.addItem(self.timeSliderPlot, row=7, col=0, rowspan=2)
    
        return

    def clearPlots(self):
        """
        Clears the plots of any data
        """
        self.timeSeriesPlot.clear()
        self.timeSliderPlot.clear()

        return

    
    def displayDatasets(self, datasets):
        """
        Formats DataTab data for plotting with the TimeSeriesPlot class

        Parameters
        ----------
        datasets: list
            List of InternalDatasetIDs to be plotted

        Returns
        -------
        None.

        """

        # Slice out the data required for the plotting
        plotData = self.parent.parent.dataTable.loc[(slice(None), datasets), 'Value']

        # Slice out units for each of the plots
        if len(self.parent.parent.datasetTable) > 0:
            plotUnits = self.parent.parent.datasetTable.loc[datasets]['DatasetUnits'].to_list()

            plotNames = self.parent.parent.datasetTable.loc[datasets]['DatasetName'].to_list()
            plotParameters = self.parent.parent.datasetTable.loc[datasets]['DatasetParameter'].to_list()
            plotNames = [plotNames[x] + ': ' + plotParameters[x] for x in range(0, len(plotNames), 1)]

        else:
            plotUnits = ['']
            plotNames = ['']

        # Perform an update on the timeseries plot
        self.timeSeriesPlot.updateData(plotData, plotNames, plotUnits)

        # If there is more than one dataset, 
        self.timeSeriesPlot.displayDatasets(datasets)
        self.timeSliderPlot.displayDatasets(datasets)

        return


class DatasetTimeseriesPlots(pg.GraphicsLayoutWidget):

    def __init__(self, dataset, parent=None):
        # Instantiate the widget and create a reference to the parent
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent

        # Get a reference to the datasetTable and the dataTable
        if dataset is None:
            self.datasetTable = pd.DataFrame()
        else:
            self.datasetTable = dataset

        # Create a color cyler
        self.colors = [
            (255, 61, 0),
            (0, 145, 234),
            (255, 214, 0),
            (0, 200, 83),
            (255, 103, 32),
            (170, 0, 255),
            (141, 110, 99),
            (198, 255, 0),
            (29, 233, 182),
            (136, 14, 79)
        ]
        self.penCycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brushCycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]

        # Instantiate the plots
        self.timeSeriesPlot = TimeSeriesLinePlot(parent=self)
        # self.timeSliderPlot = TimeSliderPlot(self)
        # self.spaghettiPlot = SpaghettiPlot(self)

        # Add the plots
        self.addItem(self.timeSeriesPlot)
        # self.addItem(self.timeSliderPlot, row=7, col=0, rowspan=2)

        return

    def clearPlots(self):
        """
        Clears the plots of any data
        """
        self.timeSeriesPlot.clear()
        # self.timeSliderPlot.clear()

        return

    def displayDatasets(self, datasets):
        # If there is more than one dataset,
        self.timeSeriesPlot.displayDatasets(datasets)
        # self.timeSliderPlot.displayDatasets(datasets)

        return


# Create a flow histogram
class dataReductionPlot(pg.PlotItem):

    def __init__(self, parent=None):

        # Instantiate the widget
        pg.PlotItem.__init__(self)
        self.b_axis = self.getAxis('bottom')
        self.b_axis.enableAutoSIPrefix(enable=False)
        self.b_axis.setLabel("Year")

        self.parent = parent
        self.setMenuEnabled(False)

        self.legend = TimeSeriesLegend(size=None, offset=(30,30))
        self.legend.setParentItem(self.vb)

        # Create a plot line to show the data
        self.line = pg.PlotCurveItem(parent=self, pen = pg.mkPen("#FF0000", width=3), antialias=False, connect='finite', symbol='o', symbolBrush = pg.mkBrush("#FF0000"), symbolPen = pg.mkPen("#000000"))
        self.dots = pg.ScatterPlotItem(parent = self, pen = pg.mkPen("#000000", width=2), antialias=False, symbol='o', symbolBrush = pg.mkBrush("#FF0000"), brush = pg.mkBrush("#FF0000"))
        
        self.medianBar = pg.PlotCurveItem(parent = self, pen = pg.mkPen((28, 217, 151,140), width=7),antialias=False, connect='finite')
        self.averageBar = pg.PlotCurveItem(parent = self, pen = pg.mkPen((25, 134, 212,140), width=7),antialias=False, connect='finite')

        # Add interaction
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)

        # Set default limits
        self.setLimits(

                xMin = 0,
                xMax = 1,
                yMin = 0,
                yMax = 1,
            
            )
        self.setRange(

                xRange = (0, 1),
                yRange = (0, 1)
            )


        # Add a text box to instruct user how to show data
        self.noDataTextItem = pg.TextItem(html = '<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset from the list to view data.</div>')
        self.addItem(self.noDataTextItem)
        self.noDataTextItem.setPos(0.5, 0.5)

        self.highlightCircleItem = pg.ScatterPlotItem(parent = self, pen = pg.mkPen("#000000", width=4), antialias=False, symbol='o', symbolBrush = pg.mkBrush("FFF000"), brush = pg.mkBrush("FFF000"))

        self.isThereData = False

        return

    def mouseMoved(self, event):
        if self.isThereData:
            # Get the mouse position
            pos = QtCore.QPoint(event.x(), event.y())

            # Check that the overall widget actually contains the mouse point
            if self.sceneBoundingRect().contains(pos):

                 # Get the mousepoint in relation to the plot
                mousePoint = self.vb.mapSceneToView(pos)
                x_ = mousePoint.x()

                # Round x value to the nearest date
                idx = int(x_ - x_%86400)
                date = takeClosest(self.x, idx)
                idx2 = np.where(self.x==date)
                yval = round(self.y[idx2[0]][0],2)
                self.legend.items[2][1].setText(self.line.opts['name']+' <strong>'+str(yval) + ' ' + self.units + '</strong>')
                self.highlightCircleItem.setData([date], [yval], size=10)

    def displayDataset(self, dataset, period, method, customFunction):
        """
        """
        # Clear any existing data
        self.clear()

        self.isThereData = False

        # Make sure there's actually data to display
        if dataset not in self.parent.parent.parent.dataTable.index.levels[1]:
            self.addItem(self.noDataTextItem)
            self.noDataTextItem.setPos(0.5, 0.5)
            return
        data = self.parent.parent.parent.dataTable.loc[(slice(None), dataset), 'Value']

        if data.empty:
            self.addItem(self.noDataTextItem)
            self.noDataTextItem.setPos(0.5, 0.5)
            
            return
        self.isThereData = True

         # Remove the old legend
        self.legend.scene().removeItem(self.legend)

        # Instantiate a legend
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)
        


        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # Process the Data
        self.data = resampleDataSet(
            data,
            period,
            method,
            customFunction
        )
        self.data = self.data.dropna()
        

        # Update the line data
        x = np.array(self.data.index.astype('int64'))/1000000000
        self.x = x
        y = self.data.values
        self.y = y
        median = np.nanmedian(y)
        average = np.nanmean(y)
        
        self.b_axis.setTicks([[(i, (datetime(1970,1,1)+timedelta(seconds=i)).strftime('%Y')) for i in x], [(i, (datetime(1970,1,1)+timedelta(seconds=i)).strftime('%Y')) for i in x]])

        self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
        self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
        self.yMax = np.nanmax([self.yMax, np.nanmax(y)])
        self.yMin = np.nanmin([self.yMin, np.nanmin(y)])

        self.line.setData(x, y, name="Aggregated Data")
        self.dots.setData(x, y)
        self.medianBar.setData(x, len(x)*[median], name = 'Median')
        self.averageBar.setData(x, len(x)*[average], name = 'Average')

        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.yrange = self.yMax - self.yMin

            self.setLimits(

                xMin = self.xMin,
                xMax = self.xMax,
                yMin = self.yMin - self.yrange/10,
                yMax = self.yMax + self.yrange/10,
            
            )
            self.setRange(

                xRange = (self.xMin, self.xMax),
                yRange = (self.yMin  - self.yrange/10, self.yMax  + self.yrange/10)
            )
        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)

        # Show the grid
        self.showGrid(True, True, 0.85)

        self.addItem(self.medianBar)
        self.addItem(self.averageBar)
        self.addItem(self.line)
        self.addItem(self.dots)
        self.addItem(self.highlightCircleItem)

        self.units = self.getAxis("left").labelText

        self.legend.items[0][1].setText(self.medianBar.opts['name']+' <strong>'+str(round(median,2)) + ' ' + self.units + '</strong>')
        self.legend.items[1][1].setText(self.averageBar.opts['name']+' <strong>'+str(round(average,2)) + ' ' + self.units + '</strong>')

        return

        




# The Time slider plot displays a smaller version of the Period of Record data with a Time Slider Control overlay
class TimeSliderPlot(pg.PlotItem):

    def __init__(self, parent = None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self, axisItems={"bottom":DateTimeAxis(orientation = "bottom")})
        self.parent = parent
        self.setMenuEnabled(False)

        # Create 10 PlotCurveItems to work with
        self.items_ = [pg.PlotCurveItem(parent = self, pen = parent.penCycler[i%10], antialias = False, connect='finite') for i in range(100)]

        # Create a slider region
        self.region = pg.LinearRegionItem(brush=pg.mkBrush(100,100,100,50))
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
        newRegion = self.region.getRegion()
        if not any(np.isinf(newRegion)):
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

        # Re-Instantiate Limits
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # Create a new item for each dataset
        for i, dataset in enumerate(datasets):

            # Get the Data
            x = np.array(self.parent.parent.parent.dataTable.loc[(slice(None), dataset), 'Value'].index.get_level_values(0).astype('int64'))/1000000000 # Dates in seconds since epoch
            y = self.parent.parent.parent.dataTable.loc[(slice(None), dataset), 'Value'].values

            # Check if there is data to plot!
            if any([x.size == 0, x.shape != y.shape]):
                continue

            # Set new limits
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax = np.nanmax([self.yMax, np.nanmax(y)])
            self.yMin = np.nanmin([self.yMin, np.nanmin(y)])

            # Set the data for the i-th PlotCurveItem
            self.items_[i].setData(x, y, connect='finite')

            # Add the item to the plot
            self.addItem(self.items_[i])

        # Set the data limits and the current ranges and bounds
        #print('SLIDER ',self.xMax, self.xMin, self.yMax, self.yMin)
        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.setLimits(

                xMin = self.xMin,
                xMax = self.xMax,
                yMin = self.yMin,
                yMax = self.yMax,
                minXRange = self.xMax - self.xMin,
                minYRange = self.yMax - self.yMin

            )
        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)
        self.region.setRegion([self.xMin, self.xMax])
        self.region.setBounds([self.xMin, self.xMax])
        self.region.setZValue(-10)

        # Re-Add the region (it got deleted when we cleared ["self.clear()"])
        self.addItem(self.region)

        return


# Time Series Plot to display Time Series Data
class TimeSeriesLinePlot(pg.PlotItem):

    def __init__(self, parent=None):

        # Instantiate the widget and create a reference to the parent
        pg.PlotItem.__init__(self, axisItems={"bottom":DateTimeAxis(orientation = "bottom")})
        self.parent = parent
        self.setMenuEnabled(False)

        # Set the dataset properties into the function
        self.datasets = None
        self.unitAttributes = None

        # Instantiate Limits
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # Instantiate a legend
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # Create a new viewbox to store the second axis
        self.viewbox_axis2 = pg.ViewBox()

        # Add the axis and viewbox to the plotItem's viewbox
        self.showAxis("right")
        self.parent.scene().addItem(self.viewbox_axis2)
        self.getAxis("right").linkToView(self.viewbox_axis2)
        self.viewbox_axis2.setXLink(self)

        def updateViews():
            ## view has resized; update auxiliary views to match
            
            self.viewbox_axis2.setGeometry(self.vb.sceneBoundingRect())
            
            ## need to re-update linked axes since this was called
            ## incorrectly while views had different shapes.
            ## (probably this should be handled in ViewBox.resizeEvent)
            self.viewbox_axis2.linkedViewChanged(self.vb, self.viewbox_axis2.XAxis)

        # Set default limits
        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRange=(0, 1), yRange=(0, 1))
        self.viewbox_axis2.setRange(xRange=(0, 1), yRange=(0, 1))

        updateViews()
        self.vb.sigResized.connect(updateViews)

        # Add a text box to instruct user how to show data
        self.noDataTextItem = pg.TextItem(html = '<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset from the list to view data.</div>')
        self.addItem(self.noDataTextItem)
        self.noDataTextItem.setPos(0.5, 0.5)

        # Add interaction
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)

        # Create 10 PlotCurveItems to work with
        self.items_ = [self.createPlotItem(i) for i in range(50)]
        #self.items_ = [pg.PlotCurveItem(parent = self, pen = parent.penCycler[i%10], antialias = False, connect='finite') for i in range(50)]
        self.items_axis2 = [self.createPlotItem(i) for i in range(50)]
        #self.items_axis2 = [pg.PlotCurveItem(parent = self, pen = parent.penCycler[(i+5)%10], antialias = False, connect='finite') for i in range(50)]
        self.circleItems_ = [self.createCircleItem(i) for i in range(50)]
        #self.circleItems_ = [pg.ScatterPlotItem(size=10, alpha=1, brush=parent.brushCycler[i%10]) for i in range(50)]
        self.circleItems_axis2 = [self.createCircleItem(i) for i in range(50)]
        #self.circleItems_axis2 = [pg.ScatterPlotItem(size=10, alpha=1, brush=parent.brushCycler[(i+5)%10]) for i in range(50)]
        self.datasets = []

        return

    def updateData(self, datasets, datasetsNames, unitAttributes):
        """
        Updates the data within the object for plotting

        """

        self.datasets = datasets
        self.datasetsNames = datasetsNames
        self.unitAttributes = unitAttributes

    
    def createCircleItem(self, i):
        """
        Create a circle Item
        """
        ci = pg.ScatterPlotItem(size=10, alpha=1, brush=self.parent.brushCycler[i%10])
        ci.isActive = False
        return ci

    def createPlotItem(self, i):
        """
        Creates a line plot item
        """
        pi = pg.PlotCurveItem(parent = self, pen = self.parent.penCycler[i%10], antialias = False, connect='finite')
        pi.isActive = False
        return pi

    def mouseMoved(self, event):

        # Don't do anything if there are no datasets
        if self.datasets is None:
            return
        
        # Get the mouse position
        pos = QtCore.QPoint(event.x(), event.y())

        # Check that the overall widget actually contains the mouse point
        if self.sceneBoundingRect().contains(pos):

            # Get the mousepoint in relation to the plot
            mousePoint = self.vb.mapSceneToView(pos)
            x_ = mousePoint.x()

            # Round x value to the nearest date
            idx = int(x_ - x_%86400)
            
            # Iterate over the active items and display the data points in the legend
            legendCount = 0
            for i, item in enumerate(self.items_):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData==date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legendCount][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circleItems_[i].setData([date], [yval])
                    legendCount += 1
            
            # Iterate over the second axis items
            for j, item in enumerate(self.items_axis2):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData==date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legendCount][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circleItems_axis2[j].setData([date], [yval])
                    legendCount += 1

    def displayDatasets(self, datasetInternalIDs):
        """
        datasets = [100103, 313011, ...]
        """
        
        # Clear any existing datasets
        for j, item in enumerate(self.items_axis2):
            if item.isActive:

                item.isActive = False
                self.viewbox_axis2.removeItem(item)
                self.viewbox_axis2.removeItem(self.circleItems_axis2[j])

        self.clear()

        # Re-Instantiate Limits
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMin2 = np.inf
        self.yMax = -np.inf
        self.yMax2 = -np.inf

        # Remove the old legend
        self.legend.scene().removeItem(self.legend)

        # Instantiate a legend
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # Keep track of current datasets
        # self.datasets = datasets

        # Primary units for left hand axis
        primaryUnits = self.unitAttributes[0].upper()
        y2UnitList = []

        # Create a new item for each dataset
        for i, dataset in enumerate(datasetInternalIDs):

            # Get the Dataset Title
            d = self.datasets.loc[:, (dataset)]
            title = self.datasetsNames[i]

            # Get the Data
            x = self.datasets.loc[:, (dataset)].index.astype('int64').values/1000000000 # Dates in seconds since epoch
            y = self.datasets.loc[:, (dataset)].values

            # Check if there is data to plot!
            if any([x.size == 0, x.shape != y.shape]):
                continue

            # Set new limits
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])

            # Figure out which axis to plot on
            unitsEquivalent = sameUnits(primaryUnits, self.unitAttributes[i].upper())
            if unitsEquivalent[0]:
                
                self.yMax = np.nanmax([self.yMax, np.nanmax(y)])
                self.yMin = np.nanmin([self.yMin, np.nanmin(y)])
                
                # Set the data for the i-th PlotCurveItem
                self.items_[i].setData(x, y, name = title, connect='finite')
                self.items_[i].units = unitsEquivalent[1].lower()
                self.items_[i].isActive = True
                
            else:

                self.yMax2 = np.nanmax([self.yMax2, np.nanmax(y)])
                self.yMin2 = np.nanmin([self.yMin2, np.nanmin(y)])

                # set the data for the i-th second axis item
                self.items_axis2[i].setData(x, y, name = title, connect='finite')
                self.items_axis2[i].units = sameUnits(d['DatasetUnits'], self.unitAttributes[i].upper())[1].lower()
                self.items_axis2[i].isActive = True
                y2UnitList.append(self.items_axis2[i].units)

        # Add the active items
        for i, item in enumerate(self.items_): 
            if item.isActive:

                # Add the item to the plot
                self.addItem(item)
                self.addItem(self.circleItems_[i])
        
        for j, item in enumerate(self.items_axis2):
            if item.isActive:

                self.viewbox_axis2.addItem(item)
                self.viewbox_axis2.addItem(self.circleItems_axis2[j])
                self.legend.addItem(item, item.name())
        
        # Set the axis labels
        self.getAxis('left').setLabel(primaryUnits.lower())
        self.getAxis('right').setLabel(' '.join(list(set(y2UnitList))).lower())
        
        #print('PLOT ',self.xMax, self.xMin, self.yMax, self.yMin)
        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin, self.xMax), yRange=(self.yMin, self.yMax))

        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)

        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax2), np.isinf(self.yMin2)]):
            self.viewbox_axis2.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin2, yMax=self.yMax2)
            self.viewbox_axis2.setRange(

                xRange = (self.xMin, self.xMax),
                yRange = (self.yMin2, self.yMax2)
            )
        else:
            self.viewbox_axis2.setLimits(

                xMin = self.xMin,
                xMax = self.xMax,
                yMin = 0,
                yMax = 1,
            
            )
            self.viewbox_axis2.setRange(

                xRange = (self.xMin, self.xMax),
                yRange = (0, 1)
            )

        # Show the grid
        if len(y2UnitList) == 0:
            self.hideAxis('right')
        else:
            self.showAxis('right')
        self.showGrid(True, True, 0.85)

        return

class TimeSeriesLineBarPlot():

    def __init__(self, parent=None):
        """


        """
        # todo: doc string

        # Create the new chart
        self.chart = QtChart.QChart()
        self.chartView = None

        # Create the bar series
        self.barSeries = QtChart.QBarSeries()

        # Create a list of of time series
        self.timeSeries = []

        # Create the axis variables
        self.barCategories = None

    def createLinePlotItem(self, label, data):
        """
        Setup the line plot items using the existing format

        """
        # todo: doc string

        # Create the line series
        lineSeries = QtChart.QLineSeries()

        # Set the series name
        lineSeries.setName(label)

        # Append the values into the series
        for values in data:
            lineSeries.append(QtCore.QPoint(values[0], values[1]))

        # Append the line series into the class list
        self.timeSeries.append(lineSeries)

    def createBarPlotItem(self, label, data):
        """
        Create bar plots superimposed on the line plots

        """
        # todo: doc string

        # Define the set
        barSet = QtChart.QBarSet(label)

        # Add values into it
        for value in data:
            barSet.append(value)

        # Add the set into the series
        self.barSeries.append(barSet)

    def setBarCategories(self, barCategories):
        """


        """

        self.barCategories = barCategories


    def plot(self):
        """

        """
        # todo: doc string

        ### Add the data onto the chart ###
        # Add the bar chart
        self.chart.addSeries(self.barSeries)

        # Add the time series
        for series in self.timeSeries:
            self.chart.addSeries(series)

        ### Format the charts ###
        ## Create custom x axes ##
        # Instantiate the bar axis object
        xAxis = QtChart.QBarCategoryAxis()

        # Add the categories into the axis
        xAxis.append(self.barCategories)

        ## Set the x axis on all the series ##
        # Set the bar series
        self.chart.setAxisX(xAxis, self.barSeries)

        # Loop and set the time series
        for series in self.timeSeries:
            self.chart.setAxisX(xAxis, series)

        ## Create the custom y axes ##
        # Instatiate the axis object
        yAxis = QtChart.QValueAxis()

        ## Set the x axis on all the series ##
        # Set the bar series
        self.chart.setAxisY(yAxis, self.barSeries)

        # Loop and set the time series
        for series in self.timeSeries:
            self.chart.setAxisY(yAxis, series)

        ### Show the legend ###
        # Define the legend
        legend = self.chart.legend()

        # Set the visibility to true
        legend.setVisible(True)

        ### Set the chart to render ###
        self.chartView = QtChart.QChartView(self.chart)
        self.chartView.setRenderHint(QtGui.QPainter.Antialiasing)

        # Not sure if I need to do anything after this to get it render correctly


def sameUnits(unit1, unit2):
    """
    Checks if the unit1 is functionally the
    same as unit 2
    """

    unit1 = unit1.upper().strip()
    unit2 = unit2.upper().strip()

    # Check equivalency lists
    for lst in EQUIVALENCY_LISTS:
        if (unit1 in lst) and (unit2) in lst:
            return True, lst[0]

    # simple check
    if unit1 == unit2:
        return True, unit1
    
    return False, unit2


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

    
