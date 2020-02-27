import pandas as pd
import numpy as np
import requests
from datetime import datetime


def dataLoader(stationDict, startDate, endDate):
    """
    This Dataloader loads watershed averaged SNODAS data 
    from the National Water Center's NOHRSC SNODAS model.

    The only necessary parameter for this dataset is the 
    Basin ID contained in the DatasetExternalID field

    Additionally, if the "RFC" key is filled in for the 
    datasetAdditionalOptions field, it will use that specific 
    RFC. Otherwise it defaults to MBRFC

    """


    # Construct the URL
    # https://www.nohrsc.noaa.gov/interactive/html/graph.html?brfc=mbrfc&basin=2806&w=600&h=400&o=a&uc=0&by=2020&bm=2&bd=16&bh=6&ey=2020&em=2&ed=23&eh=6&data=1&units=1
    url = ( "https://www.nohrsc.noaa.gov/interactive/html/graph.html?brfc=" + "MBRFC" + 
            "&basin=" + stationDict['DatasetExternalID'] + 
            "&by=" + str(startDate.year) + 
            "&bm=" + str(startDate.month) + 
            "&bd=" + str(startDate.day) +
            "&bd=" + str(startDate.hour) + 
            "&ey=" + str(endDate.year) + 
            "&em=" + str(endDate.month) + 
            "&ed=" + str(endDate.day) + 
            "&eh=" + str(endDate.hour) + 
            "&data=2&units=1"
        )
    
    # Load the data into a dataframe
    df = pd.read_csv(url, parse_dates = True, index_col=0)

    for i, col in enumerate(df.columns):
        print(i, col)

    return


if __name__ == "__main__":
    stationDict = {"DatasetExternalID":"2806", "DatasetAdditionalOptions":{"RFC":"MBRFC"}}
    startDate = pd.to_datetime("2010-10-01")
    endDate = pd.to_datetime("2020-02-14")
    dataLoader(stationDict, startDate, endDate)