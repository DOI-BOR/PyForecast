# SEQUENTIAL MIXED FLOATING SELECTION
# ITERATES BETWEEN FORWARD AND BACKWARD FLOATING SELECTION
import copy
from numpy import Inf, random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from numba import jit

app = QApplication.instance()

class BruteForce:

  NAME = "Brute Force Selection"
  DESCR = "todo"

  def __init__(self, thread=None, configuration = None, num_predictors = None):

    self.config = configuration
    self.thread=thread
    self.num_predictors = len(self.config.predictor_pool)
    self.forcings = ['0' if not p.forced else '1' for p in self.config.predictor_pool.predictors]
    self.num_forced = sum([int(f) for f in self.forcings])
    self.forcings = int(''.join(self.forcings), base=2)
    self.total = (2**self.num_predictors-self.num_forced)-1
    self.completed = []
    self.current_index = 0
    self.running = True
    self.progress = 0
    self.num_possible = (2**(self.num_predictors-self.num_forced)) - 1

  def finish(self):

    num_evaluated = len(self.completed)
    
    print(f"Evaluated {num_evaluated} out of {self.num_possible+1} possible models")
    self.running = False

  @staticmethod
  @jit(nopython=True, cache=True)
  def convert_int_to_array(num, num_p):
    return list([bool(num & (1<<n)) for n in range(num_p)])[::-1]
  
  def next(self, last_score=Inf, score_type = 0):

    if not self.running:
      return -1
    if self.current_index < 2**self.num_predictors:
      self.progress = int(100 * self.current_index / 2**self.num_predictors)
      model = (self.current_index | self.forcings)
      if model in self.completed:
        self.current_index += 1
        return self.next()
      else:
        self.current_index += 1
        self.completed.append(model)
        return model
    else:
      self.progress = 100
      self.finish()
      return -1

    # if self.current_index <= self.total:
    #   self.progress = int(100 * self.current_index / self.total)
    #   if self.current_index == self.total:
    #     self.finish()
    #   model = (self.current_index | self.forcings)
    #   if model in self.completed:
    #     if not self.running:
    #       return -1
    #     self.current_index += 1
    #     return self.next()
    #   else:
    #     self.current_index += 1
    #     self.completed.append(model)
    #     return model
    
   

    


