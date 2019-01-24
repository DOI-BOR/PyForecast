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
 
    # Set up the soap service
    NRCS = Client('http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL')

    # Get the station triplet
    triplet = NRCS.service.getStations(
        stationIds = stationDict['ID'],
        networkCds = ["SNTL","SNOW"],
        logicalAnd = True
    )
    # Set the station parameters to download the data
    if stationDict['Parameter'] == 'SWE' or stationDict['Parameter'] == 'SWE_SnowCourse':
        soilFlag = False
        param_db_name = 'WTEQ'
        param_unit = 'inches'
        if stationDict['TYPE'] == 'SNOTEL':
            duration = 'DAILY'
        elif stationDict['TYPE'] == 'SNOWCOURSE':
            duration = 'SEMIMONTHLY'
        else:
            pass

    elif stationDict['Parameter'] == 'Precip':
        soilFlag = False
        param_db_name = 'PRCP'
        param_unit = 'inches'
        duration = 'DAILY'

    
    elif stationDict['Parameter'] == 'SOIL':
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
        df2['SNOTEL | ' + stationDict['Name'] + ' | ' + stationDict['Parameter'] + ' | ' + str(depth) + ' in. | ' + param_unit] = [pd.to_numeric(value, errors='coerce') for value in data[0]['values']]
        df2 = df2[~df2.index.duplicated(keep='first')] # Remove duplicates from the dataset
        df2 = df2[~df2.index.isnull()]
        df = pd.concat([df, df2], axis = 1)
        return df

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
        
        if stationDict['TYPE'] == 'SNOWCOURSE':
            df2 = pd.DataFrame(index=pd.to_datetime(data[0]['collectionDates']))
        else:
            actualStartDate = data[0]['beginDate']
            actualEndDate = data[0]['endDate']
            if actualStartDate != None or actualEndDate != None:
                df2 = pd.DataFrame(index = pd.date_range(actualStartDate,actualEndDate))
            else:
                df2 = pd.DataFrame()
        values = [pd.to_numeric(value, errors='coerce') for value in data[0]['values']]
        print("Values: " + str(len(values)))
        print("Index: " + str(len(df2.index)))
        df2['SNOTEL | ' + stationDict['Name'] + ' | ' + stationDict['Parameter'] + ' | ' + param_unit] = values
        df2 = df2[~df2.index.duplicated(keep='last')] # Remove duplicates from the dataset
        df2 = df2[~df2.index.isnull()]
        df = pd.concat([df, df2], axis = 1)
        return df