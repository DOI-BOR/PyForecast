#!/usr/bin/env python3

"""
Given a pickled forecast file or folder containing pickled forecast files,
convert the pickled forecast into an SQLite database.

The code will recurse the folder to find all pickled forecast files.
"""
import argparse
import pickle
import sys
from pathlib import Path


def save_pickle_to_sqlite(file: Path):
    with open(file, 'rb') as readfile:
        datasets = pickle.load(readfile)
        datasets_data = pickle.load(readfile)
        model_configurations = pickle.load(readfile)
        saved_models = pickle.load(readfile)
        saved_models_forecasts = pickle.load(readfile)
        saved_models_forecasts_eqs = pickle.load(readfile)
        saved_models_eqs = pickle.load(readfile)
        a = 1


def main(list_files_folders: list):
    for item in list_files_folders:
        item_path = Path(item)
        if item_path.is_file():
            save_pickle_to_sqlite(item_path)
        elif item_path.is_dir():
            for item in item_path.glob('**/*.fcst'):
                save_pickle_to_sqlite(item)
        else:
            raise RuntimeError(f'Unrecognized script argument: {item_path}')


if __name__ == "__main__":
    script_name = Path(sys.argv[0]).name

    # Read arguments from a command line
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
    )
    parser.add_argument(
        'list_files_folders', nargs='+',
        help='Space separated string of pickled forecast files or folder containing '
             'pickled forecast files',
    )
    args = parser.parse_args()
    main(args.list_files_folders)
