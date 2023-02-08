"""HydrologyDateTimes.py

HydrologyDateTimes.py contains convienence functions to work with
dates in hydrology. 

"""

from datetime import datetime

def water_year_start_date(date):
  """Returns the start date (`datetime.datetime`) of the water year from the
  the given "date" argument

  Parameters
  -----------
  date: `datetime.datetime`
    A python datetime
  
  Returns
  --------
  water_year_start_date: `datetime.datetime` 
    containing the date of the start of the water year (Oct 1st)
  """
  return datetime(convert_to_water_year(date)-1, 10, 1)

def current_water_year():
  """Returns the `int` year of the current water year
  """
  return convert_to_water_year(datetime.now())

def convert_to_water_year(date):
  """Returns the water year (`int`) associated with the given 'date'
  """
  return date.year if date.month < 10 else date.year+1