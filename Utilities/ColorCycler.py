from pyqtgraph import mkColor

class ColorCycler:
  COLOR_CYCLER = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

  def __init__(self):
    self.index = 0

  def next(self):
    col =  self.COLOR_CYCLER[self.index]
    self.index = (self.index + 1) % len(self.COLOR_CYCLER)
    return mkColor(col)