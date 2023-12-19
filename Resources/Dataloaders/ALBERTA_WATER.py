#### IN PROGRESS PENDING API INFORMATION FROM NATHALIE

import pandas as pd
import numpy as np

#### NOTE THAT THIS DOESN'T WORK
#### NEED TO GET BETTER API INFO FROM NATHALIE

class Dataloader(object):

  NAME = "AB_Loader"
  DESCRIPTION = ""

  def load(self, dataset, date1, date2):

    data = pd.Series()

    url = f"https://environment.alberta.ca/apps/Basins/data/porExtracts/porExtract_AB_{dataset.external_id}_{dataset.param_code}_Cmd.Merged-NRT.Public.csv"
    print(url)
    df = pd.read_csv(url, skiprows=23, encoding_errors='ignore')
    df['dt'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.set_index(df['dt'])

    df = df.iloc[:,2].resample("D").apply(np.nanmean)

    return df[date1:date2]
