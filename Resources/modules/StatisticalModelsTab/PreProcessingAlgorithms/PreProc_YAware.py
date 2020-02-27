"""
Script Name:    PreProc_YAware

Description:    This preprocessor performs Y Aware 
                scaling on the input dataset following the 
                procedure outlined in "http://www.win-vector.com/blog/2016/05/pcr_part2_yaware/".

                Essentially, the X data is transformed into the 
                range of the y data using per-predictor OLS.

                This type of processing is particulary useful in 
                PCA Regression.
"""

import numpy as np

class preprocessor(object):
    """
    'preprocessor' class contains all the standard api methods
    for NextFlow preprocessors, i.e.:

        getTransformedX():
        getTransformedY():
        transform(data): 
        inverseTransform(data):
    """

    FILE_NAME = "PreProc_YAware"
    NAME = "Y-Aware Preprocessing"

    def __init__(self, data):
        """
        Initialize the preprocessor
        """

        # Create a reference to 'data'
        self.xdata = data[:,:-1]
        self.ydata = data[:,-1]
        self.data = data

        # Create arrays to store processor information
        self.yAwareCoef = np.full(self.xdata.shape[1], np.nan)
        self.yAwareMeans = np.full(self.xdata.shape[1], np.nan)
        self.yAwareX = np.full(self.xdata.shape, np.nan)

        # Transform the data
        self.yAwareScaling()

        return


    def getTransformedX(self):
        """
        Method to return the transformed X data. X data
        is returned as a 2D numpy array:
                    #  x1       x1      x3
        x = np.array([ 
                       [X00,    X01,    X02, ...], # t1
                       [X10,    X11,    X12, ...], # t2
                       [X20,    X21,    X22, ...], # t3
                       ....
                     ])
        """

        return self.yAwareX


    def getTransformedY(self):
        """
        Method to return the transformed Y data. Y data
        is returned as a 2D numpy array:
                    #   y       
        y = np.array([ 
                       [Y00], # t1
                       [Y10], # t2
                       [Y20], # t3
                       ....
                     ])
        """

        return self.ydata
        

    def transform(self, data):
        """
        Method for transforming an input dataset 
        using the transform parameters from the
        class initialization.
        """

        # Make a copy of the data
        data_c = data.copy()

        # Multiply the x data by the yAware coefficients
        # and subtract out the yAware means.
        data_c[:,:-1] = (data_c[:,:-1]*self.yAwareCoef) - self.yAwareMeans
        
        return data_c


    def inverseTransform(self, data):
        """
        Method for returning data back to the original,
        un-transformed version using the transform
        parameters from the class initialization.
        """

        # Make a copy of the data
        data_c = data.copy()

        # Add in the yAware means and divide by the 
        # yAware coefficients.
        data_c[:,:-1] = (data_c[:,:-1] + self.yAwareMeans) / self.yAwareCoef
        
        return data_c


    def yAwareScaling(self):
        """
        Performs Y-Aware scaling on the input data, following the 
        procedure outlined in "http://www.win-vector.com/blog/2016/05/pcr_part2_yaware/"
        """

        # Iterate over the predictors and scale them into the range of Y
        for i in range(self.xdata.shape[1]):

            # Concatenate a row of 1's to the data so that we can compute an intercept
            X_ = self.xdata[:,i].copy()
            Y_ = self.ydata[~np.isnan(X_)]
            X_ = X_[~np.isnan(X_)]
            X_ = np.concatenate((np.ones(shape=X_.shape[0]).reshape(-1,1), X_.reshape(-1,1)), 1)

            # Compute the coefficients and the intercept
            coef_all = np.linalg.inv(X_.transpose().dot(X_)).dot(X_.transpose()).dot(Y_)

            # Store the coefficients and create the Y-Aware Data
            self.yAwareCoef[i] = coef_all[1]
            self.yAwareMeans[i] = np.nanmean(np.dot(coef_all[1], self.xdata[:,i]))
            self.yAwareX[:,i] = np.dot(self.yAwareCoef[i], self.xdata[:,i]) -  self.yAwareMeans[i]

        return
            



## DEBUG
if __name__ == '__main__':

    from sklearn.datasets import load_boston
    import pandas as pd

    X,Y = load_boston(return_X_y=True)
    XY = np.concatenate((X, Y.reshape(-1,1)), axis=1)
    p = preprocessor(XY)
    print('done')