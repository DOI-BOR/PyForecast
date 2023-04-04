from PyQt5.QtWidgets import *
from Utilities.DataDownloader import DataDownloaderDialog
import pandas as pd
import subprocess
import os
import time

# Get the global application
app = QApplication.instance()

class DataModelView:

  def __init__(self):

    self.dt = app.gui.DataTab

    self.dt.dataset_list.setModel(app.datasets)
    self.dt.dataset_list.selectionModel().selectionChanged.connect(self.plot_data_for_selection)
    self.dt.data_all_button.pressed.connect(self.download_all)
    self.dt.data_update_button.pressed.connect(self.download_recent)
    self.dt.edit_data_excel_button.pressed.connect(self.edit_data_excel)

  def edit_data_excel(self):

    if len(app.datasets) < 1:
      QMessageBox.information(self.dt, 'No datasets', 'You do not have any selected datasets in this file. Add a dataset to download data.')
      return

    

    d = QDialog(self.dt)
    d.setWindowTitle('Excel Editing')
    lab = QLabel("Converting your data to an excel file...", d)
    confirm_button = QPushButton("Save Changes")
    confirm_button.pressed.connect(d.accept)
    cancel_button = QPushButton("Cancel")
    cancel_button.pressed.connect(d.reject)
    ll = QVBoxLayout()
    ll.addWidget(lab)
    h = QHBoxLayout()
    h.addWidget(confirm_button)
    h.addWidget(cancel_button)
    d.setLayout(ll)
    d.setModal(True)
    d.show()
    app.processEvents()

    # Convert aatatsets to dataframe
    df = pd.DataFrame()
    names = []
    for dataset in app.datasets.datasets:
      names.append(dataset.__export_form__())
      scale, off = dataset.raw_unit.convert_to(dataset.display_unit)
      df = pd.concat([df, dataset.data*scale + off], axis=1)
    df.index = pd.DatetimeIndex(df.index)
    df.columns = names
    
    # Write Excel fle
    fn1 = app.base_dir + f'/temp_{len(os.listdir())}.xlsx'
    fn = fn1
    writer = pd.ExcelWriter(fn, engine='xlsxwriter')
    df.to_excel(writer, 'Data')
    
    workbook=writer.book
    fmt = workbook.add_format({'text_wrap':True})
    sheet = workbook.get_worksheet_by_name('Data')
    sheet.set_row(0, height=40)
    sheet.set_column("A:A", width=20)
    sheet.set_column('B:AZ', width=20, cell_format=fmt)
    # for col in range(len(df.columns)):
    #   sheet.set_cell_format(0, col+1, fmt)
    writer.save()
    del writer

    lab.setText("Your data is opening in excel. Save and close the excel documents when you're done editing.")

    proc = subprocess.Popen(args=['start', 'EXCEL.EXE', fn], stdout=subprocess.PIPE, shell=True)
    time.sleep(1)
    
    ll.addLayout(h)
    app.processEvents()

    def save_changes():
    
      df = pd.read_excel(fn, 'Data', index_col=0, header=0)
      for dataset in app.datasets.datasets:
        scale, off = dataset.raw_unit.convert_to(dataset.display_unit)
        for col in df.columns:
          if dataset.__export_form__() == col:
            dataset.data = (df[col] - off)/scale
      lab.setText('Changes Saved!')
      app.processEvents()
      time.sleep(1)
      d.close()
      self.plot_data_for_selection(self.dt.dataset_list.selectionModel().selection(), None)
    
    d.accepted.connect(save_changes)
    d.rejected.connect(d.close)
    
    

  def plot_data_for_selection(self, new_selection, _):
    selection = self.dt.dataset_list.selectionModel().selectedRows()
    selected_datasets = [app.datasets[idx.row()] for idx in selection]
    if len(selected_datasets) < 1:
      self.dt.data_viewer.clear_all()
      return
    df = pd.DataFrame()
    labels = []
    unit_list = []
    for dataset in selected_datasets:
      unit_list.append(dataset.display_unit.id)
      labels.append(dataset.__condensed_form__())
      scale, off = dataset.raw_unit.convert_to(dataset.display_unit)
      df = pd.concat([df, dataset.data*scale + off], axis=1)
    df.index = pd.DatetimeIndex(df.index)
    df.columns = labels
    self.dt.data_viewer.plot(df, unit_list=unit_list)

  def download_recent(self):
    if len(app.datasets) < 1:
      QMessageBox.information(self.dt, 'No datasets', 'You do not have any selected datasets in this file. Add a dataset to download data.')
      return
    selection = [app.datasets[idx.row()] for idx in self.dt.dataset_list.selectionModel().selection().indexes()]
    if len(selection) > 0:
      msgbox = QMessageBox()
      msgbox.setIcon(QMessageBox.Question)
      msgbox.setWindowTitle('Download for selection?')
      msgbox.setText('Download only selected datasets ("Selected") or all datasets ("All")')
      msgbox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
      buttonY = msgbox.button(QMessageBox.Yes)
      buttonY.setText('Selected')
      buttonN = msgbox.button(QMessageBox.No)
      buttonN.setText('All')
      msgbox.exec_()
      ret = msgbox.clickedButton()
      if ret == buttonN:
        selection = None

    dd = DataDownloaderDialog(all_data=False, selection=selection)

  def download_all(self):
    """
    Downloads all the data for all objects
    """
    if len(app.datasets) < 1:
      QMessageBox.information(self.dt, 'No datasets', 'You do not have any selected datasets in this file. Add a dataset to download data.')
      return
    selection = [app.datasets[idx.row()] for idx in self.dt.dataset_list.selectionModel().selection().indexes()]
    if len(selection) > 0:
      msgbox = QMessageBox()
      msgbox.setIcon(QMessageBox.Question)
      msgbox.setWindowTitle('Download for selection?')
      msgbox.setText('Download only selected datasets ("Selected") or all datasets ("All")')
      msgbox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
      buttonY = msgbox.button(QMessageBox.Yes)
      buttonY.setText('Selected')
      buttonN = msgbox.button(QMessageBox.No)
      buttonN.setText('All')
      msgbox.exec_()
      ret = msgbox.clickedButton()
      if ret == buttonN:
        selection = None
    dd = DataDownloaderDialog(all_data=True, selection=selection)

    

