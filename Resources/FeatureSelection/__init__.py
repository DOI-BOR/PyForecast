from . import SMFS, BruteForce
from collections import OrderedDict

FEATURE_SEL = OrderedDict([
  ('SMFS', SMFS.SMFS),
  ('Brute Force', BruteForce.BruteForce)
])