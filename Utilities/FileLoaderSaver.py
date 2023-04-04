from PyQt5.QtWidgets import QApplication
from Models import *
import pickle
import pandas as pd


app = QApplication.instance()

def file_version_less_than(v_file, v_check):
  """Checks if the file version is less than the check version"""
  current_version_int = int(v_file.replace('.',''))
  check_version_int = int(v_check.replace('.',''))
  return current_version_int < check_version_int
  

def load_file(f):

  # Load the file version
  f_version = pickle.load(f)

  print(f"File version is {f_version}")

  if file_version_less_than(f_version, '5.0.9'):

    # Handle older versions without unit-changing functionality
    if file_version_less_than(f_version, '5.0.3'):
      
      # Datasets
      datasets = pickle.load(f)
      for i in range(len(datasets)):
        datasets[i].raw_unit = datasets[i].unit
        datasets[i].display_unit = datasets[i].unit    
      
    else:
      datasets = pickle.load(f)

    for dataset in datasets:
      app.datasets.datasets.append(dataset)
      print(f'Added Dataset: {dataset}')
      app.datasets.insertRow(app.datasets.rowCount())
    app.datasets.dataChanged.emit(app.datasets.index(0), app.datasets.index(app.datasets.rowCount()))
    
    app.model_configurations.load_from_file(f)
    app.saved_models.load_from_file(f)
  
  else:
    
    # Datasets
    len_datasets = pickle.load(f)
    for i in range(len_datasets):
      dataset_dict = pickle.load(f)
      dataset_dict['data'] = pd.read_pickle(f, compression={'method':None})
      
      dataset = app.datasets.add_dataset(**dataset_dict)

    # Configurations
    len_configs = pickle.load(f)
    for i in range(len_configs):
      config_dict = pickle.load(f)
      config_dict['predictand'] = pickle.load(f)
      len_predictors = pickle.load(f)
      config_dict['predictor_pool'] = ModelConfigurations.PredictorPool()
      for j in range(len_predictors):
        config_dict['predictor_pool'].add_predictor(pickle.load(f))
      len_regressors = pickle.load(f)
      config_dict['regressors'] = ModelConfigurations.Regressors()
      for j in range(len_regressors):
        config_dict['regressors'].add_regressor(pickle.load(f))
      app.model_configurations.add_configuration(**config_dict)

    # Saved Models
    num_saved_models = pickle.load(f)
    for i in range(num_saved_models):
      guid = pickle.load(f)
      regression_model = pickle.load(f)
      cross_validator = pickle.load(f)
      num_predictors = pickle.load(f)
      predictor_pool = []
      for j in range(num_predictors):
        p = pickle.load(f)
        predictor_pool.append(p)
      predictand = pickle.load(f)
      training_period_start = pickle.load(f)
      training_period_end = pickle.load(f)
      training_exclude_dates = pickle.load(f)
      issue_date = pickle.load(f)
      name = pickle.load(f)
      comment = pickle.load(f)
      forecasts = pickle.load(f)
      forecast_obj = SavedModels.ForecastList()
      forecast_obj.forecasts = forecasts
      app.saved_models.add_model(
        regression_model = regression_model,
        cross_validator = cross_validator,
        predictors = predictor_pool,
        predictand = predictand,
        training_period_start = training_period_start,
        training_period_end = training_period_end,
        training_exclude_dates = training_exclude_dates,
        issue_date = issue_date,
        name = name,
        comment = comment,
        guid = guid,
        forecasts=forecast_obj
      )

def save_to_file(f):

  pickle.dump(app.PYCAST_VERSION, f, 4)

  # Datasets
  pickle.dump(len(app.datasets), f, 4) # num datasets
  for dataset in app.datasets.datasets:
    d = dataset.__dict__
    pickle.dump({
      key: d[key]  for key in d.keys() if d != 'data'
    }, f, 4)
    dataset.data.to_pickle(f, compression = {'method':None}, protocol=4)
  
  # Model Configurations
  pickle.dump(len(app.model_configurations), f, 4)
  for config in app.model_configurations.configurations:
      config_dict = {}
      for (key, value) in config.__dict__.items():
        if key in config._ok_to_pickle:
          config_dict[key] = value
      pickle.dump(config_dict, f, 4)

      pickle.dump(config.predictand, f, 4)
      
      pickle.dump(len(config.predictor_pool), f, 4)
      for dataset in config.predictor_pool:
        pickle.dump(dataset, f, 4)
      
      pickle.dump(len(config.regressors), f, 4)
      for regressor in config.regressors:
        pickle.dump(regressor, f, 4)
  
  # Saved Models
  pickle.dump(len(app.saved_models), f, 4)
  for i in range(len(app.saved_models)):
    model = app.saved_models[i]
    pickle.dump(model.guid, f, 4)
    pickle.dump(model.regression_model, f, 4)
    pickle.dump(model.cross_validator,f ,4)
    pickle.dump(len(model.predictors), f, 4)
    for p in model.predictors:
      pickle.dump(p, f, 4)
    pickle.dump(model.predictand, f, 4)
    pickle.dump(model.training_period_start, f, 4)
    pickle.dump(model.training_period_end, f, 4)
    pickle.dump(model.training_exclude_dates, f, 4)
    pickle.dump(model.issue_date, f, 4)
    pickle.dump(model.name, f, 4)
    pickle.dump(model.comment, f, 4)
    pickle.dump(model.forecasts.forecasts, f, 4)
  #app.saved_models.save_to_file(f)

