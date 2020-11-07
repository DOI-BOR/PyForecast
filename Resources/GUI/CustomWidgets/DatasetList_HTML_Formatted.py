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
LIST_DEFAULT_HTML_FORMAT = """
<b style="color:#007396; font-size:14px">{Text}</b><br>
"""

DATASET_DEFAULT_HTML_FORMAT = """
<b style="color:#007396; font-size:14px">${DatasetName}</b><br>
    <b>ID: </b>${DatasetExternalID}<br>
    <b>Type: </b>${DatasetAgency} ${DatasetType}<br>
    <b>Parameter: </b>${DatasetParameter}
"""

DATASET_INSTANCE_HTML_FORMAT = """
<b style="color:#007396; font-size:14px">${DatasetName}</b><br>
    <b>ID: </b>${DatasetExternalID}<br>
    <b>Type: </b>${DatasetAgency} ${DatasetType}<br>
    <b>Parameter: </b>${DatasetParameter}<br>
    <b>Instance: </b>${DatasetInstanceID}
"""

DATASET_DEFAULT_HTML_ICON_FORMAT = """
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

DATASET_INSTANCE_HTML_ICON_FORMAT = """
<table>
    <tr>
        <td style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"><img src="{0}"></th>
        <td align="left"><strong style="color:#007396; font-size:14px">${DatasetName}</strong><br>
                <strong>ID: </strong>${DatasetExternalID}<br>
                <strong>Type: </strong>${DatasetAgency} ${DatasetType}<br>
                <strong>Parameter: </strong>${DatasetParameter}</th><br>
                <b>Instance: </b>${DatasetInstanceID}
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

class ListHTMLFormatted(QtWidgets.QListWidget):
    """
    This subclass of the QListWidget displays data using a HTML string.
    """

    updateSignalToExternal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, itemList=None, HTML_formatting='default', objectName=None,
                 buttonText=None, addButtons=True):
        # todo: doc string

        # Initialize the QT list parent object
        QtWidgets.QListWidget.__init__(self, objectName=objectName)

        # Create a reference to the parent, as well as to the datasetTable
        self.itemList = itemList
        self.parent = parent

        # Set the HTML formatting
        if HTML_formatting == 'default':
            self.HTML_formatting = LIST_DEFAULT_HTML_FORMAT
        else:
            self.HTML_formatting = HTML_formatting

        # Configure the buttons
        self.buttonText = buttonText
        self.buttonList = []
        self.addButtons = addButtons

        # Set the widget configuration
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.verticalScrollBar().setSingleStep(15)

        # Construct the list
        self.refreshItemList()


    def setDatasetTable(self, itemList=None):
        """
        Sets the datasetTable for the list.
        """

        self.itemList = itemList
        self.refreshItemList()

        return

    def refreshItemList(self):
        """
        Refreshes the list of datasets to reflect the original dataframe.
        """

        # Clear the listwidget's items
        self.clear()
        self.buttonList = []

        if self.itemList is not None:
            for feature in self.itemList:

                # Create a new item for the widget and assign the dataset to the item's userRole
                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.UserRole, feature)

                # set the item's text to the HTML formatted version of the dataset
                htmlString = self.substituteFormatString(feature)

                item.setText(htmlString)
                item.setForeground(QtGui.QBrush(QtGui.QColor(0,0,0,0)))

                # Create a widget to display the formatted text (and a button if enabled)
                layout = QtWidgets.QVBoxLayout()
                textBox = QtWidgets.QLabel(item.text())
                textBox.setTextFormat(QtCore.Qt.RichText)
                layout.addWidget(textBox)
                if len(feature) >= 900000 and self.addButtons:
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

                # Add the item to the listwidget
                item.setSizeHint(QtCore.QSize(0, widget.sizeHint().height()))
                self.addItem(item)
                self.setItemWidget(item, widget)

        return

    def substituteFormatString(self, itemText):
        """
        Substitutes the HTML format string with actual values from the dataset.
        """

        subString = re.sub('{Text}', itemText, self.HTML_formatting)

        return subString

    def findSelectedButton(self, dummy):
        for i, button in enumerate(self.buttonList):
            if button.isChecked():
                button.setChecked(False)
                self.buttonPressSignal.emit(self.datasetTable.iloc[i].name)

        return

    def selectionChanged(self, *args, **kwargs):
        """
        Emits a signal with the updated items to allow other items to utilize the selected information

        """

        ### Filter the list to the selected rows ###
        # Get the selected indices
        selectedIndices = [self.row(x) for x in self.selectedItems()]

        # Get the corresponding list items
        selectedItems = [self.itemList[x] for x in selectedIndices]

        ### Emit the signal with the downselected list ###
        self.updateSignalToExternal.emit(selectedItems)


class DatasetListHTMLFormatted(QtWidgets.QListWidget):
    """
    This subclass of the QListWidget displays dataset from the PyForecast DatasetTable
    using a user_formatted HTML string. It also includes context menu functionality.
    """

    buttonPressSignal = QtCore.pyqtSignal(int)
    updateSignalToExternal = QtCore.pyqtSignal(pd.DataFrame)

    def __init__(self, parent=None, datasetTable=empty_dataset_list, HTML_formatting='default',
                 buttonText=None, useIcon=True, addButtons=True, objectName=None, itemColors=None):
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

        # Set the HTML formatting
        self.useIcon = useIcon
        if HTML_formatting == 'default':
            self.HTML_formatting = DATASET_DEFAULT_HTML_FORMAT
        elif self.useIcon:
            self.HTML_formatting = DATASET_DEFAULT_HTML_ICON_FORMAT
        else:
            self.HTML_formatting = HTML_formatting

        # Configure the buttons
        self.buttonText = buttonText
        self.buttonList = []
        self.addButtons = addButtons

        # Configure the colors
        self.itemColors = itemColors

        # Set the widget configuration
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.verticalScrollBar().setSingleStep(15)

        # Construct the list
        self.refreshDatasetList()

        return

    def setDatasetTable(self, datasetTable=None, itemColors=None):
        """
        Sets the datasetTable for the list.
        """
    
        self.datasetTable = datasetTable
        self.refreshDatasetList()
        self.itemColors = itemColors

        return


    def defineContextMenu(self, menuItems=None):
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

                # Set the item colors
                if self.itemColors is not None:
                    item.setBackground(self.itemColors[i])

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
                itemComboBoxText = "{0}: {3} - {1} ({2})".format(dataset['DatasetExternalID'], dataset['DatasetName'],
                                                                     dataset['DatasetParameter'], dataset['DatasetType'])
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

        # Create an initial dictionary to hold string replacement values
        replacementDict = {}

        # Add the index fields if necessary
        if not all([x in datasetRow for x in fieldNames]):
            # Get the missing fields
            missingFields = [x for x in fieldNames if x not in datasetRow]

            # Check that the field is available as an index
            if all([x in self.datasetTable.index.names for x in missingFields]):
                # Add the index fields into the dictionary
                for field in missingFields:
                    # Get the index into the table indices
                    indexTable = [x for x in range(0, len(self.datasetTable.index.names))
                                     if self.datasetTable.index.names[x] == field][0]

                    # Get the correct escaped field
                    indexField = [x for x in fieldNamesEscaped if field in x][0]

                    # Set it into the dictionary
                    replacementDict[re.escape(indexField)] = str(self.datasetTable.index[0][indexTable])

            else:
                raise AttributeError('Desired display field not in HTML dataset table')

        # Create a replacement dictionary to keep track of the escaped field name and what we are going to replace it with
        # This operation creates: {"${DatasetName}":"Gibson Reservoir", "${DatasetType}":"RESERVOIR", ...}
        for i, field in enumerate([x for x in fieldNames if x in datasetRow]):
            replacementDict[re.escape(fieldNamesEscaped[i])] = str(datasetRow[field])
        
        # Substitute the html format string
        pattern2 = re.compile('|'.join(replacementDict.keys()))
        subString = pattern2.sub(lambda m: replacementDict[re.escape(m.group(0))], self.HTML_formatting)

        return subString

    def refreshDatasetListFromExtenal(self, datasetTable):
        """
        Refreshes the datframe from an external source

        Parameters
        ----------
        self: DatasetListHTMLFormatted
        datasetTable: dataframe
            Dataframe with which to update the list

        """

        # Update the dataset table
        self.datasetTable = datasetTable

        # Trigger a table refresh
        self.refreshDatasetList()

    def updateColors(self):
        """
        Triggers a manual color update on the list between full list refreshes

        """

        for entry in range(0, self.count(), 1):
            self.item(entry).setBackground(self.itemColors[entry])


class DatasetListHTMLFormattedMultiple(QtWidgets.QListWidget):
    """
    This subclass of the QListWidget displays dataset from the PyForecast DatasetTable
    using a user_formatted HTML string. It also includes context menu functionality.
    """

    buttonPressSignal = QtCore.pyqtSignal(int)
    updateSignalToExternal = QtCore.pyqtSignal(pd.DataFrame)

    def __init__(self, parent=None, buttonText=None, useIcon=True, addButtons=True, objectName=None,
                 HTML_formatting='default', inputDataset=None, itemColors=None):
        """
        arguments:
            datasetTable =
            HTML_formatting =
            buttonText =
        """
        QtWidgets.QListWidget.__init__(self, objectName=objectName)

        empty_dataset_list_multiple = pd.DataFrame(
            # index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns=[
                'DatasetType',  # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',  # e.g. "GIBR" or "06025500"
                'DatasetInternalID',
                'DatasetInstanceID',  # e.g. 0, 1, 2
                'DatasetName',  # e.g. Gibson Reservoir
                'DatasetAgency',  # e.g. USGS
                'DatasetParameter',  # e.g. Temperature
                'DatasetParameterCode',  # e.g. avgt
                'DatasetUnits',  # e.g. CFS
                'DatasetDefaultResampling',  # e.g. average
                'DatasetDataloader',  # e.g. RCC_ACIS
                'DatasetHUC8',  # e.g. 10030104
                'DatasetLatitude',  # e.g. 44.352
                'DatasetLongitude',  # e.g. -112.324
                'DatasetElevation',  # e.g. 3133 (in ft)
                'DatasetPORStart',  # e.g. 1/24/1993
                'DatasetPOREnd',  # e.g. 1/22/2019\
                'DatasetCompositeEquation',  # e.g. C/100121,102331,504423/1.0,0.5,4.3/0,0,5
                'DatasetImportFileName',  # e.g. 'C://Users//JoeDow//Dataset.CSV'
                'DatasetAdditionalOptions'
            ]
        )

        # Create a reference to the parent, as well as to the datasetTable
        if inputDataset is not None:
            self.datasetTable = inputDataset
        else:
            self.datasetTable = empty_dataset_list_multiple
            self.datasetTable.set_index(['DatasetInternalID', 'DatasetInstanceID'], inplace=True)

        # Define the parent class
        self.parent = parent

        # Set whether the list will be unique
        self.unique = False

        # Setup the HTML formatting
        self.useIcon = useIcon
        if HTML_formatting == 'default':
            self.HTML_formatting = DATASET_INSTANCE_HTML_FORMAT
        elif self.useIcon:
            self.HTML_formatting = DATASET_INSTANCE_HTML_ICON_FORMAT
        else:
            self.HTML_formatting = HTML_formatting

        # Create the butten formatting
        self.buttonText = buttonText
        self.buttonList = []
        self.addButtons = addButtons

        # Set the colors for the list
        self.itemColors = itemColors

        # Set the widget configuration
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.verticalScrollBar().setSingleStep(15)

        # Construct the list
        self.refreshDatasetList()

        return

    def setDatasetTable(self, datasetTable=None, itemColors=None):
        """
        Sets the datasetTable for the list.
        """

        self.datasetTable = datasetTable
        self.itemColors = itemColors
        self.refreshDatasetList()

        return

    def defineContextMenu(self, menuItems=None):
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
            iterator = [(self.datasetTable.name, self.datasetTable)]

        row = 0
        if self.datasetTable is not None:
            for i, dataset in iterator:

                # Create a new item for the widget and assign the dataset to the item's userRole
                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.UserRole, dataset)

                # Set the item colors
                if self.itemColors is not None:
                    try:
                        item.setBackground(self.itemColors[row])
                    except:
                        pass

                # set the item's text to the HTML formatted version of the dataset
                htmlString = self.substituteFormatString(item.data(QtCore.Qt.UserRole), i[1])
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

                item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))

                # Create a widget to display the formatted text (and a button if enabled)
                layout = QtWidgets.QVBoxLayout()
                textBox = QtWidgets.QLabel(item.text())
                textBox.setTextFormat(QtCore.Qt.RichText)
                layout.addWidget(textBox)
                if dataset.name[0] >= 900000 and self.addButtons:
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
                widget = QtWidgets.QWidget(objectName='listItemWidget')
                widget.setLayout(layout)
                tooltipText = self.createToolTip(dataset)
                widget.setToolTip(tooltipText)

                # Set a displayrole for combo boxes
                itemComboBoxText = "{0}: {3} - {1} ({2}) {4}".format(dataset['DatasetExternalID'],
                                                                     dataset['DatasetName'],
                                                                     dataset['DatasetParameter'],
                                                                     dataset['DatasetType'],
                                                                     dataset.name[1])

                item.setData(QtCore.Qt.DisplayRole, itemComboBoxText)

                # Add the item to the listwidget
                item.setSizeHint(QtCore.QSize(0, widget.sizeHint().height() + 15))
                self.addItem(item)
                self.setItemWidget(item, widget)

                # Increment the row counter to get the correct coloration
                row += 1

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

    def substituteFormatString(self, datasetRow, instanceID):
        """
        Substitutes the HTML format string with actual values from the dataset.
        """

        # Pattern to recognize strings like "${DatasetName}"
        pattern = r"\${\w+}"

        # Get all the fieldnames in the HTML_formatstring
        fieldNamesEscaped = re.findall(pattern, self.HTML_formatting)
        fieldNames = [name[2:-1] for name in fieldNamesEscaped]

        # Create an initial dictionary to hold string replacement values
        replacementDict = {}
        replacementDict[re.escape([x for x in fieldNamesEscaped if 'DatasetInstanceID' in x][0])] = str(instanceID)

        # Create a replacement dictionary to keep track of the escaped field name and what we are going to replace it with
        # This operation creates: {"${DatasetName}":"Gibson Reservoir", "${DatasetType}":"RESERVOIR", ...}
        for i, field in enumerate([x for x in fieldNames if x in datasetRow]):
            replacementDict[re.escape(fieldNamesEscaped[i])] = str(datasetRow[field])

        # Substitute the html format string
        pattern2 = re.compile('|'.join(replacementDict.keys()))
        subString = pattern2.sub(lambda m: replacementDict[re.escape(m.group(0))], self.HTML_formatting)

        return subString

    def updateColors(self):
        """
        Triggers a manual color update on the list between full list refreshes

        """

        for entry in range(0, self.count(), 1):
            self.item(entry).setBackground(self.itemColors[entry])

    def refreshDatasetListFromExtenal(self, datasetTable):
        """
        Refreshes the datframe from an external source

        Parameters
        ----------
        self: DatasetListHTMLFormatted
        datasetTable: dataframe
            Dataframe with which to update the list

        """

        # Update the dataset table
        self.datasetTable = datasetTable

        # Trigger a table refresh
        self.refreshDatasetList()

    def showMultipleItemsSelected(self):
        # Clear the listwidget's items
        self.clear()
        self.buttonList = []

        if self.datasetTable is not None:
            item = QtWidgets.QListWidgetItem()

            #set the item's text to the HTML formatted version of the dataset
            htmlString = """
            <b style="color:#007396; font-size:14px">MULTIPLE PREDICTORS SELECTED</b><br>
                Settings shown below are from the first selected predictor<br>
                - Pressing <b style="color:#007396">Clear</b> will erase the settings for selected predictors<br>
                - Pressing <b style="color:#007396">Apply</b> will assign the settings for selected predictors<br>
                Plots shown are also from the first selected predictor
            """
            svg = os.path.abspath("resources/graphicalResources/icons/language-24px.svg")
            htmlString = htmlString.format(svg)
            item.setText(htmlString)
            item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))

            # Create a widget to display the formatted text (and a button if enabled)
            layout = QtWidgets.QVBoxLayout()
            textBox = QtWidgets.QLabel(item.text())
            textBox.setTextFormat(QtCore.Qt.RichText)
            layout.addWidget(textBox)

            widget = QtWidgets.QWidget(objectName='listItemWidget')
            widget.setLayout(layout)

            # Set a displayrole for combo boxes
            item.setData(QtCore.Qt.DisplayRole, htmlString)

            # Add the item to the listwidget
            item.setSizeHint(QtCore.QSize(0, widget.sizeHint().height() + 15))
            self.addItem(item)
            self.setItemWidget(item, widget)

        return


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
    widg = DatasetListHTMLFormatted(datasetTable=datasetTable, buttonText ='Add Dataset')
    widg.defineContextMenu(['Add Dataset', 'Remove Dataset', 'Dummy'])
    widg.show()
    
    sys.exit(app.exec_())