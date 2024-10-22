import numpy as np

# Dictionary to dscribe whether higher scores are better (True)
# or lower scores are better (False)
SCORING_RULES = {
    "R2":       True,
    "ADJ_R2":   True,
    "MAE":      False,
    "RMSE":     False,
    "MSE":      False,
    "AIC":      False,
    "AIC_C":    False,
    "STD_ERR":  False,
}

def sortScores(scores = None):
    """
    Sorts a list of scores in ascending order using
    the 'scoreCompare' function below. 

    'scores' is a list of scores such as:
        [{"ADJ_R2":0.553, "MSE":332.1}, {"ADJ_R2":0.43, "MSE":112.1}, ...]

    Scores are sorted with a quicksort algorithm
    taken from https://stackoverflow.com/questions/18262306/quicksort-with-python

    I clearly don't understand the magic behind quicksort,
    so i won't even begin to comment this code!
    """

    def partition(array, begin, end):
        pivot = begin
        for i in range(begin+1, end+1):
            if scoreCompare(oldScores = array[i]['Score'], newScores = array[begin]['Score'], nested=False):
                pivot += 1
                array[i], array[pivot]  = array[pivot], array[i]
        array[pivot], array[begin] = array[begin], array[pivot]
        return pivot

    def quicksort(array, begin=0, end=None):
        if end is None:
            end = len(array) - 1
        def _quicksort(array, begin, end):
            if begin >= end:
                return
            pivot = partition(array, begin, end)
            _quicksort(array, begin, pivot-1)
            _quicksort(array, pivot+1, end)
        return _quicksort(array, begin, end)

    # Perform quicksort
    quicksort(scores)

    return


def scoreCompare(oldScores = None, newScores = None, nested = False):
    """
    Checks wheter all the scores in the newScores list
    are better than all the scores in the oldScores list.
    Returns False otherwise.

    Note: Some models may show up with NAN scores. The non-nan
    scoring model will always win in that situation.

    The 'nested' argument specifies whether the scores are nested
    1 layer beneath the predictor strings. For example, a nested
    score may look like this:
    
        {'100101011': {"ADJ_R2":0.944, "MSE":321.1}}
    
    while an unnested score may look like this:

        {"ADJ_R2":0.844, "MSE":324.2}

    """
    if nested:

        if np.any([(np.isnan(oldScores[next(iter(oldScores))][scoreName])) for scoreName in next(iter(oldScores.values())).keys()]):

            if np.any([(np.isnan(newScores[next(iter(newScores))][scoreName])) for scoreName in next(iter(oldScores.values())).keys()]):
                return False
            
            else:
                return True
        
        return np.all([(newScores[next(iter(newScores))][scoreName] > oldScores[next(iter(oldScores))][scoreName]) if SCORING_RULES[scoreName] 
                        else (newScores[next(iter(newScores))][scoreName] < oldScores[next(iter(oldScores))][scoreName])
                        for scoreName in next(iter(oldScores.values())).keys()])

    else:
        
        if np.any([(np.isnan(oldScores[scoreName])) for scoreName in oldScores.keys()]):

            if np.any([(np.isnan(newScores[scoreName])) for scoreName in oldScores.keys()]):
                return False
            
            else:
                return True

        return np.all([(newScores[scoreName] > oldScores[scoreName]) if SCORING_RULES[scoreName] 
                        else (newScores[scoreName] < oldScores[scoreName]) 
                        for scoreName in oldScores.keys()])

class Scorers(object):
    """
    Class to contain all the different model scorers,
    and information about the scorers
    """

    # Information dictionary
    INFO = {
        "AIC_C":{
            "NAME":"Akaike Information Criterion (Small sample size)",
            "WEBSITE":"https://en.wikipedia.org/wiki/Akaike_information_criterion#Modification_for_small_sample_size",
            "HTML":"<strong>AIC<sub>C</sub></strong>",
        },
        "AIC":{
            "NAME":"Akaike Information Criterion",
            "WEBSITE":"https://en.wikipedia.org/wiki/Akaike_information_criterion",
            "HTML":"<strong>AIC</strong>",
        },
        "RMSE":{
            "NAME":"Root Mean Squared Error",
            "WEBSITE":"https://en.wikipedia.org/wiki/Root-mean-square_deviation",
            "HTML":"<strong>RMSE</strong>"
        },
        "MSE":{
            "NAME":"Mean Squared Error",
            "WEBSITE":"https://en.wikipedia.org/wiki/Mean_squared_error",
            "HTML":"<strong>MSE</strong>"
        },
        "MAE":{
            "NAME":"Mean Absolute Error",
            "WEBSITE":"https://en.wikipedia.org/wiki/Mean_absolute_error",
            "HTML":"<strong>MAE</strong>"
        },
        "R2":{
            "NAME":"Coefficient of Determination",
            "WEBSITE":"https://en.wikipedia.org/wiki/Coefficient_of_determination",
            "HTML":"<strong>R<sup>2</sup></strong>"
        },
        "ADJ_R2":{
            "NAME":"Adjusted Coefficient of Determination",
            "WEBSITE":"https://en.wikipedia.org/wiki/Coefficient_of_determination#Adjusted_R2",
            "HTML":"<strong>R<sup>2</sup><sub>adj</sub></strong>"
        },
        "STD_ERR":{
            "NAME":"Standard Error",
            "WEBSITE":"https://en.wikipedia.org/wiki/Standard_error",
            "HTML":"<strong>Standard Error</strong>"
        }
    }

    def __init__(self):
        """
        Initialize the scorers class
        """

        return


    def AIC_C(self, y_obs, y_prd, n_features):
        """
        Computes the modified Akaike information Criterion for
        small sample sizes, specified for OLS regression.
        https://en.wikipedia.org/wiki/Akaike_information_criterion

            AICc = AIC + (2p^2 + 2p) / (n - p - 1)
            
            where AIC = 2p + n(ln(SSE))

            where SSE = Σ (y_obs - y_prd)^2

        """

        aic = self.AIC(y_obs, y_prd, n_features)
        n = len(y_obs)
        
        return aic + ((2*n_features*n_features) + 2*n_features) / (n - n_features - 1)


    def AIC(self, y_obs, y_prd, n_features):
        """
        Computes the Akaike Information Criterion for 
        the model. The formula is:
        https://en.wikipedia.org/wiki/Akaike_information_criterion

            AIC = 2p + n(ln(SSE))

            where SSE = Σ (y_obs - y_prd)^2
        """

        sse = sum((y_obs-y_prd)**2)  
        n = len(y_obs)

        return 2*n_features + (n*np.log(sse))


    def MAE(self, y_obs, y_prd, n_features):
        """
        Computes the Mean Absolute Error of the predictions
        versus the observed values. The formula is:

            MAE = 1/n Σ |(y_obs - y_prd)|
        """

        return (1/len(y_obs))*sum(np.abs(y_obs - y_prd))


    def RMSE(self, y_obs, y_prd, n_features):
        """
        Computes the Root Mean Squared Error of the Predictions
        versus the observations. If the predictions
        are cross validated, then this is equivalent to the
        mean-squared prediction error. The formula is:

            MSE = 1/n Σ (y_obs - y_prd)^2
            RMSE = sqrt(MSE)
        """

        return np.sqrt(self.MSE(y_obs, y_prd, n_features))


    def MSE(self, y_obs, y_prd, n_features):
        """
        Computes the Mean Squared Error of the Predictions
        versus the observations. If the predictions
        are cross validated, then this is equivalent to the
        mean-squared prediction error. The formula is:

            MSE = 1/n Σ (y_obs - y_prd)^2
        """

        return (1/len(y_obs))*sum((y_obs - y_prd)**2)


    def R2(self, y_obs, y_prd, n_features):
        """
        Computes the coefficient of determination between
        the observed Y Values and the predicted Y Values. The 
        R2 is computed with the formula:

            r2 = 1 - SS_residual / SS_Total
            = 1 - Σ((y_obs - y_prd)^2) / Σ((y_obs - mean(y))^2)

        """
        ss_res = sum((y_obs-y_prd)**2)          # Residual sum of squares
        ss_tot = sum((y_obs-np.mean(y_obs))**2) # Total sum of squares
        r2 = 1 - (ss_res/ss_tot)                # Coefficient of Determination

        return r2


    def ADJ_R2(self, y_obs, y_prd, n_features):
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


    def STD_ERR(self,y_obs, y_prd, n_features):
        """
        Computes the standard deviation of the error term between
        the observed Y Values and the predicted Y Values. The standard
        error is computed with the formula:

            std_err = StandardDeviation(y_obs - y_prd) / SquareRoot(n_samples)

        """

        n_samples = len(y_obs)                  # Number of samples
        ss_res = (y_obs-y_prd)                  # Array of errors

        std_err = np.std(ss_res) / np.sqrt(n_samples)

        return std_err