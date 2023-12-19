from Plots.Common import pg, BarItem, ScatterItem, CurveItem
from Utilities.ColorCycler import ColorCycler
from Utilities import DateAxis
import pandas as pd
import numpy as np
from scipy.stats import linregress
from PyQt5.QtCore import QPoint

class Plot(pg.GraphicsLayoutWidget):