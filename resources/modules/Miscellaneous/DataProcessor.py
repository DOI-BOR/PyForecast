"""
Script name:    DataProcessor.py
Description:    The DataProcessor.py script processes daily data into new datasets (combinedDataset) or into 
                seasonal predictor datasets (resampleDataSet) based on format strings
"""

import pandas as pd
from datetime import datetime, timedelta
from dateutil import relativedelta
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

    _, IDs, CFs, LGs = [parser(i, x) for i,x in enumerate(combinationString.split('/'))]

    data = pd.Series([0], index=[onDatetime])

    for i, ID in enumerate(IDs):
        shiftedDatetime = onDatetime + pd.DateOffset(LGs[i])
        newData = pd.Series(dataTable.loc[(shiftedDatetime, ID), 'Value'], index=[onDatetime])
        data = np.sum([data, CFs[i]*pd.Series(newData.values, index=newData.index.get_level_values(0))], axis=0)

    return data

def combinedDataSet(dataTable, datasetTable, combinationString):
    """

    combinationStrings are formatted as follows:

    C/100121,102331,504423/1.0,0.5,4.3/0,0,5

    C/ -> Specifies combination of datasets
    id1,id2,id3,...,idN/ -> specifies predictor ID's to be combined
    cf1,cf2,cf3,...,cfN/ -> specifies coeficient to be applied to each series to be combined. 
    lg1,lg2,lg3,...,lgN/ -> specifies the time lag to apply to each series to be combined. positive integers indicate a lag in the time series. Lag in days
    
    So if you wanted a un-regulated inflow into reservoir A (inflow id 100000) which is downstream of reservoir B (inflow id 100001, outflow id 100002)
    you could write.

    newDataset = combinedDataSet(dataTable, "C/100000,100001,100002/1,1,-1/0,0,0")

    Input: 
        dataTable -> The raw datatable as a pandas multi-index dataframe
        combinationString -> The format string used to combine datasets into a new dataset

    Output:
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
        data = data.add(CFs[i]*pd.Series(newData.values, index=newData.index.get_level_values(0)))
        #data = np.sum([data, CFs[i]*pd.Series(newData.values, index=newData.index.get_level_values(0))], axis=0)
    
    # Create the dataTableAppend data
    dataTableAppend = pd.DataFrame(data, columns=['Value'], index=dates)
    

    return dataTableAppend


def resampleDataSet(dailyData, resampleString, resampleMethod, customFunction = None):
    """
    This function resamples a dataset (daily timestep) into
    a time series based on the resample string

    resample strings are formatted as follows (follwing ISO 8601)
    
    R/ -> specifies repeating interval
    YYYY-MM-DD/ -> specifies start date of repeating interval
    PnM/ -> specifies duration of repeating interval in months (This is the timeseries that is resampled )
    FnM -> specifies frequency of repetition (e.g. once a year)
    SnY -> shifts the data datetimes by n-years (SnY) or n-months (SnM)

    For example, to represent a parameter that would be resampled from daily data 
    into a March Average timeseries with one value per year, you could use:

    R/1978-03-01/P1M/F12M

    Or if you wanted a period average in February that always left out February 29th, you could specify:
    
    R/1984-02-01/P28D/F1Y    (Note the frequency F12M is the same as frequency F1Y)

    Input: 
        dailyData -> pandas Series of daily-intervaled data
        resampleString -> ISO8601 formatted resampling string (e.g. R/1978-02-01/P1M/F1Y/S1Y)
        resampleMethod -> One of 'accumulation', 'accumulation_cfs_kaf', 'average', 'first', 'last', 'max', 'min', 'custom', 'median'

        customFunction (optional) ->  if 'resampleMethod' is 'custom', you can enter a custom written 
                                      python function (as a string) to be applied to the series. Use 
                                      the variable "x" to represent the time series. 

                                      I.e. "np.mean(x) / np.std(x)" would return z-scores
    
    Output:
        resampledData -> data resampled based on format string
    """

    # Make sure the index is sorted
    dailyData.sort_index(level='Datetime', inplace=True)

    # Get today's date
    today = datetime.now()

    # Create a new empty series
    resampleData = pd.Series([], index = pd.DatetimeIndex([]))

    # Get information about the daily data
    firstDate = dailyData.index[0][0]

    # Parse the resample string
    resampleList = resampleString.split('/') # Converts 'R/1978-10-01/P1M/F1Y' into ['R', '1978-10-01', 'P1M', 'F1Y', 'S1Y']

    # Validate the list
    if resampleList[0] != 'R' or len(resampleList[1]) != 10 or resampleList[2][0] != 'P' or resampleList[3][0] != 'F': #or len(resampleList) != 4
        return resampleData, 1, 'Invalid Resample String. Format should be similar to R/1978-10-01/P1M/F1Y or R/1978-10-01/P1M/F1Y/S1Y'
    
    # Validate the resample method
    if resampleMethod not in ['accumulation', 'accumulation_cfs_kaf', 'average', 'first', 'last', 'max', 'min', 'custom', 'median']:
        return resampleData, 1, "Invalid resampling method. Provide one of 'accumulation', 'accumulation_cfs_kaf', 'average', 'first', 'last', 'max', 'min', 'custom', 'median'"

    # Parse into values
    startDate = datetime.strptime(resampleList[1], '%Y-%m-%d') # >>> datetime.date(1978, 10, 1)
    period = isodate.parse_duration(resampleList[2]) # >>> isodate.duration.Duration(0, 0, 0, years=0, months=1)
    # Change the period to 1 day if the resample method is 'first'
    if resampleMethod == 'first':
        period = isodate.parse_duration("P1D")
    frequency = isodate.parse_duration(resampleList[3].replace('F', 'P')) # >>> isodate.duration.Duration(0, 0, 0, years=1, months=1)

    # Create all the periods
    periodOffset = isodate.duration.Duration(days=0)
    if period.days == 0:
        periodOffset = isodate.duration.Duration(days=-1)
    periods = []
    tracker = startDate
    while tracker <= today: # >>> periods = [(datetime.datetime(1978-10-01), datetime.datetime(1978-11-01))]
        periods.append((tracker, tracker + period + periodOffset))
        tracker += frequency

    # Parse the function
    func = lambda x: np.nan if x.isnull().all() else (np.nanmean(x) if resampleMethod == 'average' else (
        np.nansum(x) if resampleMethod == 'accumulation' else (
            86400*(1/43560000)*np.nansum(x) if resampleMethod == 'accumulation_cfs_kaf' else (
                x.iloc[0] if resampleMethod == 'first' else (
                    x.iloc[-1] if resampleMethod == 'last' else (
                        np.nanmedian(x) if resampleMethod == 'median' else (
                            np.nanmax(x) if resampleMethod == 'max' else (
                                np.nanmin(x) if resampleMethod == 'min' else eval(customFunction)))))))))

    # Resample the data
    for idx in pd.IntervalIndex.from_tuples(periods):
        data = dailyData.loc[idx.left : idx.right]
        if resampleMethod != 'first' and resampleMethod != 'last':
            data.isMostlyThere = len(data) > int(0.95*(idx.right-idx.left).days) # Check to make sure 95% of data is there!
        else:
            data.isMostlyThere = True
        resampleData.loc[idx.left] = ( func(data) if (idx.right >= firstDate and today >= idx.right and (data.isMostlyThere)) else np.nan )

    if len(resampleList) == 5:
        shiftStrings = list(resampleList[4])
        if shiftStrings[1].isdigit():
            resampleData.index = resampleData.index + pd.offsets.DateOffset(years=int(shiftStrings[1]))
        else:
            return resampleData, 1, "Invalid Resample String. Format should be similar to R/1978-10-01/P1M/F1Y or R/1978-10-01/P1M/F1Y/S1Y"


    # Name the dataframe
    resampleData.name = dailyData.name + '_' + resampleList[1] + '_' + resampleList[2] + '_' + resampleList[3] + '_' + resampleMethod + '_' + str(customFunction)

    return resampleData