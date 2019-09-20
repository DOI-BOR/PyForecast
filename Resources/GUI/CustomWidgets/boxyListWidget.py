"""
Script Name:    boxyListWidget.py
Script Author:  Kevin Foley

Description:    This widget consists of a QListView/QAbstractItemModel 
                that displays entries about datasets to be used in the 
                FlowCast application.
"""

from PyQt5 import QtWidgets, QtCore, QtGui

class boxyListWidget(QtWidgets.QListWidget):
    """
    boxyListWidget is a subclass of a ListWidget that allows you to 
    add widgets to the List. The listitem is resized on the fly to expand to the 
    widget size. 
    """

    addElementSignal = QtCore.pyqtSignal(int) # signal emitted when new list elements are added. Emits the index
    removeElementSignal = QtCore.pyqtSignal(int) # signal emitted when a list element is removed. Emits the index

    def __init__(self, parent=None):
        """
        """
        QtWidgets.QListWidget.__init__(self)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.actions = {}
        self.widgetList = []
        self.setStyleSheet("""
        QListWidget {
            border: 0px;
        }
        QListWidget::item {
            border: 1px solid #e8e8e8;
        }
        QListWidget::item:selected {
            border: 2px solid #e8e8e8;
            background-color: #d9d9d9;
        }
        QListWidget::item:hover {
            border: 2px solid #e8e8e8;
            background-color: #d9d9d9;
        }
        """)

        return

    
    def setContextMenu(self, menuItems=[]):
        """
        Sets the context menu for the list widget. menu actions are stored in
        self.actions. Access an action by writing self.actions['item name']

        """
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        for item in menuItems:
            self.actions[item] = QtWidgets.QAction(item)
            self.addAction(self.actions[item])
        
        return


    def addWidget(self, widgetToAdd = QtWidgets.QLabel(), htmlDataForTextWidget = None, data = None):
        """
        Adds the widget to the list. Also give the widget item any associated data.
        """
        item = QtWidgets.QListWidgetItem()
        item.data_ = data
        item.widget = widgetToAdd
        if item.widget == QtWidgets.QTextEdit():
            item.HTMLdata_ = htmlDataForTextWidget
            item.widget.setText(htmlDataForTextWidget)
            item.widget.setTextFormat(QtCore.Qt.RichText)
        
        self.addItem(item)
        self.setItemWidget(item, item.widget)
        self.addElementSignal.emit(self.count() - 1)

        return        

    def removeWidget(self, idx):
        """
        Removes the widget defined by the index idx 
        """
        if idx == -1:
            return
        self.takeItem(idx)
        self.removeElementSignal.emit(idx)

        return
