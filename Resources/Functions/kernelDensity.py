import numpy as np
from scipy.stats import norm
from sklearn.neighbors import KernelDensity

"""
Script Name:        kernelDensity.py
Script Author:      Kevin Foley
"""

def performKernelDensity(meanList, scaleList, bandwidth, x):
    """
    Inputs:
        meanList:   list of forecast means
        scaleList:  list of forecast deviations
        bandwidth:  desired kde bandwidth
        x:          array of x values associated with pdfList values
    Returns an array the same size as one of the input arrays
    """

    """Process X data"""
    x = x[:,np.newaxis]

    """
    Set up the random samples. Draw 10000 random samples from each forecast
    """
    samples = np.concatenate(
        tuple([np.random.normal(meanList[i], scaleList[i], 10000) for i in range(len(meanList))]))[:,np.newaxis]
    #samples = None
    print('num nans ', np.sum(np.isnan(samples)))
    """
    Set up the kernel density estimator
    """
    if bandwidth == -999.9:
        """ Compute the estimated bandwidth """
        bandwidth = 1.06*np.std(samples, ddof=1)*(len(samples)**(-0.2))
    print('samples ',samples)
    print('bandwidth ', bandwidth)
    kde = KernelDensity(kernel='gaussian',bandwidth = bandwidth).fit(samples)
    log_dens = kde.score_samples(x)
    kernelDensArray = np.exp(log_dens)
    # newVals = []
    # for i in range(len(meanList)):
    #     mean = meanList[i]
    #     var = scaleList[i]
    #     if i == 0:
    #         newVals = np.array([norm.pdf(x_, mean, var) for x_ in x])
    #     else:
    #         newVals = newVals + np.array([norm.pdf(x_, mean, var) for x_ in x])
    # kernelDensArray = newVals.ravel() / len(meanList)
    return kernelDensArray, samples, bandwidth
