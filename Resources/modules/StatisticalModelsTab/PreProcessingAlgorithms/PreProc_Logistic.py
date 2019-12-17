"""
"""

import numpy as np

class preprocessor(object):

    name = "Logistic Preprocessing"

    def __init__(self, data):

        self.data = data

    def getTransformedX(self):

        return self.data[:, :-1]

    def getTransformedY(self):

        return self.data[:,-1]
        
    def transform(self, data):

        return data

    def inverseTransform(self, data):

        return data