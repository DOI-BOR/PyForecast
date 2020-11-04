from PyQt5 import QtWidgets, QtCore, QtGui
from resources.GUI.CustomWidgets import DatasetList_HTML_Formatted
import os
from datetime import  datetime
import isodate
from dateutil import relativedelta

class Icons(object):

    iconDict = {
        "streamflow": os.path.abspath("resources/GraphicalResources/icons/directions_boat-24px.svg"),
        "inflow": os.path.abspath("resources/GraphicalResources/icons/waves-24px.svg"),
        "snow": os.path.abspath("resources/GraphicalResources/icons/ac_unit-24px.svg"),
        "temperature": os.path.abspath("resources/GraphicalResources/icons/temperature_fahrenheit-24px.svg"),
        "precipitation": os.path.abspath("resources/GraphicalResources/icons/weather_pouring-24px.svg"),
        "index": os.path.abspath("resources/GraphicalResources/icons/radio_tower-24px.svg"),
        "soil": os.path.abspath("resources/GraphicalResources/icons/sprout-24px.svg"),
        'snotel': os.path.abspath("resources/GraphicalResources/icons/terrain-24px.svg"),
        'other': os.path.abspath("resources/GraphicalResources/icons/language-24px.svg"),
    }

class DatasetTab_searchResultsBox(object):

    FORMAT_STRING = """
        <table border="0" width="100%">
        <tr>
            <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"><img src="{IconPath}"></td>
            <td align="left"><strong style="color:#007396; font-size:14px">{DatasetName}</strong><br>
                    <strong>ID: </strong>{DatasetExternalID}<br>
                    <strong>Type: </strong>{DatasetAgency} {DatasetType}<br>
                    <strong>Parameter: </strong>{DatasetParameter}</td>
        </tr>
        <tr>
        <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"></td>
        <td style="text-align:right; color: #8c9f9d">{DatasetID}</td>
        </tr>
        </table>
        """

    def __init__(self, parent = None):

        self.parent = parent
        self.icons = Icons()
        self.usesButtons = True
        self.buttonText = "Add Dataset"
        self.contextMenu()

        return

    def iterator(self):
        if hasattr(self.parent.parent, "keywordSearchTable"):
            return self.parent.parent.keywordSearchTable.iterrows()
        else:
            return []

    def contextMenu(self):

        return

    def ToolTip(self, dataset):
        """
        Creates the tooltip text formatted into rich texh for the list item.
        The text displays the dataframe values for the item
        """

        # Initialize some text
        tooltipText = ""

        # Get the chosen dataset from the row number

        # iterate over the dataframe columns for this dataframe
        for column in dataset.index:

            # Get the data value and add it to the tooltip text
            val = dataset[column]
            if str(val) == 'nan' or str(val) == 'NaT':
                val = ''
            tooltipText += "<p style='margin:0;padding:0'><strong>{0}: </strong>{1}</br></p>".format(column, val)

        return tooltipText


    def generateHTML(self, dataset):
        """
        Generates an HTML entry for the given index in the table
        """

        # SET A DEFAULT ICON
        iconPath = os.path.abspath('resources/GraphicalResources/icons/cactus-24px.svg')

        # Figure out what Icon to use
        if "SNOTEL" in dataset.DatasetType and 'snow' in dataset.DatasetParameter.lower():
            iconPath = self.icons.iconDict['snotel']
        elif 'OTHER' in dataset.DatasetType:
            iconPath = self.icons.iconDict['other']
        else:
            for key, value in self.icons.iconDict.items():
                if key in dataset.DatasetParameter.lower():
                    iconPath = value

        html = self.FORMAT_STRING.format(
            IconPath=iconPath,
            DatasetName=dataset.DatasetName,
            DatasetExternalID=dataset.DatasetExternalID,
            DatasetAgency=dataset.DatasetAgency,
            DatasetType=dataset.DatasetType,
            DatasetParameter=dataset.DatasetParameter,
            DatasetID=dataset.name
        )

        return html


class DatasetTab_SelectedDatasetList(object):

    FORMAT_STRING = """
    <table border="0" width="100%">
    <tr>
        <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"><img src="{IconPath}"></td>
        <td align="left"><strong style="color:#007396; font-size:14px">{DatasetName}</strong><br>
                <strong>ID: </strong>{DatasetExternalID}<br>
                <strong>Type: </strong>{DatasetAgency} {DatasetType}<br>
                <strong>Parameter: </strong>{DatasetParameter}</td>
    </tr>
    <tr>
    <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"></td>
    <td style="text-align:right; color: #8c9f9d">{DatasetID}</td>
    </tr>
    </table>
    """

    def __init__(self, parent = None):

        self.parent = parent
        self.icons = Icons()
        self.usesButtons = False
        self.buttonText = ""
        self.contextMenu()

        return

    def iterator(self):
        return self.parent.parent.datasetTable.iterrows()

    def contextMenu(self):

        # Create a context menu
        self.parent.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

        # Create Button List
        self.contextList = [
            "Remove Dataset",
            "Edit Dataset"
        ]

        # Iterate over menuItems
        for item in self.contextList:

            # Create a new action in the ListWidget Object
            setattr(self.parent, item.replace(' ', '_') + 'Action', QtWidgets.QAction(item))

            # Add the action to the listwidget
            self.parent.addAction(getattr(self.parent, item.replace(' ', '_') + 'Action'))

        return

    def ToolTip(self, dataset):
        """
        Creates the tooltip text formatted into rich texh for the list item.
        The text displays the dataframe values for the item
        """

        # Initialize some text
        tooltipText = ""

        # Get the chosen dataset from the row number

        # iterate over the dataframe columns for this dataframe
        for column in dataset.index:

            # Get the data value and add it to the tooltip text
            val = dataset[column]
            if str(val) == 'nan' or str(val) == 'NaT':
                val = ''
            tooltipText += "<p style='margin:0;padding:0'><strong>{0}: </strong>{1}</br></p>".format(column, val)

        return tooltipText


    def generateHTML(self, dataset):
        """
        Generates an HTML entry for the given index in the table
        """

        # SET A DEFAULT ICON
        iconPath = os.path.abspath('resources/GraphicalResources/icons/cactus-24px.svg')

        # Figure out what Icon to use
        if "SNOTEL" in dataset.DatasetType and 'snow' in dataset.DatasetParameter.lower():
            iconPath = self.icons.iconDict['snotel']
        elif 'OTHER' in dataset.DatasetType:
            iconPath = self.icons.iconDict['other']
        else:
            for key, value in self.icons.iconDict.items():
                if key in dataset.DatasetParameter.lower():
                    iconPath = value

        html = self.FORMAT_STRING.format(
            IconPath=iconPath,
            DatasetName=dataset.DatasetName,
            DatasetExternalID=dataset.DatasetExternalID,
            DatasetAgency=dataset.DatasetAgency,
            DatasetType=dataset.DatasetType,
            DatasetParameter=dataset.DatasetParameter,
            DatasetID=dataset.name
        )

        return html

class DataTab_datasetList(DatasetTab_SelectedDatasetList):
    FORMAT_STRING = """
        <table border="0" width="100%">
        <tr>
            <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"><img src="{IconPath}"></td>
            <td align="left"><strong style="color:#007396; font-size:14px">{DatasetName}</strong><br>
                    <strong>ID: </strong>{DatasetExternalID}<br>
                    <strong>Type: </strong>{DatasetAgency} {DatasetType}<br>
                    <strong>Parameter: </strong>{DatasetParameter}</td>
        </tr>
        <tr>
        <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"></td>
        <td style="text-align:right; color: #8c9f9d">{DatasetID}</td>
        </tr>
        </table>
        """

    def __init__(self, parent=None):
        DatasetTab_SelectedDatasetList.__init__(self,parent)

    def contextMenu(self):
        return

class ModelCreationTab_PredictorList(object):

    FORMAT_STRING = """
        <table border="0" width="100%">
        <tr>
            <td width="50" style="padding-left: 2px; padding-right: 10px;" align="left" valign="middle"><img src="{IconPath}"></td>
            <td align="left"><strong style="color:#007396; font-size:14px"><span style="font-size:18px;font-family:consolas;color:red">{PredictorForced}</span>{DatasetName} ({DatasetExternalID})</strong><br>
                    <strong style="color:#237539; font-size:12px">{PredictorParameter}</strong><br>
                    <strong>Method: </strong>{PredictorMethod}<br>
                    <strong>Start Date: </strong>{PredictorStartDate}<br>
                    <strong>Duration: </strong>{PredictorDuration}<br>
                    {Filling}<strong>Filled? </strong>{FillMethod}<br>
                    {Extending}<strong>Extended? </strong>{ExtendMethod}</td>
        </tr>
        </table>
        """

    def __init__(self, parent = None):

        self.dataFrame = parent.parent.modelRunsTable.iloc[-1]
        self.dataFrame2 = parent.parent.datasetTable
        self.iterator = enumerate(zip(
            self.dataFrame.PredictorPool,
            self.dataFrame.PredictorForceFlag,
            self.dataFrame.PredictorPeriods,
            self.dataFrame.PredictorMethods,
        ))
        self.icons = Icons()
        self.usesButtons = False
        self.buttonText = ""

        return


    def generateHTML(self, dataset):
        """
        Generates an HTML entry for the given index in the table
        """

        predictorID = dataset[0]
        forceFlag = dataset[1]
        period = dataset[2].split("/")
        method = dataset[3]
        startDate = datetime.strptime(period[1],'%Y-%m-%d')
        duration = isodate.parse_duration(period[2])
        rel_delta = relativedelta.relativedelta(startDate+duration, startDate)
        total_days = ((startDate+duration) - startDate).days
        total_days_1_month = ((startDate+isodate.parse_duration("P1M")) - startDate).days
        duration_string = "{0} Months, {1} Days".format(rel_delta.months, rel_delta.days) if total_days >= total_days_1_month else "{0} Days".format(total_days)


        datasetTableEntry = self.dataFrame2.loc[predictorID]

        # SET A DEFAULT ICON
        iconPath = os.path.abspath('resources/GraphicalResources/icons/cactus-24px.svg')

        # Figure out what Icon to use
        if "SNOTEL" in datasetTableEntry.DatasetType and 'snow' in datasetTableEntry.DatasetParameter.lower():
            iconPath = self.icons.iconDict['snotel']
        elif 'OTHER' in datasetTableEntry.DatasetType:
            iconPath = self.icons.iconDict['other']
        else:
            for key, value in self.icons.iconDict.items():
                if key in datasetTableEntry.DatasetParameter.lower():
                    iconPath = value

        html = self.FORMAT_STRING.format(
            IconPath=iconPath,
            PredictorForced="F " if forceFlag else "",
            PredictorParameter=datasetTableEntry.DatasetParameter,
            DatasetName=datasetTableEntry.DatasetName,
            DatasetExternalID=datasetTableEntry.DatasetExternalID,
            PredictorMethod=method.title(),
            PredictorStartDate=startDate.strftime('%B %d'),
            PredictorDuration=duration_string,
            FillMethod='NONE',
            ExtendMethod='NONE',
            Filling='NONE',
            Extending='NONE',

        )

        return html



class ListItem(QtWidgets.QListWidgetItem):

    signal_itemButtonPress = QtCore.pyqtSignal()

    def __init__(self, parent = None, itemData = None, buttonText = None):

        QtWidgets.QListWidgetItem.__init__(self)
        self.parent = parent

        self.setData(QtCore.Qt.UserRole, itemData)

        self.html = self.parent.listClass.generateHTML(itemData)

        self.widget = QtWidgets.QWidget(objectName = 'listItemWidget')

        self.textBox = QtWidgets.QLabel(self.html)
        self.textBox.setTextFormat(QtCore.Qt.RichText)
        self.textBox.setWordWrap(True)
        self.setForeground(QtGui.QBrush(QtGui.QColor(0,0,0,0)))
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.textBox)

        if buttonText:
            self.button = QtWidgets.QPushButton(buttonText)
            self.button.setCheckable(True)
            self.button.pressed.connect(lambda x: self.signal_itemButtonPress.emit())
            self.layout.addWidget(self.button)

        self.widget.setLayout(self.layout)
        self.toolTipText = self.parent.listClass.ToolTip(itemData)
        self.widget.setToolTip(self.toolTipText)

        self.setSizeHint(QtCore.QSize(0, self.widget.sizeHint().height()*1.2))

        return


class HTML_LIST(QtWidgets.QListWidget):
    """
    This is the ListWidget that displays all the
    elements in the list.
    """

    # SIGNALS
    signal_listItemClicked = QtCore.pyqtSignal(int) # EMITS THE ROW NUMBER OF THE ITEM CLICKED
    signal_listButtonClicked = QtCore.pyqtSignal(int) # EMITS THE ROW NUMBER OF THE BUTTON CLICKED


    def __init__(self, parent=None, listName=None):

        # INITIALIZE THE WIDGET
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.verticalScrollBar().setSingleStep(15)

        # LOAD THE APPROPRIATE CLASS BASED ON THE 'listName' ARGUMENT
        self.listClass = globals()[listName](self)

        # LOAD AN INITIAL LIST
        self.refreshList()

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
            self.menu.setLayoutDirection(QtCore.Qt.LeftToRight)
            self.menu.addActions(self.actions())
            self.menu.popup(self.mapToGlobal(event.pos()))

        return

    def refreshList(self):
        """
        refreshList re-generates the list from scratch.
        It should be called when underlaying DataFrames are changed
        elsewhere in the application.
        """

        # DELETE CURRENT LIST
        self.clear()

        # GENERATE NEW LIST
        for i, item in self.listClass.iterator():
            listItem = ListItem(self, item, self.listClass.buttonText if self.listClass.usesButtons else None)
            self.addItem(listItem)
            self.setItemWidget(listItem, listItem.widget)



if __name__ == '__main__':

    import pandas as pd
    import sys
    import numpy as np

    # Debugging dataset
    app = QtWidgets.QApplication(sys.argv)

    mw = QtWidgets.QMainWindow()

    mw.datasetTable = pd.DataFrame(
        index=pd.Index([], dtype=int, name='DatasetInternalID'),
        columns=[
            'DatasetType',  # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID',  # e.g. "GIBR" or "06025500"
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
            'DatasetPOREnd',  # e.g. 1/22/2019
            'DatasetAdditionalOptions'
        ]
    )

    mw.datasetTable.loc[100000] = ['RESERVOIR', 'GIBR', 'Gibson Reservoir', 'USBR', 'Inflow', 'CFS', 'in', 'Average',
                                'USBR_LOADER', '10030101', '44.254', '-109.123', '3212', '', '', '']
    mw.datasetTable.loc[100001] = ['STREAMGAGE', 'WSSW', 'Welcome Creek', 'USGS', 'Streamflow', 'CFS', 'in', 'Average',
                                'USGS_LOADER', '10030102', '44.255', '-109.273', '3212', '', '', '']
    mw.datasetTable.loc[100805] = ['SNOTEL', '633', 'Miscell Peak', 'NRCS', 'SWE', 'Inches', 'wteq', 'Sample',
                                'NRCS_LOADER', '10030101', '44.245', '-109.1123', '3212', '', '', '']

    mw.modelRunsTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ModelRunID'),
            columns = [
                "ModelTrainingPeriod",  # E.g. 1978-10-01/2019-09-30 (model trained on  WY1979-WY2019 data)
                "ForecastIssueDate",    # E.g. January 13th
                "Predictand",           # E.g. 100302 (datasetInternalID)
                "PredictandPeriod",     # E.g. R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",     # E.g. Accumulation, Average, Max, etc
                "PredictorPool",        # E.g. [100204, 100101, ...]
                "PredictorForceFlag",   # E.g. [False, False, True, ...]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, ...]
                "PredictorMethods",     # E.g. ['Accumulation', 'First', 'Last', ...]
                "RegressionTypes",      # E.g. ['Regr_MultipleLinearRegression', 'Regr_ZScoreRegression']
                "CrossValidationType",  # E.g. K-Fold (10 folds)
                "FeatureSelectionTypes",# E.g. ['FeatSel_SequentialFloatingSelection', 'FeatSel_GeneticAlgorithm']
                "ScoringParameters",    # E.g. ['ADJ_R2', 'MSE']
                "Preprocessors"         # E.g. ['PreProc_Logarithmic', 'PreProc_YAware']
            ]
        )

    mw.modelRunsTable.loc[0] = [
        "",
        "",
        "",
        "",
        "",
        [100000,100001,100805],
        [True,False,False],
        ["R/1978-03-01/P1M/F1Y","R/1978-03-11/P3D/F1Y","R/1978-03-01/P2M/F1Y"],
        ['first','average','accumulation'],
        "",
        "",
        "",
        "",
        ""
    ]

    w = HTML_LIST(mw, listName='DatasetTab_SelectedDatasetList')
    mw.setCentralWidget(w)
    mw.show()
    sys.exit(app.exec_())