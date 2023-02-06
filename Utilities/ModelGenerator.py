from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from Utilities.HydrologyDateTimes import convert_to_water_year
from Models.SavedModels import Model
from itertools import compress
import pandas as pd
import numpy as np
from time import sleep
from inspect import signature

# Get the global application
app = QApplication.instance()


class ModelGenerator(QThread):

  updateProgSignal = pyqtSignal(int)
  updateTextSignal = pyqtSignal(str)
  newModelSignal = pyqtSignal(object)

  def __init__(self, selected_configuration = None):

    QThread.__init__(self)
    self.config = selected_configuration
    

  def run(self):

    # Check for any predictors that must be postively correlated
    positive_corr = np.array([p.mustBePositive for p in self.config.predictor_pool.predictors])

    self.updateTextSignal.emit('Generating predictor and predictand data')
    for predictor in self.config.predictor_pool.predictors:
      predictor.resample()
      if not predictor.data.empty:
        predictor.data = predictor.data.loc[convert_to_water_year(self.config.training_start_date):convert_to_water_year(self.config.training_end_date)]

    self.config.predictand.resample()
    self.config.predictand.data = self.config.predictand.data.loc[convert_to_water_year(self.config.training_start_date):convert_to_water_year(self.config.training_end_date)]

    # Collate the predictor data into a numpy array
    df = pd.DataFrame()
    for predictor in self.config.predictor_pool.predictors:
      df = pd.concat([df, predictor.data], axis=1)
    df = pd.concat([df, self.config.predictand.data], axis=1).sort_index()
    df = df.loc[convert_to_water_year(self.config.training_start_date):convert_to_water_year(self.config.training_end_date)]
    df = df.drop(self.config.training_exclude_dates, errors='ignore')
    
    preproc_method = app.preprocessing_methods['INV_' + self.config.predictand.preprocessing]
    if len(signature(preproc_method).parameters) > 1:
      inverse_preproc_params = True
    else:
      inverse_preproc_params = False

    # Iterate over the regression methods
    for regressor in self.config.regressors:

      print(f"Beginning model search for regressor: {regressor.regression_model} / {regressor.scoring_metric}")

      regression_algorithm = app.regressors[regressor.regression_model](cross_validation = regressor.cross_validation)
      scorer = app.scorers[regressor.scoring_metric]
  
      # Check if we can brute force or not
      num_forced = sum([p.forced for p in self.config.predictor_pool.predictors])
      num_empty = np.sum(df.isnull().all())
      if len(self.config.predictor_pool) - num_forced - num_empty <= app.config['brute_force_under_no']:
        bruteforce = True
        self.updateTextSignal.emit('Small number of predictors. Using <strong>Brute Force</strong> Feature Selection')
      else:
        bruteforce = False
      
      # Load the feature selection method
      feature_selector_name = regressor.feature_selection if not bruteforce else 'Brute Force'
      feature_selector = app.feature_selection[feature_selector_name](self, configuration = self.config, num_predictors =len(self.config.predictor_pool) - num_forced - num_empty )

      print(f'Starting feature selection with feature selector: {feature_selector_name}')
      count = 0
      score_type = 1 if regressor.scoring_metric in ['R2'] else 0
      score = np.Inf if score_type == 0 else -np.Inf
      while feature_selector.running or count == 0:
        predictors = feature_selector.next(score, score_type)
        self.updateProgSignal.emit(feature_selector.progress)
        if predictors == -1:
          break
        bool_index = feature_selector.convert_int_to_array(predictors)
        genome = ''.join([u'\u25cf' if b else u'\u25cc' for b in bool_index])
        self.updateTextSignal.emit(f'{genome}: Score ({regressor.scoring_metric})             ')
        run_data = df.iloc[:, bool_index + [True]].dropna()
        if  df.iloc[:, bool_index+[False]].dropna().empty:
          continue
        x_data = run_data.values[:,:-1]
        predictand_data = run_data.values[:, -1]
        pos = positive_corr[bool_index]
        y_p, y_a = regression_algorithm.cross_val_predict(x_data, predictand_data)
        if inverse_preproc_params:
          y_p = preproc_method(y_p, **self.config.predictand.params)
          y_a = preproc_method(y_a, **self.config.predictand.params)
        else:
          y_p = preproc_method(y_p)
          y_a = preproc_method(y_a)
        score = scorer(y_p, y_a)
        pos_param = regression_algorithm.is_positive_corr()
        should_we_skip = False
        for i, p in enumerate(pos):
          if p:
            if not pos_param[i]:
              should_we_skip = True
          else:
            pass
        if np.isnan(score):
          should_we_skip = True
        if should_we_skip:
          continue
          
        
        model = Model(
          regression_model = regressor.regression_model,
          cross_validator = regressor.cross_validation,
          predictors =  list(compress(self.config.predictor_pool.predictors, bool_index)),
          predictand = self.config.predictand, 
          training_period_start = self.config.training_start_date,
          training_period_end = self.config.training_end_date,
          training_exclude_dates = self.config.training_exclude_dates,
          issue_date = self.config.issue_date,
          score = score,
          cross_validation = regressor.cross_validation,
          genome = bool_index,
          regressor = regressor,
          scorer = regressor.scoring_metric
        )
        
        genome = f'{genome:40.40}' if len(genome) < 40 else f'{genome:37.37}...'
        self.updateTextSignal.emit(f'{genome}: Score ({regressor.scoring_metric}) {score:12.5g}')
        self.updateProgSignal.emit(feature_selector.progress)
        self.newModelSignal.emit(model)
        count += 1
        sleep(0.01)

    self.updateTextSignal.emit("Finished")


  def stop(self):
    self.updateTextSignal.emit("Finished")
    self.terminate()
    self.wait(1000)





      

    
    
