import pandas as pd
import numpy as np

def dataTable(datasets):

    return

def datasetTable():
    """
    Creates a fake dataset table for use in debugging
    """
    datasetTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='DatasetInternalID'),
            columns = [
                'DatasetType',              # e.g. STREAMGAGE, or RESERVOIR
                'DatasetExternalID',        # e.g. "GIBR" or "06025500"
                'DatasetName',              # e.g. Gibson Reservoir
                'DatasetAgency',            # e.g. USGS
                'DatasetParameter',         # e.g. Temperature
                'DatasetUnits',             # e.g. CFS
                'DatasetDefaultResampling', # e.g. average 
                'DatasetDataloader',        # e.g. RCC_ACIS
                'DatasetHUC8',              # e.g. 10030104
                'DatasetLatitude',          # e.g. 44.352
                'DatasetLongitude',         # e.g. -112.324
                'DatasetElevation',         # e.g. 3133 (in ft)
                'DatasetPORStart',          # e.g. 1/24/1993
                'DatasetPOREnd',            # e.g. 1/22/2019
                'DatasetAdditionalOptions'
            ]
        ) 

    datasetTable.loc[100101] = {'DatasetType': "RESERVOIR",              # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID':"GIBR",        # e.g. "GIBR" or "06025500"
            'DatasetName':"GIBSON RESERVOIR",              # e.g. Gibson Reservoir
            'DatasetAgency':"USBR",            # e.g. USGS
            'DatasetParameter':"Inflow",         # e.g. Temperature
            'DatasetUnits':"CFS",             # e.g. CFS
            'DatasetDefaultResampling':"sample", # e.g. average 
            'DatasetDataloader':"UBSR_GP",        # e.g. RCC_ACIS
            'DatasetHUC8':"10030203",              # e.g. 10030104
            'DatasetLatitude':44.22,          # e.g. 44.352
            'DatasetLongitude':-111.45,         # e.g. -112.324
            'DatasetElevation':3422,         # e.g. 3133 (in ft)
            'DatasetPORStart':"3/22/1955",          # e.g. 1/24/1993
            'DatasetPOREnd':"4/22/2011",            # e.g. 1/22/2019
            'DatasetAdditionalOptions':""}
        
    datasetTable.loc[100105] = {'DatasetType': "CLIMATE",              # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID':"FEF",        # e.g. "GIBR" or "06025500"
            'DatasetName':"FAKE RESERVOIR, FAKEOPOLIS",              # e.g. Gibson Reservoir
            'DatasetAgency':"USBR",            # e.g. USGS
            'DatasetParameter':"Temperature",         # e.g. Temperature
            'DatasetUnits':"DEG",             # e.g. CFS
            'DatasetDefaultResampling':"average", # e.g. average 
            'DatasetDataloader':"USGS_NWIS",        # e.g. RCC_ACIS
            'DatasetHUC8':"10030104",              # e.g. 10030104
            'DatasetLatitude':44.233,          # e.g. 44.352
            'DatasetLongitude':-111.424,         # e.g. -112.324
            'DatasetElevation':4244,         # e.g. 3133 (in ft)
            'DatasetPORStart':"1/25/1988",          # e.g. 1/24/1993
            'DatasetPOREnd':"10/11/2019",            # e.g. 1/22/2019
            'DatasetAdditionalOptions':""}

    datasetTable.loc[100105] = {'DatasetType': "INDEX",              # e.g. STREAMGAGE, or RESERVOIR
            'DatasetExternalID':"0332",        # e.g. "GIBR" or "06025500"
            'DatasetName':"Big Sky Relative Happiness Index",              # e.g. Gibson Reservoir
            'DatasetAgency':"WMO",            # e.g. USGS
            'DatasetParameter':"Happiness Index",         # e.g. Temperature
            'DatasetUnits':"degC",             # e.g. CFS
            'DatasetDefaultResampling':"first", # e.g. average 
            'DatasetDataloader':"WMO_LOADER",        # e.g. RCC_ACIS
            'DatasetHUC8':"10030104",              # e.g. 10030104
            'DatasetLatitude':44.21,          # e.g. 44.352
            'DatasetLongitude':-111.419,         # e.g. -112.324
            'DatasetElevation':4244,         # e.g. 3133 (in ft)
            'DatasetPORStart':"1/25/1988",          # e.g. 1/24/1993
            'DatasetPOREnd':"10/11/2019",            # e.g. 1/22/2019
            'DatasetAdditionalOptions':""}

    return datasetTable