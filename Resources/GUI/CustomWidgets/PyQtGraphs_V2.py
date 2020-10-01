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
        pg.LegendItem.__init__(self, size, offset, brush=(200, 200, 200, 100))

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
            width = max(width, sample.boundingRect().width() + label.width())

        self.setGeometry(0, 0, width + 60, height)


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
        pg.PlotItem.__init__(self, args)

        # REFERENCE THE PARENT
        self.parent = parent

        # CREATE AXES
        self.setAxisItems({"bottom": DateTimeAxis(orientation='bottom')})
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

        # CONNECT SIGNALS
        self.vb.sigResized.connect(self.updateViews)

        # CREATE LINE AND CIRCLE ITEMS
        self.line_items = [self.createPlotItem(i) for i in range(50)]
        self.line_items_axis_2 = [self.createPlotItem(i) for i in range(50)]
        self.circle_items = [self.createCircleItem(i) for i in range(50)]
        self.circle_items_axis_2 = [self.createCircleItem(i) for i in range(50)]

        # INSTANTIATE PLOT LIMITS
        self.xMin = np.inf
        self.xMax = -np.inf
        self.yMin = np.inf
        self.yMax = -np.inf

        # SET DEFAULT BOUNDS
        self.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.viewbox_axis_2.setLimits(xMin=0, xMax=1, yMin=0, yMax=1)
        self.setRange(xRainge=(0,1), yRange=(0,1))
        self.viewbox_axis_2.setRange(xRainge=(0, 1), yRange=(0, 1))

        # INITIAL TEXT FOR EMPTY PLOT
        self.no_data_text_item = pg.TextItem(html = '<div style="color:#4e4e4e"><h1>Oops!</h1><br> Looks like there is no data to display.<br>Select a dataset from the list to view data.</div>')
        self.addItem(self.noDataTextItem)
        self.noDataTextItem.setPos(0.5, 0.5)

        # ADD INTERACTION
        self.parent.scene().sigMouseMoved.connect(self.mouseMoved)

        self.updateViews()

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
            idx = int(x_ - x_%864000)

            # ITERATE OVER THE ACTIVE ITEMS AND DISPLAY THE POINTS IN THE LEGEND
            legend_count = 0
            for i, item in enumerate(self.line_items):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circleItems_[i].setData([date], [yval])
                    legend_count += 1

            for j, item in enumerate(self.line_items_axis_2):
                if item.isActive:
                    date = takeClosest(item.xData, idx)
                    idx2 = np.where(item.xData == date)
                    yval = round(item.yData[idx2[0]][0],2)
                    self.legend.items[legend_count][1].setText(item.opts['name']+' <strong>'+str(yval) +' '+ item.units+'</strong>')
                    self.circleItems_[j].setData([date], [yval])
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
        Sets the data in the plot

        arguments:
            x:      np.array()
            y1:     np.array()
            y2:     np.array()
            units:  list
            labels: list
        """

        # CLEAR ANY EXISTING DATA
        for j, item in enumerate(self.items_axis2):
            if item.isActive:

                item.isActive = False
                self.viewbox_axis2.removeItem(item)
                self.viewbox_axis2.removeItem(self.circleItems_axis2[j])

        self.clear()

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




    def updateViews(self):
        """
        Update the Y2 axis view to match the y1 axis view.
        """
        self.viewbox_axis_2.setGeometry(self.vb.sceneBoungingRect())
        self.viewbox_axis_2.linkedViewChanged(self.vb, self.viewbox_axis_2.XAxis)

        return

class TimeSeriesSliderPlot(pg.PlotItem):

    def __init__(self, *args):

        return

class TimeSeriesBarAndLinePlot(pg.PlotItem):

    def __init__(self, *args):

        return

class ScatterPlot(pg.PlotItem):

    def __init__(self, *args):

        return

class LineErrorPlot(pg.PlotItem):

    def __init__(self, *args):

        return

#=======================================================================================================================
# FRONT END PLOT DEFINITIONS
#=======================================================================================================================