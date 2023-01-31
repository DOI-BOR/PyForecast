from PyQt5.QtWidgets import QApplication
import numpy as np
from sys import float_info
from collections import OrderedDict

app = QApplication.instance()

class Regressor:

  def __init__(self, cross_validation = None):

    self.exposed_params = OrderedDict(
      [
        ('Intercept', None),
        ('Coefficients', None)
      ]
    )
    
    self.cross_validation = app.cross_validation[cross_validation]
    self.coef_ = np.full((500,), np.nan)

  def is_positive_corr(self):

    return np.array([True if c>=0 else False for c in self.coef_[1:]])
  
  def update_params(self):

    for param_key in self.exposed_params.keys():

      if param_key == 'Intercept':

        self.exposed_params[param_key] = self.coef_[0]
        continue

      if param_key == 'Coefficients':

        coef = self.coef_[~np.isnan(self.coef_)]
        self.exposed_params[param_key] = coef[1:]
        continue

  def cross_val_predict(self, x, y):

    y_p = np.array([])
    y_a = np.array([])


    for indices in self.cross_validation.yield_samples(len(y)):

      x_train = x[indices]
      y_train = y[indices]

      self.train_model(x_train, y_train)
      
      idx = [not elem for elem in indices]
      x_test = x[idx]
      y_test = y[idx]
      y_p_cv = self.predict(x_test)
      
      y_p = np.append(y_p, y_p_cv)
      y_a = np.append(y_a, y_test)
    
    # Fit the model as normal
    self.train_model(x, y)
    
    return y_p, y_a
  
  def train_model(self, x, y):
    
    n_row = len(y)
    
    mX = np.column_stack([np.ones(n_row), x])
    
    if np.linalg.cond(mX) < 1/float_info.epsilon:
      a = mX.T.dot(mX)
      beta  = np.linalg.pinv(a).dot(mX.T).dot(y)
    else:
      beta = np.full(mX.shape[1], np.nan)
    self.coef_ = beta

    return

  def predict(self, x):

    if x.ndim == 1:
      mX = np.append([1], x)
    else:
      mX = np.column_stack([np.ones(len(x)), x])

    return mX.dot(self.coef_)


  