import numpy as np
import pyqtgraph as pg
from PySide6 import QtGui
from PySide6.QtGui import QAction, QPainter
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QSplitter,
                               QHBoxLayout, QVBoxLayout, QListView, QAbstractItemView,
                               QMenu)

from Plots import DataTab as DTP
from Utilities import RichTextDelegate, ColorCycler, TimeSeriesPlot, TimeSeriesSlider

# Initial PyQt Setup
pg.setConfigOption('background', pg.mkColor('#f7f7f7'))
pg.setConfigOption('foreground', pg.mkColor('#292929'))

app = QApplication.instance()


class DataTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data_all_button = QPushButton('Download all data')
        self.data_all_button.setStatusTip(
            f'Downloads all the data for all datasets in the forecast file '
            f'(from {app.settings["default_data_download_start"]:%Y-%m-%d} until now)')
        self.data_update_button = QPushButton('Download recent data')
        self.data_update_button.setStatusTip(
            f'Downloads only recent data for all datasets in the forecast file')
        self.edit_data_excel_button = QPushButton('Edit data in excel')
        self.edit_data_excel_button.setStatusTip(
            'Open the selected datasets for editing in Excel')

        # Create the dataset list
        self.dataset_list = SelectedDatasetList()

        # Create the data viewer
        self.data_viewer = DTP.Plot()

        # Layout the Tab
        layout = QHBoxLayout()

        layout2 = QVBoxLayout()
        layout2.addWidget(self.data_all_button)
        layout2.addWidget(self.data_update_button)
        layout2.addWidget(self.dataset_list)
        layout2.addWidget(self.edit_data_excel_button)
        self.w = QWidget()
        self.w.setLayout(layout2)
        self.splitter = QSplitter()
        self.splitter.addWidget(self.w)
        self.splitter.addWidget(self.data_viewer)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.splitter.splitterMoved.connect(lambda: self.updateListSize())

    def updateListSize(self):
        app.datasets.dataChanged.emit(app.datasets.index(0),
                                      app.datasets.index(app.datasets.rowCount()))
        app.gui.DataTab.w.update()
        app.gui.DataTab.dataset_list.update()


class DataViewer(pg.GraphicsLayoutWidget):

    def __init__(self, parent=None, **kwargs):

        super().__init__(parent, **kwargs)
        self.color_cycler = ColorCycler.ColorCycler()
        self.setMinimumWidth(500)

        # SET MINIMUM ROW SIZE FOR ROWS
        [self.ci.layout.setRowMinimumHeight(i, 30) for i in range(9)]

        # initialize the plots
        self.timeseriesplot = TimeSeriesPlot.TimeSeriesPlot(self.ci)
        self.timesliderplot = TimeSeriesSlider.TimeSliderPlot(self.ci)

        self.addItem(self.timeseriesplot, row=0, col=0, rowspan=7)
        self.addItem(self.timesliderplot, row=7, col=0, rowspan=2)

        self.timesliderplot.region.sigRegionChanged.connect(self.updatePlot)
        self.timeseriesplot.sigRangeChanged.connect(self.updateRegion)

        return

    def updatePlot(self):

        self.timesliderplot.region.setZValue(10)
        newRegion = self.timesliderplot.region.getRegion()
        if not any(np.isinf(newRegion)):
            self.timeseriesplot.getViewBox().setXRange(
                *self.timesliderplot.region.getRegion(),
                padding=0
            )
            for i in range(len(self.timeseriesplot.items)):
                self.timeseriesplot.items[i].viewRangeChanged()

        return

    def updateRegion(self, window, viewRange):
        self.timesliderplot.region.setZValue(10)
        self.timesliderplot.region.setRegion(viewRange[0])
        for i in range(len(self.timeseriesplot.items)):
            self.timeseriesplot.items[i].viewRangeChanged()

        return

    def plot(self, dataframe, **kwargs):
        colors = [self.color_cycler.next() for i in dataframe.columns]
        self.timeseriesplot.plot(dataframe, colors, **kwargs)
        self.timesliderplot.plot(dataframe, colors)

    def clear_all(self):
        colors = [self.color_cycler.next()]
        self.timeseriesplot.plot([[], []], colors)
        self.timesliderplot.plot([[], []], colors)


class SelectedDatasetList(QListView):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setItemDelegate(RichTextDelegate.HTMLDelegate())
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QListView.SizeAdjustPolicy.AdjustToContents)

        self.download_all_one_shot_action = QAction('Download all data for selection')
        self.download_all_one_shot_action.setStatusTip(
            'Downloads all the data for datasets in the selection'
        )

    def paintEvent(self, e):
        QListView.paintEvent(self, e)
        if (self.model()) and (self.model().rowCount(self.rootIndex()) > 0):
            return
        painter = QPainter(self.viewport())
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            'No datasets in this forecast file'
        )
        painter.end()
