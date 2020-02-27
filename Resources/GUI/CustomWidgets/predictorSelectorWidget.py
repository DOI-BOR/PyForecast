"""
Script:         predictorSelectorWidget.py

Description:    This widget appears on the Statistical Models Tab.
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np

class predictorGridModel(QtCore.QAbstractItemModel):
    """
    """

    def __init__(self, parent = None):

        # Initialize the itemmodel
        QtCore.QAbstractItemModel.__init__(self)

        return


    def loadDataIntoModel(self):
        """
        Loads the model data defined in the QTableView
        definition into the model.
        """

        # Initialize a model index array
        self.indexArray = np.array([])

        # Sort the model data by predictor groups
        sortIndex = np.argsort(self.parent.modelData["PredictorGroupMapping"])
        self.parent.modelData["PredictorGroupMapping"] = [self.parent.modelData["PredictorGroupMapping"][i] for i in sortIndex]
        self.parent.modelData["PredictorPool"] = [self.parent.modelData["PredictorPool"][i] for i in sortIndex]
        self.parent.modelData["PredictorForceFlag"] = [self.parent.modelData["PredictorForceFlag"][i] for i in sortIndex]
        self.parent.modelData["PredictorMethods"] = [self.parent.modelData["PredictorMethods"][i] for i in sortIndex]

        # Iterate over the product of the predictor groups, and methods
        # to create a model index for the widget
        for i, predictorMapping in enumerate(self.parent.modelData["PredictorGroupMapping"]):

            # Create a model index
            self.indexArray.append(self.createIndex(0, i))

        return


    def insertColumn(self, column, parent):
        """
        Inserts a single column before the given column in 
        the child items of the parent specified.
        """

        return


    def removeColumn(self, column, parent):
        """
        Removes the given column from the child 
        items of the parent specified.
        """

        return

    
    def index(self, row, columm, parent):
        """
        Returns the index of the item in the model specified 
        by the given row, column and parent index.
        """

        return

    def parent(self, index):
        """
        Returns the parent of the model item with the given index. 
        If the item has no parent, an invalid QModelIndex is returned.
        """

        return self.parent
    
    def rowCount(self, parent):
        """
        Returns the number of rows under the given parent. When the 
        parent is valid it means that rowCount is returning the number 
        of children of parent.
        """

        return

    def columnCount(self, parent):
        """
        Returns the number of cols under the given parent. When the 
        parent is valid it means that columnCount is returning the number 
        of children of parent.
        """

        return


    def data(self, index, role = QtCore.Qt.DisplayRole):
        """
        Returns the data stored under the given role for the 
        item referred to by the index.
        """


        return

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        """
        Sets the role data for the item at index to value.
        Returns true if successful; otherwise returns false.
        """

        return


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        """
        Returns the data for the given role and section in 
        the header with the specified orientation.
        """

        return


    def flags(self, index):
        """
        Returns the item flags for the given index.
        """

        return


    def getInfo(self, column):
        """
        Gets all the information about the predictorGroup/method
        located at column
        """

        # 

        return


class predictorGridStyleDelegate(QtWidgets.QStyledItemDelegate):
    """
    """

    def __init__(self, parent = None):

        # Initialize the itemdelagate
        QtWidgets.QStyledItemDelegate.__init__(self, parent)

        return


    def paint(self, painter, option, index):
        """
        """

        return


    def sizeHint(self, option, index):
        """
        """


        return

    
    def displayText(self, value, locale):
        """
        """

        return

    
    def createEditor(self, parent, option, index):
        """
        """

        return


    def setModelData(self, editor, model, index):
        """
        """


        return

    def setEditorData(self, editor, index):
        """
        """

        return




class predictorGrid(QtWidgets.QTableView):
    """
    The underlaying table housing the predictor matrix
    """

    def __init__(self, parent=None):

        # Initialze a QTableView
        QtWidgets.QTableView.__init__(self)

        # Set the display properties of the tableview
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)        
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)  

        # Set the custom item delegate
        #self.delegate = predictorGridStyleDelegate(self)
        self.setItemDelegate(self.delegate)

        # Set the selection behaviour
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Load the model without any data to start
        self.initModel(model = None)

        return
    
    def processModelIntoStrings(self):
        """
        Reads the current itemmodel and returns
        the NextFlow formatted model run list of
        strings
        """

        # Initialize the lists
        PredictorPool = []
        PredictorForceFlags = []
        PredictorPeriods = []
        PredictorMethods = []

        # Iterate over the model's predictor groups and append to the lists
        for predictorGroup in self.modelData:
            





        return PredictorPool, PredictorForceFlags, PredictorPeriods, PredictorMethods
    
    def initModel(self, model = None):
        """
        Load in the model defined by 'model'. Otherwise,
        load an empty model
        
        'model' is a dict containing the 6 columns from the 
        modelRunsTable: "PredictorGroups", "PredictorGroupMapping", 
        "PredictorPool", "PredictorForceFlag", "PredictorPeriods", 
        "PredictorMethods"

        """

        # If the model is None, initialize an empty model
        if not model:
            
            self.modelData = {
                "PredictorGroups": [],
                "PredictorGroupMapping": [],
                "PredictorPool": [],
                "PredictorForceFlag": [],
                "PredictorPeriods": [],
                "PredictorMethods": []
            }

        # Otherwise, load the provided model
        else:

            self.modelData = model

        # Load the model into the QTableView's model
        self.model().loadDataIntoModel()

    
    def paintEvent(self, event):
        """
        """
        





# DEBUG
if __name__ == '__main__':

    import pandas as pd
    import numpy as np
    from datetime import datetime
    import isodate
    import re

    

