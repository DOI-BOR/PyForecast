
# Loader name:        BOYR_ADJUSTED_INFLOWS
# Loader author:      Jordan Lanini
# Loader created:     2019-02-05
 
# WRITE LOADER BELOW ---------------------

import pandas as pd
import numpy as np
import requests
from datetime import datetime

def dataLoaderInfo():
	optionsDict={
		"Param1":"BHR IN",
		"Param1Operator":"+",
		"Param1Shift":"0",
		"Param2":"BBR QD",
		"Param2Operator":"-",
		"Param2Shift":"-1",
		"Param3":"BOYR QD",
		"Param3Operator":"-",
		"Param3Shift":"2"}
	description = "Downloads GP hydromet data as (operator1) x param1 + (operator2) x param2 + (operator3) x param3, where operator is either + or -. Shift the timeseries in days. + is forward in time, - is backward in time."
	
	return optionsDict, description

def dataLoader(stationDict, startDate, endDate):

	params = []
	ops = []
	shifts = []
	for key in stationDict.keys():
		if 'Parameter' in key:
			continue
		if 'Param' in key:
			if 'Operator'in key:
				continue
			if 'Shift'in key:
				continue
			if stationDict[key] != '':
				params.append(stationDict[key])
				ops.append(stationDict[key+'Operator'])
				shifts.append(stationDict[key+'Shift'])

	df = pd.DataFrame(index = pd.date_range(startDate, endDate))
	for i, param in enumerate(params):	
		tempStartDate=pd.Timestamp(startDate)+pd.DateOffset(days=int(shifts[i]))
		tempEndDate=pd.Timestamp(endDate)+pd.DateOffset(days=int(shifts[i]))
		syear = datetime.strftime(tempStartDate, '%Y')
		smonth = datetime.strftime(tempStartDate, '%m')
		sday = datetime.strftime(tempStartDate, '%d')
		eyear = datetime.strftime(tempEndDate, '%Y')
		emonth = datetime.strftime(tempEndDate, '%m')
		eday = datetime.strftime(tempEndDate, '%d')

		stationID = param.split(' ')[0]
		pcode = param.split(' ')[1]
		url = ("https://www.usbr.gov/gp-bin/arcread.pl?st={0}&by={1}&bm={2}&bd={3}&ey={4}&em={5}&ed={6}&pa={7}&json=1")
		url = url.format(stationID, syear, smonth, sday, eyear, emonth, eday, pcode)
		response = requests.get(url)
		data = response.json()
		dataValues = data['SITE']['DATA']
		df1 = pd.DataFrame(dataValues, index = pd.date_range(startDate, endDate))
		del df1['DATE']
		df1[pcode.upper()] = pd.to_numeric(df1[pcode.upper()])
		df1.replace(to_replace=998877, value=np.nan, inplace=True)
		df1.replace(to_replace=998877.0, value=np.nan, inplace=True)
		df1 = df1[~df1.index.duplicated(keep='first')]
		df1 = df1[~df1.index.isnull()]
		df1.columns = [param]
		df1=df1.shift(periods=-1*int(shifts[i]), freq="D")
		if ops[i] == '-':
			df1[param] = -1*df1[param]

		df = pd.concat([df1, df], axis=1)
		df = df.round(3)


	dfOut = df.sum(axis=1)
	return pd.DataFrame(dfOut)