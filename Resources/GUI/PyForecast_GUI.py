"""
Script Name:        PyForecast_GUI.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      Apr 2, 2018

Description:        'PyForecast_GUI' is a PyQt5 GUI for the PyForecast application. 
                    The GUI includes all the visual aspects of the application (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

#//////////////////////////// IMPORT LIBRARIES /////////////////////////////////////////
#//     Here we load the necessary packages and libraries that 'PyForecast_GUI.py' needs
#//     in order to run properly.

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

import os
import platform

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.widgets import TextBox
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.dates as mdates
import matplotlib.font_manager as fm

import numpy as np
import pandas as pd
from datetime import datetime

import ctypes
import subprocess

from Resources.GIS import CLIMATE_DIVISIONS

#///////////////////////// SET COMMON PROPERTIES ////////////////////////////////////////
#//     Here we set the common properties that will be used across classes and objects.
#//     These are essentially global variables.

# Set the taskbar Icon
myappid = u'reclamation.PyForecast.2b'
if platform.system() == 'Windows':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Load the trebuchet font into a matplotlib property
prop = fm.FontProperties(fname = r'Resources/Fonts_Icons_Images/Trebuchet MS.ttf')

# Set up some validators to only allow integers in some forms
onlyInt = QtGui.QIntValidator()


#///////////////////////// DEFINE SPECIAL CLASSES ///////////////////////////////////////
#//     PyForecast has additional functionality on top of the default PyQt5 classes, 
#//     requiring us to extend those classes to include things like context menus,
#//     javascript webmaps, and matplotlib plots.

# Define a custom QComboBox that reroutes mouse wheel events
# https://stackoverflow.com/questions/3241830/qt-how-to-disable-mouse-scrolling-of-qcombobox/11866474#11866474
class CustomQComboBox(QtWidgets.QComboBox):
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super(CustomQComboBox, self).__init__(*args, **kwargs)  
        self.scrollWidget=scrollWidget
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QtWidgets.QComboBox.wheelEvent(self, *args, **kwargs)
        else:
            return self.scrollWidget.wheelEvent(*args, **kwargs)
    

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  CUSTOM PLOTS |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Define class for a Matplotlib plot that displays one axes object
class PlotCanvas_1Plot(FigureCanvas):

    # Initialize the graph
    def __init__(self, parent=None, dpi = 100):
        
        # Add a figure and an axes object
        self.fig = Figure(dpi = dpi)
        self.fig.patch.set_facecolor("#e8e8e8")
        self.axes = self.fig.add_subplot(111)

        # Intialize the FigureCanvas
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        FigureCanvas.updateGeometry(self)

        # Initialize the plot with no data
        self.add_to_plot([0],[0])
        self.draw_plot()
    
    # Define a function to add data to the plot
    def add_to_plot(self, X, Y, label='', color='blue'):
        #label = label[0:20]
        self.axes.plot(X,Y,color=color, label=label)
    
    # Define a function to draw the plot
    def draw_plot(self):
        
        self.axes.legend(loc = 2) # Place the legend in the top-left corner
        self.axes.minorticks_on() # Self explanatory
        self.axes.grid(True, which='major', color = 'k', alpha=0.4) # Set the major grid
        self.axes.grid(True, which='minor', color = 'k', alpha=0.2, linestyle='--') # Set the minor grid
        self.axes.set_xlabel('Date', fontproperties = prop) # Set the X-axis label
        self.axes.set_ylabel('Value', fontproperties = prop) # Set the Y-axis label
        self.fig.tight_layout() # Expand graph to fit window
        self.draw()

    # Define a function to add correlation information to the plot
    def draw_corr_plot(self, X, Y, xname=None, yname=None):

        self.clear_plot()
        self.draw()

        xname = xname[0:20]
        yname = yname[0:20]

        # Convert the X, Y to arrays
        x = np.array(X)
        y = np.array(Y)

        # Create a linear matrix
        A = np.vstack([x, np.ones(len(x))]).T

        # Get the least squares coeff and intercept
        model = np.linalg.lstsq(A, y, rcond=None)
        m = model[0][:-1]
        b = model[0][-1]

        # Create the y-hat line
        y_hat = m*x + b
        print(y_hat)

        # Generate statistics
        y_bar = np.sum(y)/len(y)
        ssReg = np.sum((y_hat-y_bar)**2)
        ssTot = np.sum((y-y_bar)**2)
        r2 = np.round((ssReg/ssTot), 3)

        # Add data to the plot
        self.axes.plot(X, Y, color='#0a85cc', marker = 'o', linestyle = '')
        self.axes.set_xlabel(xname)
        self.axes.set_ylabel(yname)
        self.axes.plot(x, y_hat, 'g-', label="r2: {0}".format(str(r2)))
        self.axes.grid(True, which='major', color = 'k', alpha=0.4) # Set the major grid
        self.axes.grid(True, which='minor', color = 'k', alpha=0.2, linestyle='--') # Set the minor grid
        self.axes.legend(loc = 2) # Place the legend in the top-left corner
        self.fig.tight_layout()
        self.draw()


    # Define a function to clear the plot
    def clear_plot(self, a = None):

        self.axes.cla()

# Define a class for displaying 3 vertical line plots
class PlotCanvas_3Plot(FigureCanvas):

    # Initialize the graph
    def __init__(self, parent=None, dpi = 100):
        
        # Add a figure and an axes object
        self.fig = plt.figure(dpi = dpi)
        self.fig.patch.set_facecolor("#e8e8e8")
        self.axes1 = plt.subplot2grid((2,2),(0,0), rowspan=2)
        self.axes2 = plt.subplot2grid((2,2),(0,1))
        self.axes3 = plt.subplot2grid((2,2),(1,1))
        


        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)
        self.add_to_plot1([],[])
        self.add_to_plot2([0],[0])
        self.add_to_plot3([0],[0],linefmt = 'k-', markerfmt ='ro', basefmt = 'k-')
        self.draw_plot()

    # Define a function to add horizontal lines and vertical lines to the plots
    def add_current_forecast(self, currentForecast, label = '', color = 'red', marker = 'o', linestyle = '-', alpha = 1):
        self.axes1.axvline(x=currentForecast, color = '#505359', linewidth=2)
        self.axes2.axhline(y=currentForecast, color = '#505359', linewidth=2)
        
    def draw_box(self, lowleft, width):
        print(lowleft)
        self.axes1.add_patch(patches.Rectangle(lowleft, width, width, fill=True, facecolor=(1,0,0,0.3), edgecolor="r", linewidth=2,))
    
    # Define functions to add data to the plots
    # This is a scatter / line plot
    def add_to_plot1(self, X, Y, label = '', color = 'red', marker = 'o', linestyle = '-', alpha = 1):
        self.axes1.plot(X, Y, color = color, label = label, marker = marker, linestyle = linestyle, alpha = alpha)
    
    # This is a scatter / line plot
    def add_to_plot2(self, X, Y, color = 'red', label = '', linestyle = '-', marker = 'o', linewidth = 2, alpha = 1 ):
        self.axes2.plot(X, Y, color = color, label = label, linestyle = linestyle, marker = marker, linewidth = linewidth, alpha = alpha )

    # This is a stem plot
    def add_to_plot3(self, X, Y, linefmt = 'k-', markerfmt ='bo', basefmt = 'k-', color = '#00347c'):
        (markers, stemlines, baseline) = self.axes3.stem(X, Y, linefmt = linefmt, basefmt = basefmt)
        plt.setp(markers, color = color, marker = 'o')

    # Define a function to draw the axes objects and plot the figure
    def draw_plot(self):
        self.axes1.minorticks_on()
        self.axes1.grid(True, which='Major', color = 'k', linestyle = '-', alpha = 0.4)
        self.axes1.grid(True, which = 'Minor', color = 'k', linestyle = '--', alpha = 0.2)
        self.axes1.set_axisbelow(True)
        self.axes1.set_xlabel('Forecast', fontproperties = prop)
        self.axes1.set_ylabel('Observed', fontproperties = prop)

        years = mdates.YearLocator()

        self.axes2.legend(loc = 2)
        self.axes2.minorticks_on()
        self.axes2.grid(True, which='Major', color = 'k', alpha = 0.4)
        self.axes2.grid(True, which = 'Minor', color = 'k', alpha = 0.2, linestyle = '--')
        self.axes2.xaxis.set_minor_locator(years)
        self.axes2.set_axisbelow(True)
        self.axes2.set_xlabel('Year', fontproperties = prop)
        self.axes2.set_ylabel('Inflow', fontproperties = prop)
        self.axes2.legend()

        self.axes3.minorticks_on()
        self.axes3.xaxis.set_minor_locator(years)
        self.axes3.grid(True, which='Major', color = 'k', alpha = 0.4)
        self.axes3.grid(True, which = 'Minor', color = 'k', alpha = 0.2, linestyle = '--')
        self.axes3.set_axisbelow(True)
        self.axes3.set_xlabel('Year', fontproperties = prop)
        self.axes3.set_ylabel('Residual', fontproperties = prop)

        plt.tight_layout(rect=[0,0.03,1,0.93])
        self.draw()

    # Define a function to clear the plots
    def clear_plot(self):
        self.axes1.cla()
        self.axes2.cla()
        self.axes3.cla()

# Define a class for a Matplotlib plot that displays three axes objects
class PlotCanvas_2Plot(FigureCanvas):

    # Initialize the graph
    def __init__(self, parent=None, dpi = 100):
        
        # Add a figure and an axes object
        self.fig = plt.figure(dpi = dpi)
        self.fig.patch.set_facecolor("#e8e8e8")
        self.axes1 = plt.subplot2grid((2,2),(0,0), colspan=2)
        self.axes2 = plt.subplot2grid((2,2),(1,0), colspan=2)

        # Intialize the FigureCanvas
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # Initialize the plot with no data
        self.add_to_plot1([0],[0])
        self.add_to_plot2([0],[0])

        self.draw_plot()

    # Define a function to add horizontal lines and vertical lines to the plots
    def add_current_forecast(self, currentForecast):

        self.axes3.axhline(y=currentForecast, color = 'green', linewidth=2)
    
    # Define a function to add data to the scatter / line plot in axes item 1
    def add_to_plot1(self, X, Y, label = '', color = '#00347c', marker = 'o', linestyle = '-', alpha = 1, zorder=1):

        self.axes1.plot(X, Y, color = color, label = label, marker = marker, linestyle = linestyle, alpha = alpha, zorder=1)
    
    # Define a function to add data to the line plot in axes item 2
    def add_to_plot2(self, X, Y, color = '#00347c', label = '', linestyle = '-', marker = 'o', linewidth = 2, alpha = 1, zorder=1 ):

        self.axes2.plot(X, Y, color = color, label = label, linestyle = linestyle, marker = marker, linewidth = linewidth, alpha = alpha, zorder=1 )
    
    # Define a function to draw the plots
    def draw_plot(self):

        # Draw the first axes object
        self.axes1.minorticks_on()
        self.axes1.grid(True, which='Major', color = 'k', linestyle = '-', alpha = 0.4)
        #self.axes1.grid(True, which = 'Minor', color = 'k', linestyle = '--', alpha = 0.2)
        self.axes1.set_axisbelow(True)
        self.axes1.set_xlabel('Forecast', fontproperties = prop)
        self.axes1.set_ylabel('Probability', fontproperties = prop)

        self.axes2.minorticks_on()
        self.axes2.grid(True, which='Major', color = 'k', linestyle = '-', alpha = 0.4)
        #self.axes2.grid(True, which = 'Minor', color = 'k', linestyle = '--', alpha = 0.2)
        self.axes2.set_axisbelow(True)
        self.axes2.set_xlabel('Forecast', fontproperties = prop)
        self.axes2.set_ylabel('Cumulative Probability', fontproperties = prop)
        self.axes2.yaxis.set_ticks([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        self.axes2.set_ylim(0, 1)


        plt.tight_layout(rect=[0,0.03,1,0.93])
        self.draw()

    # Define a function to clear the plots
    def clear_plot(self):

        self.axes1.cla()
        self.axes2.cla()

# Define a class to add a Nevigation bar to the bottom of plots
class NavigationToolbar(NavigationToolbar2QT):

    # We don't need all the buttons, so we specify the tools we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if t[0] in ( 'Home', 'Pan', 'Zoom', 'Save')]

class toggleButton(QtWidgets.QPushButton):

    def __init__(self, text=''):
        QtWidgets.QPushButton.__init__(self)
        self.toggleStatus = 0
        self.pressed.connect(self.updateToggleStatus)
        self.setText(text)
    
    def updateToggleStatus(self):
        
        self.toggleStatus += 1
        if self.toggleStatus == 3:
            self.toggleStatus = 0

        print(self.toggleStatus)

        return

# Define a custom Tree View widget to be used to view equations and forecasts on the summary page
class SummTreeView(QtWidgets.QWidget):

    # Initialize a QTreeView and start with a blank tree
    def __init__(self, parent=None):

        # intitialize the treeview
        QtWidgets.QWidget.__init__(self)
        #QtWidgets.QTreeView.__init__(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.header = QtWidgets.QTextEdit()
        self.header.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Select Forecast</strong></br>
                                    <p style="margin:0; font-size:14px;">Use the list to select a forecast to view from this file.</p>
                                    </div>""")
        self.header.setReadOnly(True)
        self.treeView = CustomTreeView()
        self.treeView.setHeaderHidden(True)
        self.header.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.header.setMaximumHeight(90)
        self.treeView.setFrameStyle(QtWidgets.QFrame.NoFrame)

        # Set a custom context menu for the tree
        self.treeView.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.delAction = QtWidgets.QAction("Delete model from summary", None)
        self.ensembleAction = QtWidgets.QAction("Send model to Ensembles Tab", None)
        self.treeView.addAction(self.delAction)
        self.treeView.addAction(self.ensembleAction)

        # Set the widget layout
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.treeView)
        self.setLayout(self.layout)


"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  CUSTOM TREE   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""


class CustomTreeView(QtWidgets.QTreeView):

    deletedItem = QtCore.pyqtSignal(list)
    forcedItem = QtCore.pyqtSignal(list)
    dataAnalysisItem = QtCore.pyqtSignal(list)
    droppedPredictor = QtCore.pyqtSignal(list)
    # Initialize a QTreeView and start with a blank tree
    def __init__(self, parent=None, dragFrom = False, dropTo = False, menuFunctions=['']):

        # intitialize the treeview
        QtWidgets.QTreeView.__init__(self)

        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)

        if dragFrom:
            self.setDragEnabled(True)
            
        if dropTo:
            print('accepts drops')
            self.setAcceptDrops(True)
            self.viewport().setAcceptDrops(True)

        self.setDropIndicatorShown(True)

        # Set the context menu
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        if 'OPENEXCEL' in menuFunctions:
            self.openExcelAction = QtWidgets.QAction("Open in Excel")
            self.addAction(self.openExcelAction)

        if 'DELETE' in menuFunctions:
            self.delAction = QtWidgets.QAction("Delete")
            self.addAction(self.delAction)
            self.delAction.triggered.connect(self.deleteRow)

        if 'FORCE' in menuFunctions:
            self.forceAction = QtWidgets.QAction("(Un)Force")
            self.addAction(self.forceAction)
            self.forceAction.triggered.connect(self.forceRow)

        if 'DANALYSIS' in menuFunctions:
            self.dataAnalysisAction = QtWidgets.QAction("Data Analysis")
            self.addAction(self.dataAnalysisAction)
            self.dataAnalysisAction.triggered.connect(self.dataAnalysis)
        
        if "SENDDENS" in menuFunctions:
            self.sendAction = QtWidgets.QAction("Send to Density Tab")
            self.addAction(self.sendAction)
        
        if "GENCURRENT" in menuFunctions:
            self.genAction = QtWidgets.QAction("Generate Current Forecast")
            self.addAction(self.genAction)

        # Set to be read-only
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    
    def dropEvent(self, event):

        prdID = -1
        pos = event.pos()

        # Get the item's text
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
           mod = QtGui.QStandardItemModel()
           mod.dropMimeData(event.mimeData(),QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())
           item = mod.item(0,0)
           itemText = item.text()
        else:
            print('wrongMimeType')
            event.ignore()
            return

        # TODO: [JR] Need to detect if dropped item is a station and if so, programmatically add the predictors under it to the receiving equation for GitHub Issue #31

        # Ensure that the item is a valid predictor
        if item.hasChildren():

            numChildren = item.rowCount()
            print('item has {0} children'.format(numChildren))
            for i in range(numChildren):
                child = item.child(i)
                if 'prdID: ' in child.text():
                    prdID = child.text()[7:]
                    break
        
            if prdID == -1:
                print('no prdid')
                event.ignore()
                return
        
        else:
            print('no children')
            event.ignore()
            return

        # Make sure that the event's pos is OK
        dropIndex = self.indexAt(pos)
        dropItem = self.model.itemFromIndex(dropIndex)
        if dropItem.text() == 'PredictorPool':
            equation = dropItem.parent().text()
            self.lastIndex = dropIndex        
            self.droppedPredictor.emit([prdID, equation])
            event.accept()
        else:
            event.ignore()
            return


    def deleteRow(self):
        print('deleteRow')
        currentIndex = self.currentIndex()
        item = self.model.itemFromIndex(currentIndex)
        parent = item.parent().parent()
        text = item.text()
        try:
            text = text.split(':')[0].strip(' ')
            test = int(text)
            if len(text) == 5:
                self.model.removeRow(currentIndex.row(), currentIndex.parent())
                self.deletedItem.emit([text, parent.text()])
        except Exception as e:
            print(e)
            return


    def forceRow(self):
        print('forceRow')
        currentIndex = self.currentIndex()
        item = self.model.itemFromIndex(currentIndex)
        parent = item.parent().parent()
        text = item.text()
        try:
            text = text.split(':')[0].strip(' ')
            test = int(text)
            if len(text) == 5:
                self.forcedItem.emit([text, parent.text()])
        except Exception as e:
            print(e)
            return


    def dataAnalysis(self):
        print('dataAnalysis')
        currentIndex = self.currentIndex()
        item = self.model.itemFromIndex(currentIndex)
        parent = item.parent()#.parent()
        text = item.text()
        try:
            if parent == None:
                self.dataAnalysisItem.emit([text, parent])
        except Exception as e:
            print(e)
            return


    def addToTree(self, dict_, levels_in_max = None, exclude_keys=[]):
        self.model = QtGui.QStandardItemModel()
        self.addDictToModel(self.model, dict_, initial = True, levels_in_max = levels_in_max, levels_in = 1, exclude_keys = exclude_keys)
        self.setModel(self.model) 

    def addDictToModel(self, model, dict_, initial=True, levels_in_max = None, levels_in = 1, exclude_keys = [], forcedPredIds = []):
       
        # Check for recursion
        if initial == True:
            parentItem = model.invisibleRootItem()
        else:
            parentItem = model
        try:
            if not isinstance(dict_, dict):
                if dict_ in exclude_keys:
                    return
                item = QtGui.QStandardItem(str(dict_))
                parentItem.appendRow(item)
                return
            # Iterate through each key in the dictionary
            for key, values in dict_.items():

                if key in exclude_keys:
                    continue

                # If the values are a dict, re-enter the funciton recursively
                if isinstance(values, dict):
                    item = QtGui.QStandardItem(str(key))
                    parentItem.appendRow(item)
                    if levels_in <= levels_in_max:

                        if key == 'PredictorPool':
                            self.addDictToModel(item, values, initial=False, levels_in_max=levels_in_max, levels_in=levels_in + 1, exclude_keys=exclude_keys, forcedPredIds = dict_['ForcedPredictors'])
                        else:
                            self.addDictToModel(item, values, initial=False, levels_in_max=levels_in_max, levels_in=levels_in+1,exclude_keys = exclude_keys)

                elif isinstance(values, list):
                    item = QtGui.QStandardItem(str(key))
                    parentItem.appendRow(item)
                    for value in values:
                        self.addDictToModel(item, value, initial=False, levels_in_max = levels_in_max, levels_in=levels_in+1,exclude_keys = exclude_keys)
                else:
                    if isinstance(key, datetime):
                        key = datetime.strftime(key, '%Y')
                    if key in forcedPredIds:
                        item = QtGui.QStandardItem(str(key) + ': ' + u'\u24BB' + str(values))
                    else:
                        item = QtGui.QStandardItem(str(key) + ': ' + str(values))

                    parentItem.appendRow(item)
        except:
            print('\nERROR:')
            print(dict_)
            print("\n")


"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  CUSTOM TABLE |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""
# The custom table view can be initialized with many options:
# rowLock / colLock (bool) sets the selection behavior so that users must select entire rows or columns, instead of individual cells
# cols / rows (int) sets the initial number of rows and columns
# headers (list of strings) sets the initial header labels
# menuFunctions (list of strings from 'COPY','OPEN','DELETEROW','DELETECOL')
# readOnly (bool) sets the entire table to be readonly



# Define a custom QTableView widget for the regression tab for the data and forecastOptions
class CustomTableView(QtWidgets.QTableWidget):

    deletedRowEmission = QtCore.pyqtSignal(list)
    deletedColumnEmission = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, rowLock = False, colLock = False, cols = 0, rows = 0, headers = [''], menuFunctions = [''], readOnly = True, dragFrom=False):

        # Initialize the tableview with options
        QtWidgets.QTableWidget.__init__(self)
        self.setColumnCount(cols)
        self.setRowCount(rows)
        self.readOnly = readOnly
        if rowLock:
            self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        elif colLock:
            pass
            #self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectColumns)
        else:
            pass
        if dragFrom:
            self.setDragEnabled(True)

        if readOnly:
            self.readOnly = True
        else:
            self.readOnly = False



        #self.setGridStyle(QtCore.Qt.DotLine)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.verticalHeader().setVisible(False)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.setHorizontalHeaderLabels(headers)
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)


        # Create a context menu for the tableview
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        if 'COPY' in menuFunctions:
            self.copyAction = QtWidgets.QAction("Copy selection", None)
            self.addAction(self.copyAction)
            self.copyAction.triggered.connect(self.copyFromTable)
        
        if 'OPEN' in menuFunctions:
            self.openAction = QtWidgets.QAction("Open in spreadsheet", None)
            self.addAction(self.openAction)
            self.openAction.triggered.connect(self.openInSpreadsheet)
        
        if 'DELETEROW' in menuFunctions:
            self.deleteRowAction = QtWidgets.QAction("Delete table row", None)
            self.addAction(self.deleteRowAction)
            self.deleteRowAction.triggered.connect(lambda: self.deleteFromTable('row'))

        if 'DELETECOL' in menuFunctions:
            self.deleteColAction = QtWidgets.QAction("Delete table column", None)
            self.addAction(self.deleteColAction)
            self.deleteColAction.triggered.connect(lambda: self.deleteFromTable('col'))
        
        if 'SAVEFCST' in menuFunctions:
            self.saveFcstAction = QtWidgets.QAction("Save Forecast", None)
            self.addAction(self.saveFcstAction)
        
        if "REGSTAT" in menuFunctions:
            self.regStatAction = QtWidgets.QAction("View Principal Components", None)
            self.addAction(self.regStatAction)


    # Defing a function to delete items from the table
    def deleteFromTable(self, option, rowID = None, colID = None):

        if option == 'row':
            items = self.selectedItems()
            self.deletedRowEmission.emit(items)
            self.removeRow(self.currentRow())

        elif option == 'col':
            currentCol = self.currentColumn()
            colName = self.horizontalHeaderItem(currentCol).text()
            self.deletedColumnEmission.emit(colName)
            self.removeColumn(self.currentColumn())
        
        elif option == 'customrow':
            self.removeRow(rowID)
        
        else:
            pass


    # Define a function to copy items from the table
    def copyFromTable(self):

        # Set up and clear the clipboard
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode = cb.Clipboard)
        prev_row = -1

        # Get the selected items
        items = self.selectedItems()

        # Initialize a string to store the copied items
        clip_string = ""

        # Loop through items and add them to the clipboard
        for i, item in enumerate(items):

            if i == 0:
                clip_string += item.text()
                prev_row = item.row()
                continue
            
            if item.row() == prev_row:
                clip_string += '\t'
                clip_string += item.text()
                prev_row = item.row()
            
            else:
                clip_string += '\n'
                clip_string += item.text()
                prev_row = item.row()
        
        # Set the clipboard with the clip_text
        cb.setText(clip_string, mode = cb.Clipboard)

        return clip_string

    # Define a function to add a row to the table from a list
    def addRow(self, list_):

        # Get the current row
        currentRow = self.rowCount()

        # insert a new row
        self.insertRow(currentRow)

        # add the items from the list
        for i, listItem in enumerate(list_):
            print(list_)
            item = QtWidgets.QTableWidgetItem(str(listItem))

            self.setItem(
                currentRow, i, item
            )
        if self.readOnly:
            self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # Resize the columns and stretch the last column
        #self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        self.resizeColumnsToContents()


    # Define a function to convert a table to a dataframe
    def toDataFrame(self):

        # get the number of rows and column, and the header
        rows = self.rowCount()
        cols = self.columnCount()
        headers = [self.horizontalHeaderItem(i).text() for i in range(cols)]

        # Convert to a stringIO csv file
        if rows != 0:
            self.selectAll()

            from io import StringIO
            rawString = self.copyFromTable()
            rawString = StringIO(rawString)

            df = pd.read_csv(rawString, sep="\t", names = headers, dtype = str)

            # If the first column contains datetimes, use that as the index
            try:
                df.set_index(pd.DatetimeIndex(pd.to_datetime(df[df.columns[0]])), inplace = True)
                del df[df.columns[0]]
                return df
            except:
                print('couldnt convert times')
                return df
        
        else:
            return pd.DataFrame()

    # Define a function to create a table from a dataset directory
    def TableFromDatasetDirectory(self, dataDir):

        # Create a dataframe from the first dataDir Entry
        df = pd.DataFrame().from_dict(dataDir[0]['Data'], orient='columns')
        print(df)
        df.columns = [dataDir[0]['Name'] + '|' + dataDir[0]['Parameter'] + '|' + dataDir[0]['Units']]

        # Iterate through the remaining datasets (through each dataset)
        for dataset in dataDir[1:]:

            # Convert the dataset into a series
            try:
                series = pd.DataFrame().from_dict(dataset['Data'], orient='columns')
                series.columns = [dataset['Name'] + '|' + dataset['Parameter'] + '|' + dataset['Units']]
            except:
                print(dataset['Name'])
                print(pd.DataFrame().from_dict(dataset['Data'], orient='columns'))
            #  Append the series to the new dataframe
            df = pd.concat([df, series], axis=1)

        # Create a table from the dataframe
        self.createTableFromDataFrame(df)

    # Define a function to add a dataframe to the table
    def createTableFromDataFrame(self, data):

        # Clear any existing data
        self.setRowCount(0)
        self.setColumnCount(0)

        # Intitialize the dimensions and headers
        self.setRowCount(len(data.index))
        self.setColumnCount(len(data.columns)+1)

        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem(str("Date")))
        for i in range(len(data.columns)):
            colHeader = data.columns[i].split('|')
            name = colHeader[0]
            param = colHeader[1]
            unit = colHeader[2]
            self.setHorizontalHeaderItem(i+1, QtWidgets.QTableWidgetItem(str(
                "{0}\nParameter: {1}\nUnits: {2}".format(name,param,unit)
            )))

        # Iterate through the dataframe and set each item
        for i in range(len(data.index)):
            item = QtWidgets.QTableWidgetItem(str(data.index[i])[0:10])
            self.setItem(i, 0, item)
            for j in range(len(data.columns)):    
                col = list(data.columns)[j]
                val = data[col].iloc[i]
                item = QtWidgets.QTableWidgetItem(str(val))
                if self.readOnly:
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j+1, item)
        #self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        self.resizeColumnsToContents()
    
    
    
    # Open in spreadsheet
    def openInSpreadsheet(self):
        data = self.toDataFrame()
        tempFileName = "tmp"+str(int(np.random.random()*10000)) + '.csv'
        data.to_csv(path_or_buf='Resources/tempFiles/'+tempFileName)
        try:
            try:
                subprocess.check_call(['cmd','/c','start','Resources/tempFiles/'+tempFileName])
            except Exception as e:
                print(e)
                subprocess.check_call(['open','Resources/tempFiles/'+tempFileName])
        except:
            pass
         

# Define a custom Web Map widget using MapBox
class WebMap(QtWebEngineWidgets.QWebEnginePage):

    # Create a signal to emit console messages from Javascript
    java_msg_signal = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):

        # Initialize the web map
        QtWebEngineWidgets.QWebEnginePage.__init__(self)
        url = QtCore.QUrl.fromLocalFile(os.path.abspath('Resources/WebResources/WebMap.html'))
        self.load(url)

    # Override the 'acceptNavigationRequest' function to open href links in another browser
    def acceptNavigationRequest(self, url,  _type, isMainFrame):

        # Screen nvaigation requests for href links
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:

            QtGui.QDesktopServices.openUrl(url)    
            return False
        
        else: 
            return True

    # Override the 'javaScriptConsoleMessage' function to send console messages to a signal/slot
    def javaScriptConsoleMessage(self, lvl, msg, line, source):

        # Only allow INFO level console messages to be emitted
        if lvl != 0:
            return

        # Split the recieved message by commas into a list and emit it through to the reciever.
        self.java_msg_signal.emit(msg)

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  SUMMARY TAB  |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Define a custom widget to display forecast information on the summary tab
class FcstInfoPane(QtWidgets.QWidget):

    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setupUI()
    
    # Define the layout of the custom widget
    def setupUI(self):

        self.layout = QtWidgets.QHBoxLayout() # Set the layout for the custom widget
        
        # Create the Forecast metadata section
        #self.forecastMetaLayout = QtWidgets.QVBoxLayout() # Set a vertical layout for the forecast metadata section
        self.forecastMetaLayout = QtWidgets.QGridLayout()
        self.forecastMeta_ForecastID = QtWidgets.QLabel('Forecast ID: ')
        self.forecastMeta_ForecastID.setMaximumWidth(200)
        self.forecastMeta_ForecastIDLine = QtWidgets.QLineEdit()
        self.forecastMeta_ForecastIDLine.setReadOnly(True)
        self.forecastMeta_ForecastIDLine.setMinimumWidth(200)
        self.forecastMeta_ForecastIDLine.setMaximumWidth(400)
        self.forecastMetaLayout.addWidget(self.forecastMeta_ForecastID, 0, 0)
        self.forecastMetaLayout.addWidget(self.forecastMeta_ForecastIDLine, 0, 1)
        self.forecastMeta_Target = QtWidgets.QLabel('Forecast Target: ')
        self.forecastMeta_TargetLine = QtWidgets.QLineEdit()
        self.forecastMeta_TargetLine.setReadOnly(True)
        self.forecastMeta_TargetLine.setMaximumWidth(400)
        self.forecastMetaLayout.addWidget(self.forecastMeta_Target, 1, 0)
        self.forecastMetaLayout.addWidget(self.forecastMeta_TargetLine, 1, 1)
        self.forecastMeta_Period = QtWidgets.QLabel('Forecast Period: ')
        self.forecastMeta_PeriodLine = QtWidgets.QLineEdit()
        self.forecastMeta_PeriodLine.setReadOnly(True)
        self.forecastMeta_PeriodLine.setMaximumWidth(400)
        self.forecastMetaLayout.addWidget(self.forecastMeta_Period, 2, 0)
        self.forecastMetaLayout.addWidget(self.forecastMeta_PeriodLine, 2, 1)
        self.forecastMeta_Frequency = QtWidgets.QLabel('Forecast Frequency: ')
        self.forecastMeta_FrequencyLine = QtWidgets.QLineEdit()
        self.forecastMeta_FrequencyLine.setReadOnly(True)
        self.forecastMeta_FrequencyLine.setMaximumWidth(400)
        self.forecastMetaLayout.addWidget(self.forecastMeta_Frequency, 3, 0)
        self.forecastMetaLayout.addWidget(self.forecastMeta_FrequencyLine, 3, 1)
        self.forecastMeta_Forecaster = QtWidgets.QLabel('Forecaster: ')
        self.forecastMeta_ForecasterLine = QtWidgets.QLineEdit()
        self.forecastMeta_ForecasterLine.setReadOnly(True)
        self.forecastMeta_ForecasterLine.setMaximumWidth(400)
        self.forecastMetaLayout.addWidget(self.forecastMeta_Forecaster, 4, 0)
        self.forecastMetaLayout.addWidget(self.forecastMeta_ForecasterLine, 4, 1)
        
        self.forecastInfo_Heading1 = QtWidgets.QLabel('Forecast Notes: ')
        self.forecastInfo_Heading1Line = QtWidgets.QPlainTextEdit()
        self.forecastInfo_Heading1Line.setReadOnly(True)
        self.forecastInfo_Heading1Line.setMaximumWidth(400)
        widg = QtWidgets.QWidget()
        self.forecastMetaLayout.addWidget(self.forecastInfo_Heading1, 5, 0)
        self.forecastMetaLayout.addWidget(self.forecastInfo_Heading1Line, 5, 1)
        self.forecastInfo_ForecastLayout = QtWidgets.QHBoxLayout()
        self.forecastInfo_10Fcst = QtWidgets.QLabel('10%: ')
        self.forecastInfo_10FcstLine = QtWidgets.QLineEdit()
        self.forecastInfo_10FcstLine.setReadOnly(True)
        self.forecastInfo_30Fcst = QtWidgets.QLabel('30%: ')
        self.forecastInfo_30FcstLine = QtWidgets.QLineEdit()
        self.forecastInfo_30FcstLine.setReadOnly(True)
        self.forecastInfo_50Fcst = QtWidgets.QLabel('50%: ')
        self.forecastInfo_50FcstLine = QtWidgets.QLineEdit()
        self.forecastInfo_50FcstLine.setReadOnly(True)
        self.forecastInfo_70Fcst = QtWidgets.QLabel('70%: ')
        self.forecastInfo_70FcstLine = QtWidgets.QLineEdit()
        self.forecastInfo_70FcstLine.setReadOnly(True)
        self.forecastInfo_90Fcst = QtWidgets.QLabel('90%: ')
        self.forecastInfo_90FcstLine = QtWidgets.QLineEdit()
        self.forecastInfo_90FcstLine.setReadOnly(True)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_10Fcst)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_10FcstLine)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_30Fcst)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_30FcstLine)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_50Fcst)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_50FcstLine)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_70Fcst)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_70FcstLine)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_90Fcst)
        self.forecastInfo_ForecastLayout.addWidget(self.forecastInfo_90FcstLine)
        widg.setLayout(self.forecastInfo_ForecastLayout)
        self.forecastMetaLayout.addWidget(widg, 6, 0, 1, 2)


        # Create the Forecast information section
        self.forecastInfoLayout = QtWidgets.QGridLayout()
        self.forecastInfo_Heading2 = QtWidgets.QLabel('Equation:')
        self.forecastInfoLayout.addWidget(self.forecastInfo_Heading2, 0, 0)
        self.forecastInfoTable = CustomTableView(self, rowLock=True, cols = 2, rows = 0, headers = ['Parameter','Coefficient'])
        self.forecastInfoTable.setMinimumWidth(400)
        self.forecastInfoLayout.addWidget(self.forecastInfoTable, 1, 0, 1, 2)

        # Create the current data view window
        self.forecastCurrentData = CustomTableView(self, rowLock=True, cols=2, rows=0, headers=['Predictor','Value'])
        self.forecastCurrentData.setMinimumSize(QtCore.QSize(300,200))
        self.forecastCurrentData.setMaximumSize(QtCore.QSize(500,1000))

        # Lay out the forecast information pane
        self.layout.addLayout(self.forecastMetaLayout)
        line1 = QtWidgets.QFrame()
        line1.setLineWidth(0)
        line1.setFrameShape(QtWidgets.QFrame.VLine)
        line1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.layout.addWidget(line1)
        self.layout.addLayout(self.forecastInfoLayout)
        line2 = QtWidgets.QFrame()
        line2.setLineWidth(0)
        line2.setFrameShape(QtWidgets.QFrame.VLine)
        line2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.layout.addWidget(line2)
        self.layout.addWidget(self.forecastCurrentData)
        self.setLayout(self.layout)

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  STATIONS TAB  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Define a custom widget to display selected station information on the stations tab
class StationInfoPane(QtWidgets.QWidget):

    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setupUI()
    
    # Define the layout of the custom widget
    def setupUI(self):

        # Create a layout for the widget
        self.layout = QtWidgets.QVBoxLayout()
        self.scrollArea =  QtWidgets.QScrollArea(self)
        self.formScroll = QtWidgets.QFrame(self.scrollArea)

        # Add a header and description 
        self.stationHeader = QtWidgets.QTextEdit()
        self.stationHeader.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Select Datasets</strong></br>
                                    <p style="margin:0; font-size:14px;">Use the map to select climatalogical stations that should be included in the analysis. The program will download period of record data for each dataset selected.</p>
                                    </div>""")
        self.stationHeader.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.stationHeader.setReadOnly(True)
        self.stationHeader.setMaximumHeight(125)

        # Add a table to display selected stations
        self.stationTable = CustomTableView(self, rowLock = True, cols = 6, rows = 0, headers = ['PYID','Type','ID','Name','Parameter','URL'], menuFunctions=['COPY','OPEN','DELETEROW'])

        # Add a section to add other datasets
        self.otherDataLayout = QtWidgets.QGridLayout()
        self.stationLabel = QtWidgets.QLabel('Other Datasets:')
        self.otherDataLayout.addWidget(self.stationLabel, 0, 0, 1, 4)

        # NRCC dataset layout
        self.nrccLabel = QtWidgets.QLabel('NRCC')
        self.nrccLabel.setMinimumWidth(100)
        self.nrccLabel.setMaximumWidth(100)
        self.nrccInfoButton = QtWidgets.QLabel()
        self.nrccInfoButton.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.nrccInfoButton.setScaledContents(True)
        self.nrccInfoButton.setToolTip('<html><head/><body><p>NRCC gridded precipitation and temperature data, averaged by watershed.</p></body></html>')
        self.nrccInput = QtWidgets.QLineEdit()
        self.nrccInput.setPlaceholderText("Enter HUC8:")
        self.nrccButton = QtWidgets.QPushButton('Add')
        self.otherDataLayout.addWidget(self.nrccLabel, 1, 0, 1, 1)
        self.otherDataLayout.addWidget(self.nrccInfoButton, 1, 1, 1, 1)
        self.otherDataLayout.addWidget(self.nrccInput, 1, 2, 1, 1)
        self.otherDataLayout.addWidget(self.nrccButton, 1, 3, 1, 1)

        # Prism dataset layout
        self.prismLabel = QtWidgets.QLabel('PRISM')
        self.prismLabel.setMinimumWidth(100)
        self.prismLabel.setMaximumWidth(100)
        self.prismInfoButton = QtWidgets.QLabel()
        self.prismInfoButton.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.prismInfoButton.setScaledContents(True)
        self.prismInfoButton.setToolTip('<html><head/><body><p>PRISM gridded precipitation and temperature data, averaged by watershed.</p></body></html>')
        self.prismInput = QtWidgets.QLineEdit()
        self.prismInput.setPlaceholderText("Enter HUC8:")
        self.prismButton = QtWidgets.QPushButton('Add')
        self.otherDataLayout.addWidget(self.prismLabel, 2, 0, 1, 1)
        self.otherDataLayout.addWidget(self.prismInfoButton, 2, 1, 1, 1)
        self.otherDataLayout.addWidget(self.prismInput, 2, 2, 1, 1)
        self.otherDataLayout.addWidget(self.prismButton, 2, 3, 1, 1)

        # PDSI dataset 
        self.pdsiLabel = QtWidgets.QLabel("PDSI")
        self.pdsiLabel.setMinimumWidth(100)
        self.pdsiLabel.setMaximumWidth(100)
        self.pdsiInfoButton = QtWidgets.QLabel()
        self.pdsiInfoButton.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.pdsiInfoButton.setScaledContents(True)
        self.pdsiInfoButton.setToolTip('<html><head/><body><p>Palmer Drought Severity Index by Climate Division</p></body></html>')
        self.pdsiInput = CustomQComboBox(self.formScroll)
        self.pdsiInput.addItems(list(CLIMATE_DIVISIONS.divisions.keys()))
        self.pdsiButton = QtWidgets.QPushButton('Add')
        self.otherDataLayout.addWidget(self.pdsiLabel, 3, 0, 1, 1)
        self.otherDataLayout.addWidget(self.pdsiInfoButton, 3, 1, 1, 1)
        self.otherDataLayout.addWidget(self.pdsiInput, 3, 2, 1, 1)
        self.otherDataLayout.addWidget(self.pdsiButton, 3, 3, 1, 1)

        # SOI / ENSO dataset layout
        self.ensoLabel = QtWidgets.QLabel('Climate')
        self.ensoLabel.setMinimumWidth(100)
        self.ensoLabel.setMaximumWidth(100)
        self.ensoInfoButton = QtWidgets.QLabel()
        self.ensoInfoButton.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.ensoInfoButton.setToolTip('<html><head/><body><p>Various climate indices.</br></br> See www.cpc.ncep.noaa.gov for more information.</p></body></html>')
        self.ensoInput = CustomQComboBox(self.formScroll)
        self.ensoInput.addItem('Nino3.4 SST')
        self.ensoInput.addItem('Nino3.4 SST Anomaly')
        self.ensoInput.addItem('PNA Teleconnection')
        self.ensoInput.addItem('AMO Teleconnection')
        self.ensoInput.addItem("PDO Teleconnection")
        self.ensoInput.addItem("Arctic Oscillation Index")
        #self.ensoInput.addItem('Mauna Loa CO2')
        self.ensoButton = QtWidgets.QPushButton('Add')
        self.otherDataLayout.addWidget(self.ensoLabel, 4, 0, 1, 1)
        self.otherDataLayout.addWidget(self.ensoInfoButton, 4, 1, 1, 1)
        self.otherDataLayout.addWidget(self.ensoInput, 4, 2, 1, 1)
        self.otherDataLayout.addWidget(self.ensoButton, 4, 3, 1, 1)

        # Other Web Service data
        self.webServiceLabel = QtWidgets.QLabel("Web Dataset")
        self.webServiceLabel.setMinimumWidth(100)
        self.webServiceLabel.setMaximumWidth(100)
        self.webServiceInfo = QtWidgets.QLabel()
        self.webServiceInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.webServiceInfo.setToolTip('<html><head/><body><p>Add a dataset using a custom dataloader</p></body></html>')
        self.webServiceButton = QtWidgets.QPushButton("Define Web Dataset")
        self.otherDataLayout.addWidget(self.webServiceLabel, 5, 0, 1, 1)
        self.otherDataLayout.addWidget(self.webServiceInfo, 5, 1, 1, 1)
        self.otherDataLayout.addWidget(self.webServiceButton, 5, 2, 1, 2)


        # Build the widget
        self.layout.addWidget(self.stationHeader)
        self.layout.addWidget(self.stationTable)
        line1 = QtWidgets.QFrame()
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Plain)
        line1.setLineWidth(0)
        self.layout.addWidget(line1)
        self.layout.addLayout(self.otherDataLayout)
        self.setLayout(self.layout)

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  DATA TAB  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Define a custom widget to display options for the data tab
class DataOptionsPane(QtWidgets.QWidget):

    # Initialize a custom QWidget
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        self.setupUI()
    
    # Define the layout of the custom widget
    def setupUI(self):

        # Create a layout for the widget
        self.layout = QtWidgets.QVBoxLayout()

        # Add a header and description
        self.header1 = QtWidgets.QTextEdit()
        self.header1.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Acquire Datasets</strong></br>
                                    <p style="margin:0; font-size:14px;">Specify options to download and process selected datasets. Import your Excel and CSV spreadsheets.</p>
                                    </div>""")
        self.header1.setReadOnly(True)
        self.header1.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.header1.setMaximumHeight(100)

        # layout the options in a grid
        self.optionsGrid = QtWidgets.QGridLayout()
        self.optionsGrid.setColumnStretch(0, 1)
        self.optionsGrid.setColumnStretch(1, 0)
        self.optionsGrid.setColumnStretch(2, 1)
        self.optionsGrid.setColumnStretch(3, 1)
        self.optionsGrid.setColumnStretch(4, 1)
        
        # POR option
        self.porLabel = QtWidgets.QLabel("POR")
        self.porInfo = QtWidgets.QLabel() 
        self.porInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.porInfo.setScaledContents(True)
        self.porInfo.setToolTip('<html><head/><body><p>PyForecast will attempt to download daily station data based on the POR or the start year specified here.</p></body></html>')
        self.porYes = QtWidgets.QCheckBox("POR")
        self.porYes.setChecked(True)
        self.porYes.stateChanged.connect(lambda: self.porToggle())
        self.porNo = QtWidgets.QCheckBox("Years")
        self.porNo.setChecked(False)
        self.porNo.stateChanged.connect(lambda: self.porToggle())
        self.porGroup = QtWidgets.QButtonGroup(self)
        self.porGroup.addButton(self.porYes)
        self.porGroup.addButton(self.porNo)
        self.porInput = QtWidgets.QLineEdit()
        self.porInput.setText("30")
        self.porInput.setValidator(onlyInt)
        self.porT1 = QtWidgets.QLineEdit()
        self.porT1.setText(str(datetime.today().year - 30))
        self.porT1.setValidator(onlyInt)
        self.porT1.setVisible(False)
        self.porT2 = QtWidgets.QLineEdit()
        self.porT2.setText(str(datetime.today().year))
        self.porT2.setValidator(onlyInt)
        self.porT2.setDisabled(True)
        self.porT2.setVisible(False)
        self.optionsGrid.addWidget(self.porLabel, 0, 0, 1, 1)
        self.optionsGrid.addWidget(self.porInfo, 0, 1, 1, 1)
        self.optionsGrid.addWidget(self.porYes, 0, 2, 1, 1)
        self.optionsGrid.addWidget(self.porNo, 0, 3, 1, 1)
        self.optionsGrid.addWidget(self.porInput, 1, 2, 1, 2)
        self.optionsGrid.addWidget(self.porT1, 1, 2, 1, 1)
        self.optionsGrid.addWidget(self.porT2, 1, 3, 1, 1)

        # IMPUTE SWE option
        # self.sweImputeLabel = QtWidgets.QLabel("Impute SNOTEL")
        # self.sweImputeInfo =  QtWidgets.QLabel() 
        # self.sweImputeInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        # self.sweImputeInfo.setScaledContents(True)
        # self.sweImputeInfo.setToolTip('<html><head/><body><p>Fill incomplete SNOTEL data using MICE Imputation. Works if 3 or more SWE stations are included.</p></body></html>')
        # self.sweImputeInputYes = QtWidgets.QCheckBox("Yes")
        # self.sweImputeInputYes.setChecked(False)
        # self.sweImputeInputNo = QtWidgets.QCheckBox("No")
        # self.sweImputeInputNo.setChecked(True)
        # self.sweGroup = QtWidgets.QButtonGroup(self)
        # self.sweGroup.addButton(self.sweImputeInputYes)
        # self.sweGroup.addButton(self.sweImputeInputNo)
        # self.optionsGrid.addWidget(self.sweImputeLabel, 1, 0, 1, 1)
        # self.optionsGrid.addWidget(self.sweImputeInfo, 1, 1, 1, 1)
        # self.optionsGrid.addWidget(self.sweImputeInputYes, 1, 2, 1, 1)
        # self.optionsGrid.addWidget(self.sweImputeInputNo, 1, 3, 1, 1)

        # Interpolate Option
        self.interpLabel = QtWidgets.QLabel("Fill NaN's")
        self.interpInfo = QtWidgets.QLabel() 
        self.interpInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.interpInfo.setScaledContents(True)
        self.interpInfo.setToolTip('<html><head/><body><p>Interpolate missing data using cubic splines. Fills a maximum of 3 days of missing data.</p></body></html>')
        self.interpInputYes = QtWidgets.QCheckBox("Yes")
        self.interpInputYes.setChecked(True)
        self.interpInputNo = QtWidgets.QCheckBox("No")
        self.interpInputNo.setChecked(False)
        self.interpGroup = QtWidgets.QButtonGroup(self)
        self.interpGroup.addButton(self.interpInputYes)
        self.interpGroup.addButton(self.interpInputNo)
        self.optionsGrid.addWidget(self.interpLabel, 2, 0, 1, 1)
        self.optionsGrid.addWidget(self.interpInfo, 2, 1, 1, 1)
        self.optionsGrid.addWidget(self.interpInputYes, 2, 2, 1, 1)
        self.optionsGrid.addWidget(self.interpInputNo, 2, 3, 1, 1)

        # Data download
        self.downloadButton = QtWidgets.QPushButton("Download")
        self.optionsGrid.addWidget(self.downloadButton, 3, 0, 1, 4)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.optionsGrid.addWidget(self.progressBar, 4, 0, 1, 4)

        line1 = QtWidgets.QFrame()
        line1.setFrameShape(QtWidgets.QFrame.HLine)
        line1.setFrameShadow(QtWidgets.QFrame.Plain)
        line1.setLineWidth(0)
        spacer = QtWidgets.QWidget()
        spacer.setMinimumHeight(20)
        spacer.setMaximumHeight(20)
        self.optionsGrid.addWidget(line1, 5, 0, 1, 4)
        self.optionsGrid.addWidget(spacer, 6, 0, 1, 4)

        # Data update
        self.updateLabel = QtWidgets.QLabel('Update Data')
        self.updateInfo = QtWidgets.QLabel() 
        self.updateInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.updateInfo.setScaledContents(True)
        self.updateInfo.setToolTip('<html><head/><body><p>Update the data table with current data measured since the last update.</p></body></html>')
        self.updateButton = QtWidgets.QPushButton('Update')
        self.optionsGrid.addWidget(self.updateLabel,7,0,1,1)
        self.optionsGrid.addWidget(self.updateInfo,7,1,1,1)
        self.optionsGrid.addWidget(self.updateButton,7,2,1,2)


        # Data import label
        self.importLabel = QtWidgets.QLabel("Import dataset")
        self.importInfo = QtWidgets.QLabel() 
        self.importInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.importInfo.setScaledContents(True)
        self.importInfo.setToolTip('<html><head/><body><p>Import data from a CSV or Excel File. Data is appended to the table. See the documentation for instructions.</p></body></html>')
        self.importButton = QtWidgets.QPushButton("Import")
        self.optionsGrid.addWidget(self.importLabel, 8, 0, 1, 1)
        self.optionsGrid.addWidget(self.importInfo, 8, 1, 1, 1)
        self.optionsGrid.addWidget(self.importButton, 8, 2, 1, 2)
        

        # View missing data button
        #self.missingLabel = QtWidgets.QLabel("View Missing")
        #self.missingInfo = QtWidgets.QLabel()
        #self.missingInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        #self.missingInfo.setScaledContents(True)
        #self.missingInfo.setToolTip('<html><head/><body><p>View the serial completeness of your dataset.</p></body></html>')
        #self.missingButton = QtWidgets.QPushButton("View")
        #self.optionsGrid.addWidget(self.missingLabel, 9, 0, 1, 1)
        #self.optionsGrid.addWidget(self.missingInfo, 9, 1, 1, 1)
        #self.optionsGrid.addWidget(self.missingButton, 9, 2, 1, 2)


        # View Data Analysis UI button
        self.matrixLabel = QtWidgets.QLabel("Data Analysis")
        self.matrixInfo = QtWidgets.QLabel()
        self.matrixInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.matrixInfo.setScaledContents(True)
        self.matrixInfo.setToolTip('<html><head/><body><p>View the dataset correlations using a matrix plot.</p></body></html>')
        self.matrixButton = QtWidgets.QPushButton("View")
        self.optionsGrid.addWidget(self.matrixLabel, 9, 0, 1, 1)
        self.optionsGrid.addWidget(self.matrixInfo, 9, 1, 1, 1)
        self.optionsGrid.addWidget(self.matrixButton, 9, 2, 1, 2)


        spacer = QtWidgets.QWidget()
        spacer.setMaximumHeight(1200)
        self.optionsGrid.addWidget(spacer, 10, 0, 1, 4)


        # Build the widget
        self.layout.addWidget(self.header1)
        self.layout.addLayout(self.optionsGrid)
        self.setLayout(self.layout)


    def porToggle(self):
        if self.porYes.isChecked():
            self.porInput.setVisible(True)
            self.porT1.setVisible(False)
            self.porT2.setVisible(False)
        else:
            self.porInput.setVisible(False)
            self.porT1.setVisible(True)
            self.porT2.setVisible(True)
        return

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  FORECAST OPTIONS TAB  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Define a custom widget to display options for the data tab
class FcstOptionsPane(QtWidgets.QWidget):

    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setupUI()
        self.setFixedWidth(420)
    
    # Define the layout of the custom widget
    def setupUI(self):

        # Create a layout for the widget
        self.layout = QtWidgets.QVBoxLayout()

        # Create a header to top the pane
        self.header = QtWidgets.QTextEdit()
        self.header.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Set Options</strong></br>
                                    <p style="margin:0; font-size:14px;">Specify the properties of your forecasts. Construct predictor variables to be used in forecast equations. View correlations between variables.</p>
                                    </div>""")
        self.header.setReadOnly(True)
        self.header.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.header.setMaximumHeight(90)

        # Build the left side of the options pane
        self.gridLayout1 = QtWidgets.QGridLayout()
        self.scrollArea =  QtWidgets.QScrollArea(self)
        self.formScroll = QtWidgets.QFrame(self.scrollArea)
        self.periodLabel = QtWidgets.QLabel("Forecast Period")
        self.periodInfo = QtWidgets.QLabel() 
        self.periodInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.periodInfo.setToolTip('<html><head/><body><p>Set the inflow volume period for your forecast (defaults to April - July)</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.periodInfo)
        hlayout.addWidget(self.periodLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.gridLayout1.addLayout(hlayout, 0, 0, 1, 4)
        self.periodStartInput = CustomQComboBox(self.formScroll)
        self.periodStartInput.addItems(['January','February','March','April','May','June','July','August','September','October','November','December'])
        self.periodStartInput.setCurrentIndex(3)
        self.gridLayout1.addWidget(self.periodStartInput, 1, 0, 1, 2)
        self.periodEndInput = CustomQComboBox(self.formScroll)
        self.periodEndInput.addItems(['January','February','March','April','May','June','July','August','September','October','November','December'])
        self.periodEndInput.setCurrentIndex(6)
        self.gridLayout1.addWidget(self.periodEndInput, 1, 2, 1, 2)
        self.freqLabel = QtWidgets.QLabel("Forecast Frequency")
        self.freqInfo = QtWidgets.QLabel() 
        self.freqInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.freqInfo.setToolTip('<html><head/><body><p>Specify how many forecast equations should be produced each water year. Default monthly.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.freqInfo)
        hlayout.addWidget(self.freqLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.gridLayout1.addLayout(hlayout, 2, 0, 1, 4)
        self.freqInput = CustomQComboBox(self.formScroll)
        self.freqInput.addItems(["Monthly", "Bi-Monthly"])
        self.gridLayout1.addWidget(self.freqInput, 3, 0, 1, 4)
        self.eqStartLabel = QtWidgets.QLabel("Forecasts start on:")
        self.eqStartInfo = QtWidgets.QLabel() 
        self.eqStartInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.eqStartInfo.setToolTip('<html><head/><body><p>Specify the first month in which you will issue a forecast.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.eqStartInfo)
        hlayout.addWidget(self.eqStartLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.gridLayout1.addLayout(hlayout, 4, 0, 1, 4)
        self.eqStartInput = CustomQComboBox(self.formScroll)
        self.eqStartInput.addItems(['January','February','March','April','May','June','July','August','September','October','November','December'])
        self.gridLayout1.addWidget(self.eqStartInput, 5, 0, 1, 4)
        self.wateryearStartInfo = QtWidgets.QLabel()
        self.wateryearStartInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.wateryearStartInfo.setToolTip('<html><head/><body><p>Specify the first month of your water year</p></body></html>')
        self.wateryearStartLabel = QtWidgets.QLabel("Wateryear starts on:")
        self.wateryearStartInput = CustomQComboBox(self.formScroll)
        self.wateryearStartInput.addItems(['January','February','March','April','May','June','July','August','September','October','November','December'])
        self.wateryearStartInput.setCurrentIndex(9)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.wateryearStartInfo)
        hlayout.addWidget(self.wateryearStartLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.gridLayout1.addLayout(hlayout, 6, 0, 1, 4)
        self.gridLayout1.addWidget(self.wateryearStartInput, 7, 0, 1, 4)
        self.targetLabel = QtWidgets.QLabel("Forecast Target:")
        self.targetInfo = QtWidgets.QLabel() 
        self.targetInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.targetInfo.setToolTip('<html><head/><body><p>Specify the dataset that you are forecasting. Only streamflow variables can be chosen.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.targetInfo)
        hlayout.addWidget(self.targetLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.gridLayout1.addLayout(hlayout, 8, 0, 1, 4)
        self.targetInput = CustomQComboBox(self.formScroll)
        self.gridLayout1.addWidget(self.targetInput, 9, 0, 1, 4)
        self.precipLabel = QtWidgets.QLabel("Accumulate Precipitation")
        self.precipInfo = QtWidgets.QLabel() 
        self.precipInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.precipInfo.setToolTip('<html><head/><body><p>Create predictors that accumulates precipitation. User defines accumulation period.</p></body></html>')
        self.precipInputYes = QtWidgets.QCheckBox("Yes")
        self.precipInputYes.setChecked(True)
        self.precipInputNo = QtWidgets.QCheckBox("No")
        self.precipInputNo.setChecked(False)
        self.precipGroup = QtWidgets.QButtonGroup()
        self.precipGroup.addButton(self.precipInputYes)
        self.precipGroup.addButton(self.precipInputNo)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.precipInfo)
        hlayout.addWidget(self.precipLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        hlayout.addWidget(self.precipInputYes)
        hlayout.addWidget(self.precipInputNo)
        self.gridLayout1.addLayout(hlayout, 10, 0, 1, 4)
        self.accumLabel = QtWidgets.QLabel("Accumulate From:")
        self.accumStart = CustomQComboBox(self.formScroll)
        self.accumStart.addItems(['October','November','December','January','February','March','April','May','June','July','August','September'])
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.accumLabel)
        hlayout.addWidget(self.accumStart)
        self.gridLayout1.addLayout(hlayout, 11, 0, 1, 4)
        self.forecasterLabel = QtWidgets.QLabel("Forecaster: ")
        self.forecasterInput = QtWidgets.QLineEdit()
        self.forecasterInput.setPlaceholderText("Name:")
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.forecasterLabel)
        hlayout.addWidget(self.forecasterInput)
        self.gridLayout1.addLayout(hlayout, 12, 0, 1, 4)
        self.forecastNotes = QtWidgets.QPlainTextEdit()
        self.forecastNotes.setMaximumHeight(50)
        self.forecastNotes.setPlaceholderText("Notes...")
        self.forecastNotesLabel = QtWidgets.QLabel("Forecast Notes:")
        self.gridLayout1.addWidget(self.forecastNotesLabel, 13, 0, 1, 4)
        self.gridLayout1.addWidget(self.forecastNotes, 14, 0, 1, 4)
        self.applyButton = QtWidgets.QPushButton("Apply Options")
        self.gridLayout1.addWidget(self.applyButton, 15, 0, 1, 4)
        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Plain)
        hline.setLineWidth(0)
        self.gridLayout1.addWidget(hline, 16, 0, 1, 4)
        self.updateButton = QtWidgets.QPushButton("Update Predictors")
        self.gridLayout1.addWidget(self.updateButton, 17, 0, 1, 4)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.gridLayout1.addWidget(self.progressBar, 18, 0, 1, 4)
        self.progressLabel = QtWidgets.QLabel(" ")
        self.gridLayout1.addWidget(self.progressLabel, 19, 0, 1, 4)

        # Build the widget
        self.scroll = QtWidgets.QScrollArea()
        self.scrollContent = QtWidgets.QWidget()
        self.scrollContent.setFixedWidth(380)
        self.scroll.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scrollLayout = QtWidgets.QVBoxLayout()
        self.scrollLayout.addWidget(self.header)
        self.scrollLayout.addLayout(self.gridLayout1)
        self.scrollContent.setLayout(self.scrollLayout)
        self.scroll.setWidget(self.scrollContent)

        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)

class FcstOptionsTrees(QtWidgets.QWidget):
    
    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setupUI()
    
    # Define the layout of the custom widget
    def setupUI(self):

        # Create a layout for the widget
        self.layout = QtWidgets.QHBoxLayout()

        # Set up the first tree
        self.tree1Layout = QtWidgets.QVBoxLayout()
        self.tree1Label = QtWidgets.QLabel("All Available Predictors")
        self.tree1Info = QtWidgets.QLabel() 
        self.tree1Info.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.tree1Info.setToolTip('<html><head/><body><p>Drag available predictors into specific forecasts</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.tree1Info)
        hlayout.addWidget(self.tree1Label)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.tree1Layout.addLayout(hlayout)
        self.tree1 = CustomTreeView(self, dragFrom=True, dropTo=False, menuFunctions=['OPENEXCEL'])
        self.tree1.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.tree1Layout.addWidget(self.tree1)

        # Set up the second tree
        self.tree2Layout = QtWidgets.QVBoxLayout()
        self.tree2Label = QtWidgets.QLabel("Equation Pools")
        self.tree2Info = QtWidgets.QLabel() 
        self.tree2Info.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.tree2Info.setToolTip('<html><head/><body><p>Drag available predictors into specific forecasts</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.tree2Info)
        hlayout.addWidget(self.tree2Label)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.tree2Layout.addLayout(hlayout)
        self.tree2 = CustomTreeView(self, dragFrom=True, dropTo=True, menuFunctions=['DELETE','FORCE','DANALYSIS'])
        self.tree2.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.tree2Layout.addWidget(self.tree2)

        # Lay out the widget
        self.layout.addLayout(self.tree1Layout)
        vline = QtWidgets.QFrame()
        vline.setFrameShape(QtWidgets.QFrame.VLine)
        vline.setFrameShadow(QtWidgets.QFrame.Plain)
        self.layout.addWidget(vline)
        self.layout.addLayout(self.tree2Layout)
        self.setLayout(self.layout)

class plotsPane(QtWidgets.QWidget):
    prdIDSignal = QtCore.pyqtSignal(str)
    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setAcceptDrops(True)
        
        self.setupUI()
    
    # Define the layout of the custom widget
    def setupUI(self):

        self.layout = QtWidgets.QGridLayout()
        self.tsPlot = PlotCanvas_1Plot()
        self.tsPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.corrPlot = PlotCanvas_1Plot()
        self.corrPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        vlayout = QtWidgets.QVBoxLayout()
        self.clearButton = QtWidgets.QPushButton("Clear Plots")
        self.clearButton.setMaximumWidth(40)
        self.axesButton = QtWidgets.QPushButton("Use 2 Axes")
        self.axesButton.setMaximumWidth(40)
        self.corrButton = QtWidgets.QPushButton("Correlation")
        self.corrButton.setMaximumWidth(40)
        vlayout.addWidget(self.clearButton)
        vlayout.addWidget(self.axesButton)
        vlayout.addWidget(self.corrButton)
        self.layout.addLayout(vlayout, 0, 0, 1, 1)
        self.layout.addWidget(self.tsPlot, 0, 1, 1, 1)
        self.layout.addWidget(self.corrPlot, 0, 2, 1, 1)
        self.tsNav = NavigationToolbar(self.tsPlot, self)
        self.corrNav = NavigationToolbar(self.corrPlot, self)
        self.layout.addWidget(self.tsNav, 1, 1, 1, 1)
        self.layout.addWidget(self.corrNav, 1, 2, 1, 1)
        self.setLayout(self.layout)

    # Define the behaviour for droping data into the graphs
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):

        prdID = -1
        pos = event.pos()

        # Get the item's text
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
           mod = QtGui.QStandardItemModel()
           mod.dropMimeData(event.mimeData(),QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())
           item = mod.item(0,0)
           itemText = item.text()
        else:
            print('wrongMimeType')
            event.ignore()
            return
        
        # Ensure that the item is a valid predictor
        if item.hasChildren():

            numChildren = item.rowCount()
            print('item has {0} children'.format(numChildren))
            for i in range(numChildren):
                child = item.child(i)
                if 'prdID: ' in child.text():
                    prdID = child.text()[7:]
                if 'Name' in child.text():
                    prdID = child.text()
                    break
        
            if prdID == -1:
                print('no prdid')
                event.ignore()
                return
        
        else:
            print('no children')
            event.ignore()
            return
        
        
        self.prdIDSignal.emit(prdID)
        event.accept()

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  REGRESSION TAB  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Set up a standard regression tab
class StandardRegressionTab(QtWidgets.QWidget):

    # Initialize a custom widget
    def __init__(self, parent=None, model = 'default'):

        QtWidgets.QWidget.__init__(self)
        self.setupUI(model)
    
    def setupUI(self,model='none'):

        # Set the tab layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout2 = QtWidgets.QVBoxLayout()
        self.scrollArea =  QtWidgets.QScrollArea(self)
        self.formScroll = QtWidgets.QFrame(self.scrollArea)

        # Add widgets to the layout
        self.eqSelectLabel = QtWidgets.QLabel("Select Equation")
        self.eqSelectInfo = QtWidgets.QLabel() 
        self.eqSelectInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.eqSelectInfo.setToolTip('<html><head/><body><p>Which forecast equation are you trying to generate.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.eqSelectInfo)
        hlayout.addWidget(self.eqSelectLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.eqSelect = CustomQComboBox(self.formScroll)
        self.eqSelect.addItems([])
        self.layout.addWidget(self.eqSelect)
        self.featSelMethodLabel = QtWidgets.QLabel("Feature Selection Method")
        self.featSelMethodInfo = QtWidgets.QLabel() 
        self.featSelMethodInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.featSelMethodInfo.setToolTip('<html><head/><body><p>Defines how predictors are added to models. See documentation for more info.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.featSelMethodInfo)
        hlayout.addWidget(self.featSelMethodLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.featSelInput = CustomQComboBox(self.formScroll)
        self.featSelInput.addItems(["Sequential Floating Forward Selection", "Sequential Floating Backwards Selection", "Brute Force"])#["Forward Selection","Backward Selection",["Sequential Floating Forward Selection"],"Floating Backward"])
        self.layout.addWidget(self.featSelInput)
        self.numModelsLabel = QtWidgets.QLabel("Number of Models")
        self.numModelsInfo = QtWidgets.QLabel() 
        self.numModelsInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.numModelsInfo.setToolTip('<html><head/><body><p>Defined how many models will be built in parallel using the feature selection scheme specified above.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.numModelsInfo)
        hlayout.addWidget(self.numModelsLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.numModelsInput = QtWidgets.QLineEdit()
        self.numModelsInput.setText("50")
        self.numModelsInput.setValidator(onlyInt)
        self.layout.addWidget(self.numModelsInput)
        self.crossValLabel = QtWidgets.QLabel("Cross Validation Method")
        self.crossValInfo = QtWidgets.QLabel() 
        self.crossValInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.crossValInfo.setToolTip('<html><head/><body><p>Defines the cross-validation scheme to score models as predictors are added. See documentation.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.crossValInfo)
        hlayout.addWidget(self.crossValLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.crossValInput = CustomQComboBox(self.formScroll)
        self.crossValInput.addItems(["Leave One Out","K-Fold (5 folds)","K-Fold (10 folds)"])
        self.layout.addWidget(self.crossValInput)
        self.scoreLabel = QtWidgets.QLabel("Model Scoring Method")
        self.scoreInfo = QtWidgets.QLabel() 
        self.scoreInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.scoreInfo.setToolTip('<html><head/><body><p>Defines the parameter used to score models as predictors are added. </p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.scoreInfo)
        hlayout.addWidget(self.scoreLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.scoreInput = CustomQComboBox(self.formScroll)
        self.scoreInput.addItems(["Cross Validated Adjusted R2","Root Mean Squared Prediction Error","Cross Validated Nash-Sutcliffe","Mean Absolute Error"])
        self.layout.addWidget(self.scoreInput)

        self.distLabel = QtWidgets.QLabel("Inflow Distribution")
        self.distInfo = QtWidgets.QLabel() 
        self.distInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.distInfo.setToolTip('<html><head/><body><p>Defines the assumed distribution of inflows to the reservoir </p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.distInfo)
        hlayout.addWidget(self.distLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.distInput = CustomQComboBox(self.formScroll)
        self.distInput.addItems(["Normal"])#, "Lognormal"])
        self.layout.addWidget(self.distInput)

        self.regrButton = QtWidgets.QPushButton("Run " + model)
        self.layout.addWidget(self.regrButton)
        self.regrProgress = QtWidgets.QProgressBar()
        self.regrProgress.setValue(0)
        self.layout.addWidget(self.regrProgress)

        self.regModLabel = QtWidgets.QLabel("Models Analyzed: ")
        self.layout.addWidget(self.regModLabel)

        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Plain)
        self.layout.addWidget(hline)

        self.bestModelTable = CustomTableView(self, rowLock = True, colLock = False, cols =5, rows = 0, headers = ['prdIDs','MAE','RMSE','CV Adjusted R2','CV NSE'], menuFunctions = ['SAVEFCST', 'REGSTAT'], readOnly = True, dragFrom=False)
        self.bestModelTable.setMinimumHeight(250)
        self.layout.addWidget(self.bestModelTable)

        self.predAnlysButton = QtWidgets.QPushButton("Model Analysis")
        self.layout.addWidget(self.predAnlysButton)

        self.scroll = QtWidgets.QScrollArea()
        self.scrollContent = QtWidgets.QWidget()
        #self.scrollContent.setMinimumWidth(370)
        self.scroll.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.scrollLayout = self.layout
        #self.scrollLayout.addLayout(self.layout)
        self.scrollContent.setLayout(self.scrollLayout)
        self.scroll.setWidget(self.scrollContent)
        self.scroll.setWidgetResizable(True)

        self.layout2.addWidget(self.scroll)

        # Lay out the tab
        self.setLayout(self.layout2)

# Set up a Artificial Neural Network regression tab
class ANNRegressionTab(QtWidgets.QWidget):

    # Initialize a custom widget
    def __init__(self, parent=None, model = 'default'):

        QtWidgets.QWidget.__init__(self)
        self.setupUI(model)
    
    def setupUI(self,model='none'):

        # Set the tab layout
        self.layout = QtWidgets.QVBoxLayout()
        self.scrollArea =  QtWidgets.QScrollArea(self)
        self.formScroll = QtWidgets.QFrame(self.scrollArea)

        # Add the options
        self.bigLabel = QtWidgets.QLabel("COMING SOON........")
        self.layout.addWidget(self.bigLabel)
        self.structureLabel = QtWidgets.QLabel("Hidden Layers")
        self.structureInfo = QtWidgets.QLabel() 
        self.structureInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.structureInfo.setToolTip('<html><head/><body><p>How many hidden layers will the MLP neural network have.</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.structureInfo)
        hlayout.addWidget(self.structureLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.structureInput = CustomQComboBox(self.formScroll)
        self.structureInput.addItems(["1 Hidden Layer","2 Hidden Layers","3 Hidden Layers"])
        self.layout.addWidget(self.structureInput)

        self.hiddenNeuronsLabel = QtWidgets.QLabel("Add Layer Neurons")
        self.hiddenNeuronsInfo = QtWidgets.QLabel()
        self.hiddenNeuronsInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.hiddenNeuronsInfo.setToolTip('<html><head/><body><p>Define the number of neurons in each hidden layer</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.hiddenNeuronsInfo)
        hlayout.addWidget(self.hiddenNeuronsLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        self.hiddenNeuronsLayer1Label = QtWidgets.QLabel("Layer 1 Neurons: ")
        self.hiddenNeuronsLayer1Input = QtWidgets.QLineEdit()
        self.hiddenNeuronsLayer1Input.setValidator(onlyInt)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.hiddenNeuronsLayer1Label)
        hlayout.addWidget(self.hiddenNeuronsLayer1Input)
        self.layout.addLayout(hlayout)
        self.hiddenNeuronsLayer2Label = QtWidgets.QLabel("Layer 2 Neurons: ")
        self.hiddenNeuronsLayer2Input = QtWidgets.QLineEdit()
        self.hiddenNeuronsLayer2Input.setValidator(onlyInt)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.hiddenNeuronsLayer2Label)
        hlayout.addWidget(self.hiddenNeuronsLayer2Input)
        self.layout.addLayout(hlayout)
        self.hiddenNeuronsLayer3Label = QtWidgets.QLabel("Layer 3 Neurons: ")
        self.hiddenNeuronsLayer3Input = QtWidgets.QLineEdit()
        self.hiddenNeuronsLayer3Input.setValidator(onlyInt)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.hiddenNeuronsLayer3Label)
        hlayout.addWidget(self.hiddenNeuronsLayer3Input)
        self.layout.addLayout(hlayout)
        
        # Build the widget
        self.setLayout(self.layout)

# Set up a Gaussian Process regression tab
class GPRegressionTab(QtWidgets.QWidget):

    # Initialize a custom widget
    def __init__(self, parent=None, model = 'default'):

        QtWidgets.QWidget.__init__(self)
        self.setupUI(model)
    
    def setupUI(self,model='none'):

        # Set the tab layout
        self.layout = QtWidgets.QVBoxLayout()
        self.bigLabel = QtWidgets.QLabel('COMING SOON...')
        self.layout.addWidget(self.bigLabel)
        self.setLayout(self.layout)
        self.scrollArea =  QtWidgets.QScrollArea(self)
        self.formScroll = QtWidgets.QFrame(self.scrollArea)

# Set up the regression selection pane
class RegressionSelectionPane(QtWidgets.QWidget):

    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setupUI()
        self.setStyleSheet("""
        QWidget {padding:0}
        QTabBar::tab { min-width: 50 }
        """)
    
    # Define the layout of the custom widget
    def setupUI(self):

        # Create a layout for the widget
        self.layout = QtWidgets.QVBoxLayout()

        # Create a header to top the pane
        self.header = QtWidgets.QTextEdit()
        self.header.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Perform Regressions</strong></br>
                                    <p style="margin:0; font-size:14px;">Build regression models to generate forecast equations and forecast objects. View and save well-performing models.</p>
                                    </div>""")
        self.header.setReadOnly(True)
        self.header.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.header.setMaximumHeight(80)

        # Put in a tabwidget
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setStyleSheet("""
        QTabBar {background: #e8e8e8}
        """)
        self.mlrTab = StandardRegressionTab(self, "MLR")
        self.pcarTab = StandardRegressionTab(self, "PCAR")
        self.zscrTab = StandardRegressionTab(self, "ZSCR")
        self.annTab = StandardRegressionTab(self, 'ANN')
        self.gprTab = GPRegressionTab(self)
        self.tabWidget.addTab(self.mlrTab, "MLR")
        self.tabWidget.addTab(self.pcarTab, "PCAR")
        self.tabWidget.addTab(self.zscrTab, "ZSCR")
        self.tabWidget.addTab(self.annTab, "ANN")
        self.tabWidget.addTab(self.gprTab, "GPR")

        # Build the widget
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  DENSITY ANALYSIS TAB  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

# Set up the regression selection pane
class DensityPane(QtWidgets.QWidget):

    # Initialize a custom QWidget
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self)
        self.setupUI()
        self.setFixedWidth(350)
    
    # Define the layout of the custom widget
    def setupUI(self):

        # Create a layout for the widget
        self.layout = QtWidgets.QVBoxLayout()

        # Create a header to top the pane
        self.header = QtWidgets.QTextEdit()
        self.header.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Analyze Forecast Density</strong></br>
                                    <p style="margin:0; font-size:14px;">Discover trends in forecasts by constructing forecast PDFs and CDFs. Store forecast density predictions and plots.</p>
                                    </div>""")
        self.header.setReadOnly(True)
        self.header.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.header.setMaximumHeight(90)
        self.layout.addWidget(self.header)

        # Table to display selected forecasts
        self.selectedFcstLabel = QtWidgets.QLabel("Selected Forecasts")
        self.selectedFcstInfo = QtWidgets.QLabel()
        self.selectedFcstInfo.setPixmap(QtGui.QPixmap(os.path.abspath("Resources/Fonts_Icons_Images/infoHover.png")).scaled(30,30, QtCore.Qt.KeepAspectRatio))
        self.selectedFcstInfo.setToolTip('<html><head/><body><p>Select forecasts to analyze and choose Run Analysis</p></body></html>')
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.selectedFcstInfo)
        hlayout.addWidget(self.selectedFcstLabel)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(400,40,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.layout.addLayout(hlayout)
        label = QtWidgets.QLabel("Equation")
        self.forecastEquationSelect = QtWidgets.QComboBox()
        hlayout=QtWidgets.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addWidget(self.forecastEquationSelect)
        self.layout.addLayout(hlayout)
        self.selectedFcstTable = CustomTableView(self, rowLock=True, cols=2, headers=['FcstID','Forecast'])
        self.selectedFcstTable.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.selectedFcstTable)

        # Bandwidth selection
        bwidthlabel = QtWidgets.QLabel("Bandwidth:")
        self.bwidthEdit = QtWidgets.QLineEdit()
        self.bwidthEdit.setText("AUTO")
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(bwidthlabel)
        hlayout.addWidget(self.bwidthEdit)
        self.layout.addLayout(hlayout)

        # Buttons to run and clear the density estimation list
        self.runButton = QtWidgets.QPushButton("Run Analysis")
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.runButton)
        self.layout.addLayout(hlayout)

        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Plain)
        self.layout.addWidget(hline)

        # Define the output options

        self.showExceedanceButton = QtWidgets.QPushButton("Exceedance Table")
        self.clearPlotButton = QtWidgets.QPushButton("Clear Plots")
        self.clearPlotButton.setEnabled(False)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.showExceedanceButton)
        hlayout.addWidget(self.clearPlotButton)
        self.layout.addLayout(hlayout)


        # Build the widget
        self.setLayout(self.layout)

"""
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||  WINDOW  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
"""

#///////////////////////// DEFINE THE GUI ///////////////////////////////////////////////
#//     Here we actually layout the GUI, element by element. 

class UI_MainWindow(object):
    
    def setupUi(self, MainWindow):

        #///////////// Set up the window geometry /////////////////
        MainWindow.resize(1200, 750)
        MainWindow.setMinimumSize(QtCore.QSize(900, 750))
        MainWindow.setWindowTitle("PyForecast v2.0")

        #///////////// Set up the menus ///////////////////////////
        # Initiate a menu widget
        self.menu = self.menuBar()

        # Create a File Menu and add the File menu buttons
        self.fileMenu = self.menu.addMenu("File")
        self.newAction = QtWidgets.QAction('New Forecast', MainWindow)
        self.newAction.setShortcut("Ctrl+N")
        self.saveAction = QtWidgets.QAction('Save Forecast', MainWindow)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAsAction = QtWidgets.QAction('Save Forecast As...', MainWindow)
        self.openAction = QtWidgets.QAction('Open Forecast', MainWindow)
        self.openAction.setShortcut("Ctrl+O")
        self.addLoaderAction = QtWidgets.QAction("Edit Dataloaders",MainWindow)
        self.setCustomDatetimeAction = QtWidgets.QAction('Set custom datetime', MainWindow)
        #self.blueThemeAction = QtWidgets.QAction("Blue / Gray")
        #self.yellowThemeAction = QtWidgets.QAction("Yellow / Black")
        # self.ConnectAction = QtWidgets.QAction('Connect to HDB', MainWindow) <- May be added later
        # self.ExportFcstAction = QtWidgets.QAction('Export Forecast to Spreadsheet', MainWindow) <- May be added later
        self.exitAction = QtWidgets.QAction('Exit PyForecast', MainWindow)
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.addLoaderAction)
        #self.fileMenu.addSeparator()
        #self.editThemeMenu = self.fileMenu.addMenu("Change Color Theme")
        #self.editThemeMenu.addAction(self.blueThemeAction)
        #self.editThemeMenu.addAction(self.yellowThemeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.setCustomDatetimeAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        # Create an About Menu and add the About menu buttons
        self.aboutMenu = self.menu.addMenu("About")
        self.docAction = QtWidgets.QAction('Documentation', MainWindow)
        self.versionAction = QtWidgets.QAction('Version Info',MainWindow)
        self.aboutMenu.addAction(self.docAction)
        self.aboutMenu.addAction(self.versionAction)

        # Add the menubar to the window
        MainWindow.setMenuBar(self.menu)

        #///////////// Set up the Main Window layout ///////////////////////////
        # The Tab Widget will be the central widget of the application
        self.tabWidget = QtWidgets.QTabWidget(MainWindow)

        # There are 5 tabs in the application
        self.summaryTab = QtWidgets.QWidget() # The container for the Summary Tab
        self.stationsTab = QtWidgets.QWidget() # The container for the Stations Tab
        self.dataTab = QtWidgets.QWidget() # The container for the Data Tab
        self.fcstOptionsTab = QtWidgets.QWidget() # The container for the Forecast Options Tab
        self.regressionTab = QtWidgets.QWidget() # The container for the Regression Tab
        self.densityAnalysisTab = QtWidgets.QWidget() # The container for the Density Tab

        #///////////// Set up the Stations Tab /////////////////////////////////
        #// The Stations Tab is divided into 2 main elements: The webmap station selector,
        #// and the selected stations pane.

        # Set up the layout for the tab
        self.stationsTab.layout = QtWidgets.QHBoxLayout(self)

        # Add a horizontal splitter to divide the map from the station information pane
        self.stationsTab.splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.stationsTab.mapPane = QtWebEngineWidgets.QWebEngineView(self)
        self.stationsTab.mapPane.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.stationsTab.page = WebMap(self)
        self.stationsTab.mapPane.setPage(self.stationsTab.page)
        self.stationsTab.page.java_msg_signal.connect(self.onNewData)
        self.stationsTab.stationInfoPane = StationInfoPane(self)
        self.stationsTab.splitter1.addWidget(self.stationsTab.mapPane)
        self.stationsTab.splitter1.addWidget(self.stationsTab.stationInfoPane)

        # Lay out the tab
        self.stationsTab.layout.addWidget(self.stationsTab.splitter1)
        self.stationsTab.setLayout(self.stationsTab.layout)

        # Add the tab to the tabwidget
        self.tabWidget.addTab(self.stationsTab, "Stations")

        #///////////// Set up the Data Tab /////////////////////////////////
        #// The Data Tab id divided into 3 main elements. The data options 
        #// pane allows users to specify Period of record information, as well
        #// as specify alternate sources for data. The table displays the curent
        #// daily data, and the plot window plots the data over the POR

        # Set up the layout for the tab
        self.dataTab.layout = QtWidgets.QHBoxLayout(self)

        # Add a horizontal splitter to divide the data options pane from the data table
        self.dataTab.splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.dataTab.dataOptions = DataOptionsPane(self)
        self.dataTab.dataOptions.setMinimumWidth(280)
        self.dataTab.dataOptions.setMaximumWidth(280)
        self.dataTab.dataTable = CustomTableView(self, colLock=True, cols=0, rows=0, menuFunctions=['COPY','OPEN','DELETECOL'], readOnly = False)
        self.dataTab.dataTable.setWordWrap(True)
        self.dataTab.splitter1.addWidget(self.dataTab.dataOptions)
        self.dataTab.splitter1.addWidget(self.dataTab.dataTable)

        # Add a vertical splitter to divide the table from the plots
        self.dataTab.splitter2 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.dataTab.plots = PlotCanvas_1Plot(self)
        self.dataTab.splitter2.addWidget(self.dataTab.splitter1)
        self.dataTab.splitter2.addWidget(self.dataTab.plots)
        self.dataTab.dataNav = NavigationToolbar(self.dataTab.plots, self.dataTab)
        self.dataTab.splitter2.addWidget(self.dataTab.dataNav)

        # Finish the tab
        self.dataTab.layout.addWidget(self.dataTab.splitter2)
        self.dataTab.setLayout(self.dataTab.layout)
        self.tabWidget.addTab(self.dataTab, "Data")

        #///////////// Set up the Forecast Options Tab /////////////////////////////////
        #// The Forecast options tab is divided into 3 sections. The Options section
        #// allows users to specify the options used to create predictors and equations.
        #// The table shows the transformed predictors. The Correlations plot 
        #// shows correlations between 2 variables in the transform plot

        # Set up the layout of the Tab
        
        self.fcstOptionsTab.layout = QtWidgets.QHBoxLayout()

        # Add a horizontal splitter to split the table from the plots
        self.fcstOptionsTab.splitter2 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.fcstOptionsTab.dualTreeView = FcstOptionsTrees(self)
        self.fcstOptionsTab.splitter2.addWidget(self.fcstOptionsTab.dualTreeView)

        # Add a vertical splitter to split the tree from the plots - place tree in plots
        self.fcstOptionsTab.splitter3 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.fcstOptionsTab.plotsPane = plotsPane()
        self.fcstOptionsTab.splitter3.addWidget(self.fcstOptionsTab.splitter2)
        self.fcstOptionsTab.splitter3.addWidget(self.fcstOptionsTab.plotsPane)

        # Add a horizontal splitter to split the options pane from the tree and plots - place tree & plots in options
        self.fcstOptionsTab.splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.fcstOptionsTab.optionsPane = FcstOptionsPane(self)
        self.fcstOptionsTab.splitter1.addWidget(self.fcstOptionsTab.optionsPane)
        self.fcstOptionsTab.splitter1.addWidget(self.fcstOptionsTab.splitter3)

        # Lay out the tab - place the options widget
        self.fcstOptionsTab.layout.addWidget(self.fcstOptionsTab.splitter1)

        self.fcstOptionsTab.setLayout(self.fcstOptionsTab.layout)
        self.tabWidget.addTab(self.fcstOptionsTab, "Forecast Options")

        #///////////// Set up the Regressions Tab /////////////////////////////////
        #// The Regressions tab is divided into 2 main sections with 1 subsection.
        #// The Plot and forecast information section shows the output of the 
        #// regression models (both a plot and an equation), and the regression
        #// selection pane allows the user to choose regression types to run.

        # Set up the layou of the tab
        self.regressionTab.layout = QtWidgets.QHBoxLayout()
        self.regressionTab.layout2 = QtWidgets.QVBoxLayout()

        # Add a vertical splitter to split the plots from the options pane
        self.regressionTab.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.regressionTab.plots = PlotCanvas_3Plot(self)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.regressionTab.plots)
        widget1 = QtWidgets.QWidget()
        layout1 = QtWidgets.QHBoxLayout()
        self.regressionTab.toggleButton = toggleButton("  Toggle Cross-Validation  ")
        layout1.addWidget(self.regressionTab.toggleButton)
        layout1.setAlignment(QtCore.Qt.AlignLeft)
        widget1.setLayout(layout1)
        splitter.addWidget(widget1)
        self.regressionTab.equationBox = QtWidgets.QPlainTextEdit()
        self.regressionTab.equationBox.setReadOnly(True)
        splitter.addWidget(self.regressionTab.equationBox)
        layout.addWidget(splitter)
        widget.setLayout(layout)
        
        self.regressionTab.regrSelectPane = RegressionSelectionPane(self)
        self.regressionTab.regrSelectPane.setMinimumWidth(430)
        self.regressionTab.splitter.addWidget(widget)
        self.regressionTab.splitter.addWidget(self.regressionTab.regrSelectPane)

        # Lay out the tab
        self.regressionTab.layout.addWidget(self.regressionTab.splitter)
        self.regressionTab.setLayout(self.regressionTab.layout)
        self.tabWidget.addTab(self.regressionTab, "Regression")

        #/////////// Set up the Summary Tab ////////////////////////////////////
        #// The Summary tab had 3 main elements: The forecast selection tree,
        #// the forecast information window, and the forecast plot window.

        # Set up a layout for the tab
        self.summaryTab.layout = QtWidgets.QHBoxLayout(self)

        # Add a horizontal splitter to divide the forecast selection pane from the plots
        self.summaryTab.splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.summaryTab.fcstSelectionPane = QtWidgets.QWidget()
        self.summaryTab.fcstSelectionPane.layout = QtWidgets.QVBoxLayout()
        self.summaryTab.fcstSelectionPane.header = QtWidgets.QTextEdit()
        self.summaryTab.fcstSelectionPane.header.setHtml("""<div style="font-family:Trebuchet MS"><strong style="margin:0; font-size:20px">Select Forecast</strong></br>
                                    <p style="margin:0; font-size:14px;">Use the list to select a forecast to view from this file.</p>
                                    </div>""")
        self.summaryTab.fcstSelectionPane.header.setReadOnly(True)
        self.summaryTab.fcstSelectionPane.header.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.summaryTab.fcstSelectionPane.header.setMaximumHeight(90)

        self.summaryTab.fcstTree = CustomTreeView(self, menuFunctions=["GENCURRENT","DELETE"], dragFrom=False, dropTo=False)
        self.summaryTab.fcstTree.setFrameStyle(QtWidgets.QFrame.NoFrame)

        self.summaryTab.fcstSelectionPane.layout.addWidget(self.summaryTab.fcstSelectionPane.header)
        self.summaryTab.fcstSelectionPane.layout.addWidget(self.summaryTab.fcstTree)
        self.summaryTab.fcstSelectionPane.setLayout(self.summaryTab.fcstSelectionPane.layout)

        self.summaryTab.plots = PlotCanvas_3Plot(self)
        self.summaryTab.splitter1.addWidget(self.summaryTab.fcstSelectionPane)
        self.summaryTab.splitter1.addWidget(self.summaryTab.plots)

        # Add a vertical splitter to dive the horizontal splitter from the forecast information pane
        self.summaryTab.splitter2 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.summaryTab.fcstInfoPane = FcstInfoPane(self)
        self.summaryTab.splitter2.addWidget(self.summaryTab.splitter1)
        self.summaryTab.splitter2.addWidget(self.summaryTab.fcstInfoPane)

        # Lay out the tab
        self.summaryTab.layout.addWidget(self.summaryTab.splitter2)
        self.summaryTab.setLayout(self.summaryTab.layout)

        # Add the tab to the tabWidget
        self.tabWidget.addTab(self.summaryTab, "Forecast")

        #///////////// Set up the Density Estimation Tab /////////////////////////////////
        #// The Density Estimation Tab allows users to visualize the distribution of forecasts 
        #// from a particular month or from multiple months. 

        # Set the layout for the tab
        self.densityAnalysisTab.layout = QtWidgets.QHBoxLayout()

        # Add a vertical spliiter to divide the options pane from the plots
        self.densityAnalysisTab.splitter = QtWidgets.QSplitter()
        self.densityAnalysisTab.densityPane = DensityPane(self)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.densityAnalysisTab.plots = PlotCanvas_2Plot(self)
        layout.addWidget(self.densityAnalysisTab.plots )
        hlayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("10%:")
        self.densityAnalysisTab.pct10Edit = QtWidgets.QLineEdit()
        hlayout.addWidget(label)
        hlayout.addWidget(self.densityAnalysisTab.pct10Edit)
        label = QtWidgets.QLabel("30%:")
        self.densityAnalysisTab.pct30Edit = QtWidgets.QLineEdit()
        hlayout.addWidget(label)
        hlayout.addWidget(self.densityAnalysisTab.pct30Edit)
        label = QtWidgets.QLabel("50%:")
        self.densityAnalysisTab.pct50Edit = QtWidgets.QLineEdit()
        hlayout.addWidget(label)
        hlayout.addWidget(self.densityAnalysisTab.pct50Edit)
        label = QtWidgets.QLabel("70%:")
        self.densityAnalysisTab.pct70Edit = QtWidgets.QLineEdit()
        hlayout.addWidget(label)
        hlayout.addWidget(self.densityAnalysisTab.pct70Edit)
        label = QtWidgets.QLabel("90%:")
        self.densityAnalysisTab.pct90Edit = QtWidgets.QLineEdit()
        hlayout.addWidget(label)
        hlayout.addWidget(self.densityAnalysisTab.pct90Edit)
        layout.addLayout(hlayout)
        widget.setLayout(layout)
        self.densityAnalysisTab.splitter.addWidget(self.densityAnalysisTab.densityPane)
        self.densityAnalysisTab.splitter.addWidget(widget)

        # Lay out the tab
        self.densityAnalysisTab.layout.addWidget(self.densityAnalysisTab.splitter)
        self.densityAnalysisTab.setLayout(self.densityAnalysisTab.layout)
        self.tabWidget.addTab(self.densityAnalysisTab, "Density Analysis")

        #//////////// Finish GUI Layout ////////////////////////////////////////
        MainWindow.setCentralWidget(self.tabWidget)

        
    def onNewData(self, data):
        print(data)