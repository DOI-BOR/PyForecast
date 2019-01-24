
# Loader name:        BOYR_ADJUSTED_INFLOWS
# Loader author:      KEVIN FOLEY
# Loader created:     2019-01-08
 
# WRITE LOADER BELOW ---------------------

import pandas as pd
import numpy as np
import requests
from datetime import datetime

def dataLoaderInfo():
	optionsDict={
		"Param1":"",
		"Param1Operator":"+",
		"Param2":"",
		"Param2Operator":"+",
		"Param3":"",
		"Param3Operator":"+"}
	description = "Downloads GP hydromet data as (operator1)param1 + (operator2)param2 + (operator3)param3, where operator is either + or -"
	return optionsDict, description

def dataLoader(stationDict, startDate, endDate):
	syear = datetime.strftime(startDate, '%Y')
	smonth = datetime.strftime(startDate, '%m')
	sday = datetime.strftime(startDate, '%d')
	eyear = datetime.strftime(endDate, '%Y')
	emonth = datetime.strftime(endDate, '%m')
	eday = datetime.strftime(endDate, '%d')

	params = []
	ops = []
	for key in stationDict.keys():
		if 'Parameter' in key:
			continue
		if 'Param' in key:
			if 'Operator' in key:
				continue
			if stationDict[key] != '':
				params.append(stationDict[key])
				ops.append(stationDict[key+'Operator'])

	df = pd.DataFrame(index = pd.date_range(startDate, endDate))

	for i, param in enumerate(params):
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
		if ops[i] == '-':
			df1[param] = -1*df1[param]
		df = pd.concat([df1, df], axis=1)
		df = df.round(3)

	dfOut = df.sum(axis=1)
	return pd.DataFrame(dfOut)