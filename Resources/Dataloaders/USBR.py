from datetime import datetime
from io import StringIO

import pandas as pd
import urllib3


class Dataloader(object):
    NAME = "USBR"
    DESCRIPTION = ("USBR Missouri Basin HydroMet System. Requires a valid "
                   "HydroMet Site ID and Parameter Code.")

    def load(self, dataset, date1, date2):

        if 'MB' in dataset.agency or 'GP' in dataset.agency:

            url = ('https://www.usbr.gov/gp-bin/webarccsv.pl?'
                   f'parameter={dataset.external_id}%20{dataset.param_code}'
                   f'&syer={date1.year}&smnth={date1.month}&sdy={date1.day}'
                   f'&eyer={date2.year}&emnth={date2.month}&edy={date2.day}'
                   f'&format=4')
            df = pd.read_csv(url, index_col=0, parse_dates=True,
                             na_values=['MISSING', 'NO RECORD   ', '998877'],
                             header=0, names=[f'{dataset.guid}'])

            df = df.loc[date1:date2]

            return df.iloc[:, 0]

        elif 'PN' in dataset.agency or 'CPN' in dataset.agency:

            # Download instructions for daily PN data:
            base_url = 'https://www.usbr.gov/pn-bin/daily.pl'
            params = {
                'list': f'{dataset.external_id} {dataset.param_code}',
                'start': datetime.strftime(date1, '%Y-%m-%d'),
                'end': datetime.strftime(date2, '%Y-%m-%d'),
                'format': 'csv'
            }

            # Download instructions for monthly PN data:
            if 'monthly2daily' in dataset.opts:
                base_url = 'https://www.usbr.gov/pn-bin/monthly.pl'
                params['flags'] = 'false'

            # Download the data and check for a valid response
            http = urllib3.PoolManager()
            response = http.request('GET', base_url, fields=params)
            if response.status == 200:
                data = response.data.decode('utf-8')
            else:
                return pd.Series()

            # Parse the data into a dataframe
            df = pd.read_csv(
                StringIO(data), parse_dates=['DateTime'], index_col=['DateTime'])

            # convert to monthly if needed
            if 'monthly2daily' in dataset.opts:
                df = ConvertMonthlyToDaily(df)

            column_name = (
                'USBR'
                f' | {dataset.external_id.upper()}'
                f' | {dataset.param_code.upper()}'
                f' | {str(dataset.display_unit).upper()}'
            )
            df.columns = [column_name]
            df = df.dropna()
            df = df.round(3)

            return df

        else:
            return pd.Series()


def ConvertMonthlyToDaily(df: pd.DataFrame) -> pd.DataFrame:
    # convert to daily frequency and fill forward
    df_daily = df.asfreq('D', method='ffill')
    # divide monthly value applied to each day by the number of days in the month
    # NOTE: this assumes the monthly value was accumulated uniformly during the month
    df_daily = df_daily / df_daily.index.days_in_month

    return df_daily
