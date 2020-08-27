from PyQt5 import QtWidgets, QtCore, QtGui
from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetListHTMLFormatted

class CombinedDatasetTbl(QtWidgets.QTableWidget):
    """
    """
    def __init__(self, parent = None):

        QtWidgets.QTableWidget.__init__(self)
        self.parent = parent
        self.setColumnCount(5)
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(["", "", "Dataset", "Coef.", "Lag (days)"])
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, 20)
        self.setColumnWidth(2, 270)
        self.setColumnWidth(3, 50)
        self.setColumnWidth(4, 70)
        self.addRow(0)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        
        return

    def addRow(self, idx):
        self.setRowCount(idx+1)
        addWidg = addRemoveButton(add=True, idx=idx)
        addWidg.clicked.connect(lambda : self.addRow(self.rowCount()))
        removeWidg = addRemoveButton(add=False, idx = idx)
        removeWidg.clicked.connect(lambda : self.removeRow(removeWidg.idx) if removeWidg.idx != 0 else print("idx: {0}".format(removeWidg.idx)))
        datasetSelect = datasetComboBox(self.parent)
        coefficient = QtWidgets.QLineEdit()
        validator = QtGui.QDoubleValidator(-1000000,100000,10)
        coefficient.setValidator(validator)
        coefficient.setText("1")
        lagSelect = QtWidgets.QSpinBox()
        lagSelect.setMinimum(-365)
        lagSelect.setMaximum(0)

        self.setCellWidget(idx, 0, addWidg)
        self.setCellWidget(idx, 1, removeWidg)
        self.setCellWidget(idx, 2, datasetSelect)
        self.setCellWidget(idx, 3, coefficient)
        self.setCellWidget(idx, 4, lagSelect)

        self.horizontalHeader().setStretchLastSection(True)


        return



class datasetComboBox(QtWidgets.QComboBox):

    def __init__(self, parent = None):
        QtWidgets.QComboBox.__init__(self)
        self.parent = parent
        self.setAutoFillBackground(True)
        self.datasetList = DatasetListHTMLFormatted(self, datasetTable = self.parent.datasetTable, HTML_formatting ="", addButtons = False)
        
        self.setModel(self.datasetList.model())
        self.setView(self.datasetList)

        self.datasetList.itemActivated.connect(lambda item: self.setCurrentIndex(self.datasetList.row(item)))

        self.datasetList.itemPressed.connect(lambda x: self.setCurrentIndex(self.datasetList.row(x)))
        self.currentIndexChanged.connect(lambda x: self.hidePopup())

class addRemoveButton(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()
    def __init__(self, parent = None, add = True, idx = 0):
        QtWidgets.QLabel.__init__(self, "")
        self.setAutoFillBackground(True)
        if add:
            self.pic = QtGui.QPixmap("resources/GraphicalResources/icons/plusIcon.png")
            self.picHover = QtGui.QPixmap("resources/GraphicalResources/icons/plusIconDark.png")
        else:
            self.pic = QtGui.QPixmap("resources/GraphicalResources/icons/xIcon.png")
            self.picHover = QtGui.QPixmap("resources/GraphicalResources/icons/xIconDark.png")
        
        self.picHover = self.picHover.scaled(20,20)
        self.pic = self.pic.scaled(20,20)

        self.setPixmap(self.pic)
        self.idx = idx
        return

    def mousePressEvent(self, ev):
        self.setPixmap(self.picHover)
    def mouseReleaseEvent(self, ev):
        self.setPixmap(self.pic)
        self.clicked.emit()

if __name__ == '__main__':
    import sys
    import os

    app = QtWidgets.QApplication(sys.argv)
    widg = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    but = addRemoveButton(add = False)
    layout.addWidget(but)
    widg.setLayout(layout)
    widg.show()

    sys.exit(app.exec_())