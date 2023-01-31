from datetime import datetime, timedelta

def water_year_start_date(date):
  return datetime(convert_to_water_year(date)-1, 10, 1)

def current_water_year():
  n = datetime.now()
  if n.month >= 10:
    return n.year+1
  else:
    return n.year

def convert_to_water_year(date):
  return date.year if date.month < 10 else date.year+1