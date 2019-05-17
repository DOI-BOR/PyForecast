"""
Script Name:    PyQtGraphs
Description:    This file provides plotting funcitonality for the NextFlow Application 
                primarily by modifying the PyQtGraph library to provide interaction and
                performance enhancements. 
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
from PyQt5 import QtWidgets
import numpy as np
import pandas as pd
from datetime import datetime
from pyqtgraph.graphicsItems.LegendItem import LegendItem, ItemSample, PlotDataItem
from bisect import bisect_left

def updateSize_(self):
    if self.size is not None:
        return
        
    height = 0
    width = 0
    for sample, label in self.items:
        height += max(sample.boundingRect().height(), label.height()) + 3
        width = max(width, sample.boundingRect().width()+label.width())
    self.setGeometry(0, 0, width+60, height)

def addItem_(self, item, name):
    label = pg.LabelItem(name, justify='left')
    if isinstance(item, ItemSample):
        sample = item
        sample.setFixedWidth(20)
    else:
        sample = ItemSample(item)     
        sample.setFixedWidth(20)   
    row = self.layout.rowCount()
    self.items.append((sample, label))
    self.layout.addItem(sample, row, 0)
    self.layout.addItem(label, row, 1)
    self.updateSize()

def viewRangeChanged_(self):
            self.xDisp = self.yDisp = None
            self.updateItems()

def updateItems_(self):
        
        curveArgs = {}
        for k,v in [('pen','pen'), ('shadowPen','shadowPen'), ('fillLevel','fillLevel'), ('fillBrush', 'brush'), ('antialias', 'antialias'), ('connect', 'connect'), ('stepMode', 'stepMode'), ('clipToView' ,'clipToView'), ('autoDownsample', 'autoDownsample'), ('downsampleMethod', 'downsampleMethod')]:
            curveArgs[v] = self.opts[k]
        
        scatterArgs = {}
        for k,v in [('symbolPen','pen'), ('symbolBrush','brush'), ('symbol','symbol'), ('symbolSize', 'size'), ('data', 'data'), ('pxMode', 'pxMode'), ('antialias', 'antialias')]:
            if k in self.opts:
                scatterArgs[v] = self.opts[k]
        
        x,y = self.getData()
        #scatterArgs['mask'] = self.dataMask
        
        if curveArgs['pen'] is not None or (curveArgs['brush'] is not None and curveArgs['fillLevel'] is not None):
            self.curve.setData(x=x, y=y, **curveArgs)
            self.curve.show()
        else:
            self.curve.hide()
        
        if scatterArgs['symbol'] is not None:
            self.scatter.setData(x=x, y=y, **scatterArgs)
            self.scatter.show()
        else:
            self.scatter.hide()

def getData_(self):
        if self.xData is None:
            return (None, None)
        
        if self.xDisp is None:
            x = self.xData
            y = self.yData
            
            if self.opts['fftMode']:
                x,y = self._fourierTransform(x, y)
                # Ignore the first bin for fft data if we have a logx scale
                if self.opts['logMode'][0]:
                    x=x[1:]
                    y=y[1:]                
            if self.opts['logMode'][0]:
                x = np.log10(x)
            if self.opts['logMode'][1]:
                y = np.log10(y)
            ds = self.opts['downsample']
            if not isinstance(ds, int):
                ds = 1

            if True: #self.opts['autoDownsample']:
                # this option presumes that x-values have uniform spacing
                range_ = self.viewRect()
                if range_ is not None:
                    dx = float(x[-1]-x[0]) / (len(x)-1)
                    x0 = (range_.left()-x[0]) / dx
                    x1 = (range_.right()-x[0]) / dx
                    width = self.getViewBox().width()
                    if width != 0.0:
                        ds = int(max(1, int((x1-x0) / (width*self.opts['autoDownsampleFactor']))))
                    ## downsampling is expensive; delay until after clipping.
            
            if True: #self.opts['clipToView']:

                range_ = self.viewRect()
                if range_ is not None and len(x) > 1:
                    dx = float(x[-1]-x[0]) / (len(x)-1)
                    # clip to visible region extended by downsampling value
                    x0 = np.clip(int((range_.left()-x[0])/dx)-1*ds , 0, len(x)-1)
                    x1 = np.clip(int((range_.right()-x[0])/dx)+2*ds , 0, len(x)-1)
                    x = x[x0:x1]
                    y = y[x0:x1]

            if ds > 1:
                if self.opts['downsampleMethod'] == 'subsample':
                    x = x[::ds]
                    y = y[::ds]
                elif self.opts['downsampleMethod'] == 'mean':
                    n = len(x) // ds
                    x = x[:n*ds:ds]
                    y = y[:n*ds].reshape(n,ds).mean(axis=1)
                elif self.opts['downsampleMethod'] == 'peak':
                    n = len(x) // ds
                    x1 = np.empty((n,2))
                    x1[:] = x[:n*ds:ds,np.newaxis]
                    x = x1.reshape(n*2)
                    y1 = np.empty((n,2))
                    y2 = y[:n*ds].reshape((n, ds))
                    y1[:,0] = y2.max(axis=1)
                    y1[:,1] = y2.min(axis=1)
                    y = y1.reshape(n*2)
                
            if self.opts["stepMode"]:

                # and only if clip to view or auto-downsampling is enabled
                if self.opts['clipToView'] or self.opts['autoDownsample']:
                    if (x is None and y is None) or (len(x) == 0 and len(y) == 0):
                        if self.opts["stepMode"]:
                            x = np.array([0,0])
                            y = np.array([0])
                    # if there is data
                    if x is not None:
                        # if step mode is enabled and len(x) != len(y) + 1
                        if len(x) == len(y):
                            if len(x) > 2:
                                x = np.append(x, (x[-1] - x[-2]) + x[-1])

                    
            self.xDisp = x
            self.yDisp = y
        return x,y 

pg.setConfigOption('background', '#ffffff')
pg.setConfigOption('foreground', 'k')

PlotDataItem.getData = getData_
PlotDataItem.updateItems = updateItems_
PlotDataItem.viewRangeChanged = viewRangeChanged_

LegendItem.addItem = addItem_
LegendItem.updateSize = updateSize_
LegendItem.mouseDragEvent = lambda s, e: None

class TimeAxisItem(pg.AxisItem):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickSpacing(self, minVal, maxVal, size):
        """
        """
        if maxVal - minVal >= 15*365.24*86400:
            return [(10*365.24*86400, 0), (10*365.24*86400, 0)]
        elif maxVal - minVal >= 6*365.24*86400:
            return [(4*365.24*86400, 0), (4*365.24*86400, 0)]
        elif maxVal - minVal >= 365.24*86400:
            return [(365.24*86400, 0), (365.24*86400, 0)]
        elif maxVal - minVal >= 45*86400:
            return [(31*86400, 0), (31*86400, 0)]
        elif maxVal - minVal >= 26*86400:
            return [(20*86400, 0), (20*86400, 0)]
        elif maxVal - minVal < 100:
            return [(10,0), (1, 0)]
        elif maxVal - minVal >= 15*86400:
            return [(12*86400, 0), (12*86400, 0)]
        elif maxVal - minVal >= 8*86400:
            return [(4*86400, 0), (4*86400, 0)]
        else:
            return [(86400,0), (86400,0)]

    def tickStrings(self, values, scale, spacing):
        """
        Rename the tick strings from EPOCH integers to datetime strings
        """
        if spacing > 7*365.24*86400:
            return [datetime.utcfromtimestamp(value).strftime('%Y-%m') for value in values]
        return [datetime.utcfromtimestamp(value).strftime('%Y-%m-%d') for value in values]

class TimeSeriesSliderPlot(pg.GraphicsLayoutWidget):
    """
    Example taken from pyqtgraph/examples/crosshair.py
    """
    def __init__(self):
        super(TimeSeriesSliderPlot, self).__init__()
        
        self.p1 = self.addPlot(row=0, col=0, rowspan=8, axisItems={"bottom":TimeAxisItem(orientation="bottom")})
        self.p2 = self.addPlot(row=8, col=0, axisItems={"bottom":TimeAxisItem(orientation="bottom")})
        
        [self.ci.layout.setRowMinimumHeight(i, 50) for i in range(9)]
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.p1.addLegend()
        self.p2.addItem(self.region, ignoreBounds=True)
        self.p1.setMenuEnabled(False)
        self.p2.setMenuEnabled(False)

        self.region.sigRegionChanged.connect(self.update)
        self.p1.sigRangeChanged.connect(self.updateRegion)

        self.p1.scene().sigMouseMoved.connect(self.mouseMoved)

    def mouseMoved(self, event):
        try:
            pos = QtCore.QPoint(event.x(), event.y())
            if self.p1.sceneBoundingRect().contains(pos):
                mousePoint = self.p1.vb.mapSceneToView(pos)
                x_ = mousePoint.x()
                y_ = mousePoint.y()
                idx = int(x_ - x_%86400)
                ts = datetime.utcfromtimestamp(idx).strftime('%Y-%m-%d')
                for i, item in enumerate(self.p1CurveItems):
                    date = takeClosest(item.xDisp, idx)
                    idx2 = np.where(item.xData==date)
                    yval = round(item.yData[idx2][0],2)
                    unit = self.unitList[i]
                    self.p1.legend.items[i][1].setText(self.names[i]+' <strong>'+str(yval)+' '+unit+'</strong>')
                    self.circleItems[i].setData([date], [yval])
                if hasattr(self, "crossHairText"):
                    self.crossHairText.setHtml('<strong>'+ts+'</strong>')
                    self.crossHairText.setPos(x_, y_)
        except Exception as e:
            return

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)
        [self.p1.items[i].viewRangeChanged() for i in range(len(self.p1.items))]
    
    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setZValue(10)
        self.region.setRegion(rgn)
        [self.p1.items[i].viewRangeChanged() for i in range(len(self.p1.items))]
    
    def add_data_to_plots(self, dataFrame, types = None, fill_below=True, changed_col = None, datasets=None):
        """
        """

        # Check to make sure the dataframe actually contains data!
        if np.all(pd.isnull(dataFrame.values)):
            print("Whatcha trying to do!")
            return
            
        
        cc = colorCycler()
        dataset_ids = list(set(dataFrame.index.get_level_values(1)))
        self.dates = dataFrame.index.levels[0].astype('int64')/1000000000
        self.names = [datasets.loc[id_]['DatasetName'] for id_ in dataset_ids]
        self.unitList = [datasets.loc[id_]['DatasetUnits'] for id_ in dataset_ids]
        units = list(set(self.unitList))
        units = ', '.join(units)

        yMin = dataFrame.min()
        yMax = dataFrame.max()
        yRange = yMax - yMin

        xMin = min(self.dates)
        xMax = max(self.dates)
        xRange = xMax - xMin

        if not changed_col == None:
            for col in changed_col:
                current_bounds = self.p1.vb.viewRange()
                y = np.array(dataFrame.loc[(slice(None), col)].values, dtype='float')
                x = np.array(dataFrame.loc[(slice(None), col)].index, dtype='int64')/1000000000

                x_ = x
                y_ = y
                dataItemsP1 = self.p1.listDataItems()
                dataItemsP1Names = [item.opts['name'] for item in dataItemsP1]
                dataItemsP2 = self.p2.listDataItems()
                dataItemsP2Names = [item.opts['name'] for item in dataItemsP2]
                p1Item = dataItemsP1[dataItemsP1Names.index(datasets.loc[col]['DatasetName'])]
                p2Item = dataItemsP2[dataItemsP2Names.index(datasets.loc[col]['DatasetName'])]
                p1Item.setData(x_, y_, antialias=True)
                p2Item.setData(x_, y_, antialias=True)
                self.p1.vb.setRange(xRange = current_bounds[0], yRange = current_bounds[1])
                self.p2.setLimits(  xMin = xMin, 
                                xMax = xMax, 
                                yMin = yMin, 
                                yMax = yMax,
                                minXRange = xRange,
                                minYRange = yRange)
                self.p1.setLimits(  xMin = xMin, 
                                xMax = xMax, 
                                yMin = min([yMin,0]), 
                                yMax = yMax + yRange/5,
                                maxYRange = 7*yRange/5)
            return

        [self.p1.removeItem(i) for i in self.p1.listDataItems()]
        [self.p2.removeItem(i) for i in self.p2.listDataItems()]
        self.p1.legend.scene().removeItem(self.p1.legend)
        if hasattr(self, "crossHairText"):
            self.p1.removeItem(self.crossHairText)
        self.p1.addLegend()
        self.p2.setLimits(  xMin = xMin, 
                            xMax = xMax, 
                            yMin = yMin, 
                            yMax = yMax,
                            minXRange = xRange,
                            minYRange = yRange)
        self.p1.setLimits(  xMin = xMin, 
                            xMax = xMax, 
                            yMin = min([yMin,0]), 
                            yMax = yMax + yRange/5,
                            maxYRange = 7*yRange/5)
        self.p1.setRange(yRange = [ min([yMin,0]), yMax])

        self.circleItems = []
        self.p1CurveItems = []
        self.p2CurveItems = []

        if types == None:
            types = [datasets.loc[i]['DatasetAdditionalOptions']['PlotType'] if (isinstance(datasets.loc[i]['DatasetAdditionalOptions'], dict) and 'PlotType' in list(datasets.loc[i]['DatasetAdditionalOptions'])) else 'line' for i in dataset_ids]

        if len(types) != len(dataset_ids):
            return

        for i, col in enumerate(dataset_ids):
            y = np.array(dataFrame.loc[(slice(None), col)].values, dtype='float')
            x = np.array(dataFrame.loc[(slice(None), col)].index, dtype='int64')/1000000000
            x_ = x
            y_ = y
            idxNum = np.where(datasets.index == col)[0][0]
            pen = pg.mkPen(color=cc.getColorOpaque(idxNum), width=2)
            
            if types[i] == 'bar':
                print("Printing a bar graph")
                x_ = np.append(x_, x_[-1])
                self.p1CurveItems.append(PlotDataItem(x=x_, y=y_, connect='finite', pen=pen, stepMode = True, fillLevel=0,  fillbrush=cc.getColor(idxNum), name=self.names[i], antialias=False, downsampleMethod='subsample', autoDownsample=True, autoDownsampleFactor = 0.5, clipToView=True))
                self.p2CurveItems.append(PlotDataItem(x=x_, y=y_, connect='finite', pen=pen, stepMode = True,  brush=cc.getColor(idxNum), name=self.names[i], antialias=False, downsampleMethod='subsample', autoDownsample=True, autoDownsampleFactor = 0.5, clipToView=True))

            elif types[i] == 'line' and fill_below==True:
                self.p1CurveItems.append(PlotDataItem(x=x_, y=y_, connect='finite', pen=pen, brush=cc.getColor(idxNum), name=self.names[i], antialias=False, downsampleMethod='peak', autoDownsample=True, autoDownsampleFactor = 0.5, clipToView=True))
                self.p2CurveItems.append(PlotDataItem(x=x_, y=y_, connect='finite', pen=pen, brush=cc.getColor(idxNum), name=self.names[i], antialias=False, downsampleMethod='peak', autoDownsample=True, autoDownsampleFactor = 0.5, clipToView=True))
                
            elif types[i] == 'scatter':
                self.p1CurveItems.append(PlotDataItem(x=x_, y=y_, connect='finite', pen=pen, symbol='o', name=self.names[i], antialias=False, downsampleMethod='subsample', autoDownsample=True, autoDownsampleFactor = 0.5, clipToView=True))
                self.p2CurveItems.append(PlotDataItem(x=x_, y=y_, connect='finite', pen=pen, symbol='o', name=self.names[i], antialias=False, downsampleMethod='subsample', autoDownsample=True, autoDownsampleFactor = 0.5, clipToView=True))

            self.circleItems.append(pg.ScatterPlotItem([x_[0]], [y_[0]], pen='k', brush=cc.getColorOpaque(idxNum), size=10, alpha=1))

        [self.p1.addItem(item) for item in self.p1CurveItems]
        [self.p2.addItem(item) for item in self.p2CurveItems]
        [self.p1.addItem(item) for item in self.circleItems]
        self.p1.showGrid(True, True, 0.85)
        self.region.setRegion([xMin, xMax])
        self.region.setBounds([xMin, xMax])
        self.region.setZValue(10)
        self.crossHairText = pg.TextItem(anchor=(0,1), color = (45,45,45))
        self.p1.addItem(self.crossHairText)
        self.p1.setLabel('left', units, **{'color':'#000000', 'font-size':'14pt', 'font-family':'Arial, Helvetica, sans-serif'})
        self.p2.setLabel('left', ' ')
        return


class colorCycler():
    """
    Simple color cycler for the plots
    """
    def __init__(self):
        self.colors = [
            (55,126,184,150),
            (228,26,28,150),
            (77,175,74,150),
            (152,78,163,150),
            (255,127,0,150),
            (255,255,51,150),
            (166,86,40,150),
            (247,129,191,150)]

    def getColor(self, i):
        return self.colors[i%len(self.colors)]
    def getColorOpaque(self, i):
        col= self.colors[i%len(self.colors)]
        return (col[0], col[1], col[2], 250)

def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
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
    
    app = QtWidgets.QApplication(sys.argv)
    mw = TimeSeriesSliderPlot()
    df = pd.DataFrame(np.random.random((31,3)), columns=['A','B','C'], index=pd.date_range('2018-10-01','2018-10-31'))
    df['C'] = 3*df['C']
    df['B'] = -2*df['B']-1
    df['A'] = -1*df['A']
    mw.add_data_to_plots(df, types = ['scatter','line','bar'])
    mw.show()
    sys.exit(app.exec_())