"""
"""

import numpy as np

class preprocessor(object):

    name = "Y-Aware Principal Components Preprocessing"

    def __init__(self, data):
        """
        data: data to fit the preprocessing model to 
        """

        # Create a reference to 'data'
        self.xdata = data[:,:-1]
        self.ydata = data[:,-1]
        self.data = data

        # Create arrays to store processor information
        self.yAwareCoef = np.full(self.xdata.shape[1], np.nan)
        self.yAwareMeans = np.full(self.xdata.shape[1], np.nan)
        self.yAwareX = np.full(self.xdata.shape, np.nan)
        self.numPCs = self.xdata.shape[1]
        self.PCData = np.full(self.xdata.shape, np.nan)

        # Transform the data
        self.transform()


    def getTransformedX(self):
        """
        Return The Principal Components of the 
        data.
        """
        return self.PCData

    def getTransformedY(self):
        """
        y data is not transformed in Y-Aware PCA,
        so we just return the orignal data
        """

        return self.ydata
        

    def transform(self):
        """
        First performs Y-Aware scaling on the input data,
        then converts input data into PCs
        """

        # Do the YAware Scaling
        self.yAwareScaling()

        # Convert to PCs


        return

    def inverseTransform(self, data):

        return data

    def PCA(self):
        """
        Performs PCA on the dataset using numpy's
        linear algebra packages
        """

        # Calculate the covariance matrix
        cov = np.cov(self.yAwareX, rowvar=False)

        # Calculate the eigenvectors and eigenvalues of the covariance matrix
        self.eigVal, self.eigVec = np.linalg.eigh(cov)

        # Sort the eigenvalues in descending order (and sort the eigenvectors based on that index)
        idx = np.argsort(self.eigVal)[::-1]
        self.eigVec = self.eigVec[:, idx]
        self.eigVal = self.eigVal[idx]

        # Apply the transformation to the y-aware data+
        self.PCData = np.dot(self.yAwareX, self.eigVec)

    def yAwareScaling(self):
        """
        Performs Y-Aware scaling on the input data, following the 
        procedure outlined in "http://www.win-vector.com/blog/2016/05/pcr_part2_yaware/"
        """

        for i in range(self.xdata.shape[1]):

            # Concatenate a row of 1's to the data so that we can compute an intercept
            X_ = np.concatenate((np.ones(shape=self.xdata.shape[0]).reshape(-1,1), self.xdata[:,i].reshape(-1,1)), 1)

            # Compute the coefficients and the intercept
            coef_all = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(self.ydata)

            # Store the coefficients and create the Y-Aware Data
            self.yAwareCoef[i] = coef_all[1]
            self.yAwareMeans[i] = np.average(np.dot(coef_all[1], self.xdata[:,i]))
            self.yAwareX[:,i] = np.dot(coef_all[1], self.xdata[:,i]) -  np.average(np.dot(coef_all[1], self.xdata[:,i]))
            

## DEBUG
if __name__ == '__main__':

    from sklearn.datasets import load_boston
    import pandas as pd

    X,Y = load_boston(return_X_y=True)
    XY = np.concatenate((X, Y.reshape(-1,1)), axis=1)
    p = preprocessor(XY)
    print('done')