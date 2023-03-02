from PyQt5.QtWidgets import QApplication
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import OrderedDict

app = QApplication.instance()

class ForecastDisaggregator(object):

  def __init__(self, saved_model):

    self.model = saved_model
    self.forecasts = self.model.forecasts
    self.inflow_dataset = self.model.predictand.dataset
    self.traces = OrderedDict()


  def Disaggregate(self, years, start_date, end_date):

    if isinstance(years, int):
      years = [years]

    # Resample the target and covariates
    self.model.predictand.resample()
    for p in self.model.predictors:
      p.resample()
    
    # Compile the training data
    training_data = pd.DataFrame()
    for predictor in self.model.predictors:
      training_data = pd.concat([training_data, predictor.data], axis=1)
    
    # Append a row for perfect forecasts
    training_data = pd.concat([training_data, self.model.predictand.data], axis=1)

    # ITerate over years
    for year in years:

      self.traces[year] = OrderedDict()

      # Get the testing year
      testing_data = training_data.loc[year].values

      # Remove the forecast year from the training_data
      training_data_year = training_data.loc[~training_data.index.isin([year])]
      
      # Remove NaN's from target and training
      training_data_year = training_data_year.dropna()

      # keep reference to years
      training_years = training_data_year.index
      training_data_year = training_data_year.values

      # iterate over all exceedances
      exc_list = [int(e) for e in np.arange(start=1.25, stop=100, step=2.5)]
      for exc, val in self.forecasts.forecasts.loc[(year, slice(None))]['Value'].iteritems():
        if int(exc*100) not in exc_list:
          continue
        self.traces[year][exc] = OrderedDict()
        
        # Replace the testing value with the forecast
        testing_data[-1] = val

        # Convert the training data to PCA space
        training_PCA, eigenvals, eigenvecs = self.PCA(training_data_year.copy())
        distance_vector = self.PcaDistance(testing_data, training_PCA, eigenvecs, eigenvals)

        # Sort the distance vector and the year list
        training_years_sorted = [x for _, x in sorted(zip(distance_vector, training_years), reverse=True)]
        distance_vector.sort(reverse=True)

        # Compute the traces
        t_count = 0
        for k, analog_year_weight in enumerate(distance_vector):
          if t_count >= 5:
            continue
          y = training_years_sorted[k]
          if y >= 1999 and y <= 2019:
            t_count += 1
            idx = list(training_years).index(y)
            s = datetime(y, start_date.month, start_date.day)
            e = datetime(y, end_date.month, end_date.day)
            #trace = self.inflow_dataset.data.loc[s:e]
            #perf_fcst = training_data_year[idx][-1]

            # HACKY NCAR THING THAT JORDAN DEMANDED
            fname = f'C:\\Users\\KFoley\\Downloads\\jordandiagg\\NCAR\{y}0201\\tracemedian\\Buffalo_Bill_Inflows.local.rdf'
            with open(fname, 'r') as readfile:
              sd = readfile.readline().split(':')[1].strip()[:10]
              ed = readfile.readline().split(':')[1].strip()[:10]
            df = pd.read_csv(fname, skiprows=6, header=None)
            df = df.set_index(pd.DatetimeIndex(pd.date_range(sd, ed)))
            trace = df.loc[s:e]
            perf_fcst = float(trace.sum()*86.4/43560)
            trace = trace * (val/perf_fcst)
            self.traces[year][exc][k] = {
              'analog_year': y,
              'weight':analog_year_weight,
              'trace':trace
            }
    print()
    df = pd.DataFrame()
    labels = []
    for exc in self.traces[year]:
      for n in self.traces[year][exc]:
        y = self.traces[year][exc][n]['analog_year']
        data = self.traces[year][exc][n]['trace']
        label = f'EXC:{exc}/{n}/ANLG_YR:{y}'
        labels.append(label)
        data = self.traces[year][exc][n]['trace']
        data = data.set_axis(pd.DatetimeIndex(pd.date_range(f'{year}-04-01', f'{year}-07-31')))
        df = pd.concat([df, data], axis=1)
    df.columns = labels
    df.to_csv(f'C:/Users/KFoley/Downloads/BBR_DISAGG_NCAR_BLEND_{year}.csv')
    return self.traces

  def PcaDistance(self, testing_data, training_pc, evecs, evals):
    test = (testing_data - self.mean)/self.std
    test_pc = np.dot(test, evecs)[:self.n_pcs]

    distance_vec = []
    for i in range(len(training_pc)):
      distance = 0
      for j, pc in enumerate(training_pc[i]):
        diff = test_pc[j] - pc
        distance += (diff**2)*(evals[j])/sum(evals)
      distance_vec.append(distance)
    return distance_vec

  def PCA(self, x_data):
    
    # Standardize
    self.mean = np.nanmean(x_data, axis=0)
    self.std = np.nanstd(x_data, axis=0, ddof= 1)
    x_data -= self.mean
    x_data /= self.std

    # Compute PCA
    # Compute the covariance matrix
    cov = np.cov(x_data, rowvar = False, ddof = 1)

    # Compute the eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort the eigenvalues in decreasing order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx]
    eigenvalues = eigenvalues[idx]

    # Transform and return the parameters
    PCS = np.dot(x_data, eigenvectors)

    # figure out the 90% variance
    cum_var = np.cumsum(eigenvalues)/PCS.shape[1]
    self.n_pcs = np.where(cum_var >= 0.9)[0][0] + 1
    PCS = PCS[:, :self.n_pcs]
    eigenvalues = eigenvalues[:self.n_pcs]


    return PCS, eigenvalues, eigenvectors

  def Blend(self, obs, forecasts, blend_len, curve_par):
    return

  
