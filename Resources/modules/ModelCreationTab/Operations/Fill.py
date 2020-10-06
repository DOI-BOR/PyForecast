import pandas as pd
import matplotlib.pyplot as plt

def fill_missing(data, method, limit, order=None):
    """
    objective: function is to be used by PyForecast tool to fill missing streamflow data

    Parameters
    ----------
    data: Pandas dataframe
        Structure assumes the date as the index and 1 column of streamflow values
    method: str
        Interpolation method, options included in PyForecast are 'nearest', 'linear', 'quadratic', 'cubic', 'spline',
        'polynomial', 'pchip', and 'akima'
    limit: int
        Maximum number of consecutive missing days to fill
    order: int
        If spline or polynomial method is selected, order must be specified

    Returns
    -------
    interp_data: Pandas dataframe
        Time series with missing data values interpolated up to the maximum day limit specified

    """

    # create time series with missing data interpolated
    interp_data = data.interpolate(method=method, limit=limit, order=order)

    # Debug data for plotting
    # plot the data
    # fig, ax = plt.subplots(1, 1, gridspec_kw={})
    # fig.set_size_inches(10, 8)

    # interp_data.plot(ax=ax, linestyle='--', color='r')
    # data.plot(ax=ax, linestyle='-', color='k')
    # ax.set_ylabel("Daily Avg Inflow (cfs)")
    # ax.legend(["Missing Interpolated", "Observed Data"], loc='upper right')
    # plt.savefig('fill_missing')
    # plt.show()

    return interp_data