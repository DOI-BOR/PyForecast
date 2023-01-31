import geojson
import pandas as pd
from datetime import datetime, date

def excelToGeoJSON(fn):
    df = pd.read_excel(fn, dtype={"DatasetExternalID": str, "DatasetHUC8":str}, index_col=0)
    df.index.name = 'DatasetInternalID'
    features = []
    dataframe = df.copy()
    # Find all sites with multiple parameters
    dataframe['CheckColumn'] = dataframe['DatasetAgency'] + ' ' + dataframe['DatasetExternalID'].astype(str)
    dataframe['DatasetPORStart'] = [dataframe['DatasetPORStart'][i].isoformat() for i in dataframe.index]
    dataframe['DatasetPOREnd'] = [dataframe['DatasetPOREnd'][i].isoformat() for i in dataframe.index]
    extraParms = dataframe[dataframe.duplicated('CheckColumn')]
    extraParmsList = list(extraParms['CheckColumn'])
    sites = dataframe[~dataframe.duplicated('CheckColumn')]
    sites['Name'] = [str(i) for i in sites.index]
    def preprocessSites(X):
        if X['CheckColumn'] in extraParmsList:
            matches = extraParms[extraParms['CheckColumn'] == X['CheckColumn']]
            X['Name'] = str(X['Name']) + '|{0}'.format('|'.join(list(matches.index.astype(str))))
            X['DatasetParameter'] = str(X['DatasetParameter']) + '|{0}'.format('|'.join(list(matches['DatasetParameter'])))
            X['DatasetParameterCode'] = str(X['DatasetParameterCode']) + '|{0}'.format('|'.join(list(matches['DatasetParameterCode'])))
            X['DatasetUnits'] = str(X['DatasetUnits']) + '|{0}'.format('|'.join(list(matches['DatasetUnits'])))
            X['DatasetPORStart'] = str(X['DatasetPORStart']) + '|{0}'.format('|'.join(list(matches['DatasetPORStart'])))
            X['DatasetPOREnd'] = str(X['DatasetPOREnd']) + '|{0}'.format('|'.join(list(matches['DatasetPOREnd'])))
        return X
    sites = sites.apply(preprocessSites, axis=1)
    def insert_features(X):
        features.append(
            geojson.Feature(geometry=geojson.Point((X['DatasetLongitude'],
                                                    X['DatasetLatitude'])),
                            properties=dict(DatasetInternalID = str(X['Name']),
                                            DatasetType = X['DatasetType'],
                                            DatasetExternalID = X['DatasetExternalID'],
                                            DatasetName = X['DatasetName'],
                                            DatasetAgency = X['DatasetAgency'],
                                            DatasetParameter = X['DatasetParameter'],
                                            DatasetParameterCode = X['DatasetParameterCode'],
                                            DatasetUnits = X['DatasetUnits'],
                                            DatasetDefaultResampling = X['DatasetDefaultResampling'],
                                            DatasetDataloader = X['DatasetDataloader'],
                                            DatasetHUC8 = X['DatasetHUC8'],
                                            DatasetElevation = X['DatasetElevation'],
                                            DatasetPORStart = X['DatasetPORStart'],
                                            DatasetPOREnd = X['DatasetPOREnd'])))
    sites.apply(insert_features, axis=1)
    def json_serial(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type is not serializable")
    return ("""{"crs":{"type":"name","properties":{"name":"EPSG:4326"}},""" + geojson.dumps(geojson.FeatureCollection(features), allow_nan = True, sort_keys=True, default=json_serial)[1:]).replace('NaN,', '"",')
  