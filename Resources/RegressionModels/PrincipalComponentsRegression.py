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
        ('Coefficients', None),
        ('# of Princ. Comps', None)
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
      
      if param_key == '# of Princ. Comps':

        self.exposed_params[param_key] = self.n_pcs
        continue
    
  def to_princ_comps(self, data):

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
    
    self.mean = np.nanmean(x, axis=0)
    self.std = np.nanstd(x, axis=0, ddof=1)
    x_std = (x-self.mean)/self.std

    PC, self.evals, self.evecs = self.to_princ_comps(x_std)
    cum_var = np.cumsum(self.evals)/PC.shape[1]
    self.n_pcs = np.where(cum_var >= 0.9)[0][0] + 1
    PC = PC[:, :self.n_pcs]

    # Find the best

    for indices in self.cross_validation.yield_samples(len(y)):

      x_train = PC[indices]
      y_train = y[indices]

      self.train_model(x_train, y_train)
      
      idx = [not elem for elem in indices]
      x_test = x[idx]
      y_test = y[idx]
      y_p_cv = self.predict(x_test)
      
      y_p = np.append(y_p, y_p_cv)
      y_a = np.append(y_a, y_test)
    
    # Fit the model as normal
    self.train_model(PC, y)
    
    return y_p, y_a
  
  def train_model(self, x, y):
    
    n_row = len(y)
    
    mX = np.column_stack([np.ones(n_row), x])
    if np.linalg.cond(mX) < 1/float_info.epsilon:
      beta  = np.linalg.pinv(mX.T.dot(mX)).dot(mX.T).dot(y)
    else:
      beta = np.full(mX.shape[1], np.nan)

    # Convert coefficients to real space
    self.coef_ = [0]*len(self.evecs)
    for ithVec in range(0, len(self.evecs)):
      for ithPC in range(0, self.n_pcs):
        self.coef_[ithVec] = self.coef_[ithVec] + (self.evecs[ithVec][ithPC] * beta[1+ithPC])/self.std[ithVec]
    intercept = beta[0] - np.dot(self.mean, self.coef_)
    self.coef_ = np.array([intercept] + self.coef_)
    return

  def predict(self, x):

    if x.ndim == 1:
      mX = np.append([1], x)
    else:
      mX = np.column_stack([np.ones(len(x)), x])

    return mX.dot(self.coef_)
  
  


  