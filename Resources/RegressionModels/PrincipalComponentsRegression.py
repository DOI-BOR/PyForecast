from PyQt5.QtWidgets import QApplication
import numpy as np
from sys import float_info
from collections import OrderedDict
from numba import jit

app = QApplication.instance()
finfo = float_info.epsilon

class Regressor:

  def __init__(self, cross_validation = None):

    self.exposed_params = OrderedDict(
      [
        ('Intercept', None),
        ('Coefficients', None),
        ('# of Princ. Comps', None)
      ]
    )
    
    self.pc_retain = app.config['max_pc_mode_variance']
    
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
      
      if param_key == '# of Princ. Comps':

        self.exposed_params[param_key] = self.n_pcs
        continue
  
  @staticmethod
  @jit(nopython=True)
  def to_princ_comps(data):

    # Compute the covariance matrix
    cov = np.cov(data, rowvar = False, ddof = 1)

    # Compute the eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort the eigenvalues in decreasing order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx]
    eigenvalues = eigenvalues[idx]

    # Transform and return the parameters
    return np.dot(data, eigenvectors), eigenvalues, eigenvectors

  
  def cross_val_predict(self, x, y):

    y_p = np.array([])
    y_a = np.array([])

    if x.shape[1] < 2:
      y_p = np.full(y.shape, np.nan)
      y_a = y
      return y_p, y_a
    
    self.mean = np.nanmean(x, axis=0, dtype=np.float64)
    self.std = np.nanstd(x, axis=0, ddof=1)
    if any(np.isnan(self.std)):
      return np.full(y.shape, np.nan), y
    if not all(self.std): 
      return np.full(y.shape, np.nan), y
    x_std = (x-self.mean)/self.std


    PC, self.evals, self.evecs = self.to_princ_comps(x_std)
    cum_var = np.cumsum(self.evals)/PC.shape[1]
    self.n_pcs = np.where(cum_var >= self.pc_retain)[0][0] + 1
    PC = PC[:, :self.n_pcs]

    # Find the best

    for indices in self.cross_validation.yield_samples(len(y)):

      x_train = PC[indices]
      y_train = y[indices]

      self.coef_ =self.train_model(x_train, y_train, self.evecs, self.n_pcs, self.std, self.mean)
      
      idx = [not elem for elem in indices]
      x_test = x[idx]
      y_test = y[idx]
      y_p_cv = self.predict(x_test)
      
      y_p = np.append(y_p, y_p_cv)
      y_a = np.append(y_a, y_test)
    
    # Fit the model as normal
    self.coef = self.train_model(PC, y, self.evecs, self.n_pcs, self.std, self.mean)
    
    return y_p, y_a
  
  @staticmethod
  @jit(nopython=True)
  def train_model(x, y, evecs, n_pcs, std, mean):
    
    n_row = len(y)
    ones = np.ones(n_row, dtype=np.float64)
    mX = np.column_stack((ones, x))
    if np.linalg.cond(mX) < 1/finfo:
      beta  = np.linalg.pinv(mX.T.dot(mX)).dot(mX.T).dot(y)
    else:
      beta = np.full(mX.shape[1], np.nan)

    # Convert coefficients to real space
    coef_ = np.array([0]*len(evecs), dtype=np.float64)
    for ithVec in range(0, len(evecs)):
      for ithPC in range(0, n_pcs):
        coef_[ithVec] = coef_[ithVec] + (evecs[ithVec][ithPC] * beta[1+ithPC])/std[ithVec]
    intercept = beta[0] - np.dot(mean, coef_)
    coef_ = np.append(intercept, coef_)
    #coef_ = np.array([intercept] + coef_)
    return coef_

  def predict(self, x):

    if x.ndim == 1:
      mX = np.append([1], x)
    else:
      mX = np.column_stack((np.ones(len(x)), x))

    return mX.dot(self.coef_)
  
  


  