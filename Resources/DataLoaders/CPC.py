# Script Name:      CPC_CLIMATE.py
# Script Author:    Kevin Foley, Civil Engineer
# Description:      A Dataloader for climate datasets from the CPC webpage.

# Function takes the stationDict entry for the station in question
# along with datetime formatted dates and returns a datatable with columns (date, data)

import requests
import pandas as pd
from io import StringIO
import numpy as np


def dataLoader(stationDict, startDate, endDate):
    """
    This dataloader loads data from NOAA's Climate Prediction Center (CPC). The datasets
    are climate indices that are useful for long-range precipitation forecasting. 
    The "DatasetExternalID" option specifies which dataset should be downloaded. Valid 
    paramters are: 
    'nino3.4' - Nino 3.4 Sea Surface Temperature Anomaly (aka ENSO)
    'pna' - Pacific North American Index
    'amo' - Atlantic Multidecadal Oscillation
    'pdo' - Pacific Decadal Oscillation
    DEFAULT OPTIONS
    DatasetExternalID: nino3.4
    """

    # Figure out which indice we are downloading
    stationNum = stationDict['DatasetExternalID']

    # Grab the ENSO Nino3.4 data (SST and Anom)
    if stationNum == 'nino3.4':

        # We'll get as much weekly data as we can, then backfill with monthly data
        # Here are the relevant URLs
        urlMonth = 'http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices'
        urlWeek = 'http://www.cpc.ncep.noaa.gov/data/indices/wksst8110.for'

        # Get the data
        dataMonth = requests.get(urlMonth)
        dataWeek = requests.get(urlWeek)

        # Process the monthly data
        dataMonth = StringIO(dataMonth.content.decode('utf-8'))
        dataMonth = dataMonth.readlines()
        timestamps = []
        anoms = []
        for line in dataMonth[1:]:
            values = line.split()
            year = str(values[0])
            month = '0'+str(values[1])
            timestamps.append(pd.to_datetime(year + month[-2:] + '15', format='%Y%m%d'))
            anoms.append(float(values[9]))

        dfMonth = pd.DataFrame(np.array(anoms).T, index = timestamps, columns = ['Nino3.4 ANOM | Indice | degC'])

        # Process the weekly data
        dataWeek = StringIO(dataWeek.content.decode('utf-8'))
        dataWeek = dataWeek.readlines()
        timestamps = []
        anoms = []
        for line in dataWeek[4:]:
            values = line.split('     ')
            timestamps.append(pd.to_datetime(values[0]))
            anoms.append(float(values[3][4:]))

        dfWeek = pd.DataFrame(np.array(anoms).T, index = timestamps, columns = ['Nino3.4 ANOM | Indice | degC'])

        # Merge the 2 datasets, keeping all the weekly data and cutting some monthly
        dfMonth = dfMonth[dfMonth.index < dfWeek.index[0]]

        dfCombined = pd.concat([dfMonth, dfWeek]).resample('D').mean()
        dfCombined = dfCombined.fillna(method='ffill')
        dfCombined = dfCombined[dfCombined.index >= startDate]

        df = pd.DataFrame(index = pd.date_range(startDate, endDate))
        df = pd.concat([df, dfCombined], axis = 1)
        df = df[df.index >= startDate]
        df = df[df.index <= endDate]
        
        # Return the correct dataset
        return df

    # Otherwise, we'll grab the PNA dataset
    elif stationNum == 'pna':
        url = "http://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.pna.monthly.b5001.current.ascii"
        dataMonth = pd.read_csv(url, names = ['year','month','PNA | Indice'], sep='\s+')
        dataMonth['day'] = len(dataMonth.index)*[1]
        datetimes = pd.to_datetime(dataMonth[['year','month','day']])
        dataMonth.set_index(pd.DatetimeIndex(datetimes), inplace=True)
        del dataMonth['year'], dataMonth['month'], dataMonth['day']
        dataMonth = dataMonth.resample('D').mean()
        dataMonth = dataMonth.fillna(method='ffill')
        dataMonth = dataMonth[dataMonth.index >= startDate]
        df = pd.DataFrame(index = pd.date_range(startDate, endDate))
        df = pd.concat([df, dataMonth], axis = 1)
        return df

    elif stationNum == 'amo':
        """
        AMO Index"""
        url = 'https://www.esrl.noaa.gov/psd/data/correlation/amon.us.long.data'
        df = pd.read_csv(url, skiprows=1, names=['year','1','2','3','4','5','6','7','8','9','10','11','12'], sep='\s+')
        lastRow = df.index[df['year']=='AMO'].tolist()[0] -1
        df = df[df.index<lastRow]
        df = df.melt(id_vars=['year'],var_name='month')
        dates = [str(df['year'][i])+'-'+str(df['month'][i]) for i in df.index]
        df.set_index(pd.DatetimeIndex(pd.to_datetime(dates, format='%Y/%m')), inplace=True)
        df.sort_index(inplace=True)
        df['value'] = pd.to_numeric(df['value'])
        df.replace(to_replace=-99.990, value=np.nan, inplace=True)
        df = pd.DataFrame(df['value'])
        df = df.asfreq('D')
        df.fillna(method='ffill',inplace=True)
        df = df[df.index>=startDate]
        df = df[df.index<=endDate]

        return df


    # elif stationNum == 5:
    #     """
    #     Mauna Loa CO2 Trend
    #     """
    #     url = 'ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_mm_mlo.txt'
    #     df = pd.read_csv(url, index_col=False, sep='\s+', comment='#', names=['year','month','time','average_molFrac','interpolated_molFrac','trend','days'])
    #     dates = [str(df['year'][i])+'-'+str(df['month'][i]) for i in df.index]
    #     df.set_index(pd.DatetimeIndex(pd.to_datetime(dates, format='%Y/%m')), inplace=True)
    #     df = pd.DataFrame(df['trend'])
    #     df = df.asfreq('D')
    #     df.fillna(method='ffill',inplace=True)
    #     df = df[df.index>=startDate]
    #     df = df[df.index<=endDate]
    #     return df

    elif stationNum == 'pdo':
        """
        Pacific Multidecadal Oscillation (PDO)
        """
        url = "https://www.ncdc.noaa.gov/teleconnections/pdo/data.json"
        response = requests.get(url)
        response = response.json()
        data = response['data']
        dates = [pd.to_datetime(i, format='%Y%m') for i in list(data.keys())]
        values = [float(val) for val in list(data.values())]
        values = [np.nan if x == -99.99 else x for x in values]
        df = pd.DataFrame(values, index=dates, columns=['PDO'])
        df = df.asfreq('D')
        df.fillna(method='ffill', inplace=True)
        df = df[df.index>=startDate]
        df = df[df.index<=endDate]
        return df

    else:
        return pd.DataFrame()
        