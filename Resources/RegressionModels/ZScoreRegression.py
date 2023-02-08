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

    return np.array([True if c>=0 else False for c in self.real_coef])
  
  def update_params(self):

    for param_key in self.exposed_params.keys():

      if param_key == 'Intercept':

        self.exposed_params[param_key] = self.intercept
        continue

      if param_key == 'Coefficients':

        coef = self.real_coef[~np.isnan(self.real_coef)]
        self.exposed_params[param_key] = coef
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

    self.mean = np.nanmean(x, axis=0)
    self.std = np.nanstd(x, axis=0, ddof=1)

    self.z_scr = (x - self.mean) / self.std
    self.masks = [~np.isnan(self.z_scr[:,i]) & ~np.isnan(y) for i in range(self.z_scr.shape[1])]
    self.r2_scr = np.array([np.corrcoef(x=self.z_scr[self.masks[i]][:, i], y=y[self.masks[i]])[0,1]**2 for i in range(self.z_scr.shape[1])])
    numerator = np.nansum(self.r2_scr*self.z_scr,axis=1)
    divisors = np.nansum(np.where(~np.isnan(self.z_scr), self.r2_scr, np.nan),axis=1)

    C = numerator/divisors
    
    mX = np.column_stack([np.ones(n_row), C])
    
    if np.linalg.cond(mX) < 1/float_info.epsilon:
      a = mX.T.dot(mX)
      beta  = np.linalg.pinv(a).dot(mX.T).dot(y)
    else:
      beta = np.full(mX.shape[1], np.nan)
    
    self.coef_ = beta
    self.real_coef = np.array([0]*len(self.r2_scr))
    self.intercept = self.coef_[0]
    for ithTerm in range(0, len(self.r2_scr)):
      c = self.coef_[1]*self.r2_scr[ithTerm] / (self.std[ithTerm] * np.nansum(self.r2_scr))
      self.real_coef[ithTerm] = c
      self.intercept = self.intercept + -1*c*self.mean[ithTerm]

    return
  
  def predict(self, x):

    if x.ndim == 1:
      x = x.reshape(1,len(x))

    # Convert to Composite Value
    z = (x-self.mean)/self.std
    numerator = np.nansum(self.r2_scr * z, axis=1)
    divisors = np.nansum(np.where(~np.isnan(z), self.r2_scr, np.nan),axis=1)
    C = numerator / divisors

    mX = np.column_stack([np.ones(len(C)), C])

    return mX.dot(self.coef_)