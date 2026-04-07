from collections import OrderedDict

from . import SMFS, BruteForce

FEATURE_SEL = OrderedDict([
    ('SMFS', SMFS.SMFS),
    ('Brute Force', BruteForce.BruteForce)
])
