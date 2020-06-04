'''
Script Name:        WYSEO_Loader
Script Author:      Jane Doe
Description:        Loads streamflow data from the WY_SEO.

'''

# Import Libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile
INFORMATION = "ABC"

def dataLoaderInfo():

    REQUIREMENTS = ["DatasetExternalID", "DatasetType"]
    INFORMATION = """This dataloader loads in Wyoming State Engineer's office streamflow data for a station.
    
The dataloader requires 1 metadata parameter:

    Dataset ID: Must be the sites unique location ID (see J Lanini for questions about this)..."""

    return REQUIREMENTS, INFORMATION

# # Dataloader information function
# def dataLoaderInfo():

#     # Define the required options for the dataLoader.
#     # You only need a locationID to download data for a station.
#     optionsDict = {
#         "locationID":""
#     }

#     # write a short description
#     description = "Downloads daily streamflow data for a station described by a locationID"

#     return optionsDict, description

# Dataloader function
def dataLoader(stationDict, startDate, endDate):

    # Generate the URL to retreive the data
    url = "http://seoflow.wyo.gov/Data/Export_DataLocation/?location={0}&date={1}&endDate={2}&calendar=1&exportType=csv".format(
        stationDict['datasetExternalID'],
        datetime.strftime(startDate, '%Y-%m-%d'),
        datetime.strftime(endDate, '%Y-%m-%d'))
    
    # Retrieve the data using a GET request
    data = requests.get(url)

    # Check to make sure the web service call was successful
    if data.status_code == 200:
        pass
    else:
        return pd.DataFrame() # return an empty dataframe

    # This GET operation is going to return a bunch of csv files in a zipped folder

    # The data is returned in a zipped csv file. We'll temporarily write the zipped-byte-data to a string object.
    zipData = BytesIO()
    zipData.write(data.content)

    # turn into a zipfile object
    zipData = ZipFile(zipData)

    # Create an empty dataframe
    df = pd.DataFrame()

    # Iterate through each csv and read into a dataframe
    for i in range(len(zipData.infolist())):

        # Get the csv filename
        fileName = zipData.infolist()[i].filename

        # Read the csv file into the dataframe
        df2 = pd.read_csv(zipData.open(fileName), header = 1, parse_dates = True, infer_datetime_format = True, index_col=0)
        df = pd.concat([df, df2], axis=0)

    # Isolate the discharge column
    df = pd.DataFrame(df['Value (Cubic Feet Per Second)'], index = df.index)
    
    # Give the data a meaningful name
    df.columns = ['{0} | Streamflow | CFS'.format(stationDict['locationID'])]

    # Return the dataframe
    return df