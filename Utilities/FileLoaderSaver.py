import pickle
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from PySide6.QtWidgets import QApplication

from Models.ModelConfigurations import (PredictorPool, Regressor, Regressors,
                                        ResampledDataset)
from Models.SavedModels import ForecastList

app = QApplication.instance()


def file_version_less_than(v_file, v_check):
    """Checks if the file version is less than the check version"""
    current_version_int = int(v_file.replace('.', ''))
    check_version_int = int(v_check.replace('.', ''))
    return current_version_int < check_version_int


def sqlite_load_forecast(db: Path):
    db = db.with_suffix('.sqlite')
    if not db.is_file():
        print('Error: Forecast database not found:')
        print(f'{db}')
        return

    con = None
    cur = None
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.row_factory = sqlite3.Row  # allows access by column name
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute('PRAGMA journal_mode = WAL')

        app_info = cur.execute("SELECT * FROM app_info").fetchone()
        app_version = app_info['app_version']

        # load datasets
        sqlite_load_datasets(cur)

        # load model configurations
        sqlite_load_model_configurations(cur)

        # load saved models
        sqlite_load_saved_models(cur)

    except Exception as e:
        print('Error reading forecast from SQLite database:')
        print(f'{repr(e)}')

    finally:
        if con:
            cur.close()
            con.close()


def sqlite_load_saved_models(cur: sqlite3.Cursor):
    # note cur.execute().fetchall() is needed here given the other cur.execute()
    # which would otherwise clobber the in-memory rows
    for row in cur.execute("SELECT * FROM saved_models").fetchall():
        sm_dict = dict(row)
        sm_dict['issue_date'] = (
            datetime.fromisoformat(row['issue_date']))
        sm_dict['training_period_start'] = (
            datetime.fromisoformat(row['training_period_start']))
        sm_dict['training_period_end'] = (
            datetime.fromisoformat(row['training_period_end']))
        sm_dict['training_exclude_dates'] = (
            [int(x) for x in row['training_exclude_dates'].split(' ')
             if row['training_exclude_dates']])

        predictand = cur.execute(
            "SELECT * FROM saved_models_predictand "
            "WHERE saved_model_guid=?", (row['guid'],)).fetchone()
        p_dict = dict(predictand)
        p_dict['forced'] = predictand['forced'] == True
        p_dict['mustBePositive'] = predictand['mustBePositive'] == True
        p_dict['period_start'] = datetime.fromisoformat(predictand['period_start'])
        p_dict['period_end'] = datetime.fromisoformat(predictand['period_end'])
        p_dict['unit'] = app.units.get_unit(predictand['unit'])
        dataset = ResampledDataset(**p_dict)
        dataset.resample()
        sm_dict['predictand'] = dataset

        sm_dict['predictors'] = PredictorPool()
        predictors = cur.execute(
            "SELECT * FROM saved_models_predictors "
            "WHERE saved_model_guid=?", (row['guid'],))
        for predictor in predictors:
            p_dict = dict(predictor)
            p_dict['forced'] = predictor['forced'] == True
            p_dict['mustBePositive'] = predictor['mustBePositive'] == True
            p_dict['period_start'] = datetime.fromisoformat(predictor['period_start'])
            p_dict['period_end'] = datetime.fromisoformat(predictor['period_end'])
            p_dict['unit'] = app.units.get_unit(predictor['unit'])
            dataset = ResampledDataset(**p_dict)
            dataset.resample()
            sm_dict['predictors'].add_predictor(dataset)

        forecast_list = ForecastList()
        years, exceedences, values = [], [], []
        data = cur.execute(
            "SELECT year, exceedence, value FROM saved_models_forecasts "
            "WHERE saved_model_guid=?", (f'{row['guid']}',))
        for datarow in data:
            years.append(datarow['year'])
            exceedences.append(datarow['exceedence'])
            values.append(datarow['value'])
        forecast_list.forecasts = pd.DataFrame(
            index=pd.MultiIndex.from_arrays([years, exceedences],
                                            names=['Year', 'Exceedance']),
            data=values, columns=['Value'])
        sm_dict['forecast'] = forecast_list

        app.saved_models.add_model(
            regression_model=sm_dict['regression_model'],
            cross_validator=sm_dict['cross_validator'],
            predictors=sm_dict['predictors'],
            predictand=sm_dict['predictand'],
            training_period_start=sm_dict['training_period_start'],
            training_period_end=sm_dict['training_period_end'],
            training_exclude_dates=sm_dict['training_exclude_dates'],
            issue_date=sm_dict['issue_date'],
            name=sm_dict['name'],
            comment=sm_dict['comment'],
            guid=sm_dict['guid'],
            forecasts=sm_dict['forecast'],
        )


def sqlite_load_model_configurations(cur: sqlite3.Cursor):
    for row in cur.execute("SELECT * FROM model_configurations"):
        mc_dict = dict(row)
        mc_dict['issue_date'] = (
            datetime.fromisoformat(row['issue_date']))
        mc_dict['training_start_date'] = (
            datetime.fromisoformat(row['training_start_date']))
        mc_dict['training_end_date'] = (
            datetime.fromisoformat(row['training_end_date']))
        mc_dict['training_exclude_dates'] = (
            [int(x) for x in row['training_exclude_dates'].split(' ')
             if row['training_exclude_dates']])

        predictand = cur.execute(
            "SELECT * FROM model_configurations_predictand "
            "WHERE model_configuration_guid=?", (row['guid'],)).fetchone()
        p_dict = dict(predictand)
        p_dict['forced'] = predictand['forced'] == True
        p_dict['mustBePositive'] = predictand['mustBePositive'] == True
        p_dict['period_start'] = datetime.fromisoformat(predictand['period_start'])
        p_dict['period_end'] = datetime.fromisoformat(predictand['period_end'])
        p_dict['unit'] = app.units.get_unit(predictand['unit'])
        dataset = ResampledDataset(**p_dict)
        mc_dict['predictand'] = dataset

        mc_dict['predictor_pool'] = PredictorPool()
        predictors = cur.execute(
            "SELECT * FROM model_configurations_predictors "
            "WHERE model_configuration_guid=?", (row['guid'],))
        for predictor in predictors:
            p_dict = dict(predictor)
            p_dict['forced'] = predictor['forced'] == True
            p_dict['mustBePositive'] = predictor['mustBePositive'] == True
            p_dict['period_start'] = datetime.fromisoformat(predictor['period_start'])
            p_dict['period_end'] = datetime.fromisoformat(predictor['period_end'])
            p_dict['unit'] = app.units.get_unit(predictor['unit'])
            dataset = ResampledDataset(**p_dict)
            mc_dict['predictor_pool'].add_predictor(dataset)

        mc_dict['regressors'] = Regressors()
        regressors = cur.execute(
            "SELECT * FROM model_configurations_regressors "
            "WHERE model_configuration_guid=?", (row['guid'],))
        for regressor in regressors:
            mc_dict['regressors'].add_regressor(Regressor(**dict(regressor)))

        app.model_configurations.add_configuration(**mc_dict)


def sqlite_load_datasets(cur: sqlite3.Cursor):
    # note cur.execute().fetchall() is needed here given the other cur.execute()
    # which would otherwise clobber the in-memory rows
    for row in cur.execute("SELECT * FROM datasets").fetchall():
        ds_dict = dict(row)
        ds_dict['dataloader'] = app.dataloaders[row['dataloader']]['CLASS']()
        ds_dict['raw_unit'] = app.units.get_unit(row['raw_unit'])
        ds_dict['display_unit'] = app.units.get_unit(row['display_unit'])

        # Pandas.read_sql_query, Numpy, and SQLite rows were tested. Using the cur
        # object was slighlty faster and arguably more readable and capable of large
        # data reads.
        dates, values = [], []
        data = cur.execute("SELECT datetime, value FROM datasets_data "
                           "WHERE dataset_guid=?", (f'{ds_dict['guid']}',))
        for datarow in data:
            dates.append(datarow['datetime'])
            values.append(datarow['value'])
        ds_dict['data'] = pd.Series(index=pd.to_datetime(dates), data=values,
                                    name=ds_dict['guid'])

        app.datasets.add_dataset(**ds_dict)


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
        app.datasets.dataChanged.emit(app.datasets.index(0),
                                      app.datasets.index(app.datasets.rowCount()))

        app.model_configurations.load_from_file(f)
        app.saved_models.load_from_file(f)

    else:

        # Datasets
        len_datasets = pickle.load(f)
        for i in range(len_datasets):
            dataset_dict = pickle.load(f)
            dataset_dict['raw_unit'] = app.units.get_unit(dataset_dict['raw_unit'])
            dataset_dict['display_unit'] = app.units.get_unit(
                dataset_dict['display_unit'])
            dataset_dict['dataloader'] = app.dataloaders[dataset_dict['dataloader']][
                'CLASS']()
            dataset_dict['data'] = pd.read_pickle(f, compression={'method': None})

            app.datasets.add_dataset(**dataset_dict)

        # Configurations
        len_configs = pickle.load(f)
        for i in range(len_configs):
            config_dict = pickle.load(f)
            config_dict['predictand'] = pickle.load(f)
            len_predictors = pickle.load(f)
            config_dict['predictor_pool'] = PredictorPool()
            for j in range(len_predictors):
                config_dict['predictor_pool'].add_predictor(pickle.load(f))
            len_regressors = pickle.load(f)
            config_dict['regressors'] = Regressors()
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
            predictor_pool = PredictorPool()
            for j in range(num_predictors):
                predictor_pool.add_predictor(pickle.load(f))
            predictand = pickle.load(f)
            training_period_start = pickle.load(f)
            training_period_end = pickle.load(f)
            training_exclude_dates = pickle.load(f)
            issue_date = pickle.load(f)
            name = pickle.load(f)
            comment = pickle.load(f)
            forecasts = pickle.load(f)
            forecasts.index.names = ['Year', 'Exceedance']
            forecast_obj = ForecastList()
            forecast_obj.forecasts = forecasts
            app.saved_models.add_model(
                regression_model=regression_model,
                cross_validator=cross_validator,
                predictors=predictor_pool,
                predictand=predictand,
                training_period_start=training_period_start,
                training_period_end=training_period_end,
                training_exclude_dates=training_exclude_dates,
                issue_date=issue_date,
                name=name,
                comment=comment,
                guid=guid,
                forecasts=forecast_obj
            )


def sqlite_save_forecast(db: Path):
    # set database name to forecast file name with '.sqlite' extension
    db = db.with_suffix('.sqlite')

    # if the database exists, back it up
    db_backup = Path(db.with_suffix('.sqlite.bak'))
    if db.is_file():
        db.replace(db_backup)

    con = None
    cur = None
    try:
        # create in-memory database connection
        with sqlite3.connect(':memory:') as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute('PRAGMA journal_mode = WAL')

            # create all sqlite tables to store forecast information
            sqlite_create_tables(cur)

            # save app_info information
            cur.execute("INSERT INTO app_info VALUES (?, ?, ?, ?)", (
                1, app.PYCAST_VERSION, app.PYTHON_VERSION, sqlite3.sqlite_version))

            # save datasets information
            sqlite_save_datasets(cur)

            # save model configurations information
            sqlite_save_model_configurations(cur)

            # save saved models information
            sqlite_save_saved_models(cur)

        # save in-memory database to disk
        cur.execute("VACUUM INTO ?", (str(db),))

        # delete database backup if it exists
        db_backup.unlink(missing_ok=True)

    except Exception as e:
        print('Error saving forecast to an SQLite database:')
        print(f'{repr(e)}')

    finally:
        # close in-memory connection if it exists
        if con:
            cur.close()
            con.close()


def sqlite_save_saved_models(cur: sqlite3.Cursor):
    smodels, smodels_predictands, smodels_predictors, smodels_forecasts = [], [], [], []
    for saved_model in app.saved_models:
        model_values = [[saved_model.guid,
                         saved_model.name,
                         saved_model.issue_date.isoformat(),
                         saved_model.training_period_start.isoformat(),
                         saved_model.training_period_end.isoformat(),
                         ' '.join(str(x) for x in saved_model.training_exclude_dates),
                         saved_model.regression_model,
                         saved_model.cross_validator,
                         saved_model.comment]]
        smodels.extend(model_values)

        predictand_values = [[str(uuid.uuid4())
                              if not hasattr(saved_model.predictand, 'guid')
                              else saved_model.predictand.guid,
                              saved_model.guid,
                              saved_model.predictand.dataset_guid,
                              saved_model.predictand.agg_method,
                              int(saved_model.predictand.forced),
                              int(saved_model.predictand.mustBePositive),
                              saved_model.predictand.preprocessing,
                              saved_model.predictand.unit.id,
                              saved_model.predictand.period_start.isoformat(),
                              saved_model.predictand.period_end.isoformat()]]
        smodels_predictands.extend(predictand_values)

        for predictor in saved_model.predictors.predictors:
            predictor_values = [[str(uuid.uuid4())
                                 if not hasattr(predictor, 'guid')
                                 else predictor.guid,
                                 saved_model.guid,
                                 predictor.dataset_guid,
                                 predictor.agg_method,
                                 int(predictor.forced),
                                 int(predictor.mustBePositive),
                                 predictor.preprocessing,
                                 predictor.unit.id,
                                 predictor.period_start.isoformat(),
                                 predictor.period_end.isoformat()]]
            smodels_predictors.extend(predictor_values)

        forecast = saved_model.forecasts.forecasts
        year = forecast.index.get_level_values('Year').values.flatten()
        exc = forecast.index.get_level_values('Exceedance').values.flatten()
        value = forecast.values.flatten()
        data = [[saved_model.guid, x, y, z]
                for x, y, z in
                zip(year, exc, value)]
        smodels_forecasts.extend(data)

    cur.executemany("INSERT INTO saved_models "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", smodels)
    cur.executemany("INSERT INTO saved_models_predictand "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", smodels_predictands)
    cur.executemany("INSERT INTO saved_models_predictors "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", smodels_predictors)
    cur.executemany("INSERT INTO saved_models_forecasts "
                    "VALUES(?, ?, ?, ?)", smodels_forecasts)


def sqlite_save_model_configurations(cur: sqlite3.Cursor):
    configs, configs_predictands, configs_predictors, configs_regressors = [], [], [], []
    for model_config in app.model_configurations.configurations:
        config_values = [[model_config.guid,
                          model_config.name,
                          model_config.issue_date.isoformat(),
                          model_config.training_start_date.isoformat(),
                          model_config.training_end_date.isoformat(),
                          ' '.join(str(x) for x in model_config.training_exclude_dates),
                          model_config.comment]]
        configs.extend(config_values)

        predictand_values = [[str(uuid.uuid4())
                              if not hasattr(model_config.predictand, 'guid')
                              else model_config.predictand.guid,
                              model_config.guid,
                              model_config.predictand.dataset_guid,
                              model_config.predictand.agg_method,
                              int(model_config.predictand.forced),
                              int(model_config.predictand.mustBePositive),
                              model_config.predictand.preprocessing,
                              model_config.predictand.unit.id,
                              model_config.predictand.period_start.isoformat(),
                              model_config.predictand.period_end.isoformat()]]
        configs_predictands.extend(predictand_values)

        for predictor in model_config.predictor_pool.predictors:
            predictor_values = [[str(uuid.uuid4())
                                 if not hasattr(predictor, 'guid')
                                 else predictor.guid,
                                 model_config.guid,
                                 predictor.dataset_guid,
                                 predictor.agg_method,
                                 int(predictor.forced),
                                 int(predictor.mustBePositive),
                                 predictor.preprocessing,
                                 predictor.unit.id,
                                 predictor.period_start.isoformat(),
                                 predictor.period_end.isoformat()]]
            configs_predictors.extend(predictor_values)

        for regressor in model_config.regressors.regressors:
            regressor_values = [[str(uuid.uuid4())
                                 if not hasattr(regressor, 'guid')
                                 else regressor.guid,
                                 model_config.guid,
                                 regressor.cross_validation,
                                 regressor.feature_selection,
                                 regressor.regression_model,
                                 regressor.scoring_metric]]
            configs_regressors.extend(regressor_values)

    cur.executemany("INSERT INTO model_configurations "
                    "VALUES(?, ?, ?, ?, ?, ?, ?)", configs)
    cur.executemany("INSERT INTO model_configurations_predictand "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", configs_predictands)
    cur.executemany("INSERT INTO model_configurations_predictors "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", configs_predictors)
    cur.executemany("INSERT INTO model_configurations_regressors "
                    "VALUES(?, ?, ?, ?, ?, ?)", configs_regressors)


def sqlite_save_datasets(cur: sqlite3.Cursor):
    datasets, datasets_data = [], []
    for dataset in app.datasets.datasets:
        dataset_values = [[dataset.guid,
                           dataset.external_id,
                           dataset.agency,
                           dataset.name,
                           dataset.parameter,
                           dataset.param_code,
                           dataset.dataloader.NAME,
                           dataset.raw_unit.id,
                           dataset.display_unit.id,
                           dataset.name2]]
        datasets.extend(dataset_values)

        data = [[dataset.guid, x, y]
                for x, y in
                zip(dataset.data.index.astype(str), dataset.data.values.flatten())]
        datasets_data.extend(data)

    cur.executemany("INSERT INTO datasets "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", datasets)
    cur.executemany("INSERT INTO datasets_data "
                    "VALUES(?, ?, ?)", datasets_data)


def sqlite_create_tables(cur: sqlite3.Cursor):
    sqlite_tables_script = """
        CREATE TABLE app_info (
            id INTEGER PRIMARY KEY,
            app_version TEXT,
            py_version TEXT,
            db_version TEXT
        );
    
        CREATE TABLE datasets (
            guid TEXT PRIMARY KEY, 
            external_id TEXT, 
            agency TEXT, 
            name TEXT, 
            parameter TEXT, 
            param_code TEXT, 
            dataloader TEXT, 
            raw_unit TEXT, 
            display_unit TEXT, 
            name2 TEXT
        );

        CREATE TABLE datasets_data (
            dataset_guid TEXT REFERENCES datasets (guid), 
            datetime TEXT, 
            value REAL, 
            UNIQUE (dataset_guid, datetime)
        );
        
        CREATE TABLE model_configurations (
            guid TEXT PRIMARY KEY,
            name TEXT,
            issue_date TEXT,
            training_start_date TEXT,
            training_end_date TEXT,
            training_exclude_dates TEXT,
            comment TEXT
        );
        
        CREATE TABLE model_configurations_predictand (
            guid TEXT PRIMARY KEY,
            model_configuration_guid TEXT REFERENCES model_configurations (guid),
            dataset_guid TEXT REFERENCES datasets (guid),
            agg_method TEXT,
            forced INTEGER,
            mustBePositive INTEGER,
            preprocessing TEXT,
            unit TEXT,
            period_start TEXT,
            period_end TEXT
        );
        
        CREATE TABLE model_configurations_predictors (
            guid TEXT PRIMARY KEY,
            model_configuration_guid TEXT REFERENCES model_configurations (guid),
            dataset_guid TEXT REFERENCES datasets (guid),
            agg_method TEXT,
            forced INTEGER,
            mustBePositive INTEGER,
            preprocessing TEXT,
            unit TEXT,
            period_start TEXT,
            period_end TEXT
        );
        
        CREATE TABLE model_configurations_regressors (
            guid TEXT PRIMARY KEY,
            model_configuration_guid TEXT REFERENCES model_configurations (guid),
            cross_validation TEXT,
            feature_selection TEXT,
            regression_model TEXT,
            scoring_metric TEXT
        );
        
        CREATE TABLE saved_models (
            guid TEXT PRIMARY KEY,
            name TEXT,
            issue_date TEXT,
            training_period_start TEXT,
            training_period_end TEXT,
            training_exclude_dates TEXT,
            regression_model TEXT,
            cross_validator TEXT,
            comment TEXT
        );
        
        CREATE TABLE saved_models_predictand (
            guid TEXT PRIMARY KEY,
            saved_model_guid TEXT REFERENCES saved_models (guid),
            dataset_guid TEXT REFERENCES datasets (guid),
            agg_method TEXT,
            forced INTEGER,
            mustBePositive INTEGER,
            preprocessing TEXT,
            unit TEXT,
            period_start TEXT,
            period_end TEXT
        );
        
        CREATE TABLE saved_models_predictors (
            guid TEXT PRIMARY KEY,
            saved_model_guid TEXT REFERENCES saved_models (guid),
            dataset_guid TEXT REFERENCES datasets (guid),
            agg_method TEXT,
            forced INTEGER,
            mustBePositive INTEGER,
            preprocessing TEXT,
            unit TEXT,
            period_start TEXT,
            period_end TEXT
        );
        
        CREATE TABLE saved_models_forecasts (
            saved_model_guid TEXT REFERENCES saved_models (guid),
            year INTEGER,
            exceedence REAL,
            value REAL,
            UNIQUE (saved_model_guid, exceedence)
        );
    """
    cur.executescript(sqlite_tables_script)


def save_to_file(f):
    pickle.dump(app.PYCAST_VERSION, f, 4)

    # Datasets
    pickle.dump(len(app.datasets), f, 4)  # num datasets
    for dataset in app.datasets.datasets:
        d = dataset.__dict__.copy()
        d['raw_unit'] = d['raw_unit'].id
        d['display_unit'] = d['display_unit'].id
        d['dataloader'] = d['dataloader'].NAME
        pickle.dump({
            key: d[key] for key in d.keys() if key != 'data'
        }, f, 4)
        dataset.data.to_pickle(f, compression=None, protocol=4)

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
        pickle.dump(model.cross_validator, f, 4)
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
    # app.saved_models.save_to_file(f)
