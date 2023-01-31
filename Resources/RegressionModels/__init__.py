from . import MultipleLinearRegression, PrincipalComponentsRegression
from collections import OrderedDict

REGRESSORS = OrderedDict(
  [
    ("MULTIPLE LINEAR REGRESSION", MultipleLinearRegression.Regressor),
    ("PRINCIPAL COMPONENT REGRESSION", PrincipalComponentsRegression.Regressor)
  ]
)