from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta
import pandas as pd
import time

# Get the global application
app = QApplication.instance()

class DataDownloaderDialog(QDialog):

  def __init__(self, all_data=True, selection=None):
    """Constructor

    args:
      all_data (`bool`) - True: download the entire period of record data
                          False: download only recent data for the site
      selection (`list`) - list of datasets to download data for
    """

    QDialog.__init__(self)
    self.setWindowTitle('Downloading datasets')

    # Determine the start date based on the all_data parameter
    if all_data:
      self.startDate = app.config['default_data_download_start']
    else:
      self.startDate = None

    # Compile the datasets that we'll download
    if selection:
      datasets = selection
    else:
      datasets = app.datasets.datasets

    # Layout the dialog
    self.cancel_button = QPushButton('Cancel')
    self.prog_bar = QProgressBar()
    self.prog_bar.setRange(0, 100)
    self.prog_text = QPlainTextEdit()
    self.prog_text.setReadOnly(True)

    layout = QVBoxLayout()
    layout.addWidget(QLabel('Downloading Data'))
    layout.addWidget(self.prog_bar)
    layout.addWidget(self.prog_text)
    layout.addWidget(self.cancel_button)
    self.setLayout(layout)

    # Initialte the runnable
    self.runnable = DownloadRunner(self.startDate, datasets )
    
    # Runnable functionality
    self.runnable.update_prog_bar.connect(self.updateProgBar)
    self.runnable.update_prog_text.connect(self.updateProgText)
    self.runnable.finished.connect(self.readyToClose)
    self.runnable.start()

    # Connect the cancel button
    self.cancel_button.pressed.connect(self.stopDownload)
    
    self.setMinimumWidth(500)

    self.exec()

  def readyToClose(self):
    """Closes the dialog once the data finishes downloading"""
    time.sleep(1)
    self.close()

  def updateProgBar(self, float):
    """Updates the progress bar with the current status of data download"""
    self.prog_bar.setValue(int(float*100))

  def updateProgText(self, text):
    """Updates the progress text area with new status'"""
    self.prog_text.appendPlainText(text)

  def stopDownload(self):
    """Stops the download process"""
    self.runnable.stop()


class DownloadRunner(QThread):

  update_prog_bar = pyqtSignal(float)
  update_prog_text = pyqtSignal(str)

  def __init__(self, start_time = None, datasets = None):
    """Constructor

    params:
      threadactive (`bool`) - keeps track of whether the thread is running 
                              or not.
    
    args:
      start_time (`datetime`) - start datetime for dataloaders. If none,
                                only recent data is downloaded
      datasets (`list`) - list of datasets to download data for.
    """

    QThread.__init__(self)
    self.threadactive = True
    self.datasets = datasets
    self.start_time = start_time

  def run(self):
    """Responsible for downloading all the datasets"""

    self.update_prog_text.emit('Starting data download...')
    
    # Iterate over datasets and download each one separately
    for i, dataset in enumerate(self.datasets):

      # set the start time for 'get recent' downloads
      if not self.start_time:
        start = dataset.data.index[-1] \
          - pd.DateOffset(days=app.config['default_recent_data_lookback'])
        self.recent = True
      else:
        start = self.start_time
        self.recent = False

      # If we're only getting recent data, just append to existing data
      # Otherwise, overwrite existing data
      if self.recent:
        dataset.data = pd.concat([
          dataset.data, 
          dataset.dataloader.load(dataset, start, datetime.now())
          ], axis=0
        )
        dataset.data = dataset.data[~dataset.data.index.duplicated(keep='first')]
      else:
        dataset.data = dataset.dataloader.load(dataset, start, datetime.now())

      # Update the dialog with current status
      self.update_prog_text.emit(f'Downloaded {dataset.external_id} {dataset.parameter}')
      self.update_prog_bar.emit((i+1)/len(self.datasets))
      print(f"Downloaded data for {dataset}")

  def stop(self):
    """Stops the download thread and returns to application"""
    self.threadactive = False
    self.update_prog_text.emit('Recieved Cancel')
    self.terminate()
    self.wait(1000)




