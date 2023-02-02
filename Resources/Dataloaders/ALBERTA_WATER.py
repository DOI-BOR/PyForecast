#### IN PROGRESS PENDING API INFORMATION FROM NATHALIE

import pandas as pd

class Dataloader(object):

  NAME = "ALBERTA WATER"
  DESCRIPTION = ""

  def load(self, dataset, date1, date2):

    data = pd.Series()
    
    if (date2 - date1).days <= 5:

      # Use 5 day API'
      url = f'https://environment.alberta.ca/apps/Basins/data/figures/river/abrivers/stationdata/R_{dataset.param_code}_{dataset.external_id}_table.json'

      # Read JSON
      data = pd.read_json(url, )
    
    else:

      # Use POR API

    return data
