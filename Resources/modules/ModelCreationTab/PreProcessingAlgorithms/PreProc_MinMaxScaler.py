"""
Script Name:    PreProc_MinMaxScaler

Description:    This processor scales the data so
                that the maximum and minimum of all the
                predictor and target data are 0 and 1 
                respectively. 

                see: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
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

    FILE_NAME = 'PreProc_MinMaxScaler'
    NAME = "Min / Max Scaler"
    DESCRIPTION = "Scales the entire dataset (predictors and target) to the minimum and maximum of the entire dataset."

    def __init__(self, data):
        """
        Initialize the preprocessor
        """

        # Create a reference to the input data
        self.data = data

        # Create a transformed dataset
        self.transformedData = np.full(self.data.shape, np.nan)
        self.scales = np.full(self.data.shape[1], np.nan)
        self.offsets = np.full(self.data.shape[1], np.nan)

        # Scale each feature in the dataset
        for i in range(self.data.shape[1]):
            
            mx = np.nanmax(self.data[:,i])
            mn = np.nanmin(self.data[:,i])
            self.scales[i] = 1 / (mx - mn)
            self.offsets[i] = -1 * mn / (mx - mn)
            self.transformedData[:, i] = self.data[:,i]*self.scales[i] + self.offsets[i]

        return

    def getTransformedX(self):
        """
        This method returns the transformed
        x data that the preprocessor was
        trained on.
        """

        return self.transformedData[:, :-1]


    def getTransformedY(self):
        """
        This method returns the transformed
        y data that the preprocessor was
        trained on.
        """

        return self.transformedData[:,-1]
        

    def transform(self, data):
        """
        Apply the scale and the offset
        to the data supplied
        """

        data_c = data.copy()
        try:
            for i in range(data_c.shape[1]):

                data_c[:,i] = data_c[:,i] * self.scales[i] + self.offsets[i]
        except:
            for i in range(len(data_c)):

                data_c[i] = data_c[i] * self.scales[i] + self.offsets[i]
        return data_c


    def inverseTransform(self, data):
        """
        Remove the effect of the preprocessor
        on the inputted data
        """

        data_c = data.copy()

        for i in range(data_c.shape[1]):

            data_c[:,i] = (data_c[:,i] - self.offsets[i]) / self.scales[i] 

        return data_c