from random import shuffle
from numpy import full, cumsum
from numba import jit
# LEAVE ONE OUT CROSS VALIDATION, repeated 1 times
@jit(nopython=True)
def yield_samples(total):

  ret = []
  indices = list(range(total))
  folds = full(total, total//(total-1))
  folds_c = cumsum(folds)
  for i, f in enumerate(folds):
    if i == 0:
      idx = [False for r in range(f)] + [True for r in range(total-f)]
    elif i < total:
      idx = [True for r in range(folds_c[i-1])] + [False for r in range(f)] + [True for r in range(total - f - folds_c[i-1])]
    else:
      idx = [True for r in range(folds_c[-2])] + [False for r in range(f)]
    ret.append([idx[i] for i in indices])
  return ret
