# File Name:        encryptions.py
# File Author:      Kevin Foley

# Descriptions:     generates ID's for stations, datasets, forecasts etc

import numpy as np
import random
import re

def generateStationID(TYPE, NAME, PARAM, DATALOADER):

    # Strip any whitespace or weird characters
    TYPE = re.sub('[\W_.]+', '', TYPE)
    NAME = re.sub('[\W_.]+', '', NAME)
    PARAM = re.sub('[\W_.]+', '', PARAM)
    DATALOADER = re.sub('[\W_.]+', '', DATALOADER)

    # Convert the strings into lists
    TYPE = list(TYPE)
    NAME = list(NAME)
    PARAM = list(PARAM)
    DATALOADER = list(DATALOADER)

    # Get parameters
    typeInd = int(len(TYPE)/2)
    nameInd = int(len(NAME)/2)
    paramInd = int(len(PARAM)/2)
    dataloaderInd = int(len(DATALOADER)/2)

    num = ord(TYPE[0]) + ord(NAME[1]) + ord(PARAM[0]) + ord(DATALOADER[3])
    num = '{:0<4d}'.format(num)
    num = int(num) + int(100*np.random.random(1))
    


    # generate the dataset id
    datasetID = TYPE[typeInd] + NAME[nameInd] + str(num) + PARAM[paramInd] + DATALOADER[dataloaderInd]
    datasetID = datasetID.upper()

    return datasetID

def generateFcstID(TYPE, PRDIDS):
    randInt = int(1000*np.random.random(1))
    fcstID = TYPE[-2:] + PRDIDS[-1][-4:] + str(randInt) + chr(int(70*np.random.random(1) + 49)) + chr(int(70*np.random.random(1) + 49))
    return fcstID
    