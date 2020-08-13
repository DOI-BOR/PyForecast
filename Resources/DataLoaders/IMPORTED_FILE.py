# Import Libraries
import pandas as pd
import xlrd
from csv import Sniffer
import numpy as np

# Define the dataloader
def dataLoader(stationDict, startDate, endDate):
    """
    Reads the file defined by stationDict['DatasetImportFileName'] and imports
    the data from that flat file between the startDate and the endDate.
    """

    filename = stationDict['DatasetImportFileName']
    dateLabel = None
    columnLabel = None

    # Check for specific column labels
    if "?" in filename:
        filename, dateLabel, columnLabel = filename.split("?")

    # Handle Excel data
    if 'xlsx' in filename.lower():

        df = pd.read_excel(filename, parse_dates=True, )
    
    # Handle CSV style data
    else:

        with open(filename, 'r') as readfile:
                    
            dialect = Sniffer().sniff(readfile.read(1024))

            df = pd.read_csv(filename, parse_dates=True, sep = dialect.delimiter,quotechar=dialect.quotechar, lineterminator=dialect.lineterminator.replace('\r', '') )

    if dateLabel == None:
        dateLabel = df.columns[0]
        columnLabel = df.columns[1]

    # Set the index and restrict to the column with the values
    df = df.set_index(dateLabel)
    df = df[[columnLabel]]

    # Limit the data to between the first and last days (startdate, enddate)
    df = df.loc[startDate:endDate]
    df = df[~df.index.duplicated(keep='last')] # Remove duplicates from the dataset
    df = df[~df.index.isnull()]

    return df