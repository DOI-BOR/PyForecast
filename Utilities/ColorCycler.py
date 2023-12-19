"""ColorCycler.py contains a class that cycles through a list of different colors
"""
from pyqtgraph import mkColor

class ColorCycler:
  """The ColorCycler class contains a list of colors and returns the colors as
  requested with the 'next()' function.
  """

  # List of colors to cycle through
  COLOR_CYCLER = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', 
    '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

  def __init__(self):
    """Constructor"""

    self.index = 0      # Keeps track of which color we last returned
    self.col = self.COLOR_CYCLER[self.index]

    return


  def next(self):
    """Returns the next color as a Qt-compatible color"""

    # Get the next color and increment the index
    self.col =  self.COLOR_CYCLER[self.index]
    self.index = (self.index + 1) % len(self.COLOR_CYCLER)
    
    return mkColor(self.col)