import pandas as pd
import requests
from datetime import datetime
from zeep import Client
from decimal import Decimal


class Dataloader(object):

  NAME = "NRCS_WCC"
  DESCRIPTION = "USBR Missouri Basin HydroMet System. Requires a valid HydroMet Site ID and Parameter Code."

  def load(self, dataset, date1, date2):


    NRCS = Client('https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL')

    # Get the station triplet
    triplet = NRCS.service.getStations(
        stationIds = dataset.external_id,
        networkCds = ["SNTL","SNOW","SCAN"],
        logicalAnd = True
    )
    # Set the station parameters to download the data
    if dataset.parameter== 'Snow Water Equivalent':
        soilFlag = False
        param_db_name = 'WTEQ'
        param_unit = 'inches'
        if triplet[0].split(':')[2] == 'SNTL':
            duration = 'DAILY'
        elif triplet[0].split(':')[2] == 'SNOW':
            duration = 'SEMIMONTHLY'
        else:
            pass

    elif dataset.parameter == 'Precipitation':
        soilFlag = False
        param_db_name = 'PRCP'
        param_unit = 'inches'
        duration = 'DAILY'

    
    elif dataset.parameter == 'Soil Moisture':
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
    df = pd.DataFrame(index = pd.date_range(date1, date2)) # Create a dataframe to store values
    
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
            beginDate = datetime.strftime(date1, '%Y-%m-%d'),
            endDate = datetime.strftime(date2, '%Y-%m-%d'),
            alwaysReturnDailyFeb29 = 'false')
        actualStartDate = data[0]['beginDate']
        actualEndDate = data[0]['endDate']
        df2 = pd.DataFrame(index = pd.date_range(actualStartDate,actualEndDate))
        df2[dataset.guid] = [pd.to_numeric(value, errors='coerce') for value in data[0]['values']]
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
            beginDate = datetime.strftime(date1, '%Y-%m-%d'),
            endDate = datetime.strftime(date2, '%Y-%m-%d'),
            alwaysReturnDailyFeb29 = 'false')
        
        if triplet[0].split(':')[2] == 'SNOW':
            df2 = pd.DataFrame(index=pd.to_datetime(data[0]['collectionDates']))
        else:
            actualStartDate = data[0]['beginDate']
            actualEndDate = data[0]['endDate']
            if actualStartDate != None or actualEndDate != None:
                df2 = pd.DataFrame(index = pd.date_range(actualStartDate,actualEndDate))
            else:
                df2 = pd.DataFrame()
        values = [pd.to_numeric(value, errors='coerce') for value in data[0]['values']]
        df2[dataset.guid] = values
        df2 = df2[~df2.index.duplicated(keep='last')] # Remove duplicates from the dataset
        df2 = df2[~df2.index.isnull()]
        df = pd.concat([df, df2], axis = 1)

        return df.round(3)

