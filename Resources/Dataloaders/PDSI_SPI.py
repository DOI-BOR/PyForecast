import pandas as pd
import numpy as np
import requests
from io import StringIO

class Dataloader(object):

  NAME = "PDSI_SPI"
  DESCRIPTION = ""

  def load(self, dataset, date1, date2):


    URL = "https://wrcc.dri.edu/wwdt/time/regionsAll/?region={REGION}&variable={VARIABLE}"

    stationID = dataset.external_id

    if len(stationID) == 4:
      stationID = stationID[:2] + '00' + stationID[-2:]

    if dataset.param_code == 'PDSI':
      var = 7
    else:
      var = 4
    
    url = URL.format(REGION=stationID, VARIABLE=var)
    r = requests.get(url, verify=False)
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
    df = df.loc[date1:date2]
    if len(df.columns) > 1:
      df.columns = [f'{dataset.guid}'] + df.columns[1:]
    else:
      df.columns = [f'{dataset.guid}'] 
    return df.iloc[:,0]
