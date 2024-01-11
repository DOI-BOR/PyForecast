# SEQUENTIAL MIXED FLOATING SELECTION
# ITERATES BETWEEN FORWARD AND BACKWARD FLOATING SELECTION
import copy
from numpy import Inf, random, int64
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication
from time import time
from numba import jit

app = QApplication.instance()

class SMFS:

  NAME = "Sequential Mixed Floating Selection"
  DESCR = "todo"

  def __init__(self, thread = None, configuration = None, num_predictors = None):

    self.config = configuration
    self.thread = thread
    self.num_predictors = len(self.config.predictor_pool)

    # Keep a record of which predictors are to be forced into all models.
    self.forcings = ['0' if not p.forced else '1' for p in self.config.predictor_pool.predictors]
    self.num_forced = sum([int(f) for f in self.forcings])
    self.forcings = int(''.join(self.forcings), base=2)

    # Keep information about the current predictor combination.
    self.current_combo_1 = copy.deepcopy(self.forcings)
    self.current_score_1 = Inf
    self.combo_1_status = 1     # 1 == ADDING PHASE, 0 == REMOVING PHASE
    self.combo_1_best_idx = None
    self.combo_1_current_idx = 0

    # Feature selection process info
    self.completed = []
    self.progress=0
    self.running = False

    # Feature selection timer.
    self.timeout_minutes = app.config['model_search_time_limit']
    self.timeout_seconds = self.timeout_minutes*60
    self.timer_incs = list(range(int(self.timeout_seconds/10), self.timeout_seconds, int(self.timeout_seconds/10)))

   
    self.first_randomizer = True
    self.rec_cnt = 0

    self.num_possible = (2**(self.num_predictors-self.num_forced)) - 1

    return

  def finish(self):

    num_evaluated = len(self.completed)
    
    print(f"Evaluated {num_evaluated} out of {self.num_possible} possible models")
    self.running = False

  def randomize(self):


    if self.first_randomizer:
      self.current_combo_1 = (2**self.num_predictors) - 1
      self.first_randomizer = False
    else:
      self.current_combo_1 = random.randint(2**self.num_predictors, dtype=int64)
      self.current_combo_1 = self.current_combo_1 | self.forcings
  
  @staticmethod
  @jit(nopython=True, cache=True)
  def toggle_bit(num, bit_idx):
    return (num ^ (1<<bit_idx))

  @staticmethod
  @jit(nopython=True, cache=True)
  def convert_int_to_array(num, num_p):
    return list([bool(num & (1<<n)) for n in range(num_p)])[::-1]

  def next(self, last_score=None, score_type=0, recurs = False):

    self.rec_cnt += recurs
    if not self.rec_cnt:
      self.rec_cnt = 0
    if self.rec_cnt > self.num_predictors:
      #print('recursion count exceeded')
      self.randomize()
      self.rec_cnt = 0
      return -1


    # initialize the features selector with a start time.
    if not self.running:
      print(f'Feature Selector: STARTING TIMER for {self.timeout_seconds} seconds')
      self.time = time()
      self.running = True
      if score_type == 0:
        self.current_score_1 = Inf
      else:
        self.current_score_1 = -Inf
    
    # If there's no 'last_score' set last_score to +/- inf.
    if not last_score:
      if score_type == 0:
        last_score = Inf
      else:
        last_score = -Inf
    
    # Check the elapsed time to see if we need to stop. Also update progress.
    elapsed = time() - self.time
    if len(self.timer_incs)> 0:
      if (elapsed > self.timer_incs[0]):
        self.timer_incs.pop(0)
        print(f'Feature Selector: {int(elapsed)} seconds have elapsed')
    remaining = self.timeout_seconds - elapsed
    self.progress = min(100, int(100*(elapsed/self.timeout_seconds)))

    if len(self.completed) >= self.num_possible - 3:
      self.finish()
      return -1

    if remaining < 0:
      self.finish()
      return -1

    # Check if the last score beats the current score.
    # if so, set the bext idx to the last idx
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
            return self.next(last_score, score_type = score_type, recurs=True)
          self.combo_1_current_idx += 1
          self.completed.append(combo)
          return combo
        else:
          self.combo_1_current_idx += 1
          return self.next(last_score, score_type = score_type, recurs=True)
      
      else: # removing
        if (self.current_combo_1 & 2**self.combo_1_current_idx):
          combo = self.toggle_bit(self.current_combo_1, self.combo_1_current_idx)
          combo = (combo | self.forcings)
          if combo in self.completed:
            self.combo_1_current_idx += 1
            return self.next(last_score, score_type = score_type, recurs=True)
          self.combo_1_current_idx += 1
          self.completed.append(combo)
          return combo
        else:
          self.combo_1_current_idx += 1
          return self.next(last_score, score_type = score_type, recurs=True)
          
    else:

      if self.combo_1_status:

        if self.combo_1_best_idx:
          self.current_combo_1 = (self.current_combo_1 | 2**self.combo_1_best_idx)
          self.current_combo_1 = (self.current_combo_1 | self.forcings)
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          return self.next(last_score, score_type = score_type, recurs=True)
        else:
          self.combo_1_status = 0
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          return self.next(last_score, score_type = score_type, recurs=True)
        
      else:

        if self.combo_1_best_idx:
          self.current_combo_1 = self.toggle_bit(self.current_combo_1, self.combo_1_best_idx)
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          return self.next(last_score, score_type = score_type, recurs=True)
        else:
          self.combo_1_current_idx = 0
          self.combo_1_best_idx = None
          if not self.first_randomizer:
            self.combo_1_status = 1
          self.randomize()
          
          return self.next(score_type = score_type, recurs=True)
    
      