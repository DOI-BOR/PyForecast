"""
Script Name:    PreProc_NoPreProcessing

Description:    This Preprocessor does nothing to the 
                input data, and returns the same data
                as it was originally provided. Its
                transform methods do nothing.
"""

class preprocessor(object):
    """
    'preprocessor' class contains all the standard api methods
    for NextFlow preprocessors, i.e.:

        getTransformedX():
        getTransformedY():
        transform(data): 
        inverseTransform(data):
    """

    FILE_NAME = 'PreProc_NoPreProcessing'
    name = "No Preprocessing"

    def __init__(self, data):
        """
        Initialize the preprocessor
        """

        # Create a reference to the input data
        self.data = data

        return

    def getTransformedX(self):
        """
        This method returns the original
        x data. Remember, this script performs
        no preprocessing
        """

        return self.data[:, :-1]


    def getTransformedY(self):
        """
        This method returns the original
        y data. Remember, this script performs
        no preprocessing
        """

        return self.data[:,-1]
        

    def transform(self, data):
        """
        Returns the data back without applying
        any transformation.
        """

        return data


    def inverseTransform(self, data):
        """
        Returns the data back without applying
        any transformation.
        """

        return data