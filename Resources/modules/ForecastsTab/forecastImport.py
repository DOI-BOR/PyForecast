"""
"""
import pandas as pd
import requests
from datetime import datetime
from zeep import Client
from decimal import Decimal
import itertools
from fuzzywuzzy.fuzz import WRatio

class NRCSForecast(object):
    """
    """
    def __init__(self, parent = None):

        # Set up the soap service
        self.NRCS = Client('http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL')

        return

    def loadForecastPoints(self):
        """
        Loads in the NRCS forecast points from the file at resources/GIS/NRCSForecastPoints.csv
        """
        self.forecastPoints = pd.read_csv("resources/GIS/NRCSForecastPoints.csv")
        self.forecastPoints['SEARCHCOL'] = self.forecastPoints[["Station Id", "State Code", "Station Name", "County Name", "Huc.hucname"]].agg(" ".join, axis=1)
        return

    def getForecastPointsByKeywordSearch(self, keyword = None):
        
        self.forecastPoints['score'] = list(map(WRatio, zip(self.forecastPoints['SEARCHCOL'], itertools.repeat(keyword, len(self.forecastPoints)))))
        self.forecastPoints.sort_values(by=['score'], inplace=True, ascending=False)
        
        return self.forecastPoints.iloc[0:30]
    
    def getForecasts(self):

        return
    
    def getForecastEquations(self, idx = None):

        point = self.forecastPoints.loc[idx]
        stationTriplet = point['Station Id'] + ':' + point['State Code'] + ':' + point['Network Code']
        equations = self.NRCS.service.getForecastEquations(stationTriplet = stationTriplet)


        return