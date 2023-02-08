from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtGui
from Utilities import RichTextDelegate
import os

app = QApplication.instance()

class DatasetsTab(QWidget):

  def __init__(self):

    QWidget.__init__(self)
    
    # Create the Map
    self.dataset_map = DatasetMap()

    # Create the dataset list
    self.dataset_list = SelectedDatasetList()

    # Layout the Tab
    layout = QHBoxLayout()
    splitter = QSplitter()
    splitter.addWidget(self.dataset_map)
    vlayout = QVBoxLayout()
    vlayout.addWidget(QLabel('Datasets', objectName='HeaderLabel'))
    vlayout.addWidget(self.dataset_list)
    widg = QWidget()
    widg.setLayout(vlayout)
    splitter.addWidget(widg)
    layout.addWidget(splitter)
    self.setLayout(layout)


class SelectedDatasetList(QListView):

  def __init__(self):
    
    QListView.__init__(self)
    self.setMinimumWidth(300)
    self.setItemDelegate(RichTextDelegate.HTMLDelegate())
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.customContextMenuRequested.connect(self.customMenu)
    self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    self.add_action = QAction('Add new dataset')
    self.add_action.setStatusTip('Adds a new blank dataset to the list')
    self.remove_action = QAction('Remove dataset(s)')
    self.remove_action.setStatusTip('Removes the selected dataset from the list')
    self.view_action = QAction('Open dataset')
    self.view_action.setStatusTip('Opens the dataset in a new window for viewing and editing')

    self.climate_actions = []
    self.action1 = QAction('1: Multivariate Enso')
    self.action1.setData(1)
    self.climate_actions.append(self.action1)
    self.action2 = QAction('2: Pactific North American')
    self.action2.setData(2)
    self.climate_actions.append(self.action2)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Delete:
      self.remove_action.trigger()
    return super().keyPressEvent(event)

  def customMenu(self, pos):
    globalpos = self.mapToGlobal(pos)
    menu = QMenu()
    
    menu.addAction(self.view_action)
    menu.addAction(self.remove_action)
    menu.addAction(self.add_action)

    idx_menu = menu.addMenu('Add Climate Indices')
    for action in self.climate_actions:
      idx_menu.addAction(action)


    index = self.indexAt(pos)
    selected = self.selectedIndexes()

    if not index.isValid():
      self.view_action.setEnabled(False)
      self.add_action.setEnabled(True)
      list(map(lambda x: x.setEnabled(True), self.climate_actions))
      self.remove_action.setEnabled(False)
    elif len(selected)>1:
      self.view_action.setEnabled(False)
      self.remove_action.setEnabled(True)
      self.add_action.setEnabled(False)
      list(map(lambda x: x.setEnabled(True), self.climate_actions))
    else:
      self.view_action.setEnabled(True)
      self.remove_action.setEnabled(True)
      self.add_action.setEnabled(False)
      list(map(lambda x: x.setEnabled(True), self.climate_actions))

    menu.exec_(globalpos)
    

class DatasetMap(QWebEngineView):

  def __init__(self):

    QWebEngineView.__init__(self)
    self.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
    self.page = WebMapPage()
    url = QUrl.fromLocalFile(os.path.abspath(app.base_dir + '/Resources/WebMap/WebMap.html'))
    self.setPage(self.page)
    self.load(url)
    self.setContextMenuPolicy(Qt.NoContextMenu)
    self.setMinimumSize(300,300)

class WebMapPage(QWebEnginePage):
  java_msg_signal = pyqtSignal(str)

  def __init__(self):
    QWebEnginePage.__init__(self)
  def acceptNavigationRequest(self, url, _type, isMainFrame):
    if _type == QWebEnginePage.NavigationTypeLinkClicked:
      QtGui.QDesktopServices.openUrl(url)
      return False
    else:
      return True
  def javaScriptConsoleMessage(self, lvl, msg, line, source):
    self.java_msg_signal.emit(msg)