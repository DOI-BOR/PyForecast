from PyQt5 import QtWidgets, QtCore, QtGui
import pandas as pd
import os
import sys
import numpy as np
from collections import OrderedDict
import subprocess

class ListModel(QtCore.QAbstractListModel):
    """
    """
    def __init__(self, parent=None):
        """
        """
        QtCore.QAbstractItemModel.__init__(self)

        return

    def loadDatasetIntoModel(self, dataset):
        """
        """

        self.dataset = dataset

        self.indexArray = np.array([self.createIndex(i,0) for i in range(len(self.dataset))])
        
        return

    def index(self, row, column, parent = QtCore.QModelIndex()):

        return self.indexArray[row]

    def deleteDatasetFromModel(self):
        """
        """


        return

    def rowCount(self, parent = QtCore.QModelIndex()):
        """
        """
        return len(self.dataset)


    def data(self, index, role = QtCore.Qt.DisplayRole):
        """
        """
        return QtCore.QVariant(self.dataset.iloc[index.row()]['DatasetName'])



class RichTextItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """

    def paint(self, painter, option, index):
        """
        """

        # Save the current state of the painter
        painter.save()

        # Set the delegate to default to the item's options
        self.initStyleOption(option)

        # Create a QTextDocument to hold the rich text
        doc = QtGui.QTextDocument(self)

        # Set the document's text to the item's text
        doc.setHtml(option.text)

        # Set the context
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Move the painter to the top left
        painter.translate(option.rect.topLeft())
        painter.setClipRect(option.rect.translated(-option.rect.topLeft()))

        # Paint the item
        doc.documentLayout().draw(painter, ctx)

        # Restore the state of the painter
        painter.restore()

        return

    def sizeHint(self, option, index):
        """
        """

        return 


    

class ListView(QtWidgets.QListView):
    """
    """

    def __init__(self, parent=None):
        """
        """
        QtWidgets.QListView.__init__(self)
        self.setModel(ListModel(self))

        return

if __name__ == '__main__':

    datasetTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                'DatasetUnits',             # e.g. CFS
                'DatasetDefaultResampling', # e.g. average 
                'DatasetDataloader',        # e.g. RCC_ACIS
                'DatasetHUC8',              # e.g. 10030104
                'DatasetLatitude',          # e.g. 44.352
                'DatasetLongitude',         # e.g. -112.324
                'DatasetElevation',         # e.g. 3133 (in ft)
                'DatasetPORStart',          # e.g. 1/24/1993
                'DatasetPOREnd',            # e.g. 1/22/2019
                'DatasetAdditionalOptions'
            ]
        ) 

    datasetTable.loc[100101] = ['STREAMGAGE','GIBR','Gibson Reservoir','USBR','Inflow','CFS','','','','','','','','','']
    datasetTable.loc[100301] = ['STREAMGAGE','WSSW','Welcome Creek','USBR','Inflow','CFS','','','','','','','','','']

    app = QtWidgets.QApplication(sys.argv)
    widg = ListView()
    widg.model().loadDatasetIntoModel(datasetTable)
    
    widg.show()
    
    sys.exit(app.exec_())