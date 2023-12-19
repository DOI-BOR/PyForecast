import pandas as pd
import numpy as np
import requests
from ftplib import FTP
from io import BytesIO
import codecs
from datetime import datetime

class Dataloader(object):

  NAME = "PDSI_SPI"
  DESCRIPTION = ""

  filenames = []
  pdsifile = None
  filedata = BytesIO(b'')

  def parseFiles(self, line):
    line = line.split()
    self.filenames.append(line[-1])

  def load(self, dataset, date1, date2):

    date1 = pd.to_datetime(datetime(date1.year, date1.month, date1.day))
    date2 = pd.to_datetime(datetime(date2.year, date2.month, date2.day))
    f = FTP('ftp.ncdc.noaa.gov')
    f.login()
    f.cwd('/pub/data/cirs/climdiv/')
    f.retrlines('LIST', self.parseFiles)

    for file_ in self.filenames:
      if dataset.param_code == 'PDSI':
        if 'climdiv-pdsidv-v' in file_:
          self.pdsifile = file_
      else:
        if 'climdiv-sp03dv-v' in file_:
          self.pdsifile = file_

    climdiv = f'{dataset.external_id:>04}'

    if self.pdsifile is not None:
      f.retrbinary('RETR ' + self.pdsifile, self.filedata.write)
      f.close()
      self.filedata.seek(0)
      self.filedata = codecs.getreader('utf-8')(self.filedata)
      data = pd.read_csv(self.filedata, sep='\s+', header=None, dtype={0:str}, names=['index', 'jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])
      data['dcode'] = data['index'].apply(lambda v: v[:4])
      data['year'] = data['index'].apply(lambda v: v[6:10])
      data = data[data['dcode'] == climdiv]
      del data['dcode']
      del data['index']
      data = data.melt(id_vars=['year'])
      data.index = pd.DatetimeIndex(pd.to_datetime(data.year.astype(str) + '-' + data.variable, format='%Y-%b'))
      del data['variable']
      del data['year']
      data[data['value'] < -99] = np.nan
      data.columns = [f'{dataset.guid}']
      data = data.resample('D').first()
      data = data.ffill()
      if date2 > data.index[-1]:
        date2 = data.index[-1]
      data = data.loc[date1:date2]
      return data.iloc[:,0]
    return pd.Series()


if __name__ == '__main__':
  dl = Dataloader()
  from datetime import datetime
  class Dataset:
    external_id = 4804
    param_code = 'SPI'
    guid = '310412fnsg3'
  dataset = Dataset()
  data = dl.load(dataset, datetime(2010,10,1),datetime.now())
  print(data)
