# Script Name:      USBR.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      A Dataloader for USBR Data. Different REST endpoints are used for 
#                   GP / PN / LC / UC / MP regions.

# Function takes the stationDict entry for the station in question
# along with datetime formatted dates and returns a datatable with columns (date, data, flag)

# Import Libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime

def dataLoader(dataset, startDate, endDate):
    """
    This dataloader loads data from USBR Rest endpoints. The required parameters
    are "Dataset ID" which specifies the hydromet ID and the "DatasetParameterCode" which
    specifies the hydromet PCODE.  "Dataset Agency" specifies the office to retrieve 
    data from. Available options for 'Dataset Agency' are 'USBR GP' and 'USBR PN'
    DEFAULT OPTIONS
    DatasetParameterCode: IN
    """

    # Figure out which region the station belongs to:
    region = dataset['DatasetAgency'].split(' ')[1].strip(' ')

    # Get the station ID
    stationID = dataset['DatasetExternalID']

    # Get the pcode
    pcode = dataset['DatasetParameterCode']

    # ---- GP REGION -------
    if region == 'GP':

        # download instructions for GP Region
        syear = datetime.strftime(startDate, '%Y')
        smonth = datetime.strftime(startDate, '%m')
        sday = datetime.strftime(startDate, '%d')
        eyear = datetime.strftime(endDate, '%Y')
        emonth = datetime.strftime(endDate, '%m')
        eday = datetime.strftime(endDate, '%d')
        url = ("https://www.usbr.gov/gp-bin/arcread.pl?st={0}&by={1}&bm={2}&bd={3}&ey={4}&em={5}&ed={6}&pa={7}&json=1")
        url = url.format(stationID, syear, smonth, sday, eyear, emonth, eday, pcode)

        # Download the data and check for valid response
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data == []:
                return pd.DataFrame() # If the data is empty, return an empty dataframe
        else:
            return pd.DataFrame() # If we can't retrieve the data, return an empty dataframe
        
        # Parse the data into a dataframe
        dataValues = data['SITE']['DATA'] # Load the data into a list of dicts
        df = pd.DataFrame(dataValues, index = pd.date_range(startDate, endDate)) # Load into dataframe
        del df['DATE'] # Delete the date column
        df[pcode.upper()] = pd.to_numeric(df[pcode.upper()])
        df.replace(to_replace=998877, value=np.nan, inplace=True) # Replace missing data with NaN's
        df.replace(to_replace=998877.0, value=np.nan, inplace=True) # Replace missing data with NaN's
        df = df[~df.index.duplicated(keep='first')] # Remove duplicates from the dataset
        df = df[~df.index.isnull()]
        df.columns = ['USBR | ' + stationID + ' | Inflow | CFS']

        # Return the dataframe
        return df.round(3)

    # ---- PN REGION ------
    elif region == 'PN':


        # Download instructions for PN data:
        syear = datetime.strftime(startDate, '%Y')
        smonth = datetime.strftime(startDate, '%m')
        sday = datetime.strftime(startDate, '%d')
        eyear = datetime.strftime(endDate, '%Y')
        emonth = datetime.strftime(endDate, '%m')
        eday = datetime.strftime(endDate, '%d')
        url = "https://www.usbr.gov/pn-bin/daily.pl?station={0}&format=csv&year={1}&month={2}&day={3}&year={4}&month={5}&day={6}&pcode={7}"
        url = url.format(stationID, syear, smonth, sday, eyear, emonth, eday, pcode)

        # Download the data and check for a valid response
        response = requests.get(url)
        if response.status_code == 200:
            pass
        else:
            return pd.DataFrame()
        
        # Parse the data into a dataframe
        df = pd.read_csv(url, parse_dates=['DateTime']) # Read the data into a dataframe
        df.set_index(pd.DatetimeIndex(pd.to_datetime(df['DateTime'])), inplace=True) # Set the index to the datetime column
        del df['DateTime'] # Delete the redundant datetime column
        df = df[~df.index.duplicated(keep='first')] # Remove duplicates from the dataset
        df = df[~df.index.isnull()]
        df.columns = [stationID]

        # Return the dataframe
        return df.round(3)

    else:
        pass

