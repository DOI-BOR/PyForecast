import numpy as np
from collections import OrderedDict

def r2(yp, ya):
  ss_res = sum((ya-yp)**2)                # Residual sum of squares
  ss_tot = sum((ya-np.mean(ya))**2)       # Total sum of squares
  r2 = 1 - (ss_res/ss_tot)                # Coefficient of Determination
  return r2

def MSE(yp, ya):
  mse = sum((ya-yp)**2)/len(ya)
  return mse

SCORERS = OrderedDict(
  [
    ("R2", r2),
    ("MSE", MSE)
  ]
)