import pyqtgraph as pg
from PyQt5.QtGui import QColor
import numpy as np
from bisect import bisect_left

# Plotting configuration
pg.setConfigOptions(**{
    'leftButtonPan': False,
    'foreground': '#222222',
    'background': '#fffefc',
    'antialias': True,
    'useOpenGL': True}
)

class CurveItem(pg.PlotCurveItem):

    def __init__(self, color=pg.mkColor('k'), **kwargs):

        pg.PlotCurveItem.__init__(self, **kwargs)

        self.opts['antialias'] = True
        self.opts['strpMode'] = 'left'
        self.opts['fillLevel'] = kwargs['fillLevel'] if 'fillLevel' in kwargs else 0
        
        self.color = QColor(color)
        self.brush_color = QColor(self.color)
        self.brush_color.setAlpha(185)
        self.shadow_color = self.color.darker(250)

        self.pen_ = pg.mkPen(self.color, width=0.5)
        self.brush_ = pg.mkBrush(self.brush_color)
        self.shadow_ = pg.mkPen(self.shadow_color, width = 1)

        self.setPen(self.color)
        self.setBrush(self.brush_color)
        self.setShadowPen(self.shadow_)


class BarItem(pg.BarGraphItem):

    def __init__(self, color=pg.mkColor('k'), **kwargs):

        pg.BarGraphItem.__init__(self, **kwargs)

        self.color = QColor(color)
        self.brush_color = QColor(self.color)
        self.brush_color.setAlpha(185)
        self.shadow_color = self.color.darker(250)

        self.pen_ = pg.mkPen(self.color, width=1.5)
        self.brush_ = pg.mkBrush(self.brush_color)
       
        self.setOpts(
            pen=self.pen_,
            brush=self.brush_
        )

class ScatterItem(pg.ScatterPlotItem):

    def __init__(self, color=pg.mkColor('k'), **kwargs):

        pg.ScatterPlotItem.__init__(self, **kwargs)

        self.color = QColor(color)
        self.brush_color = QColor(self.color)
        self.brush_color.setAlpha(185)

        self.pen_ = pg.mkPen(self.color, width=1.5)
        self.brush_ = pg.mkBrush(self.brush_color)

        self.setPen(self.color)
        self.setBrush(self.brush_color)
        self.setSymbol('s')
        self.opts['hoverable'] = True if 'hoverable' not in kwargs else kwargs['hoverable']
        self.opts['hoverPen'] = pg.mkPen(pg.mkColor('r'), width=2)
        self.opts['tip'] = None


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
        label.setAttr('bold',True)

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

    #def clear(self):
    #    self.__init__(size = self.size, offset=self.offset)

    def updateSize(self):

        if self.size is not None:
            return

        height = 0
        width = 0

        for sample, label in self.items:
            height += max(sample.boundingRect().height(), label.height()) + 3
            width = max(width, sample.boundingRect().width() + label.width())

        self.setGeometry(0, 0, width + 60, height)

EQUIVALENCY_LISTS = [
    ["INCHES", "INCH", "IN", "IN.", '"'],
    ["METERS", "METER", "M"],
    ["CENTIMETERS","CENTIMETER", "CM"],
    ['FEET', 'FOOT', 'FT', 'FT.', "'"],
    ['CFS', 'CUBIC FEET PER SECOND', 'FT3/S', 'FT3/SEC'],
    ["CMS", "CUBIC METERS PER SECOND", "CM/S", "M3/SEC", "M3/S"],
    ['MCM', 'MILLION CUBIC METERS', 'M3M'],
    ['ACRE-FEET', 'AF', 'AC-FT', 'ACRE-FT'],
    ['KAF', 'THOUSAND ACRE-FEET', 'KAC-FT', 'THOUSAND ACRE-FT'],
    ['DEGREES', 'DEGF', 'DEG. FAHRENHEIT', 'DEGC', 'DEGREES FAHRENHEIT', 'DEGREES CELCIUS', 'DEG FAHRENHEIT', 'DEG CELCIUS', 'DEG. CELCIUS'],
    ['PERCENT', '%', 'PCT', 'PCT.'],
    ['UNITLESS', "-"],
]

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
    counts = []
    # FOR EACH ELEMENT IN THE INITIAL LIST,
    # CHECK FOR EQIVALENCE TO OTHER UNITS
    while len(unitList) > 0:
        unit = unitList[0]
        unit_simplified = sameUnits(unit, unit)[1]
        condensedList.append(unit_simplified)
        equiv_list = [sameUnits(unit_simplified, i) for i in unitList[1:]]
        counts.append(np.count_nonzero(equiv_list))
        j=0
        for i, res in enumerate(equiv_list):
            if res[0]:
                unitList.pop(i+1-j)
                j += 1
        unitList.pop(0)
    maxCountIdx = counts.index(max(counts))
    condensedList = [condensedList[maxCountIdx]] + condensedList[:maxCountIdx] + condensedList[maxCountIdx+1:]
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
        return myList[0], pos
    if pos == len(myList):
        return myList[-1], pos-1
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after, pos
    else:
        return before, pos-1