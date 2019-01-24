"""
Script Name:        DataDownloadV4.py
Script Author:      Kevin Foley, Civil Engineer, Reclamation
Last Modified:      10/15/2018

Description:        This script runs on an alternate thread. It reads the dataset
                    directory, evaluates what data needs to be downloaded, (and where
                    to download it from), and uses the datasets' designated loader to 
                    download and store the data. It utilizes pythons multiprocessing capabilities
                    to donwload datasets in parallel, improving download times.
"""

from PyQt5 import QtCore, QtWidgets
import json
import pandas as pd
import numpy as np
import importlib
from datetime import datetime, timedelta
from Resources.Functions.miscFunctions import lastWaterYear, current_date
import multiprocessing as mp

# Define a class that will contain all the signals as objects
class alternateThreadWorkerSignals(QtCore.QObject):

    # Define the signals emitted from this script
    updateProgBar = QtCore.pyqtSignal(int) # Signal to update the progress bar on the data tab
    ReturnDataToDatasetDirectory = QtCore.pyqtSignal(list) # Returns the station's data to its dataset directory entry
    finished = QtCore.pyqtSignal(bool) # Signal to tell the parent thread that the worker is done

# Define the main alternate thread worker that will actually run the download algorithm
class alternateThreadWorker(QtCore.QRunnable):

    # We pass the argument as a JSON string to compress the stationlist and the POR into one object
    def __init__(self, json_):
        super(alternateThreadWorker, self).__init__()

        # Load and parse the JSON object into relevant arguments
        self.jsonObject = json_
        self.interp = bool(self.jsonObject['FILL'] == 'True') 
        self.por = self.jsonObject['POR'] # The Period of Record text edit value
        self.update = bool(self.jsonObject['UPDATE'] == "True") # Boolean for the update option
        self.dataDir = self.jsonObject['STATIONS']['datasets'] # The list of datasets

        # Get the total number of stations
        self.totalStations = len(self.dataDir)

        # Load the signals into the worker object
        self.signals = alternateThreadWorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):

        self.signals.updateProgBar.emit(0)

        q = mp.Queue()
        procs = []
        rets = []

        for i in range(len(self.dataDir)):
            p = mp.Process(target=worker_helper, args=(q, [self.dataDir[i], self.update, self.interp, self.por]))
            procs.append(p)
            p.start()
        
        for i, p in enumerate(procs):
            ret = q.get()
            rets.append(ret)
            prog = int(100*(i+1)/self.totalStations)
            self.signals.updateProgBar.emit(prog)
        
        for p in procs:
            p.join()

        self.signals.ReturnDataToDatasetDirectory.emit(rets)
        self.signals.finished.emit(True)


def worker_helper(queue, argList):
    ret = downloadDataset(*tuple(argList))
    queue.put(ret)

def downloadDataset(dataset, update, interp, por):
    """
    """

    # Get the dataloader
    dataLoader = dataset['Decoding']['dataLoader']
    
    # Don't load imported data
    if dataLoader == 'IMPORT':
        return dataset

    if dataset['TYPE'] == 'Custom':
        mod =  importlib.import_module("Resources.DataLoaders.Custom." + dataLoader)
        dataGetFunction = getattr(mod, 'dataLoader')
    else:
        mod = importlib.import_module("Resources.DataLoaders.Default." + dataLoader)
        dataGetFunction = getattr(mod, 'dataLoader')

    # Grab any existing data from the dataset directory for this station
    data = pd.DataFrame().from_dict(dataset['Data'], orient='columns')

    # Figure out if we're updating existing data, or doing a fresh download
    if update: # We're updating!

        # Figure out the last data point in the dataset
        lastDate = data.index[-1]
        lastDate = pd.to_datetime(lastDate)

        # Set the start date of the download function to be 10 days before the last date
        startDate = lastDate - pd.DateOffset(days=10)

        # Set the end date to yesterday's date
        #endDate = pd.to_datetime('today') - pd.DateOffset(days=1)
        endDate = current_date() - pd.DateOffset(days=1)

        # Use the dataloader to download the data
        dataNew = dataGetFunction(dataset, startDate, endDate)

        # Perform any neccessary post processing
        if interp: # We will interpolate out up to 3 days of missing data
            dataNew.interpolate(method='spline', order = 3, limit = 3, inplace = True)
        dataNew.columns = [dataset['PYID']]
        # Append the data to the existing data
        data = pd.concat([data, dataNew], axis=0)
        data = data[~data.index.duplicated(keep='last')] # Remove duplicates from the dataset
        data = data[~data.index.isnull()]
        data.columns = [dataset['PYID']]

        dataset['Data'] = data.to_dict(orient='dict')
    
    else:

        # Figure out the start date and end dates
        endDate = current_date() - pd.DateOffset(days=1)
        #endDate = pd.to_datetime('today') - pd.DateOffset(days=1)
        startDate = lastWaterYear(endDate - pd.DateOffset(years=int(por))) + pd.DateOffset(days=1)

        # Download the data
        try:
            data = dataGetFunction(dataset, startDate, endDate)
        except:
            data = pd.DataFrame(np.nan, index=pd.date_range(startDate, endDate), columns=['a'])
        # Don't allow empty datasets
        if data.empty:
            print('empty dataset: {0}'.format(dataset['PYID']))

        # Perform any neccessary post processing
        if interp: # We will interpolate out up to 3 days of missing data
            try:
                data.interpolate(method='spline', order = 3, limit = 3, inplace = True)
            except:
                pass
        # Change the name of the header to the PYID
        data.columns = [dataset['PYID']]

        dataset['Data'] = data.to_dict(orient='dict')

    return dataset