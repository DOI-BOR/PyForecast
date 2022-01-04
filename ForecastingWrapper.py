######################################################
# Import modules
import resources.application as app
import os, pickle, datetime, time, warnings, sys, pandas
warnings.filterwarnings("ignore")
from PyQt5 import QtWidgets
from resources.modules.Miscellaneous.generateModel import Model

if __name__ == '__main__':
    ######################################################
    # Wrapper script inputs and outputs
    pathString = r"C:\Users\jrocha\Desktop\_TLWRK_STUFF\Forecasting\JAN2022"
    wyInput = 2022
    outList = []
    outList.append('FILENAME,RUNMESSAGE,PREDICTION,PREDICTIONRANGE[P10],PREDICTIONRANGE[P25],PREDICTIONRANGE[P50],PREDICTIONRANGE[P75],PREDICTIONRANGE[P90],XVALUES[n-Predictors]')

    ######################################################
    # Start PyForecast in the background
    print('#########################################')
    print('Starting dummy PyForecast instance in the background...')
    # Begin loading the application
    dummyApp = QtWidgets.QApplication(sys.argv)
    pyCast = app.mainWindow()
    #pyCast.show()
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
        endYear = datetime.date.today().year
        if datetime.date.today().month > 9:
            endYear = endYear + 1
        endYear = wyInput
        startYear = pyCast.dataTable.index.max()[0].year
        if startYear == endYear:
            startYear = endYear - 1
        pyCast.dataTab.startYearInput.setValue(startYear)
        pyCast.dataTab.endYearInput.setValue(endYear)
        pyCast.dataTab.freshDownloadOption.setChecked(False)
        pyCast.dataTab.updateOption.setChecked(True)
        #pyCast.dataTab.freshDownloadOption.setChecked(True)
        #pyCast.dataTab.updateOption.setChecked(False)
        pyCast.downloadData()

        while pyCast.threadPool.activeThreadCount() > 0:
            print('  still downloading data - active threads=' + str(pyCast.threadPool.activeThreadCount()))
            time.sleep(5)

        time.sleep(5)
        print('----- OK!')
        print(' ')

        #print(pyCast.dataTable.dropna().tail(n=25))

        ######################################################
        # Loop through the saved forecast models and generate forecasts
        print(fname + '#########################################')
        print('Generating forecasts...')
        for modelIdx in range(len(pyCast.savedForecastEquationsTable)):
            ithModelEntry = pyCast.savedForecastEquationsTable.iloc[modelIdx]
            ithModel = Model(parent=pyCast,forecastEquationTableEntry=ithModelEntry)
            try:
                # JR - BREAKPOINT GOES ON THE NEXT LINE
                ithModel.generate()
                if endYear not in ithModel.x.index:
                    print('Forecast cannot be issued -- missing data...')
                    ithOutListEntry = outListEntry + 'MISSING DATA ModelId=' + str(ithModelEntry.name) + ',nan,nan,nan,nan,nan,nan'
                else:
                    try:
                        # JR - BREAKPOINT GOES ON THE NEXT LINE
                        ithModel.predict(ithModel.x.loc[endYear])
                        xValues = pandas.concat([ithModel.x.loc[endYear], pyCast.datasetTable], axis=1, join="inner").iloc[:, [4, 2, 5, 3, 0]]
                        xStrings = xValues.to_string(header=False, index=False, index_names=False).split('\n')
                        xString = ','.join([' '.join(ithString.split()) for ithString in xStrings])
                        ithOutListEntry = outListEntry + 'OK ModelId=' + str(ithModelEntry.name) + ',' + str(ithModel.prediction) + ',' + str(','.join(map(str, ithModel.predictionRange.values[[10,25,50,75,90],0]))) + ',' + xString
                    except:
                        ithOutListEntry = outListEntry + 'FAILED ModelId=' + str(ithModelEntry.name) + ',nan,nan,nan,nan,nan,nan'
            except:
                ithOutListEntry = outListEntry + 'FAILED regenerating model - potential data errors...'
            outList.append(ithOutListEntry.replace("[", "").replace("]", ""))

        print('----- OK!')
        print(' ')

    ######################################################
    # Write output file
    date_time = datetime.datetime.now()
    tsString = date_time.strftime("%d%b%YT%H%M%S")
    with open(forecastDirectory + r'\ForecastWrapperOutput-' + tsString.upper() + '.csv', 'w') as f:
        for item in outList:
            f.write("%s\n" % item)
