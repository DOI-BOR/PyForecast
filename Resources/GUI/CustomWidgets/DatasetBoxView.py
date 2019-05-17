"""
Script Name:    DatasetBoxView.py
Script Author:  Kevin Foley

Description:    This widget consists of a QListView/QAbstractItemModel 
                that displays entries about datasets to be used in the 
                FlowCast application.
"""

from PyQt5 import QtWidgets, QtCore, QtGui


class DatasetBoxView(QtWidgets.QListWidget):
    """
    This sub-class of the QListWidget creates a custom view that displays datasets 
    in the dataset search 
    """
    
    removeSignal = QtCore.pyqtSignal(int)
    addSignal = QtCore.pyqtSignal(int)

    
    def __init__(self, parent=None, searchBoxView = False, editContextMenuItem = False, ForecastItem = False):
        """
        Initialize a listwidget 
        """
        QtWidgets.QListWidget.__init__(self)
        self.searchBoxView = searchBoxView
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
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

    def setContextMenu(self, options=[]):
        """
        Sets the context menu to have the options specified in the options parameter
        """
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        if "remove" in options:
            self.removeAction = QtWidgets.QAction("Remove Dataset")
            self.addAction(self.removeAction)
            self.removeAction.triggered.connect(self.removeCurrentDataset)
        
        if 'edit' in options:
            self.editAction = QtWidgets.QAction("Edit Dataset")
            self.addAction(self.editAction)
            
        
        return

    
    def updateAddedStatus(self, internalID, status='removed'):
        """
        This function searches the dataset list for the specified 'internalID' and 
        reverts the dataset item's appearance back to the original, non-selected form.
        """
        if status == 'added':
            for item in [self.item(i) for i in range(self.count())]:
                if item.dataset.name == internalID:
                    html = """<b style="color:#5fd13c; font-size:14px">{0}</b><br>
                        <b>ID: </b>{1}<br>
                        <b>Type: </b>{2}<br>
                        <b>Parameter: </b>{3}
                        """.format('&#10004; ' + item.dataset['DatasetName'], item.dataset['DatasetExternalID'], item.dataset['DatasetAgency'] + ' ' + item.dataset['DatasetType'], item.dataset['DatasetParameter'])
                    item.textbox.setText(html) 
                    return
        else:
            for item in [self.item(i) for i in range(self.count())]:
                if item.dataset.name == internalID:
                    html = """<b style="color:#0a85cc; font-size:14px">{0}</b><br>
                        <b>ID: </b>{1}<br>
                        <b>Type: </b>{2}<br>
                        <b>Parameter: </b>{3}
                        """.format(item.dataset['DatasetName'], item.dataset['DatasetExternalID'], item.dataset['DatasetAgency'] + ' ' + item.dataset['DatasetType'], item.dataset['DatasetParameter'])
                    item.textbox.setText(html) 
                    return
        return

    def removeCurrentDataset(self):
        """
        """
        idx = self.currentRow()
        if idx == -1:
            return
        try:
            datasetID = self.item(idx).dataset.name
        except:
            datasetID = self.item(idx).dataset
        self.takeItem(idx)
        self.removeSignal.emit(datasetID)

        return

    def siteAdded(self, datasetRow, textbox):
        """
        This function is called when a site is from the search list is added to the
        selected datasets list. It changes the color of the site to green in order to 
        indicate that it is selected. 
        """
        
        
        html = textbox.text()
        if '&#10004' in html:
            return
        index = html.index("#")
        color = html[index:index+7]
        html = html.replace(color, '#5fd13c')
        index = html.index('>')
        index2 = html.index('</')
        name = html[index+1:index2]
        html = html.replace(name, '&#10004; ' + name)
        textbox.setText(html)
        self.addSignal.emit(datasetRow.name)

        return


    def addAbstractEntry(self, dictionary):
        """
        dictionary of form:
            {   "Title":string,
                "subtitle1": string,
                "subtitle2": string,
                "subtitle3": string }
        """

        if not set(['Title', 'subtitle1', 'subtitle2', 'subtitle3']).issubset(set(dictionary.keys())):
            return

        for key in dictionary.keys():
            if not isinstance(dictionary[key], str):
                dictionary[key] = str(dictionary[key])

        html = """<b style="color:#0a85cc; font-size:14px">{0}</b><br>
        {1}<br>
        {2}<br>
        {3}
        """.format(dictionary['Title'], dictionary['subtitle1'], dictionary['subtitle2'], dictionary['subtitle3'])


        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        item = QtWidgets.QListWidgetItem()
        item.textbox = QtWidgets.QLabel(html)
        item.textbox.setTextFormat(QtCore.Qt.RichText)
        
        layout.addWidget(item.textbox)
        widget.setLayout(layout)

        item.dataset = dictionary
        item.setSizeHint(QtCore.QSize(0,105))
        self.addItem(item)
        self.setItemWidget(item, widget)


        return "Good"


    def addEntry(self, datasetRow):
        """
        Keyword Arguments:
        datasetRow -- Information about a single dataset. e.g. ['TR32EE','Forest Creek','322','NRCS SNOTEL Station','Snow Water Equivalent', 'Inches', 'Sample','NRCS Loader']
        """
       
        html = """<b style="color:#0a85cc; font-size:14px">{0}</b><br>
        <b>ID: </b>{1}<br>
        <b>Type: </b>{2}<br>
        <b>Parameter: </b>{3}<br>
        <i style="font-size:10px; color:#4c4c4c">{4}</i>
        """.format(datasetRow['DatasetName'], datasetRow['DatasetExternalID'], datasetRow['DatasetAgency'] + ' ' + datasetRow['DatasetType'], datasetRow['DatasetParameter'], datasetRow.name)
        
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        item = QtWidgets.QListWidgetItem()
        item.textbox = QtWidgets.QLabel(html)
        item.textbox.setTextFormat(QtCore.Qt.RichText)
        button = QtWidgets.QPushButton("Add Dataset")
        
        layout.addWidget(item.textbox)
        if self.searchBoxView:
            layout.addWidget(button)
        widget.setLayout(layout)

        
        item.dataset = datasetRow
        item.setSizeHint(QtCore.QSize(0,105))
        if self.searchBoxView:
            item.setSizeHint(QtCore.QSize(0,125))
        self.addItem(item)
        self.setItemWidget(item, widget)

        button.pressed.connect(lambda x=datasetRow: self.siteAdded(x, item.textbox))

        return




# Test implementation
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    widg = DatasetBoxView(searchBoxView=True)
    window.setCentralWidget(widg)
    window.show()
    sys.exit(app.exec_())