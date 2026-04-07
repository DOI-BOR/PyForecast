from collections import OrderedDict

from . import MultipleLinearRegression, PrincipalComponentsRegression, ZScoreRegression

REGRESSORS = OrderedDict(
    [
        ("MULTIPLE LINEAR REGRESSION", MultipleLinearRegression.Regressor),
        ("PRINCIPAL COMPONENT REGRESSION", PrincipalComponentsRegression.Regressor),
        ("Z-SCORE REGRESSION", ZScoreRegression.Regressor)
    ]
)
