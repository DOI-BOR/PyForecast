# Script Name:      NRCS_WCC.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      A Dataloader for SNOTEL and Snowcourse data in xml/soap format.
#                   Uses the SOAP protocol.

# Function takes the stationDict entry for the station in question
# along with datetime formatted dates and returns a datatable with columns (date, data, flag)

# Import libraries
import pandas as pd
import requests
from datetime import datetime
from zeep import Client
from decimal import Decimal

def dataLoader(stationDict, startDate, endDate):
    """
    This dataloader loads data from the NRCS's AWDB database. This database contains 
    snow, precipitation, and soil moisture data for SNOTEL, SNOWCOURSE, and SCAN stations 
    maintained by the NRCS. The "DatasetType" option specifies which of these three networks
    your station belongs to. The Dataset Parameter (e.g. Snow Water Equivalent) and Dataset ID
    (e.g. 304) options must be specified. Valid options for Parameter are:
    "Snow Water Equivalent", 
    "Precipitation",
    "Soil Moisture"
    DEFAULT OPTIONS
    DatasetType: SNOTEL
    """
 
    # Set up the soap service
    NRCS = Client('http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL')

    # Get the station triplet
    triplet = NRCS.service.getStations(
        stationIds = stationDict['DatasetExternalID'],
        networkCds = ["SNTL","SNOW","SCAN"],
        logicalAnd = True
    )
    # Set the station parameters to download the data
    if stationDict['DatasetParameter'] == 'Snow Water Equivalent':
        soilFlag = False
        param_db_name = 'WTEQ'
        param_unit = 'inches'
        if stationDict['DatasetType'] == 'SNOTEL':
            duration = 'DAILY'
        elif stationDict['DatasetType'] == 'SNOWCOURSE':
            duration = 'SEMIMONTHLY'
        else:
            pass

    elif stationDict['DatasetParameter'] == 'Precipitation':
        soilFlag = False
        param_db_name = 'PRCP'
        param_unit = 'inches'
        duration = 'DAILY'

    
    elif stationDict['DatasetParameter'] == 'Soil Moisture':
        soilFlag = True
        param_db_name = 'SMS'
        param_unit = 'pct'

    # If the parameter is a soil moisture, we need to get all the depths
        elements = NRCS.service.getStationElements(
            stationTriplet = triplet[0]
        )
        soil_depths = []
        for e in elements:
            if e['elementCd'] == 'SMS':
                soil_depths.append(float(e['heightDepth']['value']))
        soil_depths = list(set(soil_depths))

    else:
        soilFlag = False
        return 

    # Create a dataframe to store the data
    df = pd.DataFrame(index = pd.date_range(startDate, endDate)) # Create a dataframe to store values
    
    # Get all the data for SOIL stations and return in a dataframe
    if soilFlag:
        depth = str(soil_depths[0])
        data = NRCS.service.getData(
            stationTriplets = triplet[0],
            elementCd = param_db_name,
            ordinal = "1",
            heightDepth = {
                "value" : str(depth),
                "unitCd" : 'in'
            },
            getFlags = 'true',
            duration = 'DAILY',
            beginDate = datetime.strftime(startDate, '%Y-%m-%d'),
            endDate = datetime.strftime(endDate, '%Y-%m-%d'),
            alwaysReturnDailyFeb29 = 'false')
        actualStartDate = data[0]['beginDate']
        actualEndDate = data[0]['endDate']
        df2 = pd.DataFrame(index = pd.date_range(actualStartDate,actualEndDate))
        df2['SNOTEL | ' + stationDict['DatasetName'] + ' | ' + stationDict['DatasetParameter'] + ' | ' + str(depth) + ' in. | ' + param_unit] = [pd.to_numeric(value, errors='coerce') for value in data[0]['values']]
        df2 = df2[~df2.index.duplicated(keep='first')] # Remove duplicates from the dataset
        df2 = df2[~df2.index.isnull()]
        df = pd.concat([df, df2], axis = 1)
        return df.round(3)

    # Get all the data for SWE and PRECIP staitons and store in a dataframe
    else:
        data = NRCS.service.getData(
            stationTriplets = triplet[0],
            elementCd = param_db_name,
            ordinal = "1",
            getFlags = 'true',
            duration = duration,
            beginDate = datetime.strftime(startDate, '%Y-%m-%d'),
            endDate = datetime.strftime(endDate, '%Y-%m-%d'),
            alwaysReturnDailyFeb29 = 'false')
        
        if stationDict['DatasetType'] == 'SNOWCOURSE':
            df2 = pd.DataFrame(index=pd.to_datetime(data[0]['collectionDates']))
        else:
            actualStartDate = data[0]['beginDate']
            actualEndDate = data[0]['endDate']
            if actualStartDate != None or actualEndDate != None:
                df2 = pd.DataFrame(index = pd.date_range(actualStartDate,actualEndDate))
            else:
                df2 = pd.DataFrame()
        values = [pd.to_numeric(value, errors='coerce') for value in data[0]['values']]
        df2['SNOTEL | ' + stationDict['DatasetName'] + ' | ' + stationDict['DatasetParameter'] + ' | ' + param_unit] = values
        df2 = df2[~df2.index.duplicated(keep='last')] # Remove duplicates from the dataset
        df2 = df2[~df2.index.isnull()]
        df = pd.concat([df, df2], axis = 1)

        return df.round(3)
