"""
Script Name:    datasetTabMaster.py

Description:    This script contains all the functionality associated with the 
                Datasets Tab. Operations such as finding and defining datasets
                as well as editing and deleting datasets are defined in this 
                script. The GUI behind the datasets tab is defined in the 
                resources.GUI.Tabs.DatasetsTab script.
"""

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from resources.modules.Miscellaneous import loggingAndErrors
from resources.modules.DatasetTab import gisFunctions
from resources.GUI.Dialogs import UserDefinedDatasetDialog, createCompositeDataset
from fuzzywuzzy.fuzz import WRatio 
import multiprocessing as mp
import itertools
from time import sleep
import ast

class datasetTab(object):
    """
    DATASETS TAB
    The Datasets Tab contains information about the selected datasets. It allows users to select and 
    configure datasets using the map or the search functionality.
    """

    def __init__(self):
        """
        Initialize the tab
        """

        self.connectEvents()
        self.loadDatasetCatalog()
        self.loadDatasetMap()

        return

    def connectEvents(self):
        """
        Connects all the signal/slot events for the dataset tab
        """

        # Buttons
        self.datasetTab.keywordSearchButton.clicked.connect(        lambda x: self.searchForDataset(self.datasetTab.keywordSearchBox.text()))
        #self.datasetTab.prismButton.clicked.connect(                lambda x: self.)

        # CHECK THIS ONE
        self.datasetTab.webMapView.page.java_msg_signal.connect(lambda x: self.addDatasetToSelectedDatasets(int(x.split(':')[1])) if "ID:" in x else self.addDatasetToSelectedDatasets(str(x.split(':')[1])))


        return

    def loadDatasetCatalog(self):
        """
        Reads the dataset catalogs located at /resources/GIS/ and loads them into 2 
        dataframes ('additionalDatasetsTable', 'searchableDatasetsTable').
        """

        # Read the dataset catalogs into pandas dataframes
        self.searchableDatasetsTable = pd.read_excel("resources/GIS/PointDatasets.xlsx", index_col=0)
        self.searchableDatasetsTable.index.name = 'DatasetInternalID'
        self.additionalDatasetsTable = pd.read_excel('resources/GIS/AdditionalDatasets.xlsx', dtype={"DatasetExternalID": str}, index_col=0)
        self.additionalDatasetsTable.inex.name = 'DatasetInternalID'

        # Also, populate the climate indices 
        for i, dataset in self.additionalDatasetsTable[self.additionalDatasetsTable['DatasetType'] == 'CLIMATE INDICE'].iterrows():
            self.datasetTab.climInput.insertItem(i, text = dataset['DatasetName'], userData = dataset)
        
        # Create Completers for the watershed / climate division inputs
        self.datasetTab.prismCompleter.setModelWithDataFrame(self.additionalDatasetsTable[self.additionalDatasetsTable['DatasetAgency'] == 'PRISM'])
        self.datasetTab.nrccCompleter.setModelWithDataFrame(self.additionalDatasetsTable[self.additionalDatasetsTable['DatasetAgency'] == 'NRCC'])
        self.datasetTab.pdsiCompleter.setModelWithDataFrame(self.additionalDatasetsTable[self.additionalDatasetsTable['DatasetType'] == 'PDSI'])

        
        return

    def loadDatasetMap(self):
        """
        Loads the dataset catalog into the leaflet map
        """

        # Create a geojson file of all the point datasets
        geojson_ = gisFunctions.dataframeToGeoJSON(self.searchableDatasetsTable)

        # Load the geojson file into the web map
        self.datasetTab.webMapView.page.loadFinished.connect(lambda x: self.datasetTab.webMapView.page.runJavaScript("loadJSONData({0})".format(geojson_)))

        return


    def addDataset(self, datasetInternalID = None):
        """
        Adds the dataset defined by the datasetInternalID to the self.datasetTable table.
        This function also updates the dataset list in the GUI.

        Arguments:
            datasetInternalID -> The DatasetInternalID associated with the dataset to add. The ID's are 
                                 found in the dataset catalogs.
        """

        # Check to make sure that this dataset in not already in the datasetTable
        if datasetInternalID in list(self.datasetTable.index):

            # PRINT ERROR ABOUT THE DATASET ALREADY BEING ADDED
            return
        
        # Find the dataset from the appropriate dataset catalog
        if datasetInternalID > 99999        # This is a point dataset

            # Get the specific dataset
            dataset = self.searchableDatasetsTable.loc[datasetInternalID]
            
        else:                               # This is a HUC/CLIM/PDSI/OTHER dataset

            # Get the specific dataset
            dataset = self.additionalDatasetsTable.loc[datasetInternalID]
        
        # Append the dataset to the dataset table
        self.datasetTable = self.datasetTable.append(dataset, ignore_index = False)

        # Refresh the dataset list view
        

        return
    
    def removeDataset(self, datasetInternalID = None):
        """
        Removes the dataset defined by the datasetInternalID from the self.datasetTable table.
        This function also updates the dataset list in the GUI.

        Arguments:
            datasetInternalID -> The DatasetInternalID associated with the dataset to add. The ID's are 
                                 found in the dataset catalogs.
        """

        # Provide a warning that this will delete all associated forecasts, data, etc associated with this id

        # Begin by removing the dataset from the datasetTable
        self.datasetTable.drop(datasetInternalID, inplace = True)

        # Next remove all data from the DataTable
        self.dataTable.drop(datasetInternalID, level='DatasetInternalID', inplace = True)

        # Update the multiIndex of the DataTable
        self.dataTable.set_index(self.dataTable.index.remove_unused_levels(), inplace = True)

        return

    def searchForDataset(self, searchTerm = None):
        """
        Searched the default dataset list and returns any potential matches

        input:  searchTerm
                - The keyword or keywords to search the default dataset list for.
                  example: 'Yellowstone River Billings'
        
        output: results
                - a dataframe of results which is a subset of the searchableDatasetsTable
        """

        # Begin by disabling the search button while we look
        self.datasetTab.keywordSearchButton.setEnabled(False)

        # Ensure that the search term is longer than 4 characters (the fuzzy search doesn't work well with short search terms)
        if len(searchTerm) < 4: 

            # ADD POPUP BOX TO TELL USER ABOUT THE ERROR
            self.datasetTab.keywordSearchButton.setEnabled(True)
            return
        
        # Create a copy of the searchable dataset list
        searchTable = self.searchableDatasetsTable.copy()

        # Create a column in the searchTable containing all the keywords
        searchTable['searchColumn'] = searchTable[['DatasetName', 'DatasetType','DatasetAgency', 'DatasetExternalID']].apply(lambda x: ' '.join(x), axis=1)

        # Create a multiprocessing pool to perform the search
        pool = mp.Pool(mp.cpu_count() - 1)

        # Compute the scores (the fit score of the search term against the search column)
        searchTable['score'] = list(pool.starmap(WRatio, zip(searchTable['searchColumn'], itertools.repeat(searchTerm, len(searchTable)))))

        # Close the pool
        pool.close()
        pool.join()

        # Order the search results by score and load the results into the listWidget
        searchTable.sort_values(by=['score'], inplace=True, ascending=False)
        del searchTable['score'], searchTable['searchColumn']
        
        # NEED TO LOAD THE DATA INTO WIDGET

        self.datasetTab.keywordSearchButton.setEnabled(True)

        return