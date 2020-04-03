# Script Name:      ProcessDataV2.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:     This script converts daily data into seasonal forecast predictors. e.g. daily temperature data will be converted into month;y temperature averages.

# Import Libraries
from PyQt5 import QtGui, QtCore, QtWidgets
import json
import pandas as pd
import numpy as np
import multiprocessing as mp
from datetime import datetime
from Resources.Functions.miscFunctions import remapMonth, monthLookup

class alternateThreadWorkerSignals(QtCore.QObject):
    """
    This QObject (Qt slang for a python object) contains the signals that the QRunnable has
    access to.
    """

    # Define the signals emitted from this script
    returnForecastDict = QtCore.pyqtSignal(dict)
    returnPredictorDict = QtCore.pyqtSignal(list)
    updateProgBar = QtCore.pyqtSignal(int)
    updateProgLabel = QtCore.pyqtSignal(str)

class alternateThreadWorker(QtCore.QRunnable):
    """
    This QRunnable acts as a second thread on which to run operations. A second thread is 
    specified so that we don't hold up the main thread. 
    """

    def __init__(self, d):
        """
        This function initializes the QRunnable. The argument 'd' is a JSON dictionary that contains
        all the options specified by the user for how they want their data parsed, as well as the 
        data that needs to be parsed.
        """
        super(alternateThreadWorker, self).__init__()

        # Load and parse the json object into a dataframe and an options dict
        self.jsonObject = d
        self.options = self.jsonObject['OPTIONS']
        self.dataDir = self.jsonObject['DATA']
        self.update = self.jsonObject['UPDATE']

        # Load the signals that the worker will emit
        self.signals = alternateThreadWorkerSignals()

        # Set up the multiprocessing paramters
        self.numCPUs = mp.cpu_count() - 1 # Get the number of CPU's (leave one free)

        return
    

    def run(self):
        """
        This is the main entry point for this thread. It is called when the thread starts (after the thread initializes and the user calls the thread.start function). 
        """

        # Initialize a forecast dictionary that will store everything associated with forecast generation
        self.forecastDict = {
            "PredictorPool":{},
            "EquationPools":{},
            "Options":self.options
        }

        # determine how many forecasts equations will be generated. Example: For an april-july period with 
        # forecasts starting on January 1st, there will be 7 monthly forecast equations, or 14 bi-monhtly equations
        if self.forecastDict['Options']['fcstFreq'] == 'Monthly':
            for month in range(remapMonth(self.forecastDict['Options']['fcstStart'], wateryearStart= self.forecastDict['Options']['wateryearStart']), remapMonth(self.forecastDict['Options']['fcstPeriodEnd'], wateryearStart= self.forecastDict['Options']['wateryearStart'])+1):
                monthInv = remapMonth(month, inv=True, wateryearStart= self.forecastDict['Options']['wateryearStart']) # Convert the remapped month back to a real one
                monthInv = "0" + str(monthInv) # Zero-pad the monthe (i.e. change "2" to "02")
                monthInv = datetime.strftime(datetime.strptime(monthInv[-2:] + '011901', '%m%d%Y'), '%B')  + ' 01st' # Generate a string in the format "January 1st"
                self.forecastDict['EquationPools'][monthInv] = {"PredictorPool":{}, "Predictand":{}, "ForecastEquations":{}, "ForcedPredictors":[]}
               
        else:
            for month in range(remapMonth(self.forecastDict['Options']['fcstStart'], wateryearStart= self.forecastDict['Options']['wateryearStart']), remapMonth(self.forecastDict['Options']['fcstPeriodEnd'], wateryearStart= self.forecastDict['Options']['wateryearStart'])+1):
                monthInv = remapMonth(month, inv=True, wateryearStart= self.forecastDict['Options']['wateryearStart']) # Convert the remapped month back to a real one
                monthInv = "0" + str(monthInv) # Zero-pad the monthe (i.e. change "2" to "02")
                monthInv1 = datetime.strftime(datetime.strptime(monthInv[-2:] + '011901', '%m%d%Y'), '%B') + ' 01st' # Generate a string in the format "January 1st"
                monthInv2 = datetime.strftime(datetime.strptime(monthInv[-2:] + '011901', '%m%d%Y'), '%B') + ' 15th' # Generate a string in the format "January 15th"
                self.forecastDict['EquationPools'][monthInv1] = {"PredictorPool":{}, "Predictand":{}, "ForecastEquations":{}, "ForcedPredictors":[]}
                self.forecastDict['EquationPools'][monthInv2] = {"PredictorPool":{}, "Predictand":{}, "ForecastEquations":{}, "ForcedPredictors":[]}

        # Now we have our equationpools dict set up with one key per forecast equation in the form:
        # {"January 1st": {"Predictand":"", "Predictors":"",...}, "January 15th": {"Predictand":"", "Predictors":""},...}   

        progressCounter = 0
        maxCounter = self.forecastDict['EquationPools'].__len__() + len(self.dataDir)

        # Let's now add the known predictand to each equation key in the dict   
        for key in self.forecastDict['EquationPools']:

            self.signals.updateProgBar.emit(int(100*progressCounter/maxCounter))
            self.signals.updateProgLabel.emit("Generating {0} predictand...".format(key))
            progressCounter += 1
            print(str(progressCounter) + ' of ' + str(maxCounter) + ' -- Generating ' + key + ' equation...')

            keyMonth = key[:-5] # The "key" is of the form "January 15th" so "keyMonth" is now 'January"
            keyMonthMapped = remapMonth(keyMonth, wateryearStart=self.forecastDict['Options']['wateryearStart']) # Converts to a mapped month

            # The following code segment computes the inflow volume between a start date and an end date
            if keyMonthMapped < remapMonth(self.forecastDict['Options']['fcstPeriodStart'], wateryearStart= self.forecastDict['Options']['wateryearStart']):
                self.predictandName = self.forecastDict['Options']['fcstTarget']
                # Find the dataset the shares the same name
                index = -1
                for i, station in enumerate(self.dataDir):
                    if station['Name'] == self.predictandName:
                        index = i
                predictandData = pd.DataFrame().from_dict(self.dataDir[index]['Data'], orient='columns')
                lastDataDate = pd.to_datetime(predictandData.index[-1])
                firstWaterYear = predictandData.index[0].year + 1
                predictandData = predictandData.resample("AS").apply(self.volumetric, startDate = self.forecastDict['Options']['fcstPeriodStart'], endDate = self.forecastDict['Options']['fcstPeriodEnd']) # Apply a volumetric summing function to the dataset                if predictandData.mean() > 10000.0:
                
                if remapMonth(lastDataDate.month, wateryearStart= self.forecastDict['Options']['wateryearStart']) <= remapMonth(self.forecastDict['Options']['fcstPeriodEnd'], wateryearStart= self.forecastDict['Options']['wateryearStart']):
                    if lastDataDate.month <= 12 and lastDataDate.month > monthLookup(self.forecastDict['Options']['fcstPeriodEnd']):
                        pass
                    else:
                        predictandData = predictandData[predictandData.index.year < lastDataDate.year]

                predictandData = predictandData[predictandData.index.year >= firstWaterYear]
                
                if predictandData.mean()[0] >= 10000.0:
                    predictandData = predictandData / 1000.0
                    unit = 'KAF'
                else:
                    unit = 'AF'
                predictandData = predictandData.round(3)
                self.forecastDict['EquationPools'][key]['Predictand']['Name'] = self.predictandName + ' {0} - {1}'.format(self.forecastDict['Options']['fcstPeriodStart'],self.forecastDict['Options']['fcstPeriodEnd']) 
                self.forecastDict['EquationPools'][key]['Predictand']['Unit'] = unit
                self.forecastDict['EquationPools'][key]['Predictand']['Data'] = predictandData.to_dict(orient='dict')

            else:
                self.predictandName = self.forecastDict['Options']['fcstTarget']
                # Find the dataset the shares the same name
                index = -1
                for i, station in enumerate(self.dataDir):
                    if station['Name'] == self.predictandName:
                        index = i
                predictandData = pd.DataFrame().from_dict(self.dataDir[index]['Data'], orient='columns')
                lastDataDate = pd.to_datetime(predictandData.index[-1])
                firstWaterYear = predictandData.index[0].year + 1
                predictandData = predictandData.resample("AS").apply(self.volumetric, startDate = key, endDate = self.forecastDict['Options']['fcstPeriodEnd']) # Apply a volumetric summing function to the dataset                if predictandData.mean() > 10000.0:
                if remapMonth(lastDataDate.month, wateryearStart= self.forecastDict['Options']['wateryearStart']) <= remapMonth(self.forecastDict['Options']['fcstPeriodEnd'], wateryearStart= self.forecastDict['Options']['wateryearStart']):
                    if lastDataDate.month <= 12 and lastDataDate.month > monthLookup(self.forecastDict['Options']['fcstPeriodEnd']):
                        pass
                    else:
                        predictandData = predictandData[predictandData.index.year < lastDataDate.year]
                predictandData = predictandData[predictandData.index.year >= firstWaterYear]
                if predictandData.mean()[0] >= 10000.0:
                    predictandData = predictandData / 1000.0
                    unit = 'KAF'
                else:
                    unit = 'AF'
                predictandData = predictandData.round(3)
                self.forecastDict['EquationPools'][key]['Predictand']['Name'] = self.predictandName + ' {0} - {1}'.format(key,self.forecastDict['Options']['fcstPeriodEnd']) 
                self.forecastDict['EquationPools'][key]['Predictand']['Unit'] = unit
                self.forecastDict['EquationPools'][key]['Predictand']['Data'] = predictandData.to_dict(orient='dict')

        # Next, let's create the pool of all the available predictors
        for predictor in self.dataDir: # Iterate over all datasets

            self.signals.updateProgBar.emit(int(100*progressCounter/maxCounter))
            self.signals.updateProgLabel.emit("Generating {0}-{1} predictor sets...".format(predictor['TYPE'], predictor['Name']))
            progressCounter += 1
            print(str(progressCounter) + ' of ' + str(maxCounter) + ' -- Generating ' + predictor['TYPE'] + ' ' + predictor['Name'] + ' predictor...')

            # Re-initialize the predictor ID numbers
            if self.forecastDict['PredictorPool'] == {} or self.update:
                swe_prdID = '09000'
                reg_prdID = '00000'

            predictorData = pd.DataFrame().from_dict(predictor['Data'], orient='columns')
            name = predictor['Name']
            if name in self.forecastDict['PredictorPool']:
                name = name + predictor['Parameter']
            self.forecastDict['PredictorPool'][name] = {}

            # Construct the skeleton dictionary for each predictor, depending on its resampling method
            if predictor['Resampling'] == 'Mean':

                intervals = self.predictorDicts(mean=True)
                self.forecastDict['PredictorPool'][name] = intervals
               
                for key in intervals: # Iterate through the keys and generate mean data for that key's period
                    
                    dashLoc = key.find('-') # Parse the period (e.g. Jan1 - Jan 15) by first finding the location of the dash
                    month = monthLookup(key[:dashLoc-3]) # Get the number of the month in question
                    sday = int(key[dashLoc-3:dashLoc]) # Get the start date of the averaging period
                    eday = int(key[-2:]) # Get the end date of the averaging period
                    dataMask = (predictorData.index.month == month) & (predictorData.index.day >= sday) & (predictorData.index.day <= eday) # Mask the data to only include the desired averaging periods
                    data = predictorData.loc[dataMask] # apply the mask

                    # Compensate for water years
                    if month >= monthLookup(self.forecastDict['Options']['wateryearStart']):
                        data.index = data.index + pd.DateOffset(years=1)
                    #if month == 10 or month == 11 or month == 12:
                    #    data.index = data.index + pd.DateOffset(years=1)

                    # Add a predictor ID
                    if predictor['Parameter'] == 'SWE':
                        swe_prdID = str(int(swe_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = swe_prdID
                        prdID = swe_prdID
                    else:
                        reg_prdID = str(int(reg_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = reg_prdID
                        prdID = reg_prdID

                    # resample the data into water year sums
                    data = data.resample('AS').mean()
                    data = data.round(3)
                    data.columns = [prdID]
                    self.forecastDict['PredictorPool'][name][key]['Data'] = data.to_dict(orient='dict')

                    # Add a unit description
                    unit = predictor['Units'] + ' Avg'
                    self.forecastDict['PredictorPool'][name][key]['Unit'] = unit


            elif predictor['Resampling'] == 'Sample':

                intervals = self.predictorDicts(sample=True)
                self.forecastDict['PredictorPool'][name] = intervals

                for key in intervals:

                    month = monthLookup(key[:-3])
                    day = int(key[-2:])
                    dataMask = (predictorData.index.month == month) & (predictorData.index.day == day)
                    data = predictorData.loc[dataMask]
                    data = data.resample('AS').mean()
                    # Compensate for water years
                    if month >= monthLookup(self.forecastDict['Options']['wateryearStart']):
                        data.index = data.index + pd.DateOffset(years=1)
                    # if month == 10 or month == 11 or month == 12:
                    #     data.index = data.index + pd.DateOffset(years=1)

                    # Add a predictor ID
                    if predictor['Parameter'] == 'SWE':
                        swe_prdID = str(int(swe_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = swe_prdID
                        prdID = swe_prdID
                    else:
                        reg_prdID = str(int(reg_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = reg_prdID
                        prdID = reg_prdID

                    data = data.round(3)
                    data.columns = [prdID]
                    self.forecastDict['PredictorPool'][name][key]['Data'] = data.to_dict(orient='dict')

                    # Add a unit description
                    unit = predictor['Units']
                    self.forecastDict['PredictorPool'][name][key]['Unit'] = unit


            elif predictor['Resampling'] == 'NearestNeighbor':

                intervals = self.predictorDicts(sample=True)
                self.forecastDict['PredictorPool'][name] = intervals

                for key in intervals:

                    month = monthLookup(key[:-3])
                    day = int(key[-2:])
                    # fill data with nearest neighbor looking out 5 timesteps
                    predictorData2 = predictorData.interpolate(method='nearest',limit=5,limit_direction='both')
                    dataMask = (predictorData2.index.month == month) & (predictorData2.index.day == day)
                    data = predictorData2.loc[dataMask]
                    data = data.resample('AS').mean()
                    # Compensate for water years
                    if month >= monthLookup(self.forecastDict['Options']['wateryearStart']):
                        data.index = data.index + pd.DateOffset(years=1)
                    # if month == 10 or month == 11 or month == 12:
                    #     data.index = data.index + pd.DateOffset(years=1)

                    # Add a predictor ID
                    if predictor['Parameter'] == 'SWE':
                        swe_prdID = str(int(swe_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = swe_prdID
                        prdID = swe_prdID
                    else:
                        reg_prdID = str(int(reg_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = reg_prdID
                        prdID = reg_prdID

                    data = data.round(3)
                    data.columns = [prdID]
                    self.forecastDict['PredictorPool'][name][key]['Data'] = data.to_dict(orient='dict')

                    # Add a unit description
                    unit = predictor['Units']
                    self.forecastDict['PredictorPool'][name][key]['Unit'] = unit


            elif predictor['Resampling'] == 'Accumulation':
                if self.forecastDict['Options']['accumSelect'] == True:
                    intervals = self.predictorDicts(accum=True, accumStart=self.forecastDict['Options']['accumStart'])
                else:
                    intervals = self.predictorDicts(accum=True)
                
                self.forecastDict['PredictorPool'][name] = intervals

                for key in intervals:
                    
                    # Ensure that the index is sorted by date
                    predictorData = predictorData.sort_index()

                    # Determine the start and end dates of the interval
                    dashLoc = key.find('-')
                    smonth = monthLookup(key[:dashLoc-3])
                    sday = int(key[dashLoc-3:dashLoc])
                    emonth = monthLookup(key[dashLoc+1:-3])
                    eday = int(key[-2:])
                    wystart = monthLookup(self.forecastDict['Options']['wateryearStart'])

                    smonthMap = remapMonth(smonth, wateryearStart= self.forecastDict['Options']['wateryearStart'])
                    emonthMap = remapMonth(emonth, wateryearStart= self.forecastDict['Options']['wateryearStart'])

                    # Determine the start and end water years of the data
                    firstWaterYear = predictorData.index[0].year + 1
                    if predictorData.index[-1].month >= 10:
                        lastWaterYear = predictorData.index[-1].year + 1
                    else:
                        lastWaterYear = predictorData.index[-1].year

                    predictorData['waterYear'] = [predictorData.index[i].year if predictorData.index[i].month < wystart else predictorData.index[i].year + 1 for i in range(len(predictorData.index))]
                    predictorData['waterMonth'] = [predictorData.index[i].month - (wystart-1) if predictorData.index[i].month >= wystart else predictorData.index[i].month + (12-wystart+1) for i in range(len(predictorData.index))]

            
                    years = pd.date_range(str(firstWaterYear), str(lastWaterYear), freq="AS")
                    values = []
                    for year in years:
                        try:
                            dataMask = (predictorData['waterYear'] == year.year) & (predictorData['waterMonth'] >= smonthMap) & (predictorData['waterMonth'] <= emonthMap)
                            newData = predictorData.loc[dataMask]
                            if eday == 14:
                                lastDataMonth = newData.index[-1].month
                                lastDataYear = newData.index[-1].year
                                newData = newData[newData.index <= pd.to_datetime(str(lastDataMonth) + '-14-' + str(lastDataYear))]
                            if eday >= 28 and sday == 15:
                                lastDataMonth = newData.index[-1].month
                                lastDataYear = newData.index[-1].year
                                newData = newData[newData.index >= pd.to_datetime(str(lastDataMonth) + '-'+str(sday)+'-' + str(lastDataYear))]
                                newData = newData[newData.index <= pd.to_datetime(str(lastDataMonth) + '-'+str(eday)+'-' + str(lastDataYear))]
                            newData = newData[newData.columns[0]]
                        except Exception as e:
                            print(e)
                            newData = [0]
                        values.append(np.round(np.sum(newData),3))
                    
                    # Add a predictor ID
                    if predictor['Parameter'] == 'SWE':
                        swe_prdID = str(int(swe_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = swe_prdID
                        prdID = swe_prdID
                    else:
                        reg_prdID = str(int(reg_prdID) + 1).zfill(5)
                        self.forecastDict['PredictorPool'][name][key]['prdID'] = reg_prdID
                        prdID = reg_prdID
                    data = pd.DataFrame(values, index=years)
                    data = data.round(3)
                    data.columns=[prdID]
                    self.forecastDict['PredictorPool'][name][key]['Data'] = data.to_dict(orient='dict')

                    

                    # Add a unit description
                    unit = predictor['Units'] + ' Sum'
                    self.forecastDict['PredictorPool'][name][key]['Unit'] = unit
                    
            else:
                continue

        self.signals.updateProgBar.emit(int(100*progressCounter/maxCounter))
        self.signals.updateProgLabel.emit("Done!")
        print('Data Processing & Aggregation Complete!')
        # Return control to the main program
        if self.update:
            self.signals.returnPredictorDict.emit([self.forecastDict['PredictorPool'],self.forecastDict['EquationPools']] )
        else:
            self.signals.returnForecastDict.emit(self.forecastDict)


    # This function tells the Pandas library how to downscale monthly or bi-monthly data to
    # a water-year value. That is, it takes as input a years worth of monthly flows, and
    # returns as output a water year sum over the selected months
    def volumetric(self, arr, startDate, endDate):

        # Process the startDate and endDate into usable formats
        try:
            startDate = pd.to_datetime(startDate + ', 1901')
        except:
            startDate = pd.to_datetime(startDate + ' 01st, 1901')
        try:
            endDate = pd.to_datetime(endDate + ', 1901')
        except:
            endDate = pd.to_datetime(endDate + ' 01st, 1901')

        # Initialize an empty sum
        sum_ = 0

        # Iniatilze a counter for means

        # Iterate over the array and add to the sum if the value is within the start and end dates
        for i in range(len(arr)):

            if remapMonth(arr.index[i].month, wateryearStart= self.forecastDict['Options']['wateryearStart']) >= remapMonth(startDate.month, wateryearStart= self.forecastDict['Options']['wateryearStart']):
                if remapMonth(arr.index[i].month, wateryearStart= self.forecastDict['Options']['wateryearStart']) <= remapMonth(endDate.month, wateryearStart= self.forecastDict['Options']['wateryearStart']):
                    if remapMonth(arr.index[i].month, wateryearStart= self.forecastDict['Options']['wateryearStart']) == remapMonth(startDate.month, wateryearStart= self.forecastDict['Options']['wateryearStart']) and arr.index[i].day < startDate.day:
                        continue 
                    else:
                        sum_ += (86400 * arr[i] / 43559.9) #Add in units of acre-feet
                else:
                    continue
            else:
                continue
        
        return sum_ if sum_ != 0 else np.nan

     # This function generates a dictionary for a passed predictor
    def predictorDicts(self, mean = False, sample = False, accum = False, accumStart = None):

        # For sampled predictors:
        if mean == True:
            predictorDict = {
                "October 01-October 31":{},
                "October 01-October 14":{},
                "October 15-October 31":{},
                "November 01-November 30":{},
                "November 01-November 14":{},
                "November 15-November 30":{},
                "December 01-December 31":{},
                "December 01-December 14":{},
                "December 15-December 31":{},
                "January 01-January 31":{},
                "January 01-January 14":{},
                "January 15-January 31":{},
                "February 01-February 28":{},
                "February 01-February 14":{},
                "February 15-February 28":{},
                "March 01-March 31":{},
                "March 01-March 14":{},
                "March 15-March 31":{},
                "April 01-April 30":{},
                "April 01-April 14":{},
                "April 15-April 30":{},
                "May 01-May 31":{},
                "May 01-May 14":{},
                "May 15-May 31":{},
                "June 01-June 30":{},
                "June 01-June 14":{},
                "June 15-June 30":{},
                "July 01-July 31":{},
                "July 01-July 14":{},
                "July 15-July 31":{},
                "August 01-August 31":{},
                "August 01-August 14":{},
                "August 15-August 31":{},
                "September 01-September 30":{},
                "September 01-September 14":{},
                "September 15-September 30":{}
            }
        elif sample == True:
            predictorDict = {
                "October 14":{},
                "October 31":{},
                "November 14":{},
                "November 30":{},
                "December 14":{},
                "December 31":{},
                "January 14":{},
                "January 31":{},
                "February 14":{},
                "February 28":{},
                "March 14":{},
                "March 31":{},
                "April 14":{},
                "April 30":{},
                "May 14":{},
                "May 31":{},
                "June 14":{},
                "June 30":{},
                "July 14":{},
                "July 31":{},
                "August 14":{},
                "August 31":{},
                "September 14":{},
                "September 30":{}
            }
        elif accum == True:
            predictorDict = {
                "October 01-October 31":{},
                "October 01-October 14":{},
                "October 15-October 31":{},
                "November 01-November 30":{},
                "November 01-November 14":{},
                "November 15-November 30":{},
                "December 01-December 31":{},
                "December 01-December 14":{},
                "December 15-December 31":{},
                "January 01-January 31":{},
                "January 01-January 14":{},
                "January 15-January 31":{},
                "February 01-February 28":{},
                "February 01-February 14":{},
                "February 15-February 28":{},
                "March 01-March 31":{},
                "March 01-March 14":{},
                "March 15-March 31":{},
                "April 01-April 30":{},
                "April 01-April 14":{},
                "April 15-April 30":{},
                "May 01-May 31":{},
                "May 01-May 14":{},
                "May 15-May 31":{},
                "June 01-June 30":{},
                "June 01-June 14":{},
                "June 15-June 30":{},
                "July 01-July 31":{},
                "July 01-July 14":{},
                "July 15-July 31":{},
                "August 01-August 31":{},
                "August 01-August 14":{},
                "August 15-August 31":{},
                "September 01-September 30":{},
                "September 01-September 14":{},
                "September 15-September 30":{}
            }
            if accumStart != None:
                for month in ['October','November','December','January','February','March','April','May','June','July','August','September']:
                    if remapMonth(month, wateryearStart= self.forecastDict['Options']['wateryearStart']) >= remapMonth(accumStart, wateryearStart= self.forecastDict['Options']['wateryearStart']):
                        predictorDict[accumStart + ' 01-' + month + ' 14'] = {}
                        if month in ['October','December','January','March','May','July','August']:
                            predictorDict[accumStart + ' 01-' + month + ' 31'] = {}
                        elif month in ['November','April','June','September']:
                            predictorDict[accumStart + ' 01-' + month + ' 30'] = {}
                        else:
                            predictorDict[accumStart + ' 01-' + month + ' 28'] = {}

        else:
            return

        return predictorDict