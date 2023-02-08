from . import MultipleLinearRegression, PrincipalComponentsRegression, ZScoreRegression
from collections import OrderedDict

REGRESSORS = OrderedDict(
  [
    ("MULTIPLE LINEAR REGRESSION", MultipleLinearRegression.Regressor),
    ("PRINCIPAL COMPONENT REGRESSION", PrincipalComponentsRegression.Regressor),
    ("Z-SCORE REGRESSION", ZScoreRegression.Regressor)
  ]
)