######################################################
# Import modules
import resources.application as app
import os
import pickle
import datetime
import time
import warnings
warnings.filterwarnings("ignore")

######################################################
# Wrapper script inputs and outputs
pathString = r"C:\Users\jrocha\Desktop\_TLWRK_STUFF\ForecastRebuild\CSCI\PyCastFiles"
wyInput = 2021
outList = []
outList.append('FILENAME,RUNMESSAGE,PREDICTION,PREDICTIONRANGE')

######################################################
# Start PyForecast in the background
print('#########################################')
print('Starting dummy PyForecast instance in the background...')
pyCast = app.mainWindow()
pyCast.hide()
print('----- OK!')
print(' ')
time.sleep(5)

######################################################
# Loop through all the forecast files in the input directory
forecastDirectory = os.path.normpath(pathString)
forecastExtension = ['fcst']
forecastFiles = [fn for fn in os.listdir(forecastDirectory) if any(fn.endswith(ext) for ext in forecastExtension)]
for file in forecastFiles:
    fname = file
    fname = forecastDirectory + "\\" + fname
    outListEntry = file + ","

    ######################################################
    # Load data and populate all the PyForecast tables
    print(fname + '#########################################')
    print('Loading forecast file...')
    with open(fname, 'rb') as readfile:
        try:
            pyCast.datasetTable = pickle.load(readfile)
        except:
            print('WARNING: No datasetTable in saved forecast file...')
        try:
            pyCast.dataTable = pickle.load(readfile)
        except:
            print('WARNING: No dataTable in saved forecast file...')
        try:
            pyCast.datasetOperationsTable = pickle.load(readfile)
        except:
            print('WARNING: No datasetOperationsTable in saved forecast file...')
        try:
            pyCast.modelRunsTable = pickle.load(readfile)
        except:
            print('WARNING: No modelRunsTable in saved forecast file...')
        try:
            pyCast.forecastEquationsTable = pickle.load(readfile)
        except:
            print('WARNING: No forecastEquationsTable in saved forecast file...')
        try:
            pyCast.savedForecastEquationsTable = pickle.load(readfile)
        except:
            print('WARNING: No savedForecastEquationsTable in saved forecast file...')
        try:
            pyCast.forecastsTable = pickle.load(readfile)
        except:
            print('WARNING: No forecastsTable in saved forecast file...')
        # with open('resources/temp/user_options.txt', 'w') as writefile:
        #    writefile.write(pickle.load(readfile))
    print('----- OK!')
    print(' ')

    ######################################################
    # Download and update data to the user defined WY
    print(fname + '#########################################')
    print('Downloading and updating data...')
    startYear = pyCast.dataTable.index.max()[0].year
    pyCast.dataTab.startYearInput.setValue(startYear)
    endYear = datetime.date.today().year
    if datetime.date.today().month > 9:
        endYear = endYear + 1
    endYear = wyInput
    pyCast.dataTab.endYearInput.setValue(endYear)
    pyCast.dataTab.freshDownloadOption.setChecked(False)
    pyCast.dataTab.updateOption.setChecked(True)
    pyCast.downloadData()

    while pyCast.threadPool.activeThreadCount() > 0:
        print('  downloading data - active threads=' + str(pyCast.threadPool.activeThreadCount()))
        time.sleep(3)

    #isDonwloading = True
    #dSetIds = np.unique(pyCast.dataTable.index.get_level_values('DatasetInternalID'))
    #dSetCompletion = np.zeros((len(dSetIds),1), dtype=bool)
    #while isDonwloading:
        #for dSetIdx in range(len(dSetIds)):
        #    dSetId = dSetIds[dSetIdx]
        #    maxT = pyCast.dataTable[pyCast.dataTable.index.get_level_values('DatasetInternalID').isin([dSetId])].index.max()[0]
        #    if maxT == datetime.datetime(endYearT, 9, 30):
        #        dSetCompletion[dSetIdx] = True
        #if np.count_nonzero(dSetCompletion) == len(dSetIds):
        #    isDonwloading = False
        #else:
        #    print('Active threads = ' + str(pyCast.threadPool.activeThreadCount()))
        #    time.sleep(3)

    print('----- OK!')
    print(' ')

    ######################################################
    # Loop through the saved forecast models and generate forecasts
    print(fname + '#########################################')
    print('Generating forecasts...')
    from resources.modules.Miscellaneous.generateModel import Model
    for modelIdx in range(len(pyCast.savedForecastEquationsTable)):
        ithModelEntry = pyCast.savedForecastEquationsTable.iloc[modelIdx]
        ithModel = Model(parent=pyCast,forecastEquationTableEntry=ithModelEntry)
        ithModel.generate()
        if endYear not in ithModel.x.index:
            print('Forecast cannot be issued -- missing data...')
            outListEntry += 'Forecast cannot be issued -- missing data,NaN,NaN'
        else:
            ithModel.predict(ithModel.x.loc[endYear])
            outListEntry += 'OK ModelId=' + str(ithModelEntry.name) + ','+ str(ithModel.prediction) + ',' + str(';'.join(map(str, ithModel.predictionRange)))

    print('----- OK!')
    print(' ')

######################################################
# Write output file
date_time = datetime.datetime.now()
tsString = date_time.strftime("%d%b%YT%H%M%S")
with open(forecastDirectory + r'\ForecastWrapperOutput-' + tsString + '.csv', 'w') as f:
    for item in outList:
        f.write("%s\n" % item)