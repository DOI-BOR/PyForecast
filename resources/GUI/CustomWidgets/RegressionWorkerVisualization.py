"""
Script Name:    RegressionWorkerVisualization.py

Description:    Adds a visualization for whats going on while the
                regression worker is building models

"""

from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg
import math
import bitarray as ba
import pandas as pd
import os

ICONS = {
        "streamflow": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/directions_boat-24px.svg"),
        "inflow": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/waves-24px.svg"),
        "snow": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/ac_unit-24px.svg"),
        "temperature": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/temperature_fahrenheit-24px.svg"),
        "precipitation": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/weather_pouring-24px.svg"),
        "index": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/radio_tower-24px.svg"),
        "soil": os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/sprout-24px.svg"),
        'snotel': os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/terrain-24px.svg"),
        'other': os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/language-24px.svg"),
        'clock':os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/clock-24px.svg"),
        'function': os.path.abspath(r"C:\Users\KFoley\PycharmProjects\PyForecast\resources/GraphicalResources/icons/function-24px.svg"),
}

# STATIC LISTS
IDX = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114,
    115, 116, 117, 118, 119, 120
]

Q = [
    0, 0, 1, 1, 0, -1, -1, -1, 0, 1, 2, 2, 2, 1, 0, -1, -2, -2, -2, -2, -1, 0, 1, 2, 3, 3, 3, 3, 2, 1, 0, -1, -2, -3, -3,
    -3, -3, -3, -2, -1, 0, 1, 2, 3, 4, 4, 4, 4, 4, 3, 2, 1, 0, -1, -2, -3, -4, -4, -4, -4, -4, -4, -3, -2, -1, 0, 1, 2,
    3, 4, 5, 5, 5, 5, 5, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -5, -5, -5, -5, -5, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4,
    5, 6, 6, 6, 6, 6, 6, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6
]

R = [
    0, 1, 1, 0, -1, -1, 0, 1, 2, 2, 2, 1, 0, -1, -2, -2, -2, -1, 0, 1, 2, 3, 3, 3, 3, 2, 1, 0, -1, -2, -3, -3, -3, -3,
    -2, -1, 0, 1, 2, 3, 4, 4, 4, 4, 4, 3, 2, 1, 0, -1, -2, -3, -4, -4, -4, -4, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 5, 5,
    5, 5, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -5, -5, -5, -5, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6,
    6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -6, -6, -6, -6, -6, -6
]
class hexItemSignal(QtCore.QObject):
    hoverSignal = QtCore.pyqtSignal(int)

class hexagon_item(QtWidgets.QGraphicsPolygonItem):
    # This class contains a graphicsitem in the shape of a padded hexagon.

    def __init__(self, parent, points, z=-1, pen=QtGui.QPen(QtGui.QBrush(QtGui.QColor("#EEEEEE")), 3), brush = QtGui.QBrush(QtGui.QColor("#EEEEEE"))):

        QtWidgets.QGraphicsPolygonItem.__init__(self, QtGui.QPolygonF(points))
        self.idx = 0
        self.parent = parent
        self.object = QtCore.QObject()
        self.signals = hexItemSignal()
        self.pen = pen
        self.brush = brush
        if z > 0:
            self.setAcceptHoverEvents(True)
        self.eff = QtWidgets.QGraphicsColorizeEffect()
        self.eff.setColor(QtGui.QColor("FF0000"))
        self.setZValue(z)
        self.setBrush(brush)
        self.setPen(pen)
        self.highlightPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor("#FF0033")), 5)
        self.highlightBrush = QtGui.QBrush(QtGui.QColor(255,0,111,40))
        center = self.getCenter()
        self.setTransformOriginPoint(center)
        self.setScale(0.88)

        return


    def getCenter(self):
        # Returns the center of the hexagon in item-coordinates
        return self.boundingRect().center()


    def hoverEnterEvent(self, event):

        self.setPen(self.highlightPen)
        self.setBrush(self.highlightBrush)
        self.update()
        self.signals.hoverSignal.emit(self.idx)
        return


    def hoverLeaveEvent(self, event):

        self.setPen(self.pen)
        self.setBrush(self.brush)
        self.update()

        return


class RegressionWorkerVisualization(QtWidgets.QGraphicsView):
    hexHoverEvent = QtCore.pyqtSignal(int) # Emits the index of the hexagon being hovered over

    def __init__(self, parent):

        QtWidgets.QGraphicsView.__init__(self)

        # INITIALIZATION
        self.parent = parent
        self.array = None
        self.paused = True
        self.started = False
        self.mode = 0           # 0 == Real-time, 1 == Accumulation
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(0, 0, 640, 480)
        self.setScene(self.scene)
        self.setMouseTracking(True)
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.parent.setMouseTracking(True)
        self.resizeEvent = self.g_resizeEvent

        self.setMinimumSize(100,100)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.items = []
        self.bEffect = QtGui.QBrush(QtGui.QColor("#a78fc9"))
        self.drawPredictorGrid()

        return


    def g_resizeEvent(self, ev):

        QtWidgets.QGraphicsView.resizeEvent(self, ev)
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

        return

    def hex_to_pixel(self, q, r):

        x = (1.5 * q + 0 * r) * self.width_
        y = (math.sqrt(3) * 0.5 * q + math.sqrt(3) * r) * self.height_

        return (x + self.screen_center_[0], y + self.screen_center_[1])

    def drawBackgroundHexagons(self):

        for hex_center in ((q,r) for q in range(-50,50) for r in range(-50,50)):
            points = []
            center_pix = self.hex_to_pixel(*hex_center)

            for angle in range(0,360,60):
                rad = math.radians(angle)
                point_x = center_pix[0] + self.width_ * math.cos(rad)
                point_y = center_pix[1] + self.height_ * math.sin(rad)
                points.append(QtCore.QPointF(point_x, point_y))
            self.scene.addItem(hexagon_item(self, points, -1))
        return

    def getHexagon(self, idx):

        points = []
        q = Q[idx]
        r = R[idx]*-1
        center_pix = self.hex_to_pixel(q, r)
        for angle in range(0,360,60):
            rad = math.radians(angle)
            point_x = center_pix[0] + self.width_ * math.cos(rad)
            point_y = center_pix[1] + self.height_ * math.sin(rad)
            points.append(QtCore.QPointF(point_x, point_y))
        hex_item = hexagon_item(self, points, 1, self.pen, self.brush)
        hex_item.idx = idx
        hex_item.center_point = center_pix
        hex_item.dataset = self.parent.datasetTable.loc[self.parent.modelRunsTable.iloc[-1].PredictorPool[idx]]
        hex_item.signals.hoverSignal.connect(self.hexHoverEvent.emit)
        return hex_item

    def drawPredictorGrid(self):

        # GET SCREEN DIMENSIONS
        self.screen_size_ = self.size()
        self.screen_width_ = self.screen_size_.width()
        self.screen_height_ = self.screen_size_.height()
        self.screen_center_ = (int(self.screen_width_/2), int(self.screen_height_/2))


        # FIGURE OUT HOW MANY ROWS/COLS OF HEXAGONS
        self.numPredictors = len(self.parent.modelRunsTable.iloc[-1]['PredictorPool'])

        # GET HEXAGON DIMENSIONS
        self.size_ = 95 * 1/(math.sqrt(self.numPredictors))
        self.width_ = 2*self.size_*0.88
        self.height_ = math.sqrt(3)*self.size_

        # SET UP PENS AND BRUSH
        self.pen = QtGui.QPen(QtGui.QColor("#02527d"))
        self.pen.setWidth(5)
        self.pen.setCapStyle(QtCore.Qt.RoundCap)
        self.brush = QtGui.QBrush(QtGui.QColor(118, 174, 204,60))
        self.pen2 = QtGui.QPen(QtGui.QColor("#2C2E2E"))
        self.pen2.setWidth(3)
        self.pen2.setCapStyle(QtCore.Qt.RoundCap)
        #point = QtWidgets.QGraphicsEllipseItem(-2, -2, 4, 4)
        #point.setBrush(QtGui.QBrush(QtGui.QColor(255,0,0)))
        #point.setPos(*self.screen_center_)
        #self.scene.addItem(point)

        self.drawBackgroundHexagons()
        self.items = []
        for i in range(self.numPredictors):

            hex_item = self.getHexagon(i)
            iconPath = os.path.abspath('resources/GraphicalResources/icons/cactus-24px.svg')
            # Figure out what Icon to use
            if "SNOTEL" in hex_item.dataset.DatasetType.upper() and 'snow' in hex_item.dataset.DatasetParameter.lower():
                iconPath = ICONS['snotel']
            elif 'OTHER' in hex_item.dataset.DatasetType.upper():
                iconPath = ICONS['other']
            else:
                for key, value in ICONS.items():
                    if key in hex_item.dataset.DatasetParameter.lower():
                        iconPath = value

            svg_item = QtSvg.QGraphicsSvgItem(iconPath)
            svg_item.setPos(hex_item.center_point[0]-self.width_/2, hex_item.center_point[1]-self.height_/2)
            svg_item.setFlags(QtWidgets.QGraphicsItem.ItemClipsToShape)
            svg_item.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
            svg_item.setZValue(2)
            svg_item.setScale((self.width_/2)/12)
            self.scene.addItem(svg_item)
            self.items.append(hex_item)
            self.scene.addItem(hex_item)

        return


    def updateVisualization(self, bit_array):
        if self.started and not self.paused:
            self.array = bit_array
            for i, b in enumerate(self.array):
                if b:
                    self.items[i].setBrush(self.bEffect)
                else:
                    self.items[i].setBrush(self.brush)
            self.update()
        return

    def startVisualization(self):
        self.started = True
        self.paused = False

        return

    def endVisualization(self):
        self.started = False
        self.paused = True

        return

    def pauseVisualization(self):
        self.pause = True
        return

    def resumeVisualization(self):
        self.pause = False
        return

    
if __name__=='__main__':
    import sys
    import numpy as np
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QWidget()
    mw.datasetTable = pd.DataFrame(
        index=pd.Index([], dtype=int, name='DatasetInternalID'),
        columns=[
            'DatasetType',  # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID',  # e.g. "GIBR" or "06025500"
            'DatasetName',  # e.g. Gibson Reservoir
            'DatasetAgency',  # e.g. USGS
            'DatasetParameter',  # e.g. Temperature
            'DatasetParameterCode',  # e.g. avgt
            'DatasetUnits',  # e.g. CFS
            'DatasetDefaultResampling',  # e.g. average
            'DatasetDataloader',  # e.g. RCC_ACIS
            'DatasetHUC8',  # e.g. 10030104
            'DatasetLatitude',  # e.g. 44.352
            'DatasetLongitude',  # e.g. -112.324
            'DatasetElevation',  # e.g. 3133 (in ft)
            'DatasetPORStart',  # e.g. 1/24/1993
            'DatasetPOREnd',  # e.g. 1/22/2019
            'DatasetAdditionalOptions'
        ]
    )

    mw.datasetTable.loc[100000] = ['RESERVOIR', 'GIBR', 'Gibson Reservoir', 'USBR', 'Inflow', 'CFS', 'in', 'Average',
                                   'USBR_LOADER', '10030101', '44.254', '-109.123', '3212', '', '', '']
    mw.datasetTable.loc[100001] = ['STREAMGAGE', 'WSSW', 'Welcome Creek', 'USGS', 'Streamflow', 'CFS', 'in', 'Average',
                                   'USGS_LOADER', '10030102', '44.255', '-109.273', '3212', '', '', '']
    mw.datasetTable.loc[100805] = ['SNOTEL', '633', 'Miscell Peak', 'NRCS', 'Snow Water Equivalent', 'Inches', 'wteq', 'Sample',
                                   'NRCS_LOADER', '10030101', '44.245', '-109.1123', '3212', '', '', '']
    mw.datasetTable.loc[100806] = ['SCAN', '633', 'Miscell Peak', 'NRCS', 'Temperature', 'degF', 'wteq', 'Sample',
                                   'NRCS_LOADER', '10030101', '44.245', '-109.1123', '3212', '', '', '']
    mw.datasetTable.loc[100807] = ['SCAN', '633', 'Miscell Peak', 'NRCS', 'Precipitation', 'Inches', 'wteq', 'Sample',
                                   'NRCS_LOADER', '10030101', '44.245', '-109.1123', '3212', '', '', '']

    mw.modelRunsTable = pd.DataFrame(
        index=pd.Index([], dtype=int, name='ModelRunID'),
        columns=[
            "ModelTrainingPeriod",  # E.g. 1978-10-01/2019-09-30 (model trained on  WY1979-WY2019 data)
            "ForecastIssueDate",  # E.g. January 13th
            "Predictand",  # E.g. 100302 (datasetInternalID)
            "PredictandPeriod",
            # E.g. R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
            "PredictandMethod",  # E.g. Accumulation, Average, Max, etc
            "PredictorPool",  # E.g. [100204, 100101, ...]
            "PredictorForceFlag",  # E.g. [False, False, True, ...]
            "PredictorPeriods",  # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, ...]
            "PredictorMethods",  # E.g. ['Accumulation', 'First', 'Last', ...]
            "RegressionTypes",  # E.g. ['Regr_MultipleLinearRegression', 'Regr_ZScoreRegression']
            "CrossValidationType",  # E.g. K-Fold (10 folds)
            "FeatureSelectionTypes",  # E.g. ['FeatSel_SequentialFloatingSelection', 'FeatSel_GeneticAlgorithm']
            "ScoringParameters",  # E.g. ['ADJ_R2', 'MSE']
            "Preprocessors"  # E.g. ['PreProc_Logarithmic', 'PreProc_YAware']
        ]
    )

    mw.modelRunsTable.loc[0] = [
        "",
        "",
        "",
        "",
        "",
        [100000, 100001, 100805, 100806, 100807],
        [True, False, False],
        ["R/1978-03-01/P1M/F1Y", "R/1978-03-11/P3D/F1Y", "R/1978-03-01/P2M/F1Y", "R/1978-03-01/P1M/F1Y", "R/1978-03-11/P3D/F1Y",],
        ['first', 'average', 'accumulation','average', 'accumulation'],
        "",
        "",
        "",
        "",
        ""
    ]
    w = RegressionWorkerVisualization(mw)
    w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    mw.layout = QtWidgets.QVBoxLayout(mw)
    mw.layout.addWidget(w)
    textBox = QtWidgets.QTextEdit(mw)
    textBox.setText("HELLO")
    w.hexHoverEvent.connect(lambda i: textBox.setText("{0} is being hovered over!".format(mw.datasetTable.loc[mw.modelRunsTable.iloc[-1].PredictorPool[i]].name)))
    mw.layout.addWidget(textBox)
    button1 = QtWidgets.QPushButton("start")
    mw.layout.addWidget(button1)
    button2 = QtWidgets.QPushButton("end")
    mw.layout.addWidget(button2)
    mw.setLayout(mw.layout)

    timer = QtCore.QTimer()
    timer.setInterval(50)
    w.startVisualization()
    timer.timeout.connect(lambda: w.updateVisualization(ba.bitarray([True if x>0.5 else False for x in np.random.random(w.numPredictors)])))
    button1.pressed.connect(timer.start)
    button2.pressed.connect(timer.stop)
    mw.show()
    sys.exit(app.exec_())