#PyForecast uses 2 main datastructures to store information related to data and forecasts: The datasetDir dictionary and the forecastDict dictionary.

#Structure of the datasetDir dictionary:

self.datasetDir = {
    "datasets": [
        {
            "PYID"      : "12AR39S",
            "NAME"      : "Beaverton Rvr Near Porcupine, ID",
            "ID"        : "06024430",
            "TYPE"      : "USGS",
            "Parameter" : "Streamflow",
            "Units"     : "CFS",
            "Resampling": "Mean",
            "Decoding"  : {
                "dataLoader":"USGS_NWIS"
            },
            "Data"      : pd.DataFrame(data, index = daily),
            "lastDateTime": "Timestamp(2011-02-24)"
        },
        {...},
        {...},
        {...},
        {...}
    ]
}

#Structure of the forecastDict dictionary:

self.forecastDict = {
    "PredictorPool" : {
        "SWE-Station-222" : {
            "January 1st" : {
                "prdID" : 211,
                "Data"  : pd.DataFrame(data, index = water years)
            },
            "January 15th" : {
                "prdID" : 212,
                "Data"  : pd.DataFrame(data, index = water years)
            },
            ...,
            ...
        },
        ...,
        ...
    },
    "EquationPools" : {
        "January 1st" : {
            "PredictorPool" : {
                "prdIDs" : [101, 104, 133, 152, ..., 211]
            },
            "Predictand" : {
                "Name"  : "Porcupine Reservoir Inflow April-July",
                "Unit" : "KAF",
                "Data"  : pd.DataFrame(data, index = water years)
            },
            "ForecastEquations" : [
                {
                    "fcstID"                : 20112,
                    "Type"                  : "Linear",
                    "Coef"                  : [12.3, -22.1, -1.0, 223],
                    "PrIDs"                 : [101, 133, 221, 141],
                    "Intercept"             : [-122],
                    "Metrics"               : {
                        "R2"        : 0.43,
                        "RMSE"      : 233,
                        "Std Error" : 12,
                        "other"     : ...
                    },
                    "Cross Validation"      : "Leave-One-Out",
                    "Children Forecasts"    : [None],
                    "Forecasted"            : pd.DataFrame(forecasts, index = water years)
                },
                {...},
                {...},
                {...}
            ]
        }
    },
    "Options" : {
        "fcstPeriodStart"   : "April",
        "fcstPeriodEnd"     : "July",
        "fcstFreq"          : "BiMonthly",
        "fcstTarget"        : "Porcupine Reservoir ID (INFLOWS)",
        "forecaster"        : "Jane Doe",
        "fcstNotes"         : "The forecasts created here are ....",
        "accumSelect"       : True,
        "accumStart"        : "November"
    }
}