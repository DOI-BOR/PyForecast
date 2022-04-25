"""
Script Name:    PreProc_ZScoreScaler

Description:    This processor converts the data into its standard score (Z-Score)
                see: https://en.wikipedia.org/wiki/Standard_score
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

    FILE_NAME = 'PreProc_ZScoreScaler'
    NAME = "Z-Score Scaler"
    DESCRIPTION = "Normalizes predictor data to their respective Z-Scores."

    def __init__(self, data):
        """
        Initialize the preprocessor
        """

        # Create a reference to the input data
        self.data = data

        # Create a transformed dataset
        self.transformedData = np.full(self.data.shape, np.nan)
        self.means = np.full(self.data.shape[1], np.nan)
        self.stdevs = np.full(self.data.shape[1], np.nan)

        # Scale each feature in the dataset
        for i in range(self.data.shape[1] - 1):
            xMean = np.nanmean(self.data[:,i])
            xStDev = np.nanstd(self.data[:,i])
            self.means[i] = xMean
            self.stdevs[i] = xStDev
            self.transformedData[:, i] = (self.data[:, i] - self.means[i]) / self.stdevs[i]
        # Copy the y-data
        self.transformedData[:, -1] = self.data[:, -1]

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
            for i in range(data_c.shape[1] - 1):

                data_c[:,i] = (data_c[:,i] - self.means[i]) / self.stdevs[i]
        except:
            for i in range(len(data_c)):

                data_c[i] = (data_c[i] - self.means[i]) / self.stdevs[i]
        return data_c


    def inverseTransform(self, data):
        """
        Remove the effect of the preprocessor
        on the inputted data
        """

        data_c = data.copy()

        for i in range(data_c.shape[1] - 1):

            data_c[:,i] = (data_c[:,i] - self.offsets[i]) / self.scales[i] 

        return data_c