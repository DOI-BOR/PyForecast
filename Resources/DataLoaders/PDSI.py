import pandas as pd
import numpy as np
import requests
from datetime import datetime
from html.parser import HTMLParser

"""
This dataloader loads Palmer Drought Severity Index data from the CPC.
"""
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            if 'climdiv-pdsidv' in attrs[0][1]:
                self.link_extension = attrs[0][1]

def dataLoader(stationDict, startDate, endDate):
    """
    This dataloader loads Palmer Drought severity index data from NOAA's 
    climate prediction center. The only parameter that must be specified
    is the "DatasetExternalID". Valid parameter options are 3-digit or 4-digit 
    climate division numbers. 
    DEFAULT OPTIONS
    """

    # Get the info
    stationID = stationDict['DatasetExternalID']

    # Find the correct link
    url = 'https://www1.ncdc.noaa.gov/pub/data/cirs/climdiv'
    response = requests.get(url)
    parser = MyHTMLParser()
    parser.feed(response.text)

    # Get the data
    url = 'https://www1.ncdc.noaa.gov/pub/data/cirs/climdiv/{0}'.format(parser.link_extension)

    df = pd.read_csv(url)

    df = pd.read_csv(url, names=['code','1','2','3','4','5','6','7','8','9','10','11','12'], index_col=False, sep='\s+')
    df['code'] = df['code'].astype(str)
    li = [df['code'][i][:-6] for i in df.index]
    yr = [int(df['code'][i][-4:]) for i in df.index]
    df['divID'] = li
    df['year'] = yr
    df = df[df['divID'] == stationID]
    del df['code']
    df = df.melt(id_vars=['divID','year'], var_name=['month'])
    dateList = [pd.to_datetime(str(df['year'][i]) + '-' + str(df['month'][i]), format='%Y-%m') for i in df.index]
    df.set_index(pd.DatetimeIndex(dateList), inplace=True)
    df = df[df.index >= startDate]
    df = df[df.index <= endDate]
    df.replace(to_replace=-99.99, value=np.nan, inplace=True)
    del df['divID'], df['year'], df['month']
    df.sort_index(inplace=True)
    df = df.asfreq('D')
    df.fillna(method='ffill',inplace=True)

    return df

