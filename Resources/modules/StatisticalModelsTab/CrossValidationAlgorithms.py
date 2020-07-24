"""

"""

import numpy as np

class LOO():

    NAME = 'Leave One Out Cross Validation'

    def yield_samples(self, X, Y):

        # Get length of data
        l = len(X)

        # Yield the data with the one sample pulled out
        for i in range(l):

            x = np.concatenate((X[0:i], X[i+1:l]), axis=0)
            y = np.concatenate((Y[0:i], Y[i+1:l]))

            yield x,y, np.array(X[i]).reshape(1,-1), np.array(Y[i]).reshape(1,-1)


class KFOLD_5():
    
    NAME = "5-Fold Cross Validation"

    def yield_samples(self, X, Y):

        # Figure out how many samples will be in each fold
        fold_sizes = np.full(5, len(X) // 5, dtype=np.int)
        fold_sizes[:len(X) % 5] += 1

        # Yield samples and the leave-out data
        current_idx = 0
        for sample_size in fold_sizes:
            start, stop = current_idx, current_idx + sample_size
            yield np.concatenate((X[0:start], X[stop+1:len(X)]), axis=0), np.concatenate((Y[0:start], Y[stop+1:len(X)])), X[start:stop], Y[start:stop]
            current_idx = stop


class KFOLD_10():

    NAME = "10-Fold Cross Validation"

    def yield_samples(self, X, Y):

        # Figure out how many samples will be in each fold
        fold_sizes = np.full(10, len(X) // 10, dtype=np.int)
        fold_sizes[:len(X) % 10] += 1

        # Yield samples
        current_idx = 0
        for sample_size in fold_sizes:
            start, stop = current_idx, current_idx + sample_size
            yield np.concatenate((X[0:start], X[stop+1:len(X)]), axis=0), np.concatenate((Y[0:start], Y[stop+1:len(X)])), X[start:stop], Y[start:stop]
            current_idx = stop
