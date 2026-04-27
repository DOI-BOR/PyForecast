from PySide6.QtGui import QAction, QPainter, QDesktopServices
from PySide6.QtCore import Qt, Signal, QUrl, QPoint
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWidgets import (QApplication, QMenu, QWidget, QHBoxLayout, QVBoxLayout,
                               QSplitter, QLabel, QListView, QAbstractItemView)

from Utilities import RichTextDelegate

app = QApplication.instance()


class DatasetsTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the Map
        self.dataset_map = DatasetMap(self)

        # Create the dataset list
        self.dataset_list = SelectedDatasetList(self)

        # Layout the Tab
        layout = QHBoxLayout()

        vlayout = QVBoxLayout()
        label = QLabel('Datasets')
        label.setObjectName('HeaderLabel')
        vlayout.addWidget(label)
        vlayout.addWidget(self.dataset_list)
        self.widg = QWidget()
        self.widg.setLayout(vlayout)
        self.splitter = QSplitter()
        self.splitter.addWidget(self.dataset_map)
        self.splitter.addWidget(self.widg)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 10)
        self.splitter.setStretchFactor(1, 1)

        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.splitter.splitterMoved.connect(lambda: self.updateListSize())

    def updateListSize(self):
        app.datasets.dataChanged.emit(app.datasets.index(0),
                                      app.datasets.index(app.datasets.rowCount()))
        app.gui.DatasetsTab.widg.update()
        app.gui.DatasetsTab.dataset_list.update()


class SelectedDatasetList(QListView):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setItemDelegate(RichTextDelegate.HTMLDelegate())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QListView.SizeAdjustPolicy.AdjustToContents)
        self.customContextMenuRequested.connect(self.customMenu)

        self.add_action = QAction('Add new dataset')
        self.add_action.setStatusTip(
            'Adds a new blank dataset to the list'
        )
        self.remove_action = QAction('Remove dataset(s)')
        self.remove_action.setStatusTip(
            'Removes the selected dataset from the list'
        )
        self.view_action = QAction('Open dataset')
        self.view_action.setStatusTip(
            'Opens the dataset in a new window for viewing and editing'
        )

        self.climate_actions = []
        self.action1 = QAction('1: Multivariate Enso')
        self.action1.setData(1)
        self.climate_actions.append(self.action1)
        self.action2 = QAction('2: Pactific North American')
        self.action2.setData(2)
        self.climate_actions.append(self.action2)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_action.trigger()
        return super().keyPressEvent(event)

    def customMenu(self, point: QPoint):
        global_point = self.mapToGlobal(point)
        menu = QMenu()

        menu.addAction(self.view_action)
        menu.addAction(self.remove_action)
        menu.addAction(self.add_action)

        idx_menu = menu.addMenu('Add Climate Indices')
        for action in self.climate_actions:
            idx_menu.addAction(action)

        index = self.indexAt(point)
        selected = self.selectedIndexes()

        if not index.isValid():
            self.view_action.setEnabled(False)
            self.add_action.setEnabled(True)
            list(map(lambda x: x.setEnabled(True), self.climate_actions))
            self.remove_action.setEnabled(False)
        elif len(selected) > 1:
            self.view_action.setEnabled(False)
            self.remove_action.setEnabled(True)
            self.add_action.setEnabled(False)
            list(map(lambda x: x.setEnabled(True), self.climate_actions))
        else:
            self.view_action.setEnabled(True)
            self.remove_action.setEnabled(True)
            self.add_action.setEnabled(False)
            list(map(lambda x: x.setEnabled(True), self.climate_actions))

        menu.exec_(global_point)


class DatasetMap(QWebEngineView):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.page = WebMapPage(self)
        self.setPage(self.page)
        self.loadProgress.connect(
            lambda x:
            print(f'Loading basemap ... {x:}%')
        )
        self.loadFinished.connect(
            lambda ok:
            print(f"Loading basemap ... {'Success' if {ok} else 'Failed'}")
        )
        self.load(
            QUrl.fromLocalFile(
                app.base_dir.joinpath('Resources', 'WebMap', 'WebMap.html')
            )
        )
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setMinimumSize(300, 300)

class WebMapPage(QWebEnginePage):
    java_msg_signal = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
            True
        )

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        else:
            return True

    def javaScriptConsoleMessage(self, lvl, msg, line, source):
        self.java_msg_signal.emit(msg)
