import numpy as np
from collections import OrderedDict
from numba import jit

@jit(nopython=True)
def r2(yp, ya, num_predictors):
  ss_res = sum((ya-yp)**2)                # Residual sum of squares
  ss_tot = sum((ya-np.mean(ya))**2)       # Total sum of squares
  r2 = 1 - (ss_res/ss_tot)                # Coefficient of Determination
  return r2

@jit(nopython=True)
def MSE(yp, ya, num_predictors):
  mse = sum((ya-yp)**2)/len(ya)
  return mse

@jit(nopython=True)
def adj_r2(yp, ya, num_predictors):
  if num_predictors+1 >= len(yp):
    return np.nan
  rsq = r2(yp, ya, num_predictors)
  if (len(yp)-num_predictors-1) == 0:
    num_predictors += 1
  return 1-((1-rsq)*(len(yp)-1)/(len(yp)-num_predictors-1))

@jit(nopython=True)
def MAE(yp, ya, num_predictors):
  mae = sum((ya-yp))/len(ya)
  return mae

SCORERS = OrderedDict(
  [
    ("R2", r2),
    ("ADJ R2", adj_r2),
    ("MSE", MSE),
    ("MAE", MAE)
  ]
)