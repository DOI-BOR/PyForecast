import requests
from io import StringIO
import pandas as pd
from datetime import datetime

class Dataloader(object):

  NAME = "USBR"
  DESCRIPTION = ("USBR Missouri Basin HydroMet System. Requires a valid "
                 "HydroMet Site ID and Parameter Code.")

  def load(self, dataset, date1, date2):

    if 'MB' in dataset.agency or 'GP' in dataset.agency:

      url = ('https://www.usbr.gov/gp-bin/webarccsv.pl?'
             f'parameter={dataset.external_id}%20{dataset.param_code}&'
             f'syer={date1.year}&smnth={date1.month}&sdy={date1.day}&'
             f'eyer={date2.year}&emnth={date2.month}&edy={date2.day}&'
             f'format=4')
      df = pd.read_csv(url, index_col=0, parse_dates=True,
                       na_values=['MISSING', 'NO RECORD   ', '998877'],
                       header=0, names=[f'{dataset.guid}'])

      df = df.loc[date1:date2]

      return df.iloc[:, 0]
    
    elif 'PN' in dataset.agency or 'CPN' in dataset.agency:

        # Download instructions for daily PN data:
        url = ('https://www.usbr.gov/pn-bin/daily.pl?'
               f'station={dataset.external_id}&pcode={dataset.param_code}&'
               f'year={date1.year}&month={date1.month}&day={date1.day}&'
               f'year={date2.year}&month={date2.month}&day={date2.day}&'
               f'format=csv')

        # Download instructions for monthly PN data:
        if 'monthly2daily' in dataset.opts:
            url = ('https://www.usbr.gov/pn-bin/monthly.pl?'
                   f'parameter={dataset.external_id}%20{dataset.param_code}&'
                   f'start={datetime.strftime(date1, '%Y-%m-%d')}&'
                   f'end={datetime.strftime(date1, '%Y-%m-%d')}&'
                   f'flags=false')

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
        if 'monthly2daily' in dataset.opts:
            #print('INFO: Monthly data converted to daily')
            df[df.columns[0]] = pd.to_numeric(df[df.columns[0]],errors='coerce') #convert values to floats
            df = ConvertMonthlyToDaily(df)
        df = df[not df.index.isna()]
        df.columns = ['USBR | ' + dataset.external_id + ' | ' + dataset.param_code + ' | ' +
                      str(dataset.display_unit).upper()]
        df = df.round(3)

        # Return the dataframe
        return df

    else:
      return pd.Series()


def ConvertMonthlyToDaily(df: pd.DataFrame):
    # resample by filling forward
    df_daily = pd.DataFrame(df[df.columns[0]].resample('D').ffill())
    # get max day array
    df_daily_max_days = df_daily.index.days_in_month
    # divide monthly value by n-days - assumes monthly value is accumulated uniformly during the month
    df_daily[df_daily.columns[0]] = df_daily[df_daily.columns[0]] / df_daily_max_days

    return df_daily

