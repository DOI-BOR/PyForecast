# SEQUENTIAL MIXED FLOATING SELECTION
# ITERATES BETWEEN FORWARD AND BACKWARD FLOATING SELECTION
import copy
from numpy import Inf, random, int64
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication
from time import time

app = QApplication.instance()

class SMFS:

  NAME = "Sequential Mixed Floating Selection"
  DESCR = "todo"

  def __init__(self, thread = None, configuration = None, num_predictors = None):

    self.config = configuration
    self.thread = thread
    self.num_predictors = len(self.config.predictor_pool)
    self.forcings = ['0' if not p.forced else '1' for p in self.config.predictor_pool.predictors]
    self.forcings = int(''.join(self.forcings), base=2)
    self.current_combo_1 = copy.deepcopy(self.forcings)
    self.running = False
    self.current_score_1 = Inf
    self.combo_1_status = 1 # 1 == ADDING, 0 == REMOVING
    self.combo_1_best_idx = None
    self.combo_1_current_idx = 0

    self.completed = []
    self.progress=0

    self.timeout_minutes = app.config['model_search_time_limit']
    self.timeout_seconds = self.timeout_minutes*60
    self.timer_incs = list(range(int(self.timeout_seconds/10), self.timeout_seconds, int(self.timeout_seconds/10)))


    self.first_randomizer = True

  def finish(self):

    num_evaluated = len(self.completed)
    num_possible = (2**self.num_predictors) - 1
    print(f"Evaluated {num_evaluated} out of {num_possible} possible models")
    self.running = False

  def randomize(self):

    if self.first_randomizer:
      self.current_combo_1 = (2**self.num_predictors) - 1
      self.first_randomizer = False
    else:
      self.current_combo_1 = random.randint(2**self.num_predictors, dtype=int64)
      self.current_combo_1 = self.current_combo_1 | self.forcings
    
   
  def toggle_bit(self, num, bit_idx):
    return (num ^ (1<<bit_idx))

  def convert_int_to_array(self, num):
    return list(reversed([bool(num & (1<<n)) for n in range(self.num_predictors)]))

  def next(self, last_score=None, score_type=0):

    if not self.running:
      print(f'Feature Selector: STARTING TIMER for {self.timeout_seconds} seconds')
      self.time = time()
      self.running = True
    
    if not last_score:
      if score_type == 0:
        last_score = Inf
      else:
        last_score = -Inf
    
    elapsed = time() - self.time
    if len(self.timer_incs)> 0:
      if (elapsed > self.timer_incs[0]):
        self.timer_incs.pop(0)
        print(f'Feature Selector: {int(elapsed)} seconds have elapsed')
    remaining = self.timeout_seconds - elapsed
    self.progress = min(100, int(100*(elapsed/self.timeout_seconds)))

    if remaining < 0:
      self.finish()
      return -1

    if score_type == 0 and (last_score < self.current_score_1):
      self.current_score_1 = last_score
      self.combo_1_best_idx = self.combo_1_current_idx-1
    if score_type == 1 and (last_score > self.current_score_1):
      self.current_score_1 = last_score
      self.combo_1_best_idx = self.combo_1_current_idx-1

    if not self.combo_1_current_idx == self.num_predictors:

      if self.combo_1_status: # Adding
        if not (self.current_combo_1 & 2**self.combo_1_current_idx):
          combo = (self.current_combo_1 | 2**self.combo_1_current_idx)
          combo = (combo | self.forcings)
          if combo in self.completed:
            self.combo_1_current_idx += 1
            return self.next()
          self.combo_1_current_idx += 1
          self.completed.append(combo)
          return combo
        else:
          self.combo_1_current_idx += 1
          return self.next()
      
      else: # removing
        if (self.current_combo_1 & 2**self.combo_1_current_idx):
          combo = self.toggle_bit(self.current_combo_1, self.combo_1_current_idx)
          combo = (combo | self.forcings)
          if combo in self.completed:
            self.combo_1_current_idx += 1
            return self.next()
          self.combo_1_current_idx += 1
          self.completed.append(combo)
          return combo
        else:
          self.combo_1_current_idx += 1
          return self.next()
          
    else:

      if self.combo_1_status:
        if self.combo_1_best_idx:
          self.current_combo_1 = (self.current_combo_1 | 2**self.combo_1_best_idx)
          self.current_combo_1 = (self.current_combo_1 | self.forcings)
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          return self.next()
        else:
          self.combo_1_status = 0
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          return self.next()
      else:
        if self.combo_1_best_idx:
          self.current_combo_1 = self.toggle_bit(self.current_combo_1, self.combo_1_best_idx)
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          return self.next()
        else:
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          self.randomize()
          return self.next()
    
      