# Import Libraries
import pandas as pd
import xlrd
import numpy as np

# Define the dataloader
def dataLoader(stationDict, startDate, endDate):
    """
    Reads the file defined by stationDict['DatasetImportFileName'] and imports
    the data from that flat file between the startDate and the endDate.
    """

    filename = stationDict['DatasetImportFileName']
    
    # Handle CSV data
    if any(map(lambda x: x in filename.lower(), ['.csv', '.dat'])):
        
        df = pd.read_csv(filename, parse_dates=True, index_col=0, )

    # Otherwise, we assume it's an excel file+
    else:

        df = pd.read_excel(filename, parse_dates=True, index_col=0, )

    # Limit the data to between the first and last days (startdate, enddate)
    df = df.loc[startDate:endDate]
    df = df[~df.index.duplicated(keep='last')] # Remove duplicates from the dataset
    df = df[~df.index.isnull()]

    return df