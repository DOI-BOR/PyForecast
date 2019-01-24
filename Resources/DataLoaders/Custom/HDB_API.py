
# Loader name:        HDB_API
# Loader author:      Kevin Foley
# Loader created:     2018-09-24
 
# WRITE LOADER BELOW ---------------------

import requests # Library that performs GET/POST requests
import pandas as pd # (REQUIRED) creates datatables
import numpy as np # useful math library
from datetime import datetime # Library to deal with dates

def dataLoaderInfo():
	"""
	This function describes the inputs for the dataloader.
	svr: HDB Server
	sdi: HDB SITE_DATATYPE ID for the dataset required.
	interval: SDI interval
	"""
	optionsDict = {
		'svr':'',
		'sdi':'',
		'interval':''
	}
	
	description = 'Retrives data from the HDB data API located at https://www.usbr.gov/lc/region/g4000/riverops/_HdbWebQuery.html. Allowable inputs for "svr" are: lchdb2, uchdb2, yaohdb, ecohdb, or lbohdb. Allowable inputs for "interval" are DY and MN'

	return optionsDict, description

def dataLoader(optionsDict, startDate, endDate):
	"""
	Reads the user inputs for SDI, SVR, and INTERVAL and returns the 
	daily data between the start and end dates provided by the software.
	"""

	# Change the start and end dates to the first of the months
	startDate = startDate.replace(day=1)
	endDate = endDate.replace(day=1)

	# Construct the API call
	baseURL = 'https://www.usbr.gov/pn-bin/hdb/hdb.pl?svr={0}&sdi={1}&tstp={4}&t1={2}&t2={3}&table=R&mrid=0&format=json'.format(
		optionsDict['svr'],
		optionsDict['sdi'],
		datetime.strftime(startDate, '%Y-%m-%dT00:00'),
		datetime.strftime(endDate, '%Y-%m-%dT00:00'),
		optionsDict['interval'] )
	
	# Get the repsonse from the API
	data = requests.get(baseURL)

	# Check response and return empty dataframe if response is bad
	if data.status_code is not 200:
		return pd.DataFrame()

	# Convert the response to JSON
	data = data.json() # Convert to JSON array

	# Parse the JSON
	timestamps = [pd.to_datetime(data['Series'][0]['Data'][i]['t']) for i in range(len(data['Series'][0]['Data']))]
	values = [data['Series'][0]['Data'][i]['v'] for i in range(len(data['Series'][0]['Data']))]

	# Store JSON data in dataframe
	df = pd.DataFrame(values, index=timestamps, columns=[optionsDict['sdi']]) # Convert the data into a dataframe
	df[optionsDict['sdi']] = pd.to_numeric(df[optionsDict['sdi']]) # Convert values to floating point numbers
	df = df.resample('D').asfreq() # Ensure that data is at daily frequency
	df = df.fillna(method='ffill') # Forward fill any missing data

	df = df[~df.index.duplicated(keep='first')] # Remove duplicates from the dataset
	df = df[~df.index.isnull()]

	df.columns = ['HDB | ' + optionsDict['sdi'] + ' | Streamflow | CFS']

	return df
