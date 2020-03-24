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

        self.connectEvents()
        
        return
    
    def connectEvents(self):
        """
        Connects all the signal/slot events for the data tab
        """

        # Buttons
        self.dataTab.dowloadButton.clicked.connect(None)
        self.dataTab.endYearInput.valueChanged.connect(lambda x: self.dataTab.startYearInput.setMaximum(x))

        # ListWidget

        # Plot

        # SpreadSheet

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
        self.dataTab.statusBar.show()

        # Disable the download box inputs
        self.dataTab.startYearInput.setEnabled(False)
        self.dataTab.endYearInput.setEnabled(False)
        self.dataTab.updateOption.setEnabled(False)
        self.dataTab.freshDownloadOption.setEnabled(False)
        self.dataTab.dowloadButton.setEnabled(False)
        
        # Download data for each dataset and append to or update dataTable

        # Re-enable download box inputs
        self.dataTab.startYearInput.setEnabled(True)
        self.dataTab.endYearInput.setEnabled(True)
        self.dataTab.updateOption.setEnabled(True)
        self.dataTab.freshDownloadOption.setEnabled(True)
        self.dataTab.dowloadButton.setEnabled(True)

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
            updatedValuesNew = pd.DataFrame(merged[(merged['_merge'] == 'both') & (merged['Value_new'] != merged['Value_old']) & (merged['EditFlag'] == False)][['Value_new', 'EditFlag']])
            if not updatedValuesNew.empty:
                
                if loggingAndErrors.displayDialogYesNo("The newly fetched data contains updates to old values. Do you want to replace the old values with the updated data? \n\n Note that any updated values will affect forecasts and model skill, though no equations will be changed.")
                
                    updatedValuesNew.columns = ['Value', 'EditFlag']
                    self.dataTable = self.dataTable.append(updatedValuesNew)
                    self.dataTable = self.dataTable[~self.dataTable.index.duplicated(keep='last')]


        # Otherwise, we just replace the old datatable with the new datatable
        else:

            # Clear all existing data
            self.dataTable.drop(self.dataTable.index, inplace=True)

            # recursively call this function (artifically checking the update option)
            # to add in the new data
            self.dataTab.updateOption.setChecked(True)
            self.updateDataTableWithNewData(newData)
            self.dataTab.updateOption.setChecked(False)

        return
        