"""
Script Name:    dataTabMaster.py
Description:    This script contains all the functionality behind the User interface of the Data Tab.
"""
from resources.modules.Miscellaneous import loggingAndErrors, DataProcessor
from resources.modules.DataTab import downloadData
from resources.GUI.Dialogs.createCompositeDataset import compositeDatasetDialog
from resources.GUI.Dialogs import UserDefinedDatasetDialog
from PyQt5 import QtCore
import time
import pandas as pd
import numpy as np
from datetime import datetime

class dataTab(object):

    def setupDataTab(self):
        """
        Initializes the data tab and connect the data tab events.
        """
        self.dataTab.porT2.setText(datetime.strftime(pd.to_datetime(self.userOptionsConfig['GENERAL']['application_datetime']), '%Y'))
        self.dataTab.downloadButton.clicked.connect(self.downloadData)
        self.dataTab.importButton.clicked.connect(lambda x: self.createUserDefinedDataset(importDatasetFlag=True))
        self.dataTab.compositeButton.clicked.connect(self.openCompositeDialog)
        self.currentlyPlottedColumns = []

        return

    def resetDataTab(self):
        """
        Resets the data tab to a previous configuration based on the data in the 'userOptionsConfig'
        """
        if self.dataTable.empty:
            return
        self.displayDataInTable()
        self.dataTab.porT2.setText(datetime.strftime(pd.to_datetime(self.userOptionsConfig['GENERAL']['application_datetime']), '%Y'))
        self.currentlyPlottedColumns = self.userOptionsConfig['DATA TAB']['current_plotted_columns'].split(',')
        self.plotClickedColumns(self.currentlyPlottedColumns)
        current_bounds = self.userOptionsConfig['DATA TAB']['current_plot_bounds'].split(',')
        self.dataTab.dataPlot.p1.vb.setRange(xRange = [float(current_bounds[0]),float(current_bounds[1])], yRange = [float(current_bounds[2]),float(current_bounds[3])])

        return
    

    def storeDataTabInformation(self):
        """
        Stores the current settings for the plot and datetimes that the user has set. 
        """
        self.userOptionsConfig['DATA TAB']['por_start'] = self.dataTab.porT1.text()
        self.userOptionsConfig['DATA TAB']['current_plotted_columns'] = ','.join([str(i) for i in self.currentlyPlottedColumns])
        self.userOptionsConfig['DATA TAB']['current_plot_bounds'] = ','.join(str(x) for x in self.dataTab.dataPlot.p1.vb.viewRange()[0]) + ',' + ','.join(str(x) for x in self.dataTab.dataPlot.p1.vb.viewRange()[1])
        
        return
    
    def openCompositeDialog(self):
        """
        """
        self.compDialog = compositeDatasetDialog(self.datasetTable, self.dataTable)
        self.compDialog.returnDatasetSignal.connect(self.addNewlyCombinedDatasetToDatastores)
        self.compDialog.exec_()

    def addNewlyCombinedDatasetToDatastores(self, datasetObj):
        """
        """

        # Parse the object
        dataset = datasetObj[0]
        data = datasetObj[1]

        # Append the dataset to the datasetTable
        self.addUserDefinedDatasetToSelectedDatasets(dataset)

        # Append the data to the dataTable
        self.setDataForImportedDataset(data, composite=True)

        return

    def downloadData(self):
        """
        1. Validates the POR input.
        2. Validates the Datasets Table
        3. Instantiates a Progress Bar
        4. Downloads data for each dataset in datasets table and appends to dataTable
        """

        # 1. Validate POR input
        porT1 = self.dataTab.porT1.text()
        porT2 = self.dataTab.porT2.text()
        try:
            porT1 = pd.to_datetime(porT1+'-10-01')
            porT2 = pd.to_datetime(self.userOptionsConfig['GENERAL']['application_datetime'])
        except Exception as E:
            loggingAndErrors.showErrorMessage(self, 'Could not parse POR input: {0}'.format(E))
            return

        # 2. Validate Dataset Table
        if self.datasetTable.empty:
            loggingAndErrors.showErrorMessage(self, 'No datasets Selected')
            return
        
        # 3. Instantiate Progress Bar
        self.dataTab.downloadProgressBar.show()
        self.dataTab.downloadButton.setEnabled(False)

        # 4. Download Data For each dataset and append to dataTable
        try:
            downloadWorker = downloadData.alternateThreadWorker(self.datasetTable, porT1, porT2, self.dataTable)
            downloadWorker.signals.updateProgBar.connect(self.dataTab.downloadProgressBar.setValue)
            downloadWorker.signals.returnNewData.connect(lambda x: self.postProcessNewData(x))
            downloadWorker.signals.finished.connect(self.downloadFinished)
            self.threadPool.start(downloadWorker)
        except Exception as E:
            loggingAndErrors.showErrorMessage(self, 'Could not download data: {0}'.format(E))
            self.dataTab.downloadButton.setEnabled(True)
            self.dataTab.downloadProgressBar.hide()


        return


    def downloadFinished(self):
        """
        Hide the progress bar after the data finishes downloading
        """
        self.dataTab.downloadProgressBar.hide()
        self.dataTab.downloadButton.setEnabled(True)

        return


    @QtCore.pyqtSlot(object)
    def setDataForImportedDataset(self, data, id_ = -1, composite=False):
        """
        Stores the data from the imported dataset into the dataTable.
        """
        if id_ == -1:
            id_ = self.datasetTable.index[-1]
        data.columns =['Value']
        data.set_index([data.index, pd.Index(len(data)*[id_])], inplace=True)
        data.index.names = ['Datetime','DatasetInternalID']
        self.postProcessNewData(data, composite)
        return

    def postProcessNewData(self, newDataTable, recursionFlag = False, noPlot = False):
        """
        This function gets the raw downloaded data from the downloadData function and merges it with the existing dataset, updating any outdated 
        values, and detecting any merge conflicts.
        """

        # Don't bother with empty datatables
        if newDataTable.empty:
            return

        # First create a merged dataTable
        merged = pd.merge(left=self.dataTable, right=newDataTable, on=['Datetime','DatasetInternalID'], suffixes=('_old','_new'), indicator=True, how='outer')
        
        # Filter to only get the changed data
        merged = merged[merged.Value_old != merged.Value_new]

        # Add brand new data to the datatable
        newValues = pd.DataFrame(merged[(np.isnan(merged['Value_old'])) & (merged['_merge'] == 'right_only')][['Value_new', 'EditFlag']])
        newValues.columns = ['Value', 'EditFlag']
        newValues['EditFlag'] = [False] * len(newValues)
        self.dataTable = self.dataTable.append(newValues)
        self.dataTable = self.dataTable[~self.dataTable.index.duplicated(keep='last')]

        # Figure out which values are updated and don't need to be validated by the user
        updatedValuesNew = pd.DataFrame(merged[(merged['_merge'] == 'both') & (merged['Value_new'] != merged['Value_old']) & (merged['EditFlag'] == False)][['Value_new', 'EditFlag']])
        updatedValuesNew.columns = ['Value', 'EditFlag']
        self.dataTable = self.dataTable.append(updatedValuesNew)
        self.dataTable = self.dataTable[~self.dataTable.index.duplicated(keep='last')]

        # find the updated values that are replacing unedited original data
        #updatedValuesNew_need_validation = pd.DataFrame(merged[(merged['_merge'] == 'both') & (merged['Value_new'] != merged['Value_old']) & (merged['EditFlag'] == True)][['Value_old', 'Value_new', 'EditFlag']])
        #if loggingAndErrors.displayDialog("We've downloaded data that conflicts with your edited data. Would you like to review the conflicts? If not, we'll overwrite your edits with the new data."):
            # self.conflictReviewDialog = conflictReviewDialog(df=updatedValuesNew_need_validation, datasets = self.datasetTable)
            # This part still needs work. Theres a lot of moving parts with checkboxes/etc. 

        #TEMPORARY
        updatedValuesNew_need_validation = pd.DataFrame(merged[(merged['_merge'] == 'both') & (merged['Value_new'] != merged['Value_old']) & (merged['EditFlag'] == True)][['Value_new', 'EditFlag']])
        updatedValuesNew_need_validation.columns = ['Value', 'EditFlag']
        self.dataTable = self.dataTable.append(updatedValuesNew_need_validation)
        self.dataTable = self.dataTable[~self.dataTable.index.duplicated(keep='last')]

        # Update any composite datasets
        # Regenerate any composite datasets (assuming the original datasets still exist)
        if not recursionFlag:
            for i, dataset in self.datasetTable.iterrows():
                if dataset['DatasetDataloader'] == 'COMPOSITE':
                    combinationString = dataset['DatasetAdditionalOptions']['CompositeString']
                    reliesOn = [int(j) for j in combinationString.split('/')[1].split(',')]
                    if np.all([j in list(self.datasetTable.index) for j in reliesOn]):

                        null, df = DataProcessor.combinedDataSet(self.dataTable, self.datasetTable, combinationString, newDatasetMetaData = {})
                        df.columns =['Value']
                        df.set_index([df.index, pd.Index(len(df)*[i])], inplace=True)
                        df.index.names = ['Datetime', 'DatasetInternalID']
                        self.postProcessNewData(df, True)
                        return

                    else:
                        loggingAndErrors.showErrorMessage(self, "Composite dataset {0} ({1}) relies on a dataset that no longer exists. We did not update this dataset.".format(dataset['DatasetName'], dataset.name))

        self.displayDataInTable(noPlot)

        return

    
    def displayDataInTable(self, noPlot=False):
        """
        This function takes the dataTable and converts it into a spreadsheet-like datatable. 
        """
        if self.dataTable.empty:
            return
        self.dataTab.table.model().initialize_model_with_dataset(self.dataTable, self.datasetTable)
        self.dataTab.table.horizontalHeader().sectionClicked.connect(lambda x: self.plotClickedColumns())
        self.dataTab.table.model().changedDataSignal.connect(self.userChangedData)
        if not noPlot:
            self.plotClickedColumns([self.datasetTable.index[0]])

        return
 

    def userChangedData(self, dataChanges):
        """
        This function is triggered whenever a user changes the data in the table. 
        It updates the global data table and triggers updates in any associated forecasts. 

        dataChanges: list of changed data, i.e [date, columnName, oldValue, newValue]
        """
        self.dataTable.loc[(dataChanges[0], dataChanges[1])] = (dataChanges[3], True)
        
        if dataChanges[2] == dataChanges[3]:
            return

        changed_cols = [dataChanges[1]]

        # Update any composite datasets that are based on this data
        for i, dataset in self.datasetTable.iterrows():
            if dataset['DatasetDataloader'] == 'COMPOSITE':
                combinationString = dataset['DatasetAdditionalOptions']['CompositeString']
                reliesOn = [int(j) for j in combinationString.split('/')[1].split(',')]
                if dataChanges[1] in reliesOn:
                    if np.all([j in list(self.datasetTable.index) for j in reliesOn]):
                        newDataValue = DataProcessor.updateSingleComputedValue(self.dataTable, combinationString, dataChanges[0])
                        self.dataTable.loc[(dataChanges[0], dataset.name), 'Value'] = newDataValue
                        changed_cols.append(dataset.name)
                        

        self.plotClickedColumns(displayColumns=self.currentlyPlottedColumns, changed_col=changed_cols)

        
                        

        # NOTE, NEED TO UPDATE ANY FORECASTS BASED ON THIS DATA

        return


    def plotClickedColumns(self, displayColumns = None, changed_col = None):
        """
        This function plots the columns that the user selects
        """
        if displayColumns != None:
            self.currentlyPlottedColumns = displayColumns
        else:
            self.currentlyPlottedColumns = self.dataTab.table.getSelectedColumns()
            if self.currentlyPlottedColumns == [] or self.currentlyPlottedColumns == None:
                return
        data = self.dataTable.loc[(slice(None), self.currentlyPlottedColumns), 'Value']
        #print("Data is: ", data)
        if isinstance(displayColumns, list) and isinstance(changed_col, list):
            changed_col = [col for col in changed_col if col in displayColumns]
        else:
            changed_col = None
        self.dataTab.dataPlot.add_data_to_plots(data, changed_col = changed_col, datasets=self.datasetTable)

        return
            