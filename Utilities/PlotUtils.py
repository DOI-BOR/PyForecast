from bisect import bisect_left
import pyqtgraph as pg
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
import numpy as np
from numba import jit

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

@jit(nopython=True)
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
        return after, pos-1
    else:
        return before, pos

class TimeSeriesLegend(pg.LegendItem):
    """
    Interactive legend. (Subclassed to add
    resize capability on label changes)
    """

    def __init__(self, size=None, offset=None):

        # Instantiate the legend Item
        pg.LegendItem.__init__(self, size, offset, brush=(200, 200, 200, 140))
        self.legFont = QFont('Segoe UI')

    def addItem(self, item, name):

        # Instantiate a Label Item using the supplied Name
        label = pg.graphicsItems.LegendItem.LabelItem(name, justify='left', size='12pt')
        label.item.setFont(self.legFont)

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
        return QRectF(0, 0, 20, 20)

    def paint(self, p, *args):
        opts = self.item.opts

        p.setBrush(pg.mkBrush(opts['brush']))
        p.drawRect(QRectF(2, 2, 14, 14))
