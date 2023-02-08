from . import KFOLD10, KFOLD5, LOO
from collections import OrderedDict

CROSS_VALIDATION = OrderedDict(
  [
    ('KFOLD-10', KFOLD10),
    ('KFOLD-5', KFOLD5),
    ('LEAVE ONE OUT', LOO)
  ]
)