from PyQt5 import QtCore, QtWidgets
from resources.modules.Miscellaneous.DataProcessor import combinedDataSet
import json
import pandas as pd
import numpy as np
import importlib
from datetime import datetime, timedelta
import multiprocessing as mp
import sys

# Data Table Reference
# self.dataTable = pd.DataFrame(
#             index = pd.MultiIndex(
#                 levels=[[],[],[]],
#                 codes = [[],[],[]],
#                 names = ['Datetime','DatasetInternalID']
#             ),
#             columns = [
#                 "Value", # e.g. 24.5
#                 "EditedFlag"]) # e.g. 1 or 0 (edited or not edited)

# Define a class that will contain all the signals as objects
class alternateThreadWorkerSignals(QtCore.QObject):

    # Define the signals emitted from this script
    updateProgBar = QtCore.pyqtSignal(int) # Signal to update the progress bar on the data tab
    finished = QtCore.pyqtSignal(bool) # Signal to tell the parent thread that the worker is done
    returnNewData = QtCore.pyqtSignal(object) # returns the new data dataframe back to the main thread

# Define the main alternate thread worker that will actually run the download algorithm
class alternateThreadWorker(QtCore.QRunnable):

    def __init__(self, datasets, startDate, endDate, existingDataTable = None):
        super(alternateThreadWorker, self).__init__()

        # Load argument
        self.datasets = datasets
        self.startDate = startDate
        self.endDate = endDate
        self.existingDataTable = existingDataTable

        # Get the total number of stations
        self.totalStations = len(self.datasets)

        # Load the signals into the worker object
        self.signals = alternateThreadWorkerSignals()

        # set up a dataframe to store all the new data
        mi = pd.MultiIndex(levels=[[],[]], codes=[[],[]], names=['Datetime','DatasetInternalID'])
        self.df = pd.DataFrame(index = mi, columns = ['Value'])

    @QtCore.pyqtSlot()
    def run(self):

        self.signals.updateProgBar.emit(0)

        queue = mp.Queue()
        processes = []
        returned = []
        compositeDatasets = []
        importDatasets = []

        for dataset in self.datasets.iterrows():
            if dataset[1]['DatasetDataloader'] == 'COMPOSITE':
                compositeDatasets.append(dataset)
                continue
            elif dataset[1]['DatasetDataloader'] == 'IMPORT':
                importDatasets.append(dataset)
                continue                

            proc = mp.Process(target = worker, args = (queue, dataset[1], self.startDate, self.endDate))
            processes.append(proc)
            proc.start()

        for i, proc in enumerate(processes):
            returnValue = queue.get()
            returned.append(returnValue)
            progress = int(100*(i+1)/self.totalStations)
            self.signals.updateProgBar.emit(progress)

        for proc in processes:
            proc.join()
        
        for returnValue in returned:
            if returnValue.empty:
                continue
            self.df = pd.concat([self.df, returnValue])
        
        # Update any imported spreadsheets (assuming the file still exists)
        for i, dataset in importDatasets:
            fileName = dataset['DatasetAdditionalOptions']['Import Filename']
            try:
                if fileName[-4:] == '.csv':
                    df = pd.read_csv(fileName, index_col=0, parse_dates=True)
                elif '.xls' in fileName[-5:]:
                    df = pd.read_excel(fileName, index_col=0, parse_dates=True)
                
                df.columns =['Value']
                df.set_index([df.index, pd.Index(len(df)*[i])], inplace=True)
                df.index.names = ['Datetime', 'DatasetInternalID']
                self.df = pd.concat([self.df, df])
                
            except:
                df = self.existingDataTable.loc[(slice(None), dataset.name), 'Value']
                self.df = pd.concat([self.df, df])
                continue

        
            

        
        self.df = self.df[~self.df.index.duplicated(keep='first')]
        self.signals.returnNewData.emit(self.df)
        self.signals.finished.emit(True)

        return


def worker(queue, dataset, startDate, endDate):
    """
    This multiprocessing worker retrieves data for a dataset
    and stores it in a dataframe which it then appends to the 
    multiprocessing queue. 
    """

    # Get the dataloader
    dataloader = dataset['DatasetDataloader']
    modName = "resources.DataLoaders." + dataloader

    # Don't attempt to load imported data
    if dataloader == 'IMPORT':
        retval = pd.DataFrame()
        queue.put(retval)
        return
    
    # Load in the dataloader if it's not yet loaded
    if modName not in sys.modules:
        mod = importlib.import_module(modName)
        dataGetFunction = getattr(mod, 'dataLoader')
    else:
        mod = sys.modules[modName]
        dataGetFunction = getattr(mod, 'dataLoader')
    
    # use the dataloader to get the data
    try:
        data = dataGetFunction(dataset, startDate, endDate)
        data.columns =['Value']
        data.set_index([data.index, pd.Index(len(data)*[int(dataset.name)])], inplace=True)
        data.index.names = ['Datetime','DatasetInternalID']

    except:
        retval = pd.DataFrame()
        queue.put(retval)
        return
    
    # rput the dataframe into the queue
    retval = data
    queue.put(retval)
    return
