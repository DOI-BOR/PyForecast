import pandas as pd
import numpy as np
import requests
from io import StringIO
from datetime import datetime
from html.parser import HTMLParser

URL = "https://wrcc.dri.edu/wwdt/time/regionsAll/?region={REGION}&variable={VARIABLE}"

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
    """

    # Get the info
    stationID = stationDict['DatasetExternalID']
    datasetType = stationDict['DatasetType']

    def PDSILoader2(stationID, startDate, endDate, var):
        
        if len(stationID) == 4:
            stationID = stationID[:2] + '00' + stationID[-2:]

        url = URL.format(REGION=stationID, VARIABLE=var)
        r = requests.get(url)
        text = r.text.replace("</div>\n        \n          <div>", "\n")
        text = text[text.index("__\n")+3:text.index("</div")]
        text = StringIO(text)
        df = pd.read_csv(text)
        df = df.melt(id_vars=['Year'])
        df.index = pd.DatetimeIndex(pd.to_datetime(df['Year'].astype(str) + df['variable']))
        del df['Year']
        del df['variable']
        df = df.replace(to_replace = -9999, value = np.nan)
        df = df.sort_index()
        df = df.asfreq('D')
        df.fillna(method='ffill',inplace=True)
        df = df[df.index >= startDate]
        df = df[df.index <= endDate]
        print(df)
        return df

    def PDSILoader(stationID, startDate, endDate):
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
    
    def SPILoader(stationID, avgeringPeriod, startDate, endDate):
        url = "https://www.ncdc.noaa.gov/monitoring-content/temp-and-precip/drought/nadm/indices/spi/data/{0}-spi-us.txt".format(avgeringPeriod)
        df = pd.read_csv(url, sep='\s+', header=None, names=['DIVNO','Null','Year','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'])
        del df['Null']
        df = df.melt(id_vars=['DIVNO','Year'], var_name=['Month'])
        new = df['DIVNO'].str.split('DIV0',n=1,expand=True)
        df['DIVNO'] = new[1]
        df = df[df['DIVNO'] == str(stationID)]
        df.set_index(pd.DatetimeIndex(pd.to_datetime((df.Year.apply(str) + df.Month), format='%Y%b')), inplace=True)
        df = df[df.index >= startDate]
        df = df[df.index <= endDate]
        df.replace(to_replace=-99.99, value=np.nan, inplace=True)
        del df['DIVNO'],df['Year'],df['Month']
        df.sort_index(inplace=True)
        df = df.asfreq('D')
        df.fillna(method='ffill',inplace=True)
        return df
        

    # Load PDSI or SPI data
    if datasetType == 'PDSI':
        data = PDSILoader2(stationID, startDate, endDate, var=7)
    else:
        avgPeriod = stationDict['DatasetParameterCode']
        data = PDSILoader2(stationID, startDate, endDate, var=4)

    return data
