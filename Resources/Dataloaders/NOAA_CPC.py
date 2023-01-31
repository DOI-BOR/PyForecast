import pandas as pd
from datetime import datetime
import numpy as np


class Dataloader(object):

  NAME = "NOAA-CPC"
  DESCRIPTION = "USBR Missouri Basin HydroMet System. Requires a valid HydroMet Site ID and Parameter Code."

  def load(self, dataset, date1, date2):

    if dataset.external_id == 'MENSO':
      url = "https://psl.noaa.gov/enso/mei/data/meiv2.data"
      df = pd.read_csv(url, skiprows=1, names=['year','1','2','3','4','5','6','7','8','9','10','11','12'], sep='\s+', error_bad_lines=False)
      lastRow = df.index[df['year']=='Multivariate'].tolist()[0] -1
      df = df[df.index<lastRow]
      df = df.melt(id_vars=['year'],var_name='month')
      dates = [str(df['year'][i])+'-'+str(df['month'][i]) for i in df.index]
      df.set_index(pd.DatetimeIndex(pd.to_datetime(dates, format='%Y/%m')), inplace=True)
      df.sort_index(inplace=True)
      df['value'] = pd.to_numeric(df['value'])
      df.replace(to_replace=-999.00, value=np.nan, inplace=True)
      df = pd.DataFrame(df['value'])
      df = df.asfreq('D')
      lastDate = list(df.index)[-1]
      if lastDate.month in [1,3,5,7,8,10,12]:
          endDay = 31
      elif lastDate.month == 2:
          endDay = 28
      else:
          endDay = 30

      for day in range(lastDate.day,endDay + 1):
          df.loc[datetime(lastDate.year, lastDate.month, day)] = df.loc[lastDate]

      df.fillna(method='ffill',inplace=True)
      df = df[df.index>=date1]
      df = df[df.index<=date2]
      df.columns = [f'{dataset.guid}'] +list(df.columns[1:])
      return df.iloc[:,0]
      
    elif dataset.external_id == 'PNA':
      url = "http://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.pna.monthly.b5001.current.ascii"
      dataMonth = pd.read_csv(url, names = ['year','month','PNA | Indice'], sep='\s+')
      dataMonth['day'] = len(dataMonth.index)*[1]
      datetimes = pd.to_datetime(dataMonth[['year','month','day']])
      dataMonth.set_index(pd.DatetimeIndex(datetimes), inplace=True)
      del dataMonth['year'], dataMonth['month'], dataMonth['day']
      dataMonth.loc[dataMonth.index[-1] + pd.DateOffset(months=1) - pd.DateOffset(days=1)] = [np.nan]
      dataMonth = dataMonth.resample('D').mean()
      dataMonth = dataMonth.fillna(method='ffill')
      dataMonth = dataMonth[dataMonth.index >= date1]
      df = pd.DataFrame(index = pd.date_range(date1, date2))
      df = pd.concat([df, dataMonth], axis = 1)
      df.columns = [f'{dataset.guid}'] +list(df.columns[1:])
      return df.iloc[:,0]
      
    else:
      return pd.Series()
