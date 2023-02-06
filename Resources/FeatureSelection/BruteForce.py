# SEQUENTIAL MIXED FLOATING SELECTION
# ITERATES BETWEEN FORWARD AND BACKWARD FLOATING SELECTION
import copy
from numpy import Inf, random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

app = QApplication.instance()

class BruteForce:

  NAME = "Brute Force Selection"
  DESCR = "todo"

  def __init__(self, thread=None, configuration = None, num_predictors = None):

    self.config = configuration
    self.thread=thread
    self.num_predictors = len(self.config.predictor_pool)
    self.forcings = ['0' if not p.forced else '1' for p in self.config.predictor_pool.predictors]
    self.forcings = int(''.join(self.forcings), base=2)
    self.total = (2**num_predictors)-1
    self.completed = []
    self.current_index = 0
    self.running = True
    self.progress = 0

  def convert_int_to_array(self, num):
    return list(reversed([bool(num & (1<<n)) for n in range(self.num_predictors)]))
  
  def next(self, last_score=Inf, score_type = 0):

    if self.current_index <= self.total:
      self.progress = int(100 * self.current_index / self.total)
      if self.current_index == self.total:
        self.running = False
      model = (self.current_index | self.forcings)
      if model in self.completed:
        if not self.running:
          return -1
        self.current_index += 1
        return self.next()
      else:
        self.current_index += 1
        self.completed.append(model)
        return model
    
   

    


