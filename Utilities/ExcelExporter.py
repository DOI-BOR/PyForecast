import pandas as pd
from PyQt5.QtWidgets import QApplication

# Get the global application
app = QApplication.instance()

class Exporter:

  def __init__(self):

    return

  def export(self):

    header_1_format = {'bold':True, 'bg_color':'lime'}
    grayed_format = {'bg_color':'silver'}
    wrap_format = {'bold':True, 'bold':True, 'bg_color':'lime'}
    
    fn = app.current_file.strip('.fcst') + '.xlsx'
    writer = pd.ExcelWriter(fn, engine='xlsxwriter')
    workbook = writer.book
    header_1_format = workbook.add_format(header_1_format)
    grayed_format = workbook.add_format(grayed_format)
    wrap_format = workbook.add_format(wrap_format)
    wrap_format.set_text_wrap()

    app.gui.status_bar.showMessage('Exporting to Excel (Datasets)')
    app.processEvents()
    
    # DATASETS
    dataset_worksheet = workbook.add_worksheet('Datasets')

    for i, col in enumerate([
      'Dataset GUID', 'Dataset ID', 'Name', 'Agency', 'Parameter', 'Param Code', 
      'Raw Unit', 'Display Unit', 'Dataloader', 'Data file']
    ):
      dataset_worksheet.write(0, i, col, header_1_format)
    col_widths = (i+1)*[10]
    for i, dataset in enumerate(app.datasets.datasets):
      
      col_widths[0] = max(col_widths[0], len(dataset.guid))
      dataset_worksheet.write(i+1, 0, dataset.guid, grayed_format)

      col_widths[1] = max(col_widths[1], len(dataset.external_id))
      dataset_worksheet.write(i+1, 1, dataset.external_id)

      col_widths[2] = max(col_widths[2], len(dataset.name))
      dataset_worksheet.write(i+1, 2, dataset.name)

      col_widths[3] = max(col_widths[3], len(dataset.agency))
      dataset_worksheet.write(i+1, 3, dataset.agency)

      col_widths[4] = max(col_widths[4], len(dataset.parameter))
      dataset_worksheet.write(i+1, 4, dataset.parameter)

      col_widths[5] = max(col_widths[5], len(dataset.param_code))
      dataset_worksheet.write(i+1, 5, dataset.param_code)

      col_widths[6] = max(col_widths[6], len(dataset.raw_unit.id))
      dataset_worksheet.write(i+1, 6, dataset.unit.id)

      col_widths[7] = max(col_widths[7], len(dataset.raw_unit.id))
      dataset_worksheet.write(i+1, 7, dataset.display_unit.id)

      col_widths[7] = max(col_widths[8], len(dataset.dataloader.NAME))
      dataset_worksheet.write(i+1, 8, dataset.dataloader.NAME)

      col_widths[8] = max(col_widths[9], len(dataset.file_path))
      dataset_worksheet.write(i+1, 9, dataset.file_path)
    
    for i, width in enumerate(col_widths):
      dataset_worksheet.set_column(i, i, width)
      pass

    # Data
    app.gui.status_bar.showMessage('Exporting to Excel (Data)')
    app.processEvents()
    
    df = pd.DataFrame()
    names = []
    for dataset in app.datasets.datasets:
      names.append(dataset.__export_form__())
      scale, offset = dataset.raw_unit.convert_to(dataset.display_unit)
      df = pd.concat([df, dataset.data*scale + offset], axis=1)
    df.index = pd.DatetimeIndex(df.index)
    df.columns = names
    df.to_excel(writer, index=True, sheet_name='Data', header=False, startrow=1)
    data_sheet = workbook.get_worksheet_by_name("Data")
    data_sheet.set_column(0, 0, 22)
    for col, val in enumerate(names):
      data_sheet.write(0, col+1, val)
      data_sheet.set_column(0, col+1, 23)
    data_sheet.set_row(0, 30, wrap_format)

    # Saved Models

    app.gui.status_bar.showMessage('Exporting to Excel (Saved Models)')
    app.processEvents()

    for year in app.saved_models.list_forecast_years():

      saved_models_sheet = workbook.add_worksheet(f'Forecasts ({year})')

      columns = ['Model Name', 'Issue Date', 'Regressor', 'Cross Validation']
      columns = columns + ['Predictors', 'Target', 'Forecast (50%)']
      columns = columns + [f'{i:0.2g}%' for i in range(1, 100, 2)]

      for i, col in enumerate(columns):
        saved_models_sheet.write(0, i, col, header_1_format)
      skipcount = 0
      for i, model in enumerate(app.saved_models.saved_models):
        if year in model.forecasts.forecasts.index.get_level_values(0):
          for j, col in enumerate(columns):
            if col == 'Model Name':
              saved_models_sheet.write(i+1-skipcount, j, model.name)
            elif col == 'Issue Date':
              saved_models_sheet.write(i+1-skipcount, j, model.issue_date.strftime('%b %d'))
            elif col == 'Regressor':
              saved_models_sheet.write(i+1-skipcount, j, model.regression_model)
            elif col == 'Cross Validation':
              saved_models_sheet.write(i+1-skipcount, j, model.cross_validator)
            elif col == 'Forecast (50%)':
              val = model.forecasts.get_10_50_90(year)[1]
              saved_models_sheet.write(i+1-skipcount, j, f'{val:0.5g}')
            elif col == "Predictors":
              p_str = ', '.join([p.dataset.external_id for p in model.predictors]) 
              saved_models_sheet.write(i+1-skipcount, j, p_str)
            elif col == 'Target':
              saved_models_sheet.write(i+1-skipcount, j, model.predictand.__list_form__())
            elif col.endswith('%'):
              ex = int(col.strip('%'))/100
              val = model.forecasts.forecasts.loc[(year, ex), 'Value']
              saved_models_sheet.write(i+1-skipcount, j, f'{val:0.5g}')
        else:
          skipcount += 1
      

    workbook.close()
    

    return fn
  
