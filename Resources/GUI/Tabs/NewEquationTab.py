"""
Script Name:        NewEquationTab.py

Description:        'NewEquationTab.py' is a PyQt5 GUI for the NextFlow application. 
                    The GUI includes all the visual aspects of the New Forecast Tab (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""
from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui

import  sys
import  os

class NewEquationTab(QtWidgets.QWidget):
    """

    """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout()

        leftPane = QtWidgets.QWidget()
        midPane = QtWidgets.QWidget()
        rightPane = QtWidgets.QWidget()

        
