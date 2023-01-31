import numpy as np
from collections import OrderedDict

def minmax(s):
  min_ = np.nanmin(s)
  max_ = np.nanmax(s)
  range_ = max_ - min_
  return (s-min_)/range_, min_, max_

def inv_minmax(s, min_, max_):
  range_ = max_-min_
  return (s*range_)+min_

def standardize(s):
  mean = np.nanmean(s)
  stdev = np.nanstd(s)
  return (s-mean)/stdev, mean, stdev

def inv_standardize(s, mean, stdev):
  return (s*stdev) + mean

def pct_of_median(s):
  med = np.nanmedian(s)
  return 100*s/med, med

def inv_pct_of_median(s, med):
  return (s*med)/100

def no_pp(s):
  return s

def log(s):
  return np.log(s)

def inv_log(s):
  return np.exp(s)

def log_10(s):
  return np.log10(s)

def inv_log_10(s):
  return 10**s

METHODS = OrderedDict([
  ('NONE', no_pp),
  ('INV_NONE', no_pp),
  ('NATURAL LOG', log),
  ('INV_NATURAL LOG', inv_log),
  ('LOG (BASE 10)', log_10),
  ('INV_LOG (BASE 10)', inv_log_10),
  ('SCALE TO MIN-MAX' , minmax),
  ('INV_SCALE TO MIN-MAX', inv_minmax),
  ('STANDARDIZE' , standardize),
  ('INV_STANDARDIZE' , inv_standardize),
  ('PERCENT OF MEDIAN' , pct_of_median),
  ('INV_PERCENT OF MEDIAN' , inv_pct_of_median)
])