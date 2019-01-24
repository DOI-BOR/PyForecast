# Script Name:      Example.py
# Script Author:    Kevin Foley
# Created On:       6/22/2018

# This example pulls daily data from the USGS's daily values web service.
# It requires the following options:
#       stationNumber: The usgs station ID #
#       parameterCode:  The USGS parameter code
#       statsCode:      The USGS statistics code

# NOTE: All custom scripts must return a pandas datatable with a datetime index (1 index value per day)

#/////////////// IMPORT LIBRARIES /////////////////////////////////////////////////////////////////////

import requests # Library that performs GET/POST requests
import pandas as pd # (REQUIRED) creates datatables
import numpy as np # useful math library
from datetime import datetime # Library to deal with dates

#////////////// DEFINE THE DATALOADER INPUTS //////////////////////////////////////////////////////////

def dataLoaderInfo(): # THIS IS THE REQUIRED FUNCTION DEFINITION NAME. DO NOT CHANGE

    # \\\\\\\\\\\\ WHAT PARAMETERS ARE REQURED FOR THE WEB SERVICE CALL \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    
	optionsDict = {
        "stationNumber" : "",
        "parameterCode" : "",
        "statCode" : ""
    }

    # \\\\\\\\\\ A Short description of the dataloader (optional) \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    
	description = 'Retrieves data from the USGS NWIS API using a station id / parameter code / statistics code combination.'

	return optionsDict, description

#////////////// DEFINE THE DOWNLOAD SCRIPT ////////////////////////////////////////////////////////////////

# The following function takes a dictionary of station information (defined in the "Add custom station" dialog),
# as well as start and end dates, which are supplied by the program.
def dataLoader(optionsDict, startDate, endDate): # THIS IS THE REQUIRED FUNCTION DEFINITION NAME, DO NOT CHANGE

    # ///////// WHAT DATA NEEDS TO BE FOUND //////////////////////////////
    # Get the relevant parameters from the optionsDict
    stationID = optionsDict['stationNumber']
    param = optionsDict['parameterCode']
    stat = optionsDict['statCode']

    # ///////// WHERE TO FIND THE DATA ///////////////////////////////////
    # Set the REST Service URL and parameters
    baseURL = 'https://waterservices.usgs.gov/nwis/dv/?format=json'
    urlWithOptions = (baseURL + 
            '&sites=' + stationID +
            '&startDT=' + datetime.strftime(startDate, '%Y-%m-%d') + 
            '&endDT=' + datetime.strftime(endDate,'%Y-%m-%d') + 
            '&statCd=' + stat + '&parameterCd=' + param + '&siteStatus=all')


    # ///////// RETRIEVE THE DATA ////////////////////////////////////////
    data = requests.get(urlWithOptions)

    # Make sure that the retrieval was succesfful
    if data.status_code is not 200: 
        return pd.DataFrame() # IF unsuccessfull, return a blank dataframe

    # The data from this particular web service call comes back in JSON form, so we now convert the 
    # response to JSON
    data = data.json()

    # Create a dataframe from the data
    df = pd.DataFrame(data['value']['timeSeries'][0]['values'][0]['value'])

    # Set the index to the dateTime index
    df.set_index(pd.DatetimeIndex(pd.to_datetime(df['dateTime'])), inplace = True)
    del df['dateTime'] # Delete the redundant column

    # Replace missing data with NaN's
    df['value'].replace(to_replace = '-999999', value = np.nan, inplace = True)
    
    # Remove any duplicate data in the dataset
    df = df[~df.index.duplicated(keep='first')] # Remove duplicates from the dataset
    df = df[~df.index.isnull()]

    # Rename the columns
    df.columns = ['USGS | ' + stationID + ' | Flag', 'USGS | ' + stationID + ' | Streamflow | CFS']
    df = df['USGS | ' + stationID + ' | Streamflow | CFS']

    # Return the data frame
    return df