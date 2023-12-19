import pandas as pd
from datetime import datetime
import requests
import numpy as np


class Dataloader(object):

  NAME = "USGS_NWIS"
  DESCRIPTION = ""

  def load(self, dataset, date1, date2):

    url = ('https://waterservices.usgs.gov/nwis/dv/?format=json' +
            # Specify the sites to download
            '&sites=' + dataset.external_id +
            # Specify the start date
            '&startDT=' + datetime.strftime( date1, '%Y-%m-%d' ) +
            #Specify the end data
            '&endDT=' + datetime.strftime( date2, '%Y-%m-%d' ) +
            # Specify that we want streamflow
            '&parameterCd=' + dataset.param_code + 
            # Specify that we want daily average streamflow
            '&statCd=00003' +
            # Allow all sites
            '&siteStatus=all' )
    
    # Get the data
    response = requests.get(url)

    # Check the status code
    if response.status_code != 200:
        return 
    else:
        response = response.json()
    
    # Create a dataframe from the data
    df = pd.DataFrame(response['value']['timeSeries'][0]['values'][0]['value'])

    # Set the index to the dateTime index
    df.set_index(pd.DatetimeIndex(pd.to_datetime(df['dateTime'])), inplace = True)
    del df['dateTime'] # Delete the redundant column
    del df['qualifiers']

    # Replace missing data with NaN's
    df['value'].replace(to_replace = '-999999', value = np.nan, inplace = True)

    # Convert to numeric
    df['value'] = pd.to_numeric(df['value'])
    
    # Remove any duplicate data in the dataset
    df = df[~df.index.duplicated(keep='last')] # Remove duplicates from the dataset
    df = df[~df.index.isnull()]

    # Rename the columns
    df.columns = [f'{dataset.guid}']
    # Return the data frame
    return df.sort_index()



