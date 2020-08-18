"""
Script Name:    DatasetList_HTML_Formatted.py
Author:         Kevin Foley

Description:    This file contains the class definition for the
                dataset list that is used on the datasets tab
                and in other places in the PyForecast software.
"""

# Import Libraries
from PyQt5 import QtWidgets, QtCore, QtGui
import pandas as pd
import os
import sys
import re

# Defaults
DEFAULT_HTML_FORMAT = """
<b style="color:#007396; font-size:14px">${DatasetName}</b><br>
    <b>ID: </b>${DatasetExternalID}<br>
    <b>Type: </b>${DatasetAgency} ${DatasetType}<br>
    <b>Parameter: </b>${DatasetParameter}
"""

DEFAULT_HTML_ICON_FORMAT = """
<table>
    <tr>
        <td style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"><img src="{0}"></th>
        <td align="left"><strong style="color:#007396; font-size:14px">${DatasetName}</strong><br>
                <strong>ID: </strong>${DatasetExternalID}<br>
                <strong>Type: </strong>${DatasetAgency} ${DatasetType}<br>
                <strong>Parameter: </strong>${DatasetParameter}</th>
    </tr>
</table>
"""

datasetIcons = {
    "streamflow":       os.path.abspath("resources/graphicalResources/icons/directions_boat-24px.svg"),
    "inflow":           os.path.abspath("resources/graphicalResources/icons/waves-24px.svg"),
    "snow":             os.path.abspath("resources/graphicalResources/icons/ac_unit-24px.svg"),
    "temperature":      os.path.abspath("resources/graphicalResources/icons/temperature_fahrenheit-24px.svg"),
    "precipitation":    os.path.abspath("resources/graphicalResources/icons/weather_pouring-24px.svg"),
    "index":            os.path.abspath("resources/graphicalResources/icons/radio_tower-24px.svg"),
    "soil":             os.path.abspath("resources/graphicalResources/icons/sprout-24px.svg"),
}

empty_dataset_list = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                'DatasetParameterCode',     # e.g. avgt
                'DatasetUnits',             # e.g. CFS
                'DatasetDefaultResampling', # e.g. average 
                'DatasetDataloader',        # e.g. RCC_ACIS
                'DatasetHUC8',              # e.g. 10030104
                'DatasetLatitude',          # e.g. 44.352
                'DatasetLongitude',         # e.g. -112.324
                'DatasetElevation',         # e.g. 3133 (in ft)
                'DatasetPORStart',          # e.g. 1/24/1993
                'DatasetPOREnd',            # e.g. 1/22/2019\
                'DatasetCompositeEquation', # e.g. C/100121,102331,504423/1.0,0.5,4.3/0,0,5
                'DatasetImportFileName',    # e.g. 'C://Users//JoeDow//Dataset.CSV'
                'DatasetAdditionalOptions'
            ]
        ) 

class DatasetList_HTML_Formatted(QtWidgets.QListWidget):
    """
    This subclass of the QListWidget displays dataset from the PyForecast DatasetTable
    using a user_formatted HTML string. It also includes context menu functionality.
    """

    buttonPressSignal = QtCore.pyqtSignal(int)
    updateSignalToExternal = QtCore.pyqtSignal(pd.DataFrame)

    def __init__(self, parent=None, datasetTable = empty_dataset_list, HTML_formatting = DEFAULT_HTML_ICON_FORMAT, buttonText = None, useIcon = True, addButtons = True, objectName = None):
        """
        arguments:
            datasetTable =
            HTML_formatting = 
            buttonText = 
        """
        QtWidgets.QListWidget.__init__(self, objectName = objectName)

        # Create a reference to the parent, as well as to the datasetTable
        self.datasetTable = datasetTable
        self.parent = parent
        self.HTML_formatting = HTML_formatting if HTML_formatting != "" else DEFAULT_HTML_FORMAT
        self.buttonText = buttonText
        self.useIcon = useIcon
        self.buttonList = []
        self.addButtons = addButtons

        # Set the widget configuration
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.verticalScrollBar().setSingleStep(15)

        # Construct the list
        self.refreshDatasetList()

        return

    def setDatasetTable(self, datasetTable = None):
        """
        Sets the datasetTable for the list.
        """
    
        self.datasetTable = datasetTable
        self.refreshDatasetList()

        return



    def defineContextMenu(self, menuItems = None):
        """
        This function assigns a context menu to the widget. For example,
        if 'menuItems' is ['Remove Dataset', 'Save', 'Send to Excel'], the 
        function create the QActions > self.Remove_DatasetAction, self.SaveAction, 
        self.Send_to_ExcelAction
        """

        # Create a context menu
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        # Iterate over menuItems
        for item in menuItems:

            # Create a new action in the ListWidget Object
            setattr(self, item.replace(' ', '_') + 'Action', QtWidgets.QAction(item))

            # Add the action to the listwidget
            self.addAction(getattr(self, item.replace(' ', '_') + 'Action'))

        return


    def contextMenuEvent(self, event):
        """
        This function constructs a context
        menu only if the mouse if hovering 
        over a list item
        """

        # Check if there is a model index at the mouse point
        idx = self.indexAt(event.pos()).row()

        # If we're hovering over a dataset, we'll display the context menu
        if idx != -1:
            self.menu = QtWidgets.QMenu(self)
            self.menu.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.menu.addActions(self.actions())
            self.menu.popup(self.mapToGlobal(event.pos()))

        return


    def refreshDatasetList(self):
        """
        Refreshes the list of datasets to reflect the original dataframe.
        """

        # Clear the listwidget's items
        self.clear()
        self.buttonList = []

        # Iterate over datasets
        if isinstance(self.datasetTable, pd.DataFrame):
            iterator = list(self.datasetTable.iterrows())
        elif isinstance(self.datasetTable, pd.Series):
            iterator = [(0, self.datasetTable)]

        if self.datasetTable is not None:
            for i, dataset in iterator:

                # Create a new item for the widget and assign the dataset to the item's userRole
                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.UserRole, dataset)



                # set the item's text to the HTML formatted version of the dataset
                htmlString = self.substituteFormatString(item.data(QtCore.Qt.UserRole))
                svg = 'resources/graphicalResources/icons/cactus-24px.svg'
                if self.useIcon:
                    parameterName = dataset['DatasetParameter']
                    if "SNOTEL" in dataset['DatasetType'] and 'snow' in parameterName.lower():
                        svg = os.path.abspath("resources/graphicalResources/icons/terrain-24px.svg")
                    elif 'OTHER' in dataset['DatasetType']:
                        svg = os.path.abspath("resources/graphicalResources/icons/language-24px.svg")
                    else:
                        for key, value in datasetIcons.items():
                            if key in parameterName.lower():
                                svg = value

                htmlString = htmlString.format(svg)

                item.setText(htmlString)

                item.setForeground(QtGui.QBrush(QtGui.QColor(0,0,0,0)))

                # Create a widget to display the formatted text (and a button if enabled)
                layout = QtWidgets.QVBoxLayout()
                textBox = QtWidgets.QLabel(item.text())
                textBox.setTextFormat(QtCore.Qt.RichText)
                layout.addWidget(textBox)
                if dataset.name >= 900000 and self.addButtons:
                    self.buttonList.append(QtWidgets.QPushButton("Configure"))
                    self.buttonList[-1].setCheckable(True)
                    self.buttonList[-1].toggled.connect(self.findSelectedButton)
                    layout.addWidget(self.buttonList[-1])
                elif self.buttonText != None:
                    self.buttonList.append(QtWidgets.QPushButton(self.buttonText))
                    self.buttonList[-1].setCheckable(True)
                    self.buttonList[-1].toggled.connect(self.findSelectedButton)
                    layout.addWidget(self.buttonList[-1])
                else:
                    self.buttonList.append(QtWidgets.QPushButton(""))
                    self.buttonList[-1].setCheckable(True)
                widget = QtWidgets.QWidget(objectName = 'listItemWidget')
                widget.setLayout(layout)
                tooltipText = self.createToolTip(dataset)
                widget.setToolTip(tooltipText)

                # Set a displayrole for combo boxes
                itemComboBoxText = "{0}: {3} - {1} ({2})".format(dataset['DatasetExternalID'], dataset['DatasetName'], dataset['DatasetParameter'], dataset['DatasetType'])
                item.setData(QtCore.Qt.DisplayRole, itemComboBoxText)


                # Add the item to the listwidget
                item.setSizeHint(QtCore.QSize(0,widget.sizeHint().height() + 15))
                self.addItem(item)
                self.setItemWidget(item, widget)

        # Send the signal to update other objects that reference this list, passing the updated dataframe
        self.updateSignalToExternal.emit(pd.DataFrame(self.datasetTable))

        return

    def findSelectedButton(self, dummy):
        for i, button in enumerate(self.buttonList):
            if button.isChecked():
                button.setChecked(False)
                self.buttonPressSignal.emit(self.datasetTable.iloc[i].name)

        return

    def createToolTip(self, data):
        """
        Creates the tooltip text formatted into rich texh for the list item.
        The text displays the dataframe values for the item
        """

        # Initialize some text
        tooltipText = ""

        # iterate over the dataframe columns for this dataframe
        for column in data.index:

            # Get the data value and add it to the tooltip text
            val = data[column]
            if str(val) == 'nan' or str(val) == 'NaT':
                val = ''
            tooltipText += "<p style='margin:0;padding:0'><strong>{0}: </strong>{1}</br></p>".format(column, val)
        
        return tooltipText
        

    def substituteFormatString(self, datasetRow):
        """
        Substitutes the HTML format string with actual values from the dataset.
        """

        # Pattern to recognize strings like "${DatasetName}"
        pattern = r"\${\w+}"

        # Get all the fieldnames in the HTML_formatstring
        fieldNamesEscaped = re.findall(pattern, self.HTML_formatting)
        fieldNames = [name[2:-1] for name in fieldNamesEscaped]

        # Create a replacement dictionary to keep track of the escaped field name and what we are going to replace it with
        # This operation creates: {"${DatasetName}":"Gibson Reservoir", "${DatasetType}":"RESERVOIR", ...}
        replacementDict = dict([[re.escape(fieldNamesEscaped[i]), datasetRow[field]] for i, field in enumerate(fieldNames)])
        
        # Substitute the html format string
        pattern2 = re.compile('|'.join(replacementDict.keys()))
        subString = pattern2.sub(lambda m: replacementDict[re.escape(m.group(0))], self.HTML_formatting)

        return subString

    def refreshDatasetListFromExtenal(self, datasetTable):
        """
        Refreshes the datframe from an external source

        Parameters
        ----------
        self: DatasetList_HTML_Formatted
        datasetTable: dataframe
            Dataframe with which to update the list

        """

        # Update the dataset table
        self.datasetTable = copy.copy(datasetTable)

        # Trigger a table refresh
        self.refreshDatasetList()


# DEBUGGING
if __name__ == '__main__':

    datasetTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                'DatasetParameterCode',     # e.g. avgt
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

    datasetTable.loc[100101] = ['RESERVOIR','GIBR','Gibson Reservoir','USBR','Inflow','CFS', 'in', 'Average','USBR_LOADER','10030101','44.254','-109.123','3212','','','']
    datasetTable.loc[100301] = ['STREAMGAGE','WSSW','Welcome Creek','USGS','Streamflow','CFS', 'in', 'Average','USGS_LOADER','10030102','44.255','-109.273','3212','','','']
    datasetTable.loc[100805] = ['SNOTEL','633','Miscell Peak','NRCS','SWE','Inches', 'wteq', 'Sample','NRCS_LOADER','10030101','44.245','-109.1123','3212','','','']

    app = QtWidgets.QApplication(sys.argv)
    widg = DatasetList_HTML_Formatted(datasetTable=datasetTable, buttonText = 'Add Dataset')
    widg.defineContextMenu(['Add Dataset', 'Remove Dataset', 'Dummy'])
    widg.show()
    
    sys.exit(app.exec_())