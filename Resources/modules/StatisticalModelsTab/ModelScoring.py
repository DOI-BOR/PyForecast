import numpy as np

SCORING_RULES = {
    "ADJ_R2":   True,
    "MSE":      False
}


def scoreCompare(oldScores = None, newScores = None):
    """
    Checks wheter all the scores in the newScores list
    are better than all the scores in the oldScores list.
    Returns False otherwise.
    """
    return np.all([(newScores[scoreName] > oldScores[scoreName]) if SCORING_RULES[scoreName] 
                        else (newScores[scoreName] < oldScores[scoreName]) 
                        for scoreName in oldScores.keys()])


def AIC(y_obs, y_prd, n_features):
    """
    Computes the Akaike Information Criterion for 
    the model. The formula is:

        AIC = n(ln(2π) + ln(SSE) - ln(n)) + 2(n+p+1)

        where SSE = Σ (y_obs - y_prd)^2
    """

    sse = sum((y_obs-y_prd)**2)  
    n = len(y_obs)
    return n*(np.log(2*np.pi) + np.log(sse) - np.log(n)) + 2*(n+n_features+1)

def MSE(y_obs, y_prd, n_features):
    """
    Computes the Mean Squared Error of the Predictions
    versus the observations. If the predictions
    are cross validated, then this is equivalent to the
    mean-squared prediction error. The formula is:

        MSE = 1/n Σ (y_obs - y_prd)^2
    """

    return (1/len(y_obs))*sum((y_obs - y_prd)**2)


def ADJ_R2(y_obs, y_prd, n_features):
    """
    Computes the adjusted coefficient of determination between
    the observed Y Values and the predicted Y Values. The adjusted
    R2 is computed with the formula:

        r2 = 1 - SS_residual / SS_Total
           = 1 - Σ((y_obs - y_prd)^2) / Σ((y_obs - mean(y))^2)

        adj-r2 = 1 - (1 - r2)(n_samples - 1)/(n_samples - n_features - 1)

    """

    n_samples = len(y_obs)                  # Number of samples
    ss_res = sum((y_obs-y_prd)**2)          # Residual sum of squares
    ss_tot = sum((y_obs-np.mean(y_obs))**2) # Total sum of squares
    r2 = 1 - (ss_res/ss_tot)                # Coefficient of Determination
    
    adj_r2 = 1 - (1 - r2)*(n_samples - 1)/(n_samples - n_features - 1)

    return adj_r2