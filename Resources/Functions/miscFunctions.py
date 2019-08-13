# Script Name:      miscFunctions.py
# Script Author:    Kevin Foley
# 
# Description:      miscFunctions contains miscellaneous functions
#                   that do not fit in other catagories in the functions 
#                   folder.

from Resources.Functions.lists import HUCList
from datetime import datetime
import configparser

def isValidHUC(hucString):
    """
    This function reads the HUCList (in Resources/Functions/lists.py) and ensures that 
    the hucString input matches an entry in the list exactly.
    """

    if hucString in HUCList:
        return True
    else:
        return False



def lastWaterYear(dateToday):
    """
    This function takes a date as input and returns the starting date of the 
    water year associated with that date. E.g. is the 'dateToday' is 2011-02-24
    the function returns 2010-10-01.
    """

    month = int(dateToday.month)
    year = int(dateToday.year)
    
    if month >= 10:

        # The current date has the same year as the last water year
        last_Water_Year = datetime.strptime( '09-30-'+str( year ), '%m-%d-%Y' )

    if month < 10:

        # The current date has a year that is one year ahead of the last water year
        last_Water_Year = datetime.strptime( '09-30-'+str( year - 1 ), '%m-%d-%Y' )

    return last_Water_Year



def monthLookup(month):
    """
    This function simply converts the name of a month (e.g. 'March') to it's
    number (e.g. 3).
    """
    # First, if month is a name, not an integer, convert it to an integer
    monthDict = {
        "January":1,
        "February":2,
        "March":3,
        "April":4,
        "May":5,
        "June":6,
        "July":7,
        "August":8,
        "September":9,
        "October":10,
        "November":11,
        "December":12
    }
    if month in monthDict:
        return monthDict[month]
    else:
        return -1

def readConfig(configKey, configGroup='DEFAULT'):
    config = configparser.ConfigParser()
    config.read('Resources/tempFiles/pyforecast.cfg')
    return config[configGroup][configKey]

def writeConfig(configKey, configVal, configGroup='DEFAULT'):
    config = configparser.ConfigParser()
    config.read('Resources/tempFiles/pyforecast.cfg')
    config[configGroup][configKey] = configVal
    with open('Resources/tempFiles/pyforecast.cfg', 'w') as configfile:
        config.write(configfile)
    return

def current_date():
    """
    This function reads the Resources/tempFiles/programTime.txt file
    and returns the current date as a datetime object of that date
    """
    time=readConfig('programtime')

    date = datetime.strptime(time, '%Y-%m-%d')
    if date >= datetime.now():
        date = datetime.now()

    return date

def remapMonth(month, inv = False, arr = False, wateryearStart = 'October'):
    """
    This function takes a month (either name or number) and returns the month number
    of the water-year centric month (e.g. Input of 'October' returns 1, and input of 
    7 returns 10). By specifying the 'inv' parameter to True, you can get regular month numbers
    from water-year month numbers. The 'arr' value allows you to pass an array of months. 
    """
    try:
        month = monthLookup(month)
    except:
        pass
    if arr == True:
        monthArr = []
        for i, m in enumerate(month):
            monthArr.append(remapMonth(m))
        return monthArr
    
    if wateryearStart != 'October':
        wyStart = monthLookup(wateryearStart)
    else:
        wyStart = 10

    if inv == False:
        if month >= wyStart:
            val = month - wyStart + 1
        else:
            val = (12 - wyStart) + month + 1
    
    else:
        if month + wyStart > 13:
            val = month + wyStart - 13
        else:
            val = month + wyStart - 1

    return val