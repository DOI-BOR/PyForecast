from collections import OrderedDict

from . import KFOLD10, KFOLD5, LOO

CROSS_VALIDATION = OrderedDict(
    [
        ('KFOLD-10', KFOLD10),
        ('KFOLD-5', KFOLD5),
        ('LEAVE ONE OUT', LOO)
    ]
)
