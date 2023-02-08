import numpy as np
from collections import OrderedDict

def acc_cfs_kaf(s):
  return np.nansum(s)*86400/43560000

def acc_cms_mcm(s):
  return np.nansum(s)*0.0864

def first(s):
  s_ = s.dropna()
  if len(s_) >= 1:
    return s_.iloc[0]
  else:
    return np.nan

def last(s):
  s_ = s.dropna()
  if len(s_) >= 1:
    return s_.iloc[-1]
  else:
    return np.nan

METHODS = OrderedDict([
  ('ACCUMULATION', np.nansum),
  ('ACCUMULATION (CFS to KAF)', acc_cfs_kaf),
  ('ACCUMULATION (CMS to MCM)', acc_cms_mcm),
  ('AVERAGE', np.nanmean),
  ('MAXIMUM', np.nanmax),
  ('MINIMUM', np.nanmin),
  ('MEDIAN' , np.nanmedian),
  ('FIRST'  , first),
  ('LAST'   , last)
])