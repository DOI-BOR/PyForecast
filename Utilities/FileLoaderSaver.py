from PyQt5.QtWidgets import QApplication
import pickle


app = QApplication.instance()

def current_version_less_than(v_file, v_check):
  current_version_int = int(v_file.replace('.',''))
  check_version_int = int(v_check.replace('.',''))
  return current_version_int < check_version_int
  

def load_file(f):

  # Load the file version
  f_version = pickle.load(f)

  # Handle older versions without unit-changing functionality
  if current_version_less_than(f_version, '5.0.3'):
    # Datasets
    datasets = pickle.load(f)
    for i in range(len(datasets)):
      datasets[i].raw_unit = datasets[i].unit
      datasets[i].display_unit = datasets[i].unit    
    
  else:
    datasets = pickle.load(f)
  
  # Load the data
  app.datasets.load_from_file(datasets)
  app.model_configurations.load_from_file(f)
  app.saved_models.load_from_file(f)


def save_to_file(f):
  pickle.dump(app.PYCAST_VERSION, f, 4)
  pickle.dump(app.datasets.datasets, f, 4)
  app.model_configurations.save_to_file(f)
  app.saved_models.save_to_file(f)

