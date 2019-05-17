"""
Script name:    DataProcessor.py
Description:    The DataProcessor.py script processes daily data into new datasets (combinedDataset) or into 
                seasonal predictor datasets (resampleDataSet) based on format strings
"""

import pandas as pd
from datetime import datetime, timedelta
import isodate
import numpy as np
import re


def updateSingleComputedValue(dataTable, combinationString, onDatetime):
    """
    Updates a single value in the dataTable
    """
     # Parse and validate the combinationString
    def parser(idx, parseString):
        if idx == 0:
            return None
        elif idx == 1 or idx == 3:
            return [int(i) for i in parseString.split(',')]
        elif idx == 2:
            return [float(i) for i in parseString.split(',')]

    null, IDs, CFs, LGs = [parser(i, x) for i,x in enumerate(combinationString.split('/'))]

    data = pd.Series([0], index=[onDatetime])

    for i, ID in enumerate(IDs):
        shiftedDatetime = onDatetime + pd.DateOffset(LGs[i])
        newData = pd.Series(dataTable.loc[(shiftedDatetime, ID), 'Value'], index=[onDatetime])
        data = np.sum([data, CFs[i]*pd.Series(newData.values, index=newData.index.get_level_values(0))], axis=0)

    return data

def combinedDataSet(dataTable, datasetTable, combinationString, newDatasetMetaData = {}, existingID = -100):
    """

    combinationStrings are formatted as follows:

    C/100121,102331,504423/1.0,0.5,4.3/0,0,5

    C/ -> Specifies combination of datasets
    id1,id2,id3,...,idN/ -> specifies predictor ID's to be combined
    cf1,cf2,cf3,...,cfN/ -> specifies coeficient to be applied to each series to be combined. 
    lg1,lg2,lg3,...,lgN/ -> specifies the time lag to apply to each series to be combined. positive integers indicate a lag in the time series. Lag in days
    
    So if you wanted a un-regulated inflow into reservoir A (inflow id 100000) which is downstream of reservoir B (inflow id 100001, outflow id 100002)
    you could write.

    newDataset = combinatorialDataSet(dataTable, "C/100000,100001,100002/1,1,1/0,0,0", {"DatasetName":"Reservoir A", "DatasetParameter":"Unregulated Inflow", "DatasetUnits":"cfs"})

    Input: 
        dataTable -> The raw datatable as a pandas multi-index dataframe
        combinationString -> The format string used to combine datasets into a new dataset
        newDatasetMetaData -> dictionary of [column name : values] for the new dataset. Only provide things that you want to define personally. The software will do it's best to define the rest. 

    Output:
        datasetTableEntry -> Information about the new dataset 
        dataTableAppend -> data for the new dataset
    """

    # Parse and validate the combinationString
    def parser(idx, parseString):
        if idx == 0:
            return None
        elif idx == 1 or idx == 3:
            return [int(i) for i in parseString.split(',')]
        elif idx == 2:
            return [float(i) for i in parseString.split(',')]

    null, IDs, CFs, LGs = [parser(i, x) for i,x in enumerate(combinationString.split('/'))]

    # Retrieve the underlaying data 
    dates = np.sort(list(set(dataTable.loc[(slice(None),IDs),'Value'].index.get_level_values(0).values)))
    data = pd.Series([0 for i in dates], index=dates)

    for i, ID in enumerate(IDs):
        newData = dataTable.loc[(slice(None), ID), 'Value'].shift(LGs[i])
        data = np.sum([data, CFs[i]*pd.Series(newData.values, index=newData.index.get_level_values(0))], axis=0)
        


    # Create the datasetTableEntry
    defaults = {
        "DatasetName": "Combo: {0}".format(', '.join([str(i) for i in datasetTable.loc[IDs].DatasetName.values])),
        "DatasetParameter": '-'.join(set(datasetTable.loc[IDs].DatasetParameter.values)),
        "DatasetUnits": '-'.join(set(datasetTable.loc[IDs].DatasetUnits.values)),
        "DatasetExternalID": "Combo: {0}".format(', '.join([str(i) for i in datasetTable.loc[IDs].DatasetExternalID.values])),
        "DatasetType": "Combined Dataset",
        "DatasetDataloader":"COMPOSITE",
        "DatasetAgency": '-'.join(set(datasetTable.loc[IDs].DatasetAgency.values)),
        "DatasetAdditionalOptions": [{"CompositeString":combinationString}]
    }

    defaults.update(newDatasetMetaData)
    datasetTableEntry = pd.DataFrame(defaults, index=[max([-1, existingID])], columns = [
            'DatasetType', # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID', # e.g. "GIBR" or "06025500"
            'DatasetName', # e.g. Gibson Reservoir
            'DatasetAgency', # e.g. USGS
            'DatasetParameter', # e.g. Temperature
            'DatasetUnits', # e.g. CFS
            'DatasetDefaultResampling', # e.g. average 
            'DatasetDataloader', # e.g. RCC_ACIS
            'DatasetHUC8', # e.g. 10030104
            'DatasetLatitude',  # e.g. 44.352
            'DatasetLongitude', # e.g. -112.324
            'DatasetElevation', # e.g. 3133 (in ft)
            'DatasetPORStart', # e.g. 1/24/1993
            'DatasetPOREnd',# e.g. 1/22/2019
            'DatasetAdditionalOptions'])
    
    # Create the dataTableAppend data
    dataTableAppend = pd.DataFrame(data, columns=['Value'], index=dates)
    print(dataTableAppend)


    return datasetTableEntry, dataTableAppend


def resampleDataSet(dailyData, resampleString, resampleMethod, customFunction = None):
    """
    This function resamples a dataset (daily timestep) into
    a time series based on the resample string

    resample strings are formatted as follows (follwing ISO 8601)
    
    R/ -> specifies repeating interval
    YYYY-MM-DD/ -> specifies start date of repeating interval
    PnM/ -> specifies duration of repeating interval in months (This is the timeseries that is resampled )
    FnM -> specifies frequency of repetition (e.g. once a year)

    For example, to represent a parameter that would be resampled from daily data 
    into a March Average timeseries with one value per year, you could use:

    R/1978-03-01/P1M/F12M

    Or if you wanted a period in February that always left out February 29th, you could specify:
    
    R/1984-02-01/P28D/F1Y    (Note the frequency F12M is the same as frequency F1Y)

    Input: 
        dailyData -> pandas Series of daily-intervaled data
        resampleString -> ISO8601 formatted resampling string (e.g. R/1978-02-01/P1M/F1Y)
        resampleMethod -> One of 'accumulation', 'average', 'first', 'last', 'max', 'min', 'custom'

        customFunction (optional) ->  if 'resampleMethod' is 'custom', you can enter a custom written 
                                      python function (as a string) to be applied to the series. Use 
                                      the variable "x" to represent the time series. 

                                      I.e. "np.mean(x) / np.std(x)" would return z-scores
    
    Output:
        resampledData -> data resampled based on format string
    """

    # Get today's date
    today = datetime.now()

    # Create a new empty series
    resampleData = pd.Series([], index = pd.DatetimeIndex([]))

    # Get information about the daily data
    firstDate = dailyData.index[0]

    # Parse the resample string
    resampleList = resampleString.split('/') # Converts 'R/1978-10-01/P1M/F1Y' into ['R', '1978-10-01', 'P1M', 'F1Y']

    # Validate the list
    if len(resampleList) != 4 or resampleList[0] != 'R' or len(resampleList[1]) != 10 or resampleList[2][0] != 'P' or resampleList[3][0] != 'F':
        return resampleData, 1, 'Invalid Resample String. Format should be similar to R/1978-10-01/P1M/F1Y'
    
    # Validate the resample method
    if resampleMethod not in ['accumulation', 'average', 'first', 'last', 'max', 'min', 'custom']:
        return resampleData, 1, "Invalid resampling method. Provide one of 'accumulation', 'average', 'first', 'last', 'max', 'min', 'custom'"

    # Parse into values
    startDate = datetime.strptime(resampleList[1], '%Y-%m-%d') # >>> datetime.date(1978, 10, 1)
    period = isodate.parse_duration(resampleList[2]) # >>> isodate.duration.Duration(0, 0, 0, years=0, months=1)
    frequency = isodate.parse_duration(resampleList[3].replace('F', 'P')) # >>> isodate.duration.Duration(0, 0, 0, years=1, months=1)

    # Create all the periods
    periods = []
    tracker = startDate
    while tracker <= today: # >>> periods = [(datetime.datetime(1978-10-01), datetime.datetime(1978-11-01))]
        periods.append((tracker, tracker+period))#-timedelta(1)))
        tracker += frequency

    # Parse the function
    func = lambda x: np.nanmean(x) if resampleMethod == 'average' else (
        np.nansum(x) if resampleMethod == 'accumulation' else (
            x.iloc[0][0] if resampleMethod == 'first' else (
                x.iloc[-1][0] if resampleMethod == 'last' else (
                    np.max(x) if resampleMethod == 'max' else (
                        np.min(x) if resampleMethod == 'min' else eval(customFunction))))))

    # Resample the data
    for idx in pd.IntervalIndex.from_tuples(periods):
        resampleData.loc[idx.left] = ( func(dailyData.loc[idx.left:idx.right]) if (idx.right >= firstDate and today >= idx.right) else np.nan )

    # Name the dataframe
    resampleData.name = dailyData.name + '_' + resampleList[1] + '_' + resampleList[2] + '_' + resampleList[3] + '_' + resampleMethod + '_' + str(customFunction)

    return resampleData, 0, 'Procedure Exited Normally'