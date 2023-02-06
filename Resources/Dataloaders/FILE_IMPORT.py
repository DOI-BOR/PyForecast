import pandas as pd

class Dataloader(object):

  NAME = "Flat File Import"
  DESCRIPTION = "Reads a flat file. See Wiki for flat file formats"

  def load(self, dataset, date1, date2):

    if dataset.file_path.endswith('.csv'):
      df = pd.read_csv(dataset.file_path, index_col=0, usecols=[0,1], header=0, parse_dates=True)
    elif dataset.file_path.endswith('.xlsx'):
      df = pd.read_excel(dataset.file_path, index_col=0, usecols=[0,1], header=0, parse_dates=True)
    else:
      return pd.Series([])
    df.columns = [f'{dataset.guid}']
    df = df.loc[date1:date2]

    return df.iloc[:, 0]



