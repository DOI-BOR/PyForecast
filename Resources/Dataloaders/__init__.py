from collections import OrderedDict
import os
import importlib
from PyQt5.QtWidgets import QApplication
from Resources.Dataloaders import FILE_IMPORT, NOAA_CPC, NOAA_NCDC, NRCS_WCC, \
                                  PDSI_SPI, RCC_ACIS, USBR, USGS_NWIS, ALBERTA_WATER
app = QApplication.instance()

class Dataloaders(OrderedDict):

  def __init__(self):

    OrderedDict.__init__(self)

    self['-'] = {'DESC':EmptyDataloader.DESCRIPTION, 'CLASS':EmptyDataloader}
    self['USBR'] = {'DESC':USBR.Dataloader.DESCRIPTION, 'CLASS':USBR.Dataloader}
    self['Flat File Import'] = {'DESC':FILE_IMPORT.Dataloader.DESCRIPTION, 'CLASS':FILE_IMPORT.Dataloader}
    self['NOAA-CPC'] = {'DESC':NOAA_CPC.Dataloader.DESCRIPTION, 'CLASS':NOAA_CPC.Dataloader}
    self['NOAA_NCDC'] = {'DESC':NOAA_NCDC.Dataloader.DESCRIPTION, 'CLASS':NOAA_NCDC.Dataloader}
    self['NRCS_WCC'] = {'DESC':NRCS_WCC.Dataloader.DESCRIPTION, 'CLASS':NRCS_WCC.Dataloader}
    self['PDSI_SPI'] = {'DESC':PDSI_SPI.Dataloader.DESCRIPTION, 'CLASS':PDSI_SPI.Dataloader}
    self['RCC-ACIS'] = {'DESC':RCC_ACIS.Dataloader.DESCRIPTION, 'CLASS':RCC_ACIS.Dataloader}
    self['USGS_NWIS'] = {'DESC':USGS_NWIS.Dataloader.DESCRIPTION, 'CLASS':USGS_NWIS.Dataloader}
    self['AB_Loader'] = {'DESC':ALBERTA_WATER.Dataloader.DESCRIPTION, 'CLASS':ALBERTA_WATER.Dataloader}


  def get_loader_by_name(self, name):
    for key in self.keys():
      if key == name:
        return self[key]

class EmptyDataloader:

  NAME = '-'
  DESCRIPTION = 'No Dataloader'

  def load(self):
    return []

DATALOADERS = Dataloaders()

