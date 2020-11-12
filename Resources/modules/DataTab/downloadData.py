from PyQt5 import QtCore, QtWidgets
from resources.modules.Miscellaneous.DataProcessor import combinedDataSet
import json
import pandas as pd
import numpy as np
import importlib
from datetime import datetime, timedelta
import multiprocessing as mp
import sys

"""
Script Name:    DownloadData.py

Description:    This threadworker script fetches data from the various web endpoints, or 
                local file endpoints and compiles those datasets into a mulit-index
                data frame that can then be merged with the application-wide dataTable.

                Individual dataloaders (located at resources/DataLoaders) are initilized
                and used to download each dataset's data. All data processing
                is performed in the individual dataloader script. 

"""

class signals(QtCore.QObject):

        # Simple class to hold alternate thread's signals
        returnDataSignal = QtCore.pyqtSignal(object)
        finishedSignal = QtCore.pyqtSignal()
        updateProgressBar = QtCore.pyqtSignal(int)


class downloadDataThreadWorker(QtCore.QRunnable):
    """
    This QRunnable (https://doc.qt.io/qt-5/qrunnable.html) class contains the
    run function for the worker. It initializes on a separate thread than the
    main application process and downloads the data in the background. This
    frees up the main program for other tasks.
    """
    

    def __init__(self, parent = None):
        
        QtCore.QRunnable.__init__(self)
        self.signals = signals()

        # Create a reference to the parent, the application dataset table, and the application
        # start/end dates, the progress bar, and the status bar
        self.parent = parent
        self.datasetTable = self.parent.datasetTable
        startYear = self.parent.dataTab.startYearInput.value()
        endYear = self.parent.dataTab.endYearInput.value()
        self.progressBar = self.parent.dataTab.progressBar
        self.statusBar = self.parent.dataTab.statusBar

        # Create datetimes from the start and end years
        self.startDate = pd.to_datetime('{0}-10-01'.format(startYear - 1))
        self.endDate = pd.to_datetime('{0}-09-30'.format(endYear))

        # Print an initial message to the status bar
        self.statusBar.setText("Beginning data retrieval...")

        # Initialize the max value for the progress bar
        self.progressBar.setMaximum(len(self.datasetTable))

        # Date Range
        date_range = list(pd.date_range(self.startDate, self.endDate, freq='D'))

        # Dataset list
        datasetList = list(self.datasetTable.index)

        # Create a multi-index dataframe to store the new data. Initialize it with NaNs
        self.dataFrame = pd.DataFrame(
            index = pd.MultiIndex.from_product(
                [date_range, datasetList],
                names=['Datetime','DatasetInternalID']
                ),
            columns = ['Value']
        )

        return


    @QtCore.pyqtSlot()
    def run(self):
        """
        The run method performs the actual data retrieval by iterating over the 
        datasets and retrieving or composing each dataset
        """

        # Create a list of datasets to iterate over
        datasets = list(self.datasetTable.index)
        currentDataset = datasets[0]

        # Iterate over each dataset and stop once the program sets the current dataset to -1
        # We do it this way because the program may have to dynamically re-arrange the 
        # order of the dataset list so that composite datasets are only created after
        # the rest of the datasets are downloaded.
        while currentDataset != -1:

            # Figure out where we are in the list
            currentIndex = datasets.index(currentDataset)

            # Get the dataset definition
            dataset = self.datasetTable.loc[currentDataset]

            # Check whether the dataset is a composite dataset
            if not pd.isnull(dataset['DatasetCompositeEquation']):

                # Check whether all the datasets in the composite are available for composing
                requiredDatasets = [int(i) for i in dataset['DatasetCompositeEquation'].split('/')[1].split(',')]
                if set(requiredDatasets).issubset(set(datasets[:currentIndex])):
                    # Set status bar
                    self.statusBar.setText("Attempting to compose data for {0}".format(dataset['DatasetName']))

                    # Combine the datasets and get the data.
                    data = combinedDataSet(self.dataFrame.dropna(), self.datasetTable, dataset['DatasetCompositeEquation'])
                    data = data.astype('float64')
                    data.columns =['Value']
                    data.set_index([data.index, pd.Index(len(data)*[int(currentDataset)])], inplace=True)
                    data.index.names = ['Datetime','DatasetInternalID']
                    data.sort_index(level=['Datetime'], inplace=True)

                    self.dataFrame = pd.concat([self.dataFrame, data])
                    self.signals.updateProgressBar.emit(round(self.progressBar.value() + 0.999))

                # If we don't have all the data yet, move this dataset to the back of the list
                # and come back to it later when we do have all the data.
                else:
                    datasets.append(datasets.pop(currentIndex)) # <= This is a pretty sweet operation!

            # Download or import the data normally
            else:

                # Set the status bar and progress bar
                self.statusBar.setText("Attempting to retrieve data for {0}".format(dataset['DatasetName']))

                # Get the dataloader if we haven't already gotten it
                dataloaderModuleName = "resources.DataLoaders.{0}".format(dataset['DatasetDataloader'])
                if dataloaderModuleName not in sys.modules:
                    dataloader = importlib.import_module(dataloaderModuleName)
                else:
                    dataloader = sys.modules[dataloaderModuleName]

                # Attempt to retrieve the data and append it to the overall new dataframe
                try:

                    data = dataloader.dataLoader(dataset, self.startDate, self.endDate)
                    data = data.astype('float64')
                    data.columns =['Value']
                    data.set_index([data.index, pd.Index(len(data)*[int(currentDataset)])], inplace=True)
                    data.index.names = ['Datetime','DatasetInternalID']
                    data.sort_index(level=['Datetime'], inplace=True)
                    
                    self.dataFrame = pd.concat([self.dataFrame, data])
                    self.signals.updateProgressBar.emit(round(self.progressBar.value() + 0.999))

                except Exception as e:
                    print(e)
                    self.statusBar.setText("Failed to get data for dataset {0}".format(currentDataset))

            # Move on the the next dataset in the list. If we've finished all the datasets, set the current dataset to -1
            if currentIndex == len(datasets) - 1:

                # We've reached the end of the list
                currentDataset = -1

                # Set the status bar
                self.statusBar.setText("Finished dataset retrieval")

            # We're somewhere in the middle of the list
            else:

                if currentDataset == datasets[currentIndex]:

                    # We haven't rearranged the list
                    currentDataset = datasets[currentIndex + 1]
                
                else:
                    
                    # We rearranged the list
                    currentDataset = datasets[currentIndex]
        
        # Do some basic post-processing
        self.dataFrame = self.dataFrame[~self.dataFrame.index.duplicated(keep='last')]
        self.signals.returnDataSignal.emit(self.dataFrame)
        self.signals.finishedSignal.emit()

        return
            
