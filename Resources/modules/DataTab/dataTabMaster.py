
from resources.modules.Miscellaneous import loggingAndErrors, DataProcessor
from resources.modules.DataTab import downloadData
from PyQt5 import QtCore
import time
import pandas as pd
import numpy as np
from datetime import datetime

"""
Script Name:    dataTabMaster.py

Description:    This script contains all the functionality associated with the 
                Data Tab. Operations such as downloading and pre-processing
                raw data is performed on this tab. Daily datasets can be 
                graphed and raw data can be edited or updated on this tab.
                
                The GUI scripting for this tab can be found in the 
                /resources/GUI/Tabs/DataTab.py file.
"""

class dataTab(object):
    """
    DATA TAB
    The Data Tab contains tools for retrieveing and editing raw data associated with the
    datasets listed in the Datasets Tab.
    """

    def initializeDataTab(self):
        """
        Initializes the Tab
        """

        self.connectEventsDataTab()
        self.dataTab.spreadsheet.model().loadDataIntoModel(self.dataTable, self.datasetTable)
        
        return
    
    def connectEventsDataTab(self):
        """
        Connects all the signal/slot events for the data tab
        """

        # Buttons
        self.dataTab.downloadButton.clicked.connect(self.downloadData)
        self.dataTab.endYearInput.valueChanged.connect(lambda x: self.dataTab.startYearInput.setMaximum(x))

        # ListWidget
        self.dataTab.datasetList.itemSelectionChanged.connect(self.plotSelectedDataset)

        # Plot

        # SpreadSheet
        self.dataTab.spreadsheet.model().dataChanged.connect(lambda x, y: self.plotSelectedDataset())
        self.dataTab.spreadsheet.horizontalHeader().selectionModel().selectionChanged.connect(lambda newSelection, oldSelection: self.plotSelectedDataset(specificSelection = self.dataTab.spreadsheet.getSelectedColumns()))

        return

    def downloadData(self):
        """
        Responsible for downloading datasets from web endpoints, import files (if available),
        or combining datasets.

        Proceeds as follows:
        1 - Validate POR input, datasetTable
        2 - Instantiate progress bar, status bar
        3 - download web endpoint data and append to the dataTable
            3.1 - if we're doing a fresh download, replace everything in the datatable
            3.2 - if we're doing an update, merge new data with old datatable, preferring old data
        """

        # Validate Input
        startWaterYear = self.dataTab.startYearInput.value()
        endWaterYear = self.dataTab.endYearInput.value()
        if startWaterYear > endWaterYear:
            loggingAndErrors.showErrorMessage(self, 'Starting year must be less than ending year')
            return

        # Validate datasetTable
        if self.datasetTable.empty:
            loggingAndErrors.showErrorMessage(self, 'No datasets in file')
            return
        
        # Instantiate progress bar and status bar
        self.dataTab.progressBar.show()
        self.dataTab.progressBar.setValue(0)
        self.dataTab.progressBar.setMaximum(len(self.datasetTable))
        self.dataTab.statusBar.show()

        # Disable the download box inputs
        self.dataTab.startYearInput.setEnabled(False)
        self.dataTab.endYearInput.setEnabled(False)
        self.dataTab.updateOption.setEnabled(False)
        self.dataTab.freshDownloadOption.setEnabled(False)
        self.dataTab.downloadButton.setEnabled(False)
        
        # Download data for each dataset and append to or update dataTable
        # Here we use the application's threadPool to run this process in the background
        downloadWorker = downloadData.downloadDataThreadWorker(self)
        downloadWorker.signals.returnDataSignal.connect(self.updateDataTableWithNewData)
        downloadWorker.signals.finishedSignal.connect(self.finishedDownload)
        downloadWorker.signals.updateProgressBar.connect(self.dataTab.progressBar.setValue)
        self.threadPool.start(downloadWorker)

        return


    def finishedDownload(self):
        """
        Re-enables the input boxes when the data is done
        downloading.
        """

        # Re-enable download box inputs
        self.dataTab.progressBar.setValue(self.dataTab.progressBar.maximum())
        self.dataTab.startYearInput.setEnabled(True)
        self.dataTab.endYearInput.setEnabled(True)
        self.dataTab.updateOption.setEnabled(True)
        self.dataTab.freshDownloadOption.setEnabled(True)
        self.dataTab.downloadButton.setEnabled(True)

        return


    def updateDataTableWithNewData(self, newData):
        """
        This function takes the output of the download data
        function and either merges the data (update options)
        or replaces the data (fresh download option).

            newData = a multi-index dataTable containing
                      new data to be added or merged into
                      the dataTable. 
        """

        # Get the data retrieval option (fresh download or update)
        if self.dataTab.updateOption.isChecked():
            
            # Merge the new data into the dataTable, with a preference
            # to keep any old data
            mergedDataTable = pd.merge(
                left = self.dataTable,
                right = newData,
                on = ["Datetime", "DatasetInternalID"],
                suffixes = ("_old", "_new"),
                indicator = True,
                how= "outer"
            )

            # Filter the dataTable and just keep changed values
            mergedDataTable = mergedDataTable[mergedDataTable.Value_old != mergedDataTable.Value_new]

            # Add any brand new data to the datatable
            # New values are those where there is no old value (value_old == NaN)
            newValues = pd.DataFrame(mergedDataTable[(np.isnan(mergedDataTable['Value_old'])) & (mergedDataTable['_merge'] == 'right_only')][['Value_new', 'EditFlag']])
            newValues.columns = ['Value', 'EditFlag']
            newValues['EditFlag'] = [False] * len(newValues)
            self.dataTable = self.dataTable.append(newValues)
            self.dataTable = self.dataTable[~self.dataTable.index.duplicated(keep='last')]

            # If there are any updated values, ask the user how they want to handle it:
            # updated values are those where there are both old and new values, but they are different
            updatedValuesNew = pd.DataFrame(mergedDataTable[(mergedDataTable['_merge'] == 'both') & (mergedDataTable['Value_new'] != mergedDataTable['Value_old']) & (mergedDataTable['EditFlag'] == False)][['Value_new', 'EditFlag']])
            if not updatedValuesNew.empty:
                
                if loggingAndErrors.displayDialogYesNo("The newly fetched data contains updates to old values. Do you want to replace the old values with the updated data? \n\n Note that any updated values will affect forecasts and model skill, though no equations will be changed."):
                
                    updatedValuesNew.columns = ['Value', 'EditFlag']
                    self.dataTable = self.dataTable.append(updatedValuesNew)
                    self.dataTable = self.dataTable[~self.dataTable.index.duplicated(keep='last')]

            # Set the data for the spreadsheet and initialize the plots
            self.dataTab.spreadsheet.model().loadDataIntoModel(self.dataTable, self.datasetTable)
            self.dataTab.datasetList.setCurrentRow(0)
            #self.dataTab.plot.displayDatasets([self.datasetTable.iloc[0].name])

            


        # Otherwise, we just replace the old datatable with the new datatable
        else:

            # Clear all existing data
            self.dataTable.drop(self.dataTable.index, inplace=True)

            # recursively call this function (artifically checking the update option)
            # to add in the new data
            self.dataTab.updateOption.setChecked(True)
            self.updateDataTableWithNewData(newData)
            self.dataTab.updateOption.setChecked(False)

        # Try and recompute any plots or data elsewhere in the software
        self.plotTarget()

        return


    def plotSelectedDataset(self, specificSelection = None):
        """
        This function is called when a user selects
        one or more datasets from the left hand side list. 
        It figures out which datasets are selected and 
        sends those to the plot's 'displayDatasets' method.

        The 'specificSelection' argument (optional) will programatically
        select datasets in the dataset list before plotting. 

        -> specificSelection: list of datasetInternalIDs. e.g. [10123, 101123, ...]
        """

        # Initialize an empty dataset list
        datasetsList = []

        # Check that there is some data in the dataTable
        if self.dataTable.empty:
            return

        # Check if there are specific datasets to plot from the function call
        if specificSelection != None:

            print(specificSelection)
            if specificSelection != []:
                

                # Iterate over datasets in the list
                for i in range(self.dataTab.datasetList.count()):

                    # Select the specific datasets
                    if self.dataTab.datasetList.item(i).data(QtCore.Qt.UserRole).name in specificSelection:

                        self.dataTab.datasetList.item(i).setSelected(True)
                    
                    else:

                        self.dataTab.datasetList.item(i).setSelected(False)


        # Iterate over the selected items in the datsetList
        for item in self.dataTab.datasetList.selectedItems():

            # Make sure that the selected item has data in the datatable
            if item.data(QtCore.Qt.UserRole).name in self.dataTable.index.levels[1]:

                if np.all(pd.isna(self.dataTable.loc[(slice(None), item.data(QtCore.Qt.UserRole).name), 'Value'])):

                    continue
            
                # Get the datasetID from the item
                datasetsList.append(item.data(QtCore.Qt.UserRole).name)

            else:

                loggingAndErrors.showErrorMessage(self,"The selected dataset {0} does not have any data associated with it yet and cannot be plotted.\n\n Use the download/retieval options above to fetch data for this dataset.".format(item.data(QtCore.Qt.UserRole)['DatasetName']))

        # Check if there are any datasets to plot
        if datasetsList == []:
            return

        # Call the plot's displayDatasets method
        self.dataTab.plot.displayDatasets(datasetsList)

        return