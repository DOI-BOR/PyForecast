import pandas as pd
from datetime import datetime

class Dataloader(object):

  NAME = "USBR"
  DESCRIPTION = "USBR Missouri Basin HydroMet System. Requires a valid HydroMet Site ID and Parameter Code."

  def load(self, dataset, date1, date2):

    if 'MB' or 'GP' in dataset.agency:

      url = f'https://www.usbr.gov/gp-bin/webarccsv.pl?'+ \
            f'parameter={dataset.external_id}%20{dataset.param_code}&' + \
            f'syer={date1.year}&smnth={date1.month}&sdy={date1.day}&' + \
            f'eyer={date2.year}&emnth={date2.month}&edy={date2.day}&format=4'
      df = pd.read_csv(url, index_col=0, parse_dates=True, na_values=['MISSING', 'NO RECORD   ', 998877], header=0, names=[f'{dataset.guid}'])

      df = df.loc[date1:date2]

      return df.iloc[:, 0]
    
    elif 'PN' or 'CPN' in dataset.agency:

        # Download instructions for daily PN data:
        syear = datetime.strftime(startDate, '%Y')
        smonth = datetime.strftime(startDate, '%m')
        sday = datetime.strftime(startDate, '%d')
        eyear = datetime.strftime(endDate, '%Y')
        emonth = datetime.strftime(endDate, '%m')
        eday = datetime.strftime(endDate, '%d')
        url = "https://www.usbr.gov/pn-bin/daily.pl?station={0}&format=csv&year={1}&month={2}&day={3}&year={4}&month={5}&day={6}&pcode={7}"
        url = url.format(dataset.external_id, syear, smonth, sday, eyear, emonth, eday, dataset.param_code)

        # Download instructions for monthly PN data:
        if 'monthly2daily' in opts:
            url = "https://www.usbr.gov/pn-bin/monthly.pl?parameter={0}%20{7}&syer={1}&smnth={2}&sdy={3}&eyer={4}&emnth={5}&edy={6}&format=csv"
            url = url.format(stationID, syear, smonth, sday, eyear, emonth, eday, pcode)

        # Download the data and check for a valid response
        response = requests.get(url)
        if response.status_code == 200:
            response = response.text
        else:
            return pd.DataFrame()
        
        # Parse the data into a dataframe
        df = pd.read_csv(StringIO(response), parse_dates=['DateTime'])  # Read the data into a dataframe
        df.set_index(pd.DatetimeIndex(pd.to_datetime(df['DateTime'])), inplace=True) # Set the index to the datetime column
        del df['DateTime'] # Delete the redundant datetime column
        df = df[~df.index.duplicated(keep='first')] # Remove duplicates from the dataset
        if 'monthly2daily' in opts:
            #print('INFO: Monthly data converted to daily')
            df[df.columns[0]] = df[df.columns[0]].str.replace('[^\d.]', '') #remove data flags
            df[df.columns[0]] = pd.to_numeric(df[df.columns[0]],errors='coerce') #convert values to floats
            df = ConvertMonthlyToDaily(df)
        df = df[~df.index.isnull()]
        df.columns = ['USBR | ' + stationID + ' | ' + dataset.DatasetParameter + ' | ' +
                      str(dataset.DatasetUnits).upper()]
        df = df.round(3)

        # Return the dataframe
        return df

    else:
      return pd.Series()



