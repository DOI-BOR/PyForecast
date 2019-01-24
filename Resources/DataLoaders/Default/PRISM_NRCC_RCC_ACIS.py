# Script Name:      PRISM_NRCC_RCC_ACIS.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      A Dataloader for PRISM and NRCC Gridded datasets.

# Function takes the stationDict entry for the station in question
# along with datetime formatted dates and returns a datatable with columns (date, data)

# Import libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

def dataLoader(stationDict, startDate, endDate):

    # Get the stationID ( the HUC )
    stationID = stationDict['ID']

    # Get the parameter Code
    pcode = stationDict['Parameter']

    # Get the grid type
    grid = stationDict['TYPE']

    # First, we need to get the Bounding Box associated with the HUC

    # Generate the POST request
    baseUrl = "http://data.rcc-acis.org/General/basin"

    # Set the parameters
    params = {
        "id":str(stationID),
        "meta":"id,bbox"
    }

    # Get the BBOX:
    hucBBOX = requests.post(baseUrl, params).json()
    hucBBOX = hucBBOX['meta'][0]['bbox']
    hucBBOX = [str(coord) for coord in hucBBOX]

    # Construct the data web service call
    baseUrl = "http://data.rcc-acis.org/GridData"
    if grid == 'NRCC':
        gridNum = '1'
    else:
        gridNum = '21'
        if startDate < pd.to_datetime('1981-01-01'):
            startDate = pd.to_datetime('1981-01-01')

    if pcode == 'Precipitation':
        name = 'pcpn'
        unit = 'inches'
    else:
        name = 'avgt'
        unit = 'degF'
    params = {
        "bbox":",".join(hucBBOX),
        "sdate":datetime.strftime(startDate, '%Y%m%d'),
        "edate":datetime.strftime(endDate, "%Y%m%d"),
        "grid":gridNum,
        "elems": [{
            "name": name,
            "area_reduce":"basin_mean"
        }]
    }

    # Get the data
    data = requests.post(baseUrl, json=params)
    if data.status_code != 200:
        return pd.DataFrame()
    data = data.json() 

    dataPoints = []
    for i,datapoint in enumerate(data['data']):
        if datapoint[1] != {}:
            dataPoints.append(datapoint[1][stationID])
        else:
            dataPoints.append(np.nan)

    # Parse into dataframe
    df = pd.DataFrame(pd.to_numeric(dataPoints), columns=[grid + ' | ' + stationID + ' | ' + pcode + ' | ' + unit], index=pd.date_range(startDate, endDate))

    # Return the data
    return df