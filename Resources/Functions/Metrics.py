import numpy as np

def computeMetrics(cv_yStar, yStar, yActual, p):
    """
    Computes statistical metrics using observed values vs forecasted values.
    inputs:
     - yStar : forecastd / predicted values
     - yActual : actual / observed values
     - p : number of variables / predictors used to generate predicted values 

    outputs:
      - {
          "Cross Validated Adjusted R2" : adjusted coefficient of determination using cross validated predictand
          "Root Mean Squared Prediction Error: root-mean-squared-error using cross validated predictand
          "Cross Validated Nash Sutcliffe" : Nash Sutcliffe model efficiency coefficient using cross validated predictand
          "Adjusted R2" : <adjusted coefficient of determination using equation predictand>,
          "Root Mean Squared Error" : root-mean-squared-error using equation predictand>,
          "Nash-Sutcliffe" : Nash Sutcliffe model efficiency coefficient using equation predictand>
      }

    """

    yActual = np.array(yActual).flatten()
    yStar = np.array(yStar).flatten()
    cv_yStar = np.array(cv_yStar).flatten()

    """ Compute adjR2 values """
    yMean = float(np.mean(yActual))
    ssTotal = float(np.sum((yActual - yMean)**2))
    ssResidual = float(np.sum((yActual - yStar)**2))
    cv_ssResidual = float(np.sum((yActual - cv_yStar)**2))
    r2 = 1 - (ssResidual / ssTotal)
    cv_r2 = 1 - (cv_ssResidual / ssTotal)
    n = len(yActual)
    if n == (p+1):
        n = p + 1 + 0.00000001
    adjR2 = 1 - ((n-1)/(n-(p+1)))*(1-r2)
    cv_adjR2 = 1 - ((n-1)/(n-(p+1)))*(1-cv_r2)

    """ Compute MAE values """
    mae = float(np.sum(np.abs(yStar - yActual))) / (n-(p+1))

    """ Compute the RMSE """
    mse = ssResidual / (n-(p+1))
    cv_mse = cv_ssResidual / (n-(p+1))
    rmse = np.sqrt(mse)
    cv_rmse = np.sqrt(cv_mse)

    """ Compute the variance """
    s = ssTotal / (n-(p+1))

    """ Compute the nash-sutcliffe """
    numerator = np.sum((yStar - yActual)**2)
    cv_numerator = np.sum((cv_yStar - yActual)**2)
    denominator = np.sum((yActual - yMean)**2)
    nse = 1 - numerator / denominator
    cv_nse = 1 - cv_numerator / denominator


    return {"Cross Validated Adjusted R2" : cv_adjR2,
        "Root Mean Squared Prediction Error": cv_rmse,
        "Cross Validated Nash-Sutcliffe" : cv_nse,
        "Adjusted R2" : adjR2, 
        "Root Mean Squared Error": rmse, 
        "Nash-Sutcliffe" : nse,
        "Sample Variance" : s,
        "Mean Absolute Error" : mae}


def metricBetterThan( newMetric, oldMetric, perfMeasure ):
    """
    Function to compare two performance measure values and determine which one is more skillfull.
    """
    trueFalse = None

    if perfMeasure == "Adjusted R2" or perfMeasure == "Cross Validated Adjusted R2":
        if oldMetric > newMetric:
            trueFalse = False
        else:
            trueFalse = True

    elif perfMeasure == 'Root Mean Squared Error' or perfMeasure == 'Root Mean Squared Prediction Error' or perfMeasure == 'Mean Absolute Error':
        if oldMetric < newMetric:
            trueFalse = False
        else:
            trueFalse = True

    else:
        if oldMetric > newMetric:
            trueFalse = False
        else:
            trueFalse = True

    return trueFalse

def computeR2(yStar, yActual):
    yActual = np.array(yActual).flatten()
    yStar = np.array(yStar).flatten()
    yMean = float(np.mean(yActual))
    ssTotal = np.sum((yActual - yMean)**2)
    ssResidual = np.sum((yActual - yStar)**2)
    r2 = 1 - (ssResidual / ssTotal)
    return r2