***
# PyForecast Version 5 ![PyForecast logo][PF_ICON]
Version 5 Released January 2023
***
Develop and analyze high-performing seasonal streamflow forecasts using PyForecast, developed by Reclamation's MB-ART and CPN Regions. PyForecast takes advantage of multi-threading and multiple processor cores to analyze thousands of forecasts in minutes using cutting-edge statistical techniques.

## Table of Contents
  - [Quick Start](#quick-start)
  - [User Manual](#user-manual)
    - [Installation and Updates]()
    - [Software Overview](#software-overview)
      - [Datasets Tab](#datasets-tab)
      - [Data Tab](#data-tab)
      - [Model Configurations Tab](#model-configurations-tab)
      - [Saved Models Tab](#saved-models-tab)
      - [File Menu](#file-menu)
    - [Best Practices](#best-practices)
    - [Example Forecast Development](#example-forecast-development)
  - [Scientific Background](#scientific-background)
    - [Datasets](#datasets)
    - [Model Search](#model-search)
    - [Uncertainty](#uncertainty)
    - [Experimental Features](#experimental-features)
  - [Programming Guide](#programming-guide)

## Quick Start


## User Manual

### Installation and Updates
The latest release of PyForecast can be downloaded from the [Releases Page](https://github.com/usbr/PyForecast/releases) of this repository. 
![Picture of software releases page][RELEASES_PIC_1]

Simply download and run the installer (FOR WINDOWS MACHINES ONLY!).

PyForecast can automatically check for and download any updates using the "Check for Updates" button in the [File Menu](#file-menu).

### Software Overview
PyForecast is a statistical modeling tool useful in predicting seasonal inflows and streamflows. The tool collects meterological and hydrologic datasets, analyzes hundreds to thousands of predictor subsets, and returns well-performing statistical regressions between predictors and streamflows.

[Datasets](#datasets) are collected from web services located at NOAA, RCC-ACIS, NRCS, Reclamation, and USGS servers, and is stored locally on the user’s machine. Data can be updated with current values at any time, allowing the user to make current water-year forecasts using equations developed with the program.

After potential predictor datasets are downloaded and manipulated, the tool allows the user to develop statistically significant regression equations using multiple regression, principal components regression, and z-score regression. Models are developed using a combination of sequential feature selection and cross validation, both described in the [Scientific Background](#scientific-background) section of this document.

#### Datasets Tab
![Datasets Tab Picture][DATASET_PIC_1]
The Datasets Tab allows users to locate datasets that may be valuable for their analysis. Users can find SNOTEL stations and snow courses, reservoirs, stream gages, as well as PRISM and NRCC data gridded temperature and precipitation data, and climate indices.

Datasets are found by navigating in the datasets map to the area of interest and browsing through the dataset markers. If the user decides that a particular dataset might be useful in their analysis, they can choose the `Add Site` button in the dataset pop-up to add the dataset to the selected datasets table. (datasets can later be removed from the selected datasets table by right-clicking one or more datasets and choosing `Remove Dataset(s)`).

Note that removing datasets will also remove any forecasts or models that depend on that dataset.

Additionally, users can click within a watershed boundary to add the PRISM gridded average temperature and humidity values to their analysis. Users can also use the map-legend in the top right corner of the map to enable climate divisions and add climate-division averaged Palmer Drought Severity values to their analysis.

Right clicking the bottom of the datasets list will allow the user to `Add Climate Datasets`.

Double clicking or right clicking and choosing `Open Dataset` on a selected dataset will open the `View Dataset` dialog window allowing the user to change properties of the dataset.

![View Dataset Dialog Picture][DATASET_PIC_2]

Dataset options can be adjusted to retrieve alternative datasets from dataloaders (for example, a user could change the HydroMet parameter in a USBR dataset to retrieve reservoir forebay elevation instead of inflow). Users can also specify the units in which they want to display data. Users can also specify a file where data should be loaded from. 

##### Adding a CSV / Flat File dataset
To add a dataset from a flat file, right click in the dataset list and choose `Add new dataset`. Fill out the dataset description, and check the box labeled `Flat-file source?`. The `File Path` field is now enabled and you can choose the flat file contianing your data. Note that the only supported file format is a CSV file with 2 columns: The first column contains dates, and the second column contains data. There should be colum headers. 


#### Data Tab
![Data Tab Picture][DATA_PIC_1]
The Data Tab allows users to download data for the selected datasets. Data is downloaded in the dataset's `Raw Unit` and displayed to the user in the `Display Unit`. 

The `Download all data` button will download data for datasets using a start date of 1970-Oct-01, and ending today. The `Download recent data` button downloads data from 45-days before the datasets last datapoint until now. (Note that the 45-day parameter and the default start date of 1970-Oct-01 can both be adjusted in the [application settings](#file-menu))

Data for selected datasets can be edited by pressing the `Edit Data in Excel` button at the bottom left of the Data tab. A dialog will appear instructing the user how to save any changes.

#### Model Configurations Tab
![Model Configuration Tab Picture][MODELCONF_PIC_1]
The Model Configuration Tab allows you to set up 
#### Saved Models Tab
![Datasets Tab Picture][SAVEDMODEL_PIC_1]
#### File Menu
![File Menu Picture][FILEMENU_PIC_1]
### Best Practices
### Example Forecast Development

## Scientific Background
### Datasets
### Model Search
### Uncertainty
### Experimental Features

## Programming Guide
[PF_ICON]: Resources/Icons/AppIcon.ico "PyForecast Logo"
[DATASET_PIC_1]: Documentation/Images/DatasetsTab1.PNG "Datasets Tab"
[DATASET_PIC_2]: Documentation/Images/DatasetsTab2.PNG "Dataset Options"
[DATA_PIC_1]: Documentation/Images/DataTab1.PNG "Data Tab"
[MODELCONF_PIC_1]: Documentation/Images/ModelConfTab1.PNG "Model Configuration Tab"
[SAVEDMODEL_PIC_1]: Documentation/Images/SavedModelTab1.PNG "Saved Models Tab"
[RELEASES_PIC_1]: Documentation/Images/Releases1.PNG "Software Releases Page"
[FILEMENU_PIC_1]: Documentation/Images/FileMenu1.PNG "File Menu"