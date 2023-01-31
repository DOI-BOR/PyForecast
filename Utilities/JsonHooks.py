from datetime import datetime

def DatetimeParser(json_dict):
  items = list(json_dict.items())
  for (key, value) in items:
    if 'data_down' in key:
      print()
    if key in ['default_data_download_start']:
      if '.' not in value:
        value += '.0'
      json_dict[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')

  return json_dict
