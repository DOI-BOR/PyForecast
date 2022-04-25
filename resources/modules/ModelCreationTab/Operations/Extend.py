import pandas as pd
import numpy as np
from datetime import timedelta
from .Fill import fill_missing
# import matplotlib.pyplot as plt


def linear(data, n_predict):
    """
    Linearly extrapolate a source timeseries

    Parameters
    ----------
    data: dataseries
        date index and 1 column of streamflow values
    n_predict: int
        number of time increments to extrapolate

    Returns
    -------
    extrap_data: dataframe
        time series with observed data and extrapolated values based on final two observed values
    """

    # create time series with extrapolated data
    x = np.arange(1, n_predict + 1)
    extrap_data = data.iloc[-2] + (x - (-1)) / (0 - (-1)) * (data.iloc[-1] - data.iloc[-2])

    # linear extrapolation based on last two points in observed dataset
    # create pandas DataFrame with observed and extrapolated data
    extrap_data = pd.Series(extrap_data,
                            index=pd.date_range(start=data.last_valid_index() + timedelta(days=1),
                                                end=data.last_valid_index() + timedelta(days=n_predict)),
                            name='Value')

    ### Debugging code ###
    # plot the data
    # fig, ax = plt.subplots(1, 1, gridspec_kw={})
    # fig.set_size_inches(10, 8)
    #
    # extrap_data.plot(ax=ax, linestyle='--', color='r')
    # data.plot(ax=ax, linestyle='-', color='k')
    # ax.set_ylabel("Daily Avg Inflow (cfs)")
    # ax.legend(["Linear Extrap", "Observed Data"], loc='upper right')
    # plt.savefig('linear_extrap')
    # plt.show()

    return extrap_data


def fourier(data, n_predict, time_threshold):
    """
    Extrapolate data based on Fourier transform of the source timeseries

    Parameters
    ----------
    data: dataseries
        date index and 1 column of streamflow values
    n_predict: int
        number of time increments to extrapolate
    freq_threshold: float
        frequency threshold above which frequencies are removed
    Returns
    -------
    extrap_data: dataseries
        time series with observed data and extrapolated values from Fourier Transform
    p_filtered: float
        spectral density lost due to high frequency filter
        
    """

    # remove NANs from dataset
    idx = np.isfinite(data.values)

    # n = len(x)
    t = np.arange(0, len(data.values))

    # find linear trend in dataset
    p = np.polyfit(t[idx], data.values[idx], 1)

    # Detrend x
    trend_removed = data.values - p[0] * t

    # detrended x in frequency domain
    FFT = np.fft.fft(trend_removed)

    # frequencies of transform
    freqs = np.fft.fftfreq(len(data.values))

    ### Apply a low pass filter into the data ###
    # convert time threshold to frequency
    freq_threshold = 1 / time_threshold
    high_freq_FFT = FFT.copy()

    # remove high frequencies
    high_freq_FFT[np.abs(freqs) > freq_threshold] = 0

    # percentage of frequencies removed
    p_filtered = len(high_freq_FFT[np.abs(freqs) < freq_threshold]) / len(high_freq_FFT)

    # calculated signal from frequencies
    filtered_sig = np.fft.ifft(high_freq_FFT)

    ### Calculate the extended series ###
    indexes = list(range(len(data.values)))

    # sort indexes by frequency, lower -> higher
    indexes.sort(key=lambda i: np.absolute(freqs[i]))

    t = np.arange(0, len(data.values) + n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes:
        ampli = np.absolute(high_freq_FFT[i]) / len(data.values)  # amplitude
        phase = np.angle(high_freq_FFT[i])  # phase
        restored_sig += ampli * np.cos(2 * np.pi * freqs[i] * t + phase)  # convert frequency back to signal

    # array of fourier time series data
    fourier_series = restored_sig + p[0] * t

    # Create a data series with the extended data
    extrap_data = pd.Series(fourier_series[-n_predict:],
                            index=pd.date_range(start=data.last_valid_index() + timedelta(days=1),
                                                end=data.last_valid_index() + timedelta(days=n_predict)),
                            name='Value')

    ### Debug code ###
    # fig2, ax2 = plt.subplots(1, 1, gridspec_kw={})
    # fig2.set_size_inches(10, 8)
    # ax2.plot(data.index, data, color='deepskyblue', label='Observed Data', linewidth=3)
    # ax2.plot(extrap_data.index, fourier_series, color='r', linestyle='--', label='Fourier Transform Series',
    #          linewidth=1)
    # plt.legend(['Observed Data', 'Fourier Transform Series'])
    # plt.savefig('fourier_extrap')
    # plt.legend()
    # plt.show()

    return extrap_data, p_filtered


def extend(dataSeries, fillMethod, fillDuration, fillOrder, extendMethod, n_predict, timeFilter):
    """
    Performs initial formatting of the data to allow for correct filling behavior

    Parameters
    ----------


    Returns
    -------

    """

    ### Fill the missing data using the user specified method ###
    # Fill the data
    dataFilled = fill_missing(dataSeries, fillMethod, fillDuration, order=fillOrder)

    # Strip NaNs from the start of the series
    stopIndex = -1
    for x in range(0, len(dataFilled.values), 1):
        if np.isnan(dataFilled.values[x]):
            stopIndex = x
        else:
            break

    dataFilled = dataFilled[stopIndex + 1:]

    # Calculate the timestep of the data
    # todo: this needs to look across the time series
    # timeDifference = dataFilled.index[1:] - dataFilled.index[0:len(dataFilled.index)-1]
    # timeStep = min(timeDifference)
    timeStep = dataFilled.index[1] - dataFilled.index[0]

    # Check that there are no gaps
    # todo: Enforce gapless time series
    # timeSpacing = np.array([(dataFilled.index[x] - dataFilled.index[x-1]) > timeStep
    #                         for x in range(1, len(dataFilled), 1)]).astype(bool)
    # assert not np.any(timeSpacing), "Unable to extend. Gaps are present in the time series."

    # Check that there are no infinte values
    assert not np.any(np.isinf(dataFilled.values)), "Unable to extend. Infinite values are present in the time series."

    # Check that there are no NaNs in the data
    # todo: clip starting/ending NaN values
    # assert not np.any(np.isnan(dataFilled.values)), "Unable to extend. NaN values are present in the time series."

    if extendMethod == "linear":
        # Extend using a linear process
        extendedSeries = linear(dataFilled, n_predict)
        densityLost = 0

    elif extendMethod == 'fourier':
        # Extend using a fourier process
        # Set the filter to account for the timestep and specified time period
        if timeStep.days == 1 and timeFilter == 'Day':
            timeThreshold = 1
        elif timeStep.days == 1 and timeFilter == 'Week':
            timeThreshold = 7
        elif timeStep.days == 1 and timeFilter == 'Month':
            timeThreshold = 30
        elif timeStep.days == 1 and timeFilter == 'Year':
            timeThreshold = 365
        elif timeStep.days == 7 and timeFilter == 'Month':
            timeThreshold = 4
        elif timeStep.days == 7 and timeFilter == 'Year':
            timeThreshold = 52
        elif (timeStep.days == 30 or timeStep.days == 31 or timeStep.days == 28)  and timeFilter == 'Year':
            timeThreshold = 12

        # Call the extend function
        extendedSeries, densityLost = fourier(dataFilled, n_predict, timeThreshold)

    else:
        # Extend method is not understood by the parser
        raise NotImplementedError('Type of extension is not understood')

    return extendedSeries, densityLost

