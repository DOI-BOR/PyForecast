import pandas as pd

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
    
    else:
      return pd.Series()



