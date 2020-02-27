"""
Script Name:    PreProc_Logarithmic_Y

Description:    This preprocessor performs Logarithmic pre-processing
                on an input dataset's Y data. The Logarithmic preprocessing
                ensures that models do not lead to negative predictions.
                The trade-off for this type of pre-processing is that
                the distribution of predictions is skewed toward
                lower values (I think...).
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

    FILE_NAME = "PreProc_Logarithmic_Y"
    NAME = "Logarithmic Preprocessing"

    def __init__(self, data):
        """
        Initialize the preprocessor.
        """

        # Create a reference to the input data
        self.data = data
        
        # Create an array to store transformed data
        self.transformedData = self.data

        # take the natural logarithm of the y data, leaving the 
        # x data alone.
        self.transformedData[:, -1] = np.log(self.transformedData[:,-1])

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
        
        # The X data is found in every column execpt the last one
        return self.transformedData[:, :-1]


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

        # The y data is only found in the last column
        return self.transformedData[:,-1]


    def transform(self, data):
        """
        Method for transforming an input dataset 
        using the transform parameters from the
        class initialization.
        """

        # Make a copy of the data
        data_c = data.copy()


        # Log transform the y data
        data_c[:,-1] = np.log(data_c[:,-1])

        return data_c


    def inverseTransform(self, data):
        """
        Method for returning data back to the original,
        un-transformed version using the transform
        parameters from the class initialization.
        """

        # Make a copy of the data
        data_c = data.copy()

        # Exponentiate the y data
        data_c[:,-1] = np.exp(data_c[:,-1])
        
        return data_c


## DEBUG
if __name__ == '__main__':

    from sklearn.datasets import load_boston
    import pandas as pd

    X,Y = load_boston(return_X_y=True)
    XY = np.concatenate((X, Y.reshape(-1,1)), axis=1)
    p = preprocessor(XY)
    print('done')
