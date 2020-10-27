"""
Script Name:    PyQtGraphs.py

Description:    Contains all the subclassed plots
                for NextFlow software.
"""

#=======================================================================================================================
# IMPORT LIBRARIES
#=======================================================================================================================
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import importlib
from resources.GUI.CustomWidgets import PyQtGraphOverrides
from resources.modules.Miscellaneous.DataProcessor import resampleDataSet
from bisect import bisect_left
from statsmodels.tsa.stattools import ccf

# UNIVERSAL OPTIONS
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
try:
    pg.setConfigOptions(useOpenGL = True)
except:
    print("not using OpenGL for plots.")

#=======================================================================================================================
# STATIC RESOURCES
#=======================================================================================================================

# List to keep track of which units are equalivant. Used to condense units on plot axes
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

#=======================================================================================================================
# FUNCTIONS
#=======================================================================================================================

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

def condenseUnits(unitList):
    """
    Removes duplicate units from a list of units

    @param unitList: list
    @return: list
    """

    # INSTANTIATE A LIST TO STORE OUTPUT UNITS
    condensedList = []

    # FOR EACH ELEMENT IN THE INITIAL LIST,
    # CHECK FOR EQIVALENCE TO OTHER UNITS
    while len(unitList) > 0:
        unit = unitList[0]
        unit_simplified = sameUnits(unit, unit)[1]
        condensedList.append(unit_simplified)
        equiv_list = [sameUnits(unit_simplified, i) for i in unitList[1:]]
        j=0
        for i, res in enumerate(equiv_list):
            if res[0]:
                unitList.pop(i+1-j)
                j += 1
        unitList.pop(0)

    return condensedList

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

#=======================================================================================================================
# LOW LEVEL PLOT ITEMS (SUBCLASSES)
#=======================================================================================================================

class TimeSeriesLegend(pg.LegendItem):
    """
    Interactive legend. (Subclassed to add
    resize capability on label changes)
    """

    def __init__(self, size=None, offset=None):

        # Instantiate the legend Item
        pg.LegendItem.__init__(self, size, offset, brush=(200, 200, 200, 140))

    def addItem(self, item, name):

        # Instantiate a Label Item using the supplied Name
        label = pg.graphicsItems.LegendItem.LabelItem(name, justify='left')

        # Create the sample image to place next to the legend Item
        if isinstance(item, pg.graphicsItems.LegendItem.ItemSample):
            sample = item
            sample.setFixedWidth(20)
        elif isinstance(item, pg.BarGraphItem):
            sample = barGraphSample(item)
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
            width = max(width, sample.boundingRect().width() + label.width())

        self.setGeometry(0, 0, width + 60, height)

class barGraphSample(pg.GraphicsWidget):

    def __init__(self, item):

        pg.GraphicsWidget.__init__(self)
        self.item = item

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 20, 20)

    def paint(self, p, *args):
        opts = self.item.opts

        p.setBrush(pg.mkBrush(opts['brush']))
        p.drawRect(QtCore.QRectF(2, 2, 14, 14))


class DateTimeAxis(pg.AxisItem):
    """
    Datetime axis.

    arguments:
        fmt:    datetime format to display
                "YYYY-MM-DD" or "YYYY"
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the axisItem
        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickSpacing(self, minValue, maxValue, size):
        # Set the tick spacing based on the current zoom level
        spacing = max([1, int(0.27 * (maxValue - minValue) + 22)])
        return [(spacing, 0), (spacing, 0)]

    def tickStrings(self, values, scale, spacing):
        # Set the datetime display based on the zoom level
        if spacing > 7 * 365.24 * 86400:
            return [datetime.utcfromtimestamp(value).strftime('%Y-%m') for value in values]
        return [datetime.utcfromtimestamp(value).strftime('%Y-%m-%d') for value in values]


class DateTimeAxis_years(pg.AxisItem):

    def __init__(self, *args, **kwargs):

        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):

        return [datetime.utcfromtimestamp(value).strftime('%Y') for value in values]


class TimeSeriesPlot(pg.PlotItem):
    """
    Simple time series line plot. Plots a datetime
    on the x axis and times series on the y-axes.

    arguments:
        x:
    """

    def __init__(self, parent = None, *args):

        # INITIALIZE THE CLASS WITH THE PROVIDED ARGUMENTS
        pg.PlotItem.__init__(self, axisItems={"bottom":DateTimeAxis(orientation = "bottom")}, *args)

        # REFERENCE THE PARENT
        self.parent = parent

        # CREATE AXES
        self.showAxis("right")
        self.viewbox_axis_2 = pg.ViewBox()
        self.parent.scene().addItem(self.viewbox_axis_2)
        self.getAxis("right").linkToView(self.viewbox_axis_2)
        self.viewbox_axis_2.setXLink(self)

        # CREATE EMPTY DATA
        self.x = np.array([])
        self.y1 = np.array([[]])
        self.y2 = np.array([[]])
        self.units = []
        self.labels = []

        # CREATE LEGEND
        self.legend = TimeSeriesLegend(size=None, offset=(30,30))
        self.legend.setParentItem(self.vb)

        # INITIALIZE OPTIONS FOR THE PLOT
        self.setMenuEnabled(False)

        def updateViews():
            self.viewbox_axis_2.setGeometry(self.vb.sceneBoundingRect())
            self.viewbox_axis_2.linkedViewChanged(self.vb, self.viewbox_axis_2.XAxis)

        # CONNECT SIGNALS
        updateViews()
        self.vb.sigResized.connect(updateViews)

        # CREATE LINE AND CIRCLE ITEMS
        self.line_items = [self.createLineItem(i) for i in range(50)]
        self.line_items_axis_2 = [self.createLineItem(i) for i in range(5,55)]
        self.circle_items = [self.createCircleItem(i) for i in range(50)]
        self.circle_items_axis_2 = [self.createCircleItem(i) for i in range(5,55)]

        # INSTANTIATE PLOT LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # SET DEFAULT BOUNDS
        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis_2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRange=(0,1), yRange=(0,1))
        self.viewbox_axis_2.setRange(xRange=(0, 1), yRange=(0, 1))

        # INITIAL TEXT FOR EMPTY PLOT
        self.no_data_text_item = pg.TextItem(html = '<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset to view data.</div>')
        self.addItem(self.no_data_text_item)
        self.no_data_text_item.setPos(0.5, 0.5)

        # ADD INTERACTION
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)


        return


    def mouseMoved(self, event):
        """
        Update the legend with the specific
        data that the mouse is hovering over.
        """

        # DON'T DO ANYTHING IF THERE ARE NO DATASETS
        if self.labels == []:
            return

        # GET THE MOUSE POSITION
        pos = QtCore.QPoint(event.x(), event.y())

        # CHECK THAT THE OVERALL WIDGET ACTUALLY CONTAINS THE MOUSE POINT
        if self.sceneBoundingRect().contains(pos):

            # GET THE MOUSE POSITION IN DATA COORDINATES]
            mouse_point = self.vb.mapSceneToView(pos)
            x_ = mouse_point.x()

            # ROUND THE X VALUE TO THE NEAREST DATE
            idx = int(x_ - x_%86400)

            # ITERATE OVER THE ACTIVE ITEMS AND DISPLAY THE POINTS IN THE LEGEND
            legend_count = 0
            for i, item in enumerate(self.line_items):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items[i].setData([date], [yval])
                    legend_count += 1

            for j, item in enumerate(self.line_items_axis_2):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items_axis_2[j].setData([date], [yval])
                    legend_count += 1

        return


    def createLineItem(self, idx):
        """
        Creates and returns a line plot item
        """
        pi = pg.PlotCurveItem(
            parent = self,
            pen = self.parent.pen_cycler[idx%10],
            antialias = False,
            connect = 'finite'
        )
        pi.isActive = False
        return pi


    def createCircleItem(self, idx):
        """
        Creates and returns a circle plot item
        """
        pi = pg.ScatterPlotItem(
            size = 10,
            alpha = 1,
            brush = self.parent.brush_cycler[idx%10]
        )
        pi.isActive = False
        return pi


    def setData(self, x, y1, y2, units, labels):
        """
        Sets the data in the plot. The function can plot up to 100 series on the same plot
        (50 series in the 'y1' argument and 50 series in the 'y2' argument).

        Pass an array of datetimes to the 'x' argument, and pass an array of
        y-value arrays to one or both of the 'y' arguments.

        example:
            -> Plots 3 series total (2 on y1 axis and 1 on y2 axis).
            self.setData(
                x = np.array([datetime(2020,1,1), datetime(2020,3,1)]),
                y1 = np.array([[4.2, 32.1], [7.3, 4.3]]),
                y2 = np.array([[5.3, 4.2]]),
                units = ['cfs','cfs','degF'],
                labels = ['Hudson River','Cuyahoga River','Sea Surface Temp']


        arguments:
            x:      1-D np.array([...list of datetimes...)
            y1:     2-D np.array([...[dataset1...], [dataset2...],...)
            y2:     2-D np.array([...[dataset1...], [dataset2...],...)
            units:  list e.g. ['cfs','inches','inches']
            labels: list e.g. ['Hudson River', 'Summit Peak', 'Clover Meadows']
        """

        # CLEAR ANY EXISTING DATA
        for j, item in enumerate(self.line_items_axis_2):
            if item.isActive:

                item.isActive = False
                self.viewbox_axis_2.removeItem(item)
                self.viewbox_axis_2.removeItem(self.circle_items_axis_2[j])

        self.clear()

        # CHECK IF THERE IS ANY DATA TO PLOT
        if x.size == 0:
            return

        # CONVERT X TO INTEGER TIMES
        x = np.array(x.astype('int64')/1000000000)

        # REFERENCES
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.units = units
        self.labels = labels

        # RE-INSTANTIATE LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMin2 = np.inf
        self.yMax = -np.inf
        self.yMax2 = -np.inf

        # REMOVE THE OLD LEGEND
        self.legend.scene().removeItem(self.legend)

        # CREATE A NEW LEGEND
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # SET UP EACH AXIS
        self.y1_Num_Series = len(y1)
        self.y2_Num_Series = len(y2)
        self.y1_Axis_Units = condenseUnits(units[:self.y1_Num_Series])
        self.y2_Axis_Units = condenseUnits(units[self.y1_Num_Series:])

        # ITERATE OVER 'Y1' MEMBERS AND ACTIVATE THE ITEMS
        for i, dataset in enumerate(y1):

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax = np.nanmax([self.yMax, np.nanmax(dataset)])
            self.yMin = np.nanmin([self.yMin, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items[i].setData(x, dataset, name = labels[i], connect = 'finite')
            self.line_items[i].opts['name'] = labels[i]
            self.line_items[i].units = sameUnits(units[i], units[i])[1].lower()
            self.line_items[i].isActive = True

        # ITERATE OVER 'Y2' MEMBERS AND ACTIVATE THE ITEMS
        for j, dataset in enumerate(y2):

            k = i + j + 1

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax2 = np.nanmax([self.yMax2, np.nanmax(dataset)])
            self.yMin2 = np.nanmin([self.yMin2, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items_axis_2[j].setData(x, dataset, name=labels[k], connect='finite')
            self.line_items_axis_2[j].opts['name'] = labels[k]
            self.line_items_axis_2[j].units = sameUnits(units[k], units[k])[1].lower()
            self.line_items_axis_2[j].isActive = True

        # ADD THE ACTIVATED ITEMS TO THE PLOT
        for i, item in enumerate(self.line_items):
            if item.isActive:
                self.addItem(item)
                self.addItem(self.circle_items[i])

        for j, item in enumerate(self.line_items_axis_2):
            if item.isActive:
                self.viewbox_axis_2.addItem(item)
                self.viewbox_axis_2.addItem(self.circle_items_axis_2[j])
                self.legend.addItem(item, item.name())

        # SET THE AXIS LABELS
        self.getAxis('left').setLabel(' '.join(self.y1_Axis_Units))
        self.getAxis('right').setLabel(' '.join(self.y2_Axis_Units))

        # DO SOME FINAL WORK WITH THE RANGES AND EXTENTS
        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin, self.xMax), yRange=(self.yMin, self.yMax))

        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)

        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax2), np.isinf(self.yMin2)]):
            self.viewbox_axis_2.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin2, yMax=self.yMax2)
            self.viewbox_axis_2.setRange(

                xRange=(self.xMin, self.xMax),
                yRange=(self.yMin2, self.yMax2)
            )
        else:
            self.viewbox_axis_2.setLimits(

                xMin=self.xMin,
                xMax=self.xMax,
                yMin=0,
                yMax=1,

            )
            self.viewbox_axis_2.setRange(

                xRange=(self.xMin, self.xMax),
                yRange=(0, 1)
            )

        # SHOW GRID AND HIDE EMPTY RIGHT AXIS
        if len(self.y2_Axis_Units) == 0:
            self.hideAxis('right')
        else:
            self.showAxis('right')

        self.showGrid(True, True, 0.85)

        return


class TimeSeriesSliderPlot(pg.PlotItem):

    def __init__(self, parent = None, *args):
        """

        @param parent:
        @param args:
        """

        pg.PlotItem.__init__(self, axisItems={"bottom": DateTimeAxis(orientation='bottom')})
        self.parent = parent
        self.setMenuEnabled(False)

        self.line_items = [self.createLineItem(i) for i in range(100)]

        # CREATE A SLIDER REGION
        self.region = pg.LinearRegionItem(brush=pg.mkBrush(100, 100, 100, 50))
        self.region.setZValue(10)

        # INSTANTIATE LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf


        # ADD THE REGION
        self.addItem(self.region)

        return


    def createLineItem(self, idx):
        """
        Creates and returns a line plot item
        """
        pi = pg.PlotCurveItem(
            parent = self,
            pen = self.parent.pen_cycler[idx%10],
            antialias = False,
            connect = 'finite'
        )
        pi.isActive = False
        return pi

    def setData(self, x, y1, y2):
        """

        @param x:
        @param y1:
        @param y2:
        @param units:
        @param labels:
        @return:
        """

        # CLEAR ANY EXISTING DATA
        self.clear()

        # CONVERT X TO INTEGER SERIES
        x = x.astype("int64")/1000000000

        # REFERENCES
        self.x = x
        self.x = x
        self.y1 = y1
        self.y2 = y2

        # RE-INSTANTIATE LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMin2 = np.inf
        self.yMax = -np.inf
        self.yMax2 = -np.inf

        # ITERATE OVER 'Y1' MEMBERS AND ACTIVATE THE ITEMS
        for i, dataset in enumerate(y1):

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax = np.nanmax([self.yMax, np.nanmax(dataset)])
            self.yMin = np.nanmin([self.yMin, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items[i].setData(x, dataset, connect='finite')
            self.line_items[i].isActive = True


        # ITERATE OVER 'Y2' MEMBERS AND ACTIVATE THE ITEMS
        for j, dataset in enumerate(y2):

            k = i + j + 1

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax = np.nanmax([self.yMax, np.nanmax(dataset)])
            self.yMin = np.nanmin([self.yMin, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items[k].setData(x, dataset, connect='finite')
            self.line_items[k].isActive = True

        # ADD THE ACTIVATED ITEMS TO THE PLOT
        for i, item in enumerate(self.line_items):
            if item.isActive:
                self.addItem(item)

        # DO SOME FINAL WORK WITH THE RANGES AND EXTENTS
        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin, self.xMax), yRange=(self.yMin, self.yMax))

        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)

        self.region.setRegion([self.xMin, self.xMax])
        self.region.setBounds([self.xMin, self.xMax])
        self.region.setZValue(-10)

        # Re-Add the region (it got deleted when we cleared ["self.clear()"])
        self.addItem(self.region)

        return


class BarAndLinePlot(pg.PlotItem):

    def __init__(self, parent=None, xAxis="integer", *args):
        """
        @param parent:
        @param xAxis: 'integer' or 'datetime'
        @param args:
        """

        # INITIALIZE THE CLASS WITH PROVIDED ARGUMENTS
        if xAxis == 'datetime':
            pg.PlotItem.__init__(self, axisItems={"bottom": DateTimeAxis(orientation="bottom")}, *args)
            self.hasDatetimeAxis = True
        else:
            pg.PlotItem.__init__(self, *args)
            self.hasDatetimeAxis = False

        # REFERENCE THE PARENT
        self.parent = parent

        # CREATE AXES
        self.showAxis("right")
        self.viewbox_axis_2 = pg.ViewBox()
        self.parent.scene().addItem(self.viewbox_axis_2)
        self.getAxis("right").linkToView(self.viewbox_axis_2)
        self.viewbox_axis_2.setXLink(self)

        # CREATE EMPTY DATA
        self.x = np.array([])
        self.lineData = np.array([[]])
        self.barData = np.array([[]])
        self.units = []
        self.labels = []

        # CREATE LEGEND
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # INITIALIZE OPTIONS FOR THE PLOT
        self.setMenuEnabled(False)

        def updateViews():
            self.viewbox_axis_2.setGeometry(self.vb.sceneBoundingRect())
            self.viewbox_axis_2.linkedViewChanged(self.vb, self.viewbox_axis_2.XAxis)

        # CONNECT SIGNALS
        updateViews()
        self.vb.sigResized.connect(updateViews)

        # CREATE LINE, CIRCLE, AND BAR ITEMS
        self.line_items = [self.createLineItem(i) for i in range(50)]
        self.circle_items = [self.createCircleItem(i) for i in range(50)]
        self.bar_items = [self.createBarItem(i) for i in range(5,55)]
        self.bar_items_highlight = [self.createBarItemHighlight(i) for i in range(5,55)]

        # INSTANTIATE PLOT LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # SET DEFAULT BOUNDS
        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis_2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRange=(0, 1), yRange=(0, 1))
        self.viewbox_axis_2.setRange(xRange=(0, 1), yRange=(0, 1))

        # INITIAL TEXT FOR EMPTY PLOT
        self.no_data_text_item = pg.TextItem(
            html='<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset from the list to view data.</div>')
        self.addItem(self.no_data_text_item)
        self.no_data_text_item.setPos(0.5, 0.5)

        # ADD INTERACTION
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)

        return

    def mouseMoved(self, event):
        """

        @param event:
        @return:
        """

        # DON'T DO ANYTHING IF THERE ARE NO DATASETS
        if self.labels == []:
            return

        # GET THE MOUSE POSITION
        pos = QtCore.QPoint(event.x(), event.y())

        # CHECK THAT THE OVERALL WIDGET ACTUALLY CONTAINS THE MOUSE POINT
        if self.sceneBoundingRect().contains(pos):
            # GET THE MOUSE POSITION IN DATA COORDINATES]
            mouse_point = self.vb.mapSceneToView(pos)
            x_ = mouse_point.x()

            # ROUND THE X VALUE TO THE NEAREST DATE
            idx = int(x_ - x_%86400)

            # ITERATE OVER THE ACTIVE ITEMS AND DISPLAY THE POINTS IN THE LEGEND
            legend_count = 0
            for i, item in enumerate(self.line_items):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items[i].setData([date], [yval])
                    legend_count += 1

            for j, item in enumerate(self.bar_items):
                if item.isActive:
                    date = takeClosest(item.opts['x'], idx)
                    idx2 = np.where(item.opts['x'] == date)
                    yval = round(item.opts['height'][idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.bar_items_highlight[j].setOpts(width=self.barWidth, x=[date], height=[yval])
                    legend_count += 1

    def createLineItem(self, idx):
        """
        Creates and returns a line plot item
        """
        pi = pg.PlotCurveItem(
            parent = self,
            pen = self.parent.pen_cycler[idx%10],
            antialias = False,
            connect = 'finite'
        )
        pi.isActive = False
        return pi


    def createCircleItem(self, idx):
        """
        Creates and returns a circle plot item
        """
        pi = pg.ScatterPlotItem(
            size = 10,
            alpha = 1,
            brush = self.parent.brush_cycler[idx%10]
        )
        pi.isActive = False
        return pi

    def createBarItem(self, idx):
        """
        Creates and returns a barplot item
        """
        pi = pg.BarGraphItem(
            width = 0,
            x = [],
            height = [],
            pen = pg.mkPen(pg.mkColor((0,0,0)), width=1),
            brush = self.parent.brush_cycler[idx%10]
        )
        pi.isActive = False
        return pi

    def createBarItemHighlight(self, idx):
        """
        Creates and returns a barplot item
        """
        pi = pg.BarGraphItem(
            width = 0,
            x = [],
            height = [],
            pen = pg.mkPen(pg.mkColor((0,0,0)), width=2),
            brush = self.parent.brush_cycler[idx%10]
        )
        pi.isActive = False
        return pi

    def clearPlots(self):
        # CLEAR ANY EXISTING DATA
        for j, item in enumerate(self.bar_items):
            if item.isActive:
                item.isActive = False
                self.viewbox_axis_2.removeItem(item)
                self.viewbox_axis_2.removeItem(self.bar_items_highlight[j])

        self.clear()

        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis_2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRange=(0, 1), yRange=(0, 1))
        self.viewbox_axis_2.setRange(xRange=(0, 1), yRange=(0, 1))

        self.setTitle("")

        # REMOVE THE OLD LEGEND
        try:
            self.legend.scene().removeItem(self.legend)
        except:
            pass

        self.no_data_text_item = pg.TextItem(
            html='<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset from the list to view data.</div>')
        self.addItem(self.no_data_text_item)
        self.no_data_text_item.setPos(0.5, 0.5)

        return


    def setData(self, x, lineData, barData, units, labels, barWidth, spacing = 0):
        """

        @param x:
        @param lineData:
        @param barData:
        @param units:
        @param labels:
        @return:
        """

        # CLEAR ANY EXISTING DATA
        for j, item in enumerate(self.bar_items):
            if item.isActive:
                item.isActive = False
                self.viewbox_axis_2.removeItem(item)
                self.viewbox_axis_2.removeItem(self.bar_items_highlight[j])

        self.clear()

        # CHECK IF THERE IS ANY DATA TO PLOT
        if x.size == 0:
            return

        # CONVERT X TO INTEGER TIMES
        if self.hasDatetimeAxis:
            x = x.astype('int64') / 1000000000

        # REFERENCES
        self.x = x
        self.lineData = lineData
        self.barData = barData
        self.units = units
        self.labels = labels
        self.barWidth = barWidth - spacing/2
        

        # RE-INSTANTIATE LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMin2 = np.inf
        self.yMax = -np.inf
        self.yMax2 = -np.inf

        # REMOVE THE OLD LEGEND
        try:
            self.legend.scene().removeItem(self.legend)
        except:
            pass

        # CREATE A NEW LEGEND
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # SET UP EACH AXIS
        self.y1_Num_Series = len(lineData)
        self.y2_Num_Series = len(barData)
        self.y1_Axis_Units = condenseUnits(units[:self.y1_Num_Series])
        self.y2_Axis_Units = condenseUnits(units[self.y1_Num_Series:])

        # COMPUTE BAR WIDTH
        if self.y2_Num_Series > 1:
            self.barWidth = self.barWidth/self.y2_Num_Series
            self.xArray = [self.x for i in range(self.y2_Num_Series)]
            for i in range(self.y2_Num_Series):
                self.xArray[i] = self.x - (i-int(self.y2_Num_Series/2))*self.barWidth
        else:
            self.xArray = [self.x]


        # ITERATE OVER 'LINEDATA' MEMBERS AND ACTIVATE THE ITEMS
        for i, dataset in enumerate(lineData):

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax = np.nanmax([self.yMax, np.nanmax(dataset)])
            self.yMin = np.nanmin([self.yMin, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items[i].setData(x, dataset, name=labels[i], connect='finite')
            self.line_items[i].opts['name'] = labels[i]
            self.line_items[i].units = sameUnits(units[i], units[i])[1].lower()
            self.line_items[i].isActive = True

        # ITERATE OVER 'barData' MEMBERS AND ACTIVATE THE ITEMS
        for j, dataset in enumerate(barData):

            k = i + j

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax2 = np.nanmax([self.yMax2, np.nanmax(dataset)])
            self.yMin2 = np.nanmin([self.yMin2, np.nanmin(dataset)])

            # ADD TO PLOT
            self.bar_items[j].setOpts(x=self.xArray[j], height=dataset, name=labels[k], width=self.barWidth)
            self.bar_items[j].opts['name'] = labels[k]
            self.bar_items[j].units = sameUnits(units[k], units[k])[1].lower()
            self.bar_items[j].isActive = True

        # ADD THE ACTIVATED ITEMS TO THE PLOT
        for i, item in enumerate(self.line_items):
            if item.isActive:
                self.addItem(item)
                self.addItem(self.circle_items[i])

        for j, item in enumerate(self.bar_items):
            if item.isActive:
                self.viewbox_axis_2.addItem(item)
                self.viewbox_axis_2.addItem(self.bar_items_highlight[j])
                self.legend.addItem(item, item.name())

        # SET THE AXIS LABELS
        self.getAxis('left').setLabel(' '.join(self.y1_Axis_Units))
        self.getAxis('right').setLabel(' '.join(self.y2_Axis_Units))

        # DO SOME FINAL WORK WITH THE RANGES AND EXTENTS
        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin, self.xMax), yRange=(self.yMin, self.yMax))

        elif np.isinf(self.yMax):
            self.yMax = self.yMax2
            self.yMin = self.yMin2
            self.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin, self.xMax), yRange=(self.yMin, self.yMax))

        elif np.isinf(self.yMax2):
            self.yMax2 = self.yMax
            self.yMin2 = self.yMin
            self.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin, self.xMax), yRange=(self.yMin, self.yMax))

        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)

        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax2), np.isinf(self.yMin2)]):
            self.viewbox_axis_2.setLimits(xMin=self.xMin, xMax=self.xMax, yMin=self.yMin2, yMax=self.yMax2)
            self.viewbox_axis_2.setRange(

                xRange=(self.xMin, self.xMax),
                yRange=(self.yMin2, self.yMax2)
            )
        else:
            self.viewbox_axis_2.setLimits(

                xMin=self.xMin,
                xMax=self.xMax,
                yMin=0,
                yMax=1,

            )
            self.viewbox_axis_2.setRange(

                xRange=(self.xMin, self.xMax),
                yRange=(0, 1)
            )

        # SHOW GRID AND HIDE EMPTY RIGHT AXIS
        if len(self.y2_Axis_Units) == 0:
            self.hideAxis('right')
        else:
            self.showAxis('right')

        self.showGrid(True, True, 0.85)

        return

class BarandDoubleAxisLinePlot(pg.PlotItem):
    """
    Simple time series line plot. Plots a datetime
    on the x axis and times series on the y-axes.

    arguments:
        x:
    """
    # todo: update doc string

    def __init__(self, parent = None, *args):

        # INITIALIZE THE CLASS WITH THE PROVIDED ARGUMENTS
        pg.PlotItem.__init__(self, axisItems={"bottom":DateTimeAxis(orientation = "bottom")}, *args)

        # REFERENCE THE PARENT
        self.parent = parent

        # CREATE AXES
        self.showAxis("right")
        self.viewbox_axis_2 = pg.ViewBox()
        self.parent.scene().addItem(self.viewbox_axis_2)
        self.getAxis("right").linkToView(self.viewbox_axis_2)
        self.viewbox_axis_2.setXLink(self)

        # CREATE THE EMPTY LINE DATA
        self.x_line = np.array([])
        self.y1 = np.array([[]])
        self.y2 = np.array([[]])
        self.lineUnits = []
        self.lineLabels = []

        # CREATE THE EMPTY BAR DATA
        self.barData = np.array([[]])
        self.barUnits = []
        self.barLabels = []
        self.x_bar = np.array([])

        # CREATE LEGEND
        self.legend = TimeSeriesLegend(size=None, offset=(30,30))
        self.legend.setParentItem(self.vb)

        # INITIALIZE OPTIONS FOR THE PLOT
        self.setMenuEnabled(False)

        def updateViews():
            self.viewbox_axis_2.setGeometry(self.vb.sceneBoundingRect())
            self.viewbox_axis_2.linkedViewChanged(self.vb, self.viewbox_axis_2.XAxis)

        # CONNECT SIGNALS
        updateViews()
        self.vb.sigResized.connect(updateViews)

        # CREATE LINE AND CIRCLE ITEMS
        self.line_items = [self.createLineItem(i) for i in range(50)]
        self.line_items_axis_2 = [self.createLineItem(i) for i in range(5,55)]
        self.circle_items = [self.createCircleItem(i) for i in range(50)]
        self.circle_items_axis_2 = [self.createCircleItem(i) for i in range(5,55)]

        # INSTANTIATE PLOT LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # CREATE THE BAR ITEMS
        self.bar_items = [self.createBarItem(i) for i in range(5,55)]
        self.bar_items_highlight = [self.createBarItemHighlight(i) for i in range(5,55)]

        # SET DEFAULT BOUNDS
        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis_2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRange=(0,1), yRange=(0,1))
        self.viewbox_axis_2.setRange(xRange=(0, 1), yRange=(0, 1))

        # INITIAL TEXT FOR EMPTY PLOT
        self.no_data_text_item = pg.TextItem(html = '<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset to view data.</div>')
        self.addItem(self.no_data_text_item)
        self.no_data_text_item.setPos(0.5, 0.5)

        # ADD INTERACTION
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)


        return


    def mouseMoved(self, event):
        """
        Update the legend with the specific
        data that the mouse is hovering over.
        """

        # DON'T DO ANYTHING IF THERE ARE NO DATASETS
        if self.lineLabels == []:
            return

        # GET THE MOUSE POSITION
        pos = QtCore.QPoint(event.x(), event.y())

        # CHECK THAT THE OVERALL WIDGET ACTUALLY CONTAINS THE MOUSE POINT
        if self.sceneBoundingRect().contains(pos):

            # GET THE MOUSE POSITION IN DATA COORDINATES]
            mouse_point = self.vb.mapSceneToView(pos)
            x_ = mouse_point.x()

            # ROUND THE X VALUE TO THE NEAREST DATE
            idx = int(x_ - x_ % 86400)

            # ITERATE OVER THE ACTIVE ITEMS AND DISPLAY THE POINTS IN THE LEGEND
            legend_count = 0
            for i, item in enumerate(self.line_items):
                if item.isActive and item.opts['name'] is not None:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items[i].setData([date], [yval])
                    legend_count += 1

            for j, item in enumerate(self.line_items_axis_2):
                if item.isActive and item.opts['name'] is not None:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items_axis_2[j].setData([date], [yval])
                    legend_count += 1

            for j, item in enumerate(self.bar_items):
                if item.isActive:
                    date = takeClosest(item.opts['x'], idx)
                    idx2 = np.where(item.opts['x'] == date)

                    yval = round(self.barData[0][idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.bar_items_highlight[j].setOpts(width=self.barWidth, x=[date], height=[yval])
                    legend_count += 1

        return


    def createLineItem(self, idx):
        """
        Creates and returns a line plot item
        """
        pi = pg.PlotCurveItem(
            parent = self,
            pen = self.parent.pen_cycler[idx%10],
            antialias = False,
            connect = 'finite'
        )
        pi.isActive = False
        return pi


    def createCircleItem(self, idx):
        """
        Creates and returns a circle plot item
        """
        pi = pg.ScatterPlotItem(
            size = 10,
            alpha = 1,
            brush = self.parent.brush_cycler[idx%10]
        )
        pi.isActive = False
        return pi

    def createBarItem(self, idx):
        """
        Creates and returns a barplot item
        """
        pi = pg.BarGraphItem(
            width = 0,
            x = [],
            height = [],
            pen = pg.mkPen(pg.mkColor(self.parent.primaryColor), width=1),
            brush = pg.mkBrush(pg.mkColor(self.parent.primaryColor))
        )
        pi.isActive = False
        return pi

    def createBarItemHighlight(self, idx):
        """
        Creates and returns a barplot item
        """
        pi = pg.BarGraphItem(
            width = 0,
            x = [],
            height = [],
            pen = pg.mkPen(pg.mkColor((0,0,0)), width=2),
            brush = self.parent.brush_cycler[idx%10]
        )
        pi.isActive = False
        return pi


    def clearPlots(self):
        # CLEAR ANY EXISTING DATA
        for j, item in enumerate(self.bar_items):
            if item.isActive:
                item.isActive = False
                self.viewbox_axis_2.removeItem(item)
                self.viewbox_axis_2.removeItem(self.bar_items_highlight[j])

        self.clear()

        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis_2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRange=(0, 1), yRange=(0, 1))
        self.viewbox_axis_2.setRange(xRange=(0, 1), yRange=(0, 1))

        self.setTitle("")

        # REMOVE THE OLD LEGEND
        try:
            self.legend.scene().removeItem(self.legend)
        except:
            pass

        self.no_data_text_item = pg.TextItem(
            html='<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset from the list to view data.</div>')
        self.addItem(self.no_data_text_item)
        self.no_data_text_item.setPos(0.5, 0.5)

        return

    def setData(self, xLine, lineData1, lineData2, units, lineLabels, xBar, barData, barLabels, barUnits, barWidth,
                spacing=0):
        """
        Sets the data in the plot. The function can plot up to 100 series on the same plot
        (50 series in the 'y1' argument and 50 series in the 'y2' argument).

        Pass an array of datetimes to the 'x' argument, and pass an array of
        y-value arrays to one or both of the 'y' arguments.

        example:
            -> Plots 3 series total (2 on y1 axis and 1 on y2 axis).
            self.setData(
                x = np.array([datetime(2020,1,1), datetime(2020,3,1)]),
                y1 = np.array([[4.2, 32.1], [7.3, 4.3]]),
                y2 = np.array([[5.3, 4.2]]),
                units = ['cfs','cfs','degF'],
                labels = ['Hudson River','Cuyahoga River','Sea Surface Temp']


        arguments:
            x:      1-D np.array([...list of datetimes...)
            y1:     2-D np.array([...[dataset1...], [dataset2...],...)
            y2:     2-D np.array([...[dataset1...], [dataset2...],...)
            units:  list e.g. ['cfs','inches','inches']
            labels: list e.g. ['Hudson River', 'Summit Peak', 'Clover Meadows']
        """
        # todo: update doc string

        # CLEAR ANY EXISTING DATA
        for j, item in enumerate(self.line_items_axis_2):
            if item.isActive:

                item.isActive = False
                self.viewbox_axis_2.removeItem(item)
                self.viewbox_axis_2.removeItem(self.circle_items_axis_2[j])

        self.clear()

        # CHECK IF THERE IS ANY DATA TO PLOT
        if xLine.size == 0:
            return

        # CONVERT X TO INTEGER TIMES
        x = np.array(xLine.astype('int64')/1000000000)
        x_bar = np.array(xBar.astype('int64')/1000000000)

        # REFERENCES
        self.x_line = xLine
        self.y1 = lineData1
        self.y2 = lineData2
        self.lineUnits = units
        self.lineLabels = lineLabels

        self.x_bar = xBar
        self.barData = barData
        self.barLabels = barLabels
        self.barUnits = barUnits
        self.barWidth = (barWidth - spacing / 2) * 4

        # RE-INSTANTIATE LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMin2 = np.inf
        self.yMax = -np.inf
        self.yMax2 = -np.inf

        # REMOVE THE OLD LEGEND
        if self.legend.scene() is not None:
            self.legend.scene().removeItem(self.legend)

        # CREATE A NEW LEGEND
        self.legend = TimeSeriesLegend(size=None, offset=(30, 30))
        self.legend.setParentItem(self.vb)

        # SET UP EACH AXIS
        self.y1_Num_Series = len(lineData1)
        self.y2_Num_Series = len(lineData2)
        self.y1_Axis_Units = condenseUnits(units[:self.y1_Num_Series])
        self.y2_Axis_Units = condenseUnits(units[self.y1_Num_Series:])

        # ITERATE OVER 'Y1' MEMBERS AND ACTIVATE THE ITEMS
        for i, dataset in enumerate(lineData1):

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax = np.nanmax([self.yMax, np.nanmax(dataset)])
            self.yMin = np.nanmin([self.yMin, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items[i].setData(x, dataset, name = lineLabels[i], connect = 'finite')
            self.line_items[i].opts['name'] = lineLabels[i]
            self.line_items[i].units = sameUnits(units[i], units[i])[1].lower()
            self.line_items[i].isActive = True

        # ITERATE OVER 'Y2' MEMBERS AND ACTIVATE THE ITEMS
        for j, dataset in enumerate(lineData2):

            k = i + j + 1

            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            # SET NEW LIMITS BASED ON DATASET EXTENT
            self.xMax = np.nanmax([self.xMax, np.nanmax(x)])
            self.xMin = np.nanmin([self.xMin, np.nanmin(x)])
            self.yMax2 = np.nanmax([self.yMax2, np.nanmax(dataset)])
            self.yMin2 = np.nanmin([self.yMin2, np.nanmin(dataset)])

            # ADD TO PLOT
            self.line_items_axis_2[j].setData(x, dataset, name=lineLabels[k], connect='finite')
            self.line_items_axis_2[j].opts['name'] = lineLabels[k]
            self.line_items_axis_2[j].units = sameUnits(units[k], units[k])[1].lower()
            self.line_items_axis_2[j].isActive = True

        # Set the median value line into axis 2
        self.line_items_axis_2[len(lineData2)].setData([self.xMin - self.barWidth, self.xMax + self.barWidth], 2 * [(self.yMax2 + self.yMin2) / 2],
                                                       pen=pg.mkPen((204, 229, 255), width=4, style=QtCore.Qt.DotLine),
                                                       antialias=False, connect='finite')
        self.line_items_axis_2[len(lineData2)].units = self.line_items_axis_2[len(lineData2) - 1].units
        self.line_items_axis_2[len(lineData2)].isActive = True

        # Get the average values to plot the bar in the center
        yAverage = (self.yMax2 + self.yMin2) / 2
        yHalfRange = self.yMax2 - yAverage

        for j, dataset in enumerate(barData):
            # CHECK IF THERE IS DATA TO PLOT
            if dataset.size == 0:
                continue

            heights = dataset * yHalfRange

            # ADD TO PLOT
            self.bar_items[j].setOpts(x=x_bar[j], y0=np.ones(len(dataset)) * yAverage, height=heights, name=self.barLabels[j], width=self.barWidth)
            self.bar_items[j].opts['name'] = self.barLabels[j]
            self.bar_items[j].units = self.barUnits[j]
            self.bar_items[j].isActive = True

        # ADD THE ACTIVATED ITEMS TO THE PLOT
        for i, item in enumerate(self.line_items):
            if item.isActive:
                self.addItem(item)
                self.addItem(self.circle_items[i])

        for j, item in enumerate(self.line_items_axis_2):
            if item.isActive:
                self.viewbox_axis_2.addItem(item)
                self.viewbox_axis_2.addItem(self.circle_items_axis_2[j])

                if item.opts['name'] is not None:
                    self.legend.addItem(item, item.name())

        for j, item in enumerate(self.bar_items):
            if item.isActive:
                self.viewbox_axis_2.addItem(item)
                self.viewbox_axis_2.addItem(self.bar_items_highlight[j])

                if item.name() is not None:
                    self.legend.addItem(item, item.name())

        # SET THE AXIS LABELS
        self.getAxis('left').setLabel(' '.join(self.y1_Axis_Units))
        self.getAxis('right').setLabel(' '.join(self.y2_Axis_Units))

        # DO SOME FINAL WORK WITH THE RANGES AND EXTENTS
        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax), np.isinf(self.yMin)]):
            self.setLimits(xMin=self.xMin - self.barWidth, xMax=self.xMax + self.barWidth, yMin=self.yMin, yMax=self.yMax)
            self.setRange(xRange=(self.xMin - self.barWidth, self.xMax + self.barWidth), yRange=(self.yMin, self.yMax))

        else:
            print(self.xMax, self.xMin, self.yMax, self.yMin)

        if not any([np.isinf(self.xMax), np.isinf(self.xMin), np.isinf(self.yMax2), np.isinf(self.yMin2)]):
            self.viewbox_axis_2.setLimits(xMin=self.xMin - self.barWidth, xMax=self.xMax + self.barWidth,
                                          yMin=self.yMin2, yMax=self.yMax2)
            self.viewbox_axis_2.setRange(

                xRange=(self.xMin, self.xMax),
                yRange=(self.yMin2, self.yMax2)
            )
        else:
            self.viewbox_axis_2.setLimits(

                xMin=self.xMin,
                xMax=self.xMax,
                yMin=0,
                yMax=1,

            )
            self.viewbox_axis_2.setRange(

                xRange=(self.xMin, self.xMax),
                yRange=(0, 1)
            )

        # SHOW GRID AND HIDE EMPTY RIGHT AXIS
        if len(self.y2_Axis_Units) == 0:
            self.hideAxis('right')
        else:
            self.showAxis('right')

        self.showGrid(True, True, 0.85)

        return


class ScatterPlot(TimeSeriesPlot):

    def __init__(self, parent=None, objectName = None, *args):

        # USE TIME SERIES PLOT AS BASE CLASS
        TimeSeriesPlot.__init__(self, parent = parent, *args)

        # CHANGE THE LINE ITEMS TO CIRCLE ITEMS
        self.line_items = [self.createScatterItem(i) for i in range(50)]
        self.line_items_axis_2 = [self.createScatterItem(i) for i in range(5,55)]

        return

    def mouseMoved(self, event):
        """
        Update the legend with the specific
        data that the mouse is hovering over.
        """

        # DON'T DO ANYTHING IF THERE ARE NO DATASETS
        if self.labels == []:
            return

        # GET THE MOUSE POSITION
        pos = QtCore.QPoint(event.x(), event.y())

        # CHECK THAT THE OVERALL WIDGET ACTUALLY CONTAINS THE MOUSE POINT
        if self.sceneBoundingRect().contains(pos):

            # GET THE MOUSE POSITION IN DATA COORDINATES]
            mouse_point = self.vb.mapSceneToView(pos)
            x_ = mouse_point.x()

            # ROUND THE X VALUE TO THE NEAREST DATE
            idx = int(x_ - x_%86400)

            # ITERATE OVER THE ACTIVE ITEMS AND DISPLAY THE POINTS IN THE LEGEND
            legend_count = 0
            for i, item in enumerate(self.line_items):
                if item.isActive:
                    date = takeClosest(item.data['x'], idx)
                    idx2 = np.where(item.data['x'] == date)
                    yval = round(item.data['y'][idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items[i].setData([date], [yval])
                    legend_count += 1

            for j, item in enumerate(self.line_items_axis_2):
                if item.isActive:
                    date = takeClosest(item.data['x'], idx)
                    idx2 = np.where(item.data['x'] == date)
                    yval = round(item.data['y'][idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circle_items_axis_2[j].setData([date], [yval])
                    legend_count += 1

        return

    def createScatterItem(self, idx):
        """
        Creates and returns a scatter plot item
        """
        pi = pg.ScatterPlotItem(
            size=4,
            alpha=1,
            brush=self.parent.brush_cycler[idx % 10]
        )
        pi.isActive = False
        return pi


class LineErrorPlot(pg.PlotItem):

    def __init__(self, *args):

        return

#=======================================================================================================================
# FRONT END PLOT DEFINITIONS
#=======================================================================================================================
class ModelTabTargetPlot(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None, objectName = None):

        # INSTANTIATE THE WIDGET AND REFERENCE THE PARENT
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # CREATE A COLOR CYCLER
        self.colors = [
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150),
            (0, 115, 150)
        ]

        self.pen_cycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brush_cycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]

        # ADD PLOT
        self.plot = BarAndLinePlot(self, xAxis='datetime')
        self.addItem(self.plot, 0, 0)

        self.primaryColor = (0, 115, 150)
        self.secondaryColor = (204, 229, 255)

        return

    def clearPlots(self):

        self.plot.clearPlots()

    def displayData(self, x, y, units, labels):
        barWidth = 86400*300
        self.plot.setData(x, np.array([[]]), y.reshape(1,-1), units, labels, barWidth, spacing=0)
        #self.plot.setData(x, y.reshape(1,-1), np.array([[]]), units, labels)
        x2 = x.astype('int64')/1000000000
        medianBar = pg.PlotCurveItem(parent = self.plot, pen = pg.mkPen(self.secondaryColor, width=4, style=QtCore.Qt.DotLine), antialias=False, connect='finite')
        medianBar.setData([x2[0], x2[-1]], 2*[np.nanmedian(y)], name='Median Value: <strong>{0} {1}</strong>'.format(round(np.nanmedian(y),3), units[0]))
        self.plot.addItem(medianBar)
        xAxis = self.plot.getAxis('bottom')
        ticks = [i.year for i in x]
        xAxis.setTicks([[(x2[j], str(v)) for j, v in enumerate(ticks)]])
        buff = (np.nanmax(y) - np.nanmin(y))/10
        self.plot.setLimits(xMin=self.plot.xMin, xMax=self.plot.xMax, yMin=self.plot.yMin-buff, yMax=self.plot.yMax+buff)
        self.plot.setRange(xRange=(self.plot.xMin, self.plot.xMax), yRange=(self.plot.yMin-buff, self.plot.yMax+buff))
        self.plot.viewbox_axis_2.setLimits(xMin=self.plot.xMin, xMax=self.plot.xMax, yMin=self.plot.yMin-buff, yMax=self.plot.yMax+buff)
        self.plot.viewbox_axis_2.setRange(xRange=(self.plot.xMin, self.plot.xMax), yRange=(self.plot.yMin-buff, self.plot.yMax+buff))
        return


class DataTabPlots(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None):

        # INSTANTIATE THE WIDGET AND CREATE A REFERENCE TO THE PARENT
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent

        # SET MINIMUM ROW SIZE FOR ROWS
        [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]

        # GET A REFERENCE TO THE DATASET TABLE AND THE DATATABLE
        self.datasetTable = self.parent.parent.datasetTable
        self.dataTable = self.parent.parent.dataTable

        # CREATE A COLOR CYCLER
        self.colors = [
            (255, 61, 0),
            (0, 145, 234),
            (0, 200, 83),
            (189, 157, 0),
            (255, 103, 32),
            (170, 0, 255),
            (141, 110, 99),
            (198, 255, 0),
            (29, 233, 182),
            (136, 14, 79)
        ]

        self.pen_cycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brush_cycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]

        # INSTANTIATE THE PLOTS
        self.timeSeriesPlot = TimeSeriesPlot(self)
        self.timeSliderPlot = TimeSeriesSliderPlot(self)

        # ADD INTERACTION
        self.timeSliderPlot.region.sigRegionChanged.connect(self.updatePlot)
        self.timeSeriesPlot.sigRangeChanged.connect(self.updateRegion)

        # ADD TO LAYOUT
        self.addItem(self.timeSeriesPlot, row=0, col=0, rowspan=7)
        self.addItem(self.timeSliderPlot, row=7, col=0, rowspan=2)

        return

    def clearPlots(self):

        self.timeSeriesPlot.clear()
        self.timeSliderPlot.clear()

        return

    def displayDatasets(self, datasets):
        """

        @param datasets:
        @return:
        """

        labels = []
        units = []
        y1 = np.array([])
        y2 = np.array([]).reshape(1,-1)

        # GET A REFERENCE TO THE DATASET TABLE AND THE DATATABLE
        self.datasetTable = self.parent.parent.datasetTable
        self.dataTable = self.parent.parent.dataTable

        # FIGURE OUT THE MIN/MAX INDEX FOR THE PLOT
        min_date = self.dataTable.index.get_level_values(0).min()
        max_date = self.dataTable.index.get_level_values(0).max()


        # GET THE X ARRAY
        x = pd.date_range(start=min_date, end=max_date, freq='D')

        # CREATE A RE-INDEX OBJECT
        reindex = pd.DatetimeIndex(x)

        for i, datasetID in enumerate(datasets):

            # GET THE DATASET
            dataset = self.datasetTable.loc[datasetID]

            # GET THE DATASET TITLE
            labels.append(dataset['DatasetName'] + ': ' + dataset['DatasetParameter'])

            # GET THE UNITS
            units.append(dataset['DatasetUnits'])

            # GET THE DATA
            y = self.dataTable.loc[(slice(None), datasetID), 'Value'].droplevel(1).reindex(reindex)

            # APPEND TO THE y2 ARRAY
            y2 = np.append(y2, y.values.reshape(1,-1), axis=1 if i == 0 else 0)

        # CONVERT ALL UNITS TO THEIR BASE FORMS
        units = [sameUnits(i,i)[1] for i in units]

        # GET A COUNT OF THE UNITS TO FIND THE MOST PREVALANT ONE
        uniq, uniq_idx, uniq_count = np.unique(units, return_index=True, return_counts=True)
        max_idx = list(uniq_count).index(max(uniq_count))

        # REORDER LABELS, UNITS, AND y LISTS
        y1_indices = np.where(np.array(units) == uniq[max_idx])[0]
        y1_units = [units.pop(i-j) for j, i in enumerate(y1_indices)]
        y1_labels = [labels.pop(i-j) for j, i in enumerate(y1_indices)]
        y1 = y2[y1_indices]
        y2 = np.delete(y2, y1_indices, axis=0)
        units = y1_units + units
        labels = y1_labels + labels


        # PLOT
        self.timeSeriesPlot.setData(x.values, y1, y2, units, labels)
        self.timeSliderPlot.setData(x.values, y1, y2)

        return

    # Changes the bounds of the Time Series Plot when the slider is moved
    def updatePlot(self):

        self.timeSliderPlot.region.setZValue(10)
        newRegion = self.timeSliderPlot.region.getRegion()
        if not any(np.isinf(newRegion)):
            self.timeSeriesPlot.setXRange(*self.timeSliderPlot.region.getRegion(), padding=0)
            [self.timeSeriesPlot.items[i].viewRangeChanged() for i in
             range(len(self.timeSeriesPlot.items))]

        return

    # Changes the bounds of the slider when the Time Series Plot is moved
    def updateRegion(self, window, viewRange):

        self.timeSliderPlot.region.setZValue(10)
        self.timeSliderPlot.region.setRegion(viewRange[0])
        [self.timeSeriesPlot.items[i].viewRangeChanged() for i in range(len(self.timeSeriesPlot.items))]

        return


class FillExtendTabPlots(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None):

        # INSTANTIATE THE WIDGET AND CREATE A REFERENCE TO THE PARENT
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent

        # CREATE A COLOR CYCLER
        self.colors = [
            (255, 61, 0),
            (0, 145, 234),
            (0, 200, 83),
            (189, 157, 0),
            (255, 103, 32),
            (170, 0, 255),
            (141, 110, 99),
            (198, 255, 0),
            (29, 233, 182),
            (136, 14, 79)
        ]

        self.pen_cycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brush_cycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]

        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = None
        self.level = None
        self.units = None

        # INSTANTIATE THE PLOTS
        self.timeSeriesPlot = TimeSeriesPlot(self)

        # ADD TO LAYOUT
        self.addItem(self.timeSeriesPlot, row=0, col=0, rowspan=7)

        return

    def clearPlots(self):

        self.timeSeriesPlot.clear()

        return


    def updateData(self, dataframe, level, units):
        # todo: doc string

        self.datasetTable = dataframe
        self.level = level
        self.units = units

    def displayDatasets(self):
        """

        @param datasets:
        @return:
        """

        # Get all data on the specified level
        if self.level is not None:
            # Get the location of the index attribute in the index vector
            columnIndex = [x for x in range(0, len(self.datasetTable.index.names), 1) if
                           self.datasetTable.index.names[x] == self.level][0]

            # Find the unique entries to be plotted
            datasetLabels = list(set([x[columnIndex] for x in self.datasetTable.index]))

            # Define plot names
            plotUnits = [self.units for x in datasetLabels]

            # Remove the value field label from the data
            plotData = [self.datasetTable.loc[(slice(None), datasetLabels[x]), 'Value'].values for x in range(0, len(datasetLabels))]
            plotData = np.atleast_2d(plotData)

            # Get the plot locations
            plotLocations = self.datasetTable.loc[(slice(None), datasetLabels[0]), 'Value'].index.droplevel(1).values

            # Perform an update on the timeseries plot
            self.timeSeriesPlot.setData(plotLocations, plotData, [], plotUnits, datasetLabels)


        return

    def updateData(self, dataframe, level, units):
        # todo: doc string

        self.datasetTable = dataframe
        self.level = level
        self.units = units


class WindowTabPlots(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None):

        # INSTANTIATE THE WIDGET AND CREATE A REFERENCE TO THE PARENT
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent

        # CREATE A COLOR CYCLER
        self.colors = [
            (255, 61, 0),
            (0, 145, 234),
            (0, 200, 83),
            (189, 157, 0),
            (255, 103, 32),
            (170, 0, 255),
            (141, 110, 99),
            (198, 255, 0),
            (29, 233, 182),
            (136, 14, 79)
        ]

        self.pen_cycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brush_cycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]

        self.primaryColor = (0, 115, 150)
        self.secondaryColor = (204, 229, 255)

        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = None
        self.level = None
        self.units = None

        # INSTANTIATE THE PLOTS
        self.plot = BarandDoubleAxisLinePlot(self)

        # ADD TO LAYOUT
        self.addItem(self.plot, row=0, col=0, rowspan=7)

        return

    def clearPlots(self):
        # todo: doc string

        self.plot.clearPlots()

        return


    def displayDatasets(self, sourceName, targetName, sourceData, targetData, sourceUnits, targetUnits, barUnits):
        """

        @param datasets:
        @return:
        """

        # Clear the existing data
        self.plot.clearPlots()

        # Calculate the correlation based on the lag
        if len(sourceData) > 1:
            # Start date is before the end date, so lag is positive. Calculate a nonzero correlation to display.
            # Cross correlation between the source and target datasets
            correlation = np.atleast_2d(ccf(targetData.values, sourceData.values))
            xBar = np.atleast_2d(sourceData.index)

            dateRange = sourceData.index
            targetData = np.atleast_2d(targetData.values)
            sourceData = np.atleast_2d(sourceData.values)

            self.plot.setData(dateRange, sourceData, targetData, [sourceUnits, targetUnits], [sourceName, targetName],
                              xBar, correlation, [barUnits], ['Correlation'], 10000)

        else:
            # Start date is after the end date, so the lag is negative. Return a zero correlation
            # INITIAL TEXT FOR EMPTY PLOT
            self.no_data_text_item = pg.TextItem(html='<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset to view data.</div>')
            self.plot.addItem(self.no_data_text_item)
            self.no_data_text_item.setPos(0.5, 0.5)

        return


class ResultsTabPlots(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None, xLabel='', yLabel=''):

        # INSTANTIATE THE WIDGET AND CREATE A REFERENCE TO THE PARENT
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.parent = parent

        # Get a reference to the datasetTable and the dataTable
        self.datasetTable = None

        # INSTANTIATE THE PLOTS
        self.resultPlot = pg.PlotItem()
        self.resultPlot.getAxis('left').setLabel(yLabel, **{'font-size':'14pt'})
        self.resultPlot.getAxis('bottom').setLabel(xLabel, **{'font-size':'14pt'})
        self.resultPlot.addLegend(offset=[0, 0])
        #viewBox = self.resultPlot.getViewBox()
        #viewBox.setBackgroundColor((240, 240, 240))
        self.resultPlot.showGrid(True, True, 0.25)
        self.resultPlot.setMouseEnabled(x=False, y=False)
        self.updated = False
        self.xExtents = [0,0]
        self.yExtents = [0,0]

        self.textOverlay = pg.TextItem(html = '<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset to view data.</div>', anchor=(1,1))
        self.resultPlot.addItem(self.textOverlay)
        self.textOverlay.setPos(0, 0)

        # ADD INTERACTION
        #self.scene().sigMouseMoved.connect(self.mouseMoved)

        # ADD TO LAYOUT
        self.addItem(self.resultPlot)

        # Define default colors
        self.primaryColor = (0, 115, 150)
        self.secondaryColor = (204, 229, 255)
        self.observedColor = (0, 0, 0)

        return


    def mouseMoved(self, event):
        """
        Update the legend with the specific
        data that the mouse is hovering over.
        """

        # DON'T DO ANYTHING IF THERE ARE NO DATASETS
        if self.updated == False:
            return

        # GET THE MOUSE POSITION
        pos = QtCore.QPoint(event.x(), event.y())

        mousePoint = self.resultPlot.vb.mapSceneToView(pos)
        isValidX = self.xExtents[0] <= mousePoint.x() <= self.xExtents[1]
        isValidY = self.yExtents[0] <= mousePoint.y() <= self.yExtents[1]

        # CHECK THAT THE OVERALL WIDGET ACTUALLY CONTAINS THE MOUSE POINT
        if self.resultPlot.sceneBoundingRect().contains(pos) and isValidX and isValidY:
            self.textOverlay.setText("X=%0d, Y=%0d" % (mousePoint.x(), mousePoint.y()))
            self.resultPlot.addItem(self.textOverlay)
            self.textOverlay.setPos(mousePoint.x(), mousePoint.y())

        return


    def updateScatterPlot(self, dataframe):
        """

        @param datasets:
        @return:
        """
        self.datasetTable = dataframe
        self.resultPlot.clear()
        obs = self.datasetTable['Observed'].values
        mod = self.datasetTable['Prediction'].values
        modCv = self.datasetTable['CV-Prediction'].values

        self.resultPlot.plot(x=obs, y=modCv, pen=None,  symbolBrush=self.secondaryColor, symbolPen='w', symbol='o', symbolSize=7, name="CV-Prediction")
        z = np.polyfit(obs, modCv, 1)
        p = np.poly1d(z)
        self.resultPlot.plot(x=obs, y=p(obs), pen=pg.mkPen(color=self.secondaryColor, width=0.5, style=QtCore.Qt.DotLine))

        self.resultPlot.plot(x=obs, y=mod, pen=None, symbolBrush=self.primaryColor, symbolPen='w', symbol='h', symbolSize=14, name="Prediction")
        z = np.polyfit(obs, mod, 1)
        p = np.poly1d(z)
        self.resultPlot.plot(x=obs, y=p(obs), pen=pg.mkPen(color=self.primaryColor, width=2, style=QtCore.Qt.DotLine))

        self.updated = True
        self.xExtents = [min(obs), max(obs)]
        self.yExtents = [min(min(mod),min(modCv)), max(max(mod),max(modCv))]

        return


    def appendForecast(self, fcastValue, fcastRange, fcastLabel=None):
        """

        :param dataframe:
        :return:
        """
        self.resultPlot.clearPlots()
        self.updateScatterPlot(self.datasetTable)
        if fcastLabel is None:
            fcastLabel = 'Forecast (' + ("%.2f" % fcastValue) + ')'
        else:
            fcastLabel = str(fcastLabel) + ' Forecast (' + ("%.2f" % fcastValue) + ')'
        self.resultPlot.plot(x=[fcastValue], y=[fcastValue], pen=None, symbolBrush=(255, 0, 0), symbolPen='w', symbol='s', symbolSize=12, name=fcastLabel)

        rectItem = RectItem(QtCore.QRectF(fcastRange.loc[10], fcastRange.loc[10], fcastRange.loc[90] - fcastRange.loc[10], fcastRange.loc[90] - fcastRange.loc[10]),85)
        self.resultPlot.addItem(rectItem)

        rectItem = RectItem(QtCore.QRectF(fcastRange.loc[25], fcastRange.loc[25], fcastRange.loc[75] - fcastRange.loc[25], fcastRange.loc[75] - fcastRange.loc[25]),75)
        self.resultPlot.addItem(rectItem)

        return


    def appendSavedForecast(self, savedFcastRange, fcastLabel=None):

        #xVals = list(savedFcastRange.index)
        #yVals = savedFcastRange.values.flatten()
        #self.resultPlot.plot(x=xVals, y=yVals, pen=pg.mkPen(color=self.primaryColor, width=2),  name=('Model:' + str(fcastLabel)))
        boxItems = BoxPlotItem(savedFcastRange,70)
        self.resultPlot.hideAxis('bottom')
        self.resultPlot.addItem(boxItems)
        return


    def updateTimeSeriesPlot(self, dataframe):
        """

        @param datasets:
        @return:
        """
        self.datasetTable = dataframe
        self.resultPlot.clear()
        idx = self.datasetTable['Years'].values
        obs = self.datasetTable['Observed'].values
        mod = self.datasetTable['Prediction'].values
        modCv = self.datasetTable['CV-Prediction'].values
        self.resultPlot.plot(x=idx, y=obs, pen=pg.mkPen(color=self.observedColor, width=3),  name="Observed")
        self.resultPlot.plot(x=idx, y=mod, pen=pg.mkPen(color=self.secondaryColor, width=1, style=QtCore.Qt.DotLine),  name="CV-Prediction")
        self.resultPlot.plot(x=idx, y=modCv, pen=pg.mkPen(color=self.primaryColor, width=2),  name="Prediction")

        self.updated = True
        self.xExtents = [min(idx), max(idx)]
        self.yExtents = [min(min(obs),min(mod),min(modCv)), max(max(obs),max(mod),max(modCv))]

        return


    def updateResidualPlot(self, dataframe):
        """

        @param datasets:
        @return:
        """
        self.datasetTable = dataframe
        self.resultPlot.clear()
        idx = self.datasetTable['Years'].values
        err = self.datasetTable['PredictionError'].values
        errCv = self.datasetTable['CV-PredictionError'].values
        self.resultPlot.plot(x=idx, y=errCv, pen=None,  symbolBrush=self.secondaryColor, symbolPen='w', symbol='o', symbolSize=6, name="CV-Error")
        self.resultPlot.plot(x=idx, y=err, pen=None, symbolBrush=self.primaryColor, symbolPen='w', symbol='h', symbolSize=10, name="Error")

        self.updated = True
        self.xExtents = [min(idx), max(idx)]
        self.yExtents = [min(min(err),min(errCv)), max(max(err),max(errCv))]

        return

    def clearPlot(self):
        self.resultPlot.clear()
        return


class RectItem(pg.GraphicsObject):
    """
    Class for creating a rectangle item
    """
    def __init__(self, rect, transparency, parent=None):
        super().__init__(parent)
        self.alpha = int((100 - transparency) * 255 / 100)
        self._rect = rect
        self.picture = QtGui.QPicture()
        self._generate_picture()

    @property
    def rect(self):
        return self._rect

    def _generate_picture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen(0,0,0,0))
        painter.setBrush(pg.mkBrush(255,0,0,self.alpha))
        painter.drawRect(self.rect)
        painter.end()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class BoxPlotItem(pg.GraphicsObject):
    """
    Class for creating a boxplot item
    """
    def __init__(self, data, transparency):
        pg.GraphicsObject.__init__(self)
        self.data = data  ## data must have fields: xVal, p50, p25, p75, p10, p90
        self.alpha = int((100 - transparency) * 255 / 100)
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        try:
            w = (self.data[1][0] - self.data[0][0]) / 3.
        except:
            w = 1
        for (xVal, p50, p25, p75, p10, p90, fcast) in self.data:
            # draw box
            p.setPen(pg.mkPen(color=(0, 115, 150), width=4))
            p.setBrush(pg.mkBrush(0, 115, 150, self.alpha))
            p.drawRect(QtCore.QRectF(xVal - w, p25, w * 2, p50 - p25))
            p.drawRect(QtCore.QRectF(xVal - w, p50, w * 2, p75 - p50))
            # draw whiskers
            p.setPen(pg.mkPen(color=(0, 115, 150), width=3, style=QtCore.Qt.DotLine))
            p.drawLine(QtCore.QPointF(xVal, p10), QtCore.QPointF(xVal, p25))
            p.drawLine(QtCore.QPointF(xVal, p75), QtCore.QPointF(xVal, p90))
            p.drawLine(QtCore.QPointF(xVal - w/2, p10), QtCore.QPointF(xVal + w/2, p10))
            p.drawLine(QtCore.QPointF(xVal - w/2, p90), QtCore.QPointF(xVal + w/2, p90))
            # draw discrete forecast
            p.setPen(pg.mkPen(color=(255, 0, 0), width=8))
            p.drawLine(QtCore.QPointF(xVal - w/4, fcast), QtCore.QPointF(xVal + w/4, fcast))

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


#=======================================================================================================================
# DEBUG GRAPHICSLAYOUTWIDGET
#=======================================================================================================================
class debugPlots(pg.GraphicsLayoutWidget):

    def __init__(self, option = 'timeseries'):

        # Instantiate the widget and create a reference to the parent
        pg.GraphicsLayoutWidget.__init__(self)

        # Create a color cyler
        self.colors = [
            (255, 61, 0),
            (0, 145, 234),
            (0, 200, 83),
            (189, 157, 0),
            (255, 103, 32),
            (170, 0, 255),
            (141, 110, 99),
            (198, 255, 0),
            (29, 233, 182),
            (136, 14, 79)
        ]
        self.pen_cycler = [pg.mkPen(pg.mkColor(color), width=1.5) for color in self.colors]
        self.brush_cycler = [pg.mkBrush(pg.mkColor(color)) for color in self.colors]
        self.option = option
        if option == 'timeseries':
            self.plot = TimeSeriesPlot(self)
            self.addItem(self.plot, row=0, col=0, rowspan=7)

        elif option == 'scatter':
            self.plot = ScatterPlot(self)
            self.addItem(self.plot, row=0, col=0, rowspan=7)

        elif option=='barline':
            self.plot = BarAndLinePlot(self, 'datetime')
            self.addItem(self.plot, row=0, col=0, rowspan=7)

        elif option=='tsPlusSlider':
            self.plot = TimeSeriesPlot(self)
            self.plot2 = TimeSeriesSliderPlot(self)
            self.plot2.region.sigRegionChanged.connect(self.updatePlot)
            self.plot.sigRangeChanged.connect(self.updateRegion)
            self.addItem(self.plot, row=0, col=0, rowspan=7)
            self.addItem(self.plot2, row=7, col=0, rowspan=1)

        return

    # Changes the bounds of the Time Series Plot when the slider is moved
    def updatePlot(self):

        self.plot2.region.setZValue(10)
        newRegion = self.plot2.region.getRegion()
        if not any(np.isinf(newRegion)):
            self.plot.setXRange(*self.plot2.region.getRegion(), padding=0)
            [self.plot.items[i].viewRangeChanged() for i in
             range(len(self.plot.items))]

        return

    # Changes the bounds of the slider when the Time Series Plot is moved
    def updateRegion(self, window, viewRange):

        self.plot2.region.setZValue(10)
        self.plot2.region.setRegion(viewRange[0])
        [self.plot.items[i].viewRangeChanged() for i in range(len(self.plot.items))]

        return

    def displayData(self, x, y1, y2, units, labels):

        if self.option == 'tsPlusSlider':
            self.plot.setData(x,y1,y2,units,labels)
            self.plot2.setData(x,y1,y2)

        elif self.option == 'barline':
            self.plot.setData(x,y1,y2,units,labels, barWidth=86400, spacing=15000)

        else:
            self.plot.setData(x,y1,y2,units,labels)


# DEBUG
if __name__ == '__main__':
    import pandas as pd
    import sys

    # Debugging dataset
    app = QtWidgets.QApplication(sys.argv)

    mw = QtWidgets.QMainWindow()

    # LOAD IN SOME DATA
    mw.datasetTable = pd.DataFrame(
        index=pd.Index([], dtype=int, name='DatasetInternalID'),
        columns=[
            'DatasetType',  # e.g. STREAMGAGE, or RESERVOIR, ETC
            'DatasetExternalID',  # e.g. "GIBR" or "06025500"
            'DatasetName',  # e.g. Gibson Reservoir
            'DatasetAgency',  # e.g. USGS
            'DatasetParameter',  # e.g. Temperature
            "DatasetParameterCode",  # e.g. avgt
            'DatasetUnits',  # e.g. CFS

        ],
    )

    mw.datasetTable.loc[100000] = ["RESERVOIR", "GIBR", "Gibson Reservoir", "USBR", "Inflow", "in", 'inches']
    mw.datasetTable.loc[100001] = ["STREAMGAGE", "0120332", "Sun River Near Augusta", "USGS", "Streamflow", "00060",
                                   'cfs']

    mw.dataTable = pd.DataFrame(
        index=pd.MultiIndex(
            levels=[[], [], ],
            codes=[[], [], ],
            names=[
                'Datetime',  # E.g. 1998-10-23
                'DatasetInternalID'  # E.g. 100302
            ]
        ),
        columns=[
            "Value",  # E.g. 12.3, Nan, 0.33
            "EditFlag"  # E.g. True, False -> NOTE: NOT IMPLEMENTED
        ],
        dtype=float
    )
    mw.dataTable['EditFlag'] = mw.dataTable['EditFlag'].astype(bool)

    dates = pd.date_range('1999-10-01', '2001-09-30', freq='D')
    y1 = np.sin(0.5 * np.array(range(len(dates)))) + np.random.randint(-4, 5)
    y2 = np.cos(0.2 * np.array(range(len(dates))))

    for i in range(len(dates)):
        if i == 40:
            # Test case for NaNs
            mw.dataTable.loc[(dates[i], 100000), 'Value'] = np.nan
        else:
            mw.dataTable.loc[(dates[i], 100000), 'Value'] = y1[i]
        mw.dataTable.loc[(dates[i], 100001), 'Value'] = y2[i]


    # LOAD UP A PLOT WIDGET
    plot = DataTabPlots(mw)
    mw.setCentralWidget(plot)
    plot.displayDatasets([100000, 100001])
    mw.show()
    sys.exit(app.exec_())