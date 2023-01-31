import pandas as pd
import requests
from datetime import datetime
import numpy as np


class Dataloader(object):

  NAME = "RCC-ACIS"
  DESCRIPTION = "USBR Missouri Basin HydroMet System. Requires a valid HydroMet Site ID and Parameter Code."

  def load(self, dataset, date1, date2):

    # Get the stationID ( the HUC )
    stationID = dataset.external_id

    # Get the parameter Code
    pcode = dataset.param_code

    # Get the grid type
    grid = dataset.agency

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
        if date1 < pd.to_datetime('1981-01-01'):
            date1 = pd.to_datetime('1981-01-01')

    if pcode == 'prec':
        name = 'pcpn'
        unit = 'inches'
    else:
        name = 'avgt'
        unit = 'degF'
    params = {
        "bbox":",".join(hucBBOX),
        "sdate":datetime.strftime(date1, '%Y%m%d'),
        "edate":datetime.strftime(date2, "%Y%m%d"),
        "grid":gridNum,
        "elems": [{
            "name": name,
            "area_reduce":"basin_mean"
        }]
    }

    # Get the data
    data = requests.post(baseUrl, json=params, timeout=60)
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
    df = pd.DataFrame(pd.to_numeric(dataPoints), columns=[dataset.guid], index=pd.date_range(date1, date2))

    # Return the data
    return df.round(3).iloc[:,0]



