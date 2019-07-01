# Script Name:      NCDC.py
# Script Author:    Jon Rocha, Civil Engineer
# Description:      A Dataloader for NCDC Data.

# Function takes the stationDict entry for the station in question
# along with datetime formatted dates and returns a datatable with columns (date, data, flag)

# Import Libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime


def dataLoader(stationDict, startDate, endDate):

    # Get the station ID
    stationID = stationDict['ID']

    # Get the pcode
    pcode = stationDict['Parameter']

    # Create the output dataframe
    dfOut = pd.DataFrame(index=pd.date_range(startDate, endDate))

    # Download instructions for NCDC data:
    t1 = datetime.strftime(startDate, '%Y-%m-%d' )
    t2 = datetime.strftime(endDate, '%Y-%m-%d' )
    url = "https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations={0}&dataTypes={1}&startDate={2}&endDate={3}&boundingBox=90,-180,-90,180&units=standard"
    url = url.format(stationID, pcode, t1, t2)
    print(url)

    # Download the data and check for a valid response
    response = requests.get(url)
    if response.status_code == 200:
        pass
    else:
        return pd.DataFrame()

    # Parse the data into a dataframe
    df = pd.read_csv(url, parse_dates=['DATE'])  # Read the data into a dataframe
    df.set_index(pd.DatetimeIndex(pd.to_datetime(df['DATE'])),
                 inplace=True)  # Set the index to the datetime column
    del df['DATE']  # Delete the redundant datetime column
    del df['STATION']  # Delete the station column
    df = df[~df.index.duplicated(keep='first')]  # Remove duplicates from the dataset
    df = df[~df.index.isnull()]
    df.columns = ['NCDC | ' + stationID + ' | Weather | X']

    # Send the data to the output dataframe
    dfOut = pd.concat([df, dfOut], axis=1)
    dfOut = dfOut.round(3)
    print(dfOut)

    # Return the dataframe
    return dfOut


