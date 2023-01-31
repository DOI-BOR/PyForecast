from random import shuffle
from numpy import full, cumsum

# 10-FOLD CROSS VALIDATION, repeated 10 times
def yield_samples(total):

  

  ret = []
  for j in range(10):
    indices = list(range(total))
    shuffle(indices)

    folds = full(10, total//10)
    folds[:total%10] += 1
    folds_c = cumsum(folds)
    for i, f in enumerate(folds):
      if i == 0:
        idx = [False for r in range(f)] + [True for r in range(total-f)]
      elif i < 9:
        idx = [True for r in range(folds_c[i-1])] + [False for r in range(f)] + [True for r in range(total - f - folds_c[i-1])]
      else:
        idx = [True for r in range(folds_c[-2])] + [False for r in range(f)]
      
      ret.append([idx[i] for i in indices])
  return ret
