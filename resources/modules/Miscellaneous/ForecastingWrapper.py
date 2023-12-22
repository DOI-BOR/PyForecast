######################################################
# Import modules
import resources.application as app
import os, pickle, datetime, time, warnings, sys, pandas
warnings.filterwarnings("ignore")
from PyQt5 import QtWidgets, QtCore
from resources.modules.Miscellaneous.generateModel import Model


def forceUpdate(pyCast, fName, statusMessage):
    pyCast.setWindowTitle("PyForecast V" + pyCast.softwareVersion + " - " + str(fName))
    pyCast.resetDatasetTab()
    pyCast.resetDataTab()
    pyCast.resetModelCreationTab()
    pyCast.resetForecastsTab()
    pyCast.updateStatusMessage(statusMessage)

    qm = QtWidgets.QMessageBox()
    qm.setText(statusMessage)
    qm.setStandardButtons(QtWidgets.QMessageBox.Yes)
    qm.setDefaultButton(QtWidgets.QMessageBox.Yes)
    QtCore.QTimer.singleShot(2000, lambda: qm.done(0))
    qm.exec_()


def startForecast(pyCast, forecastDIR, forecastWY):
    ######################################################
    # Wrapper script inputs and outputs
    pathString = forecastDIR #r"C:\Users\jrocha\Desktop\_TLWRK_STUFF\Forecasting\06JUN2023"
    wyInput = forecastWY #2023
    outList = []
    outList.append('FILENAME,RUNMESSAGE,PREDICTION,PREDICTIONRANGE[P10],PREDICTIONRANGE[P25],PREDICTIONRANGE[P50],PREDICTIONRANGE[P75],PREDICTIONRANGE[P90],MODELEQUATION,MODELVARIABLES[n-Predictors],XVALUES[n-Predictors]')

    ######################################################
    # Start PyForecast in the background
    print('#########################################')
    # Begin loading the application
    print('----- OK!')
    print(' ')
    time.sleep(2)

    ######################################################
    # Loop through all the forecast files in the input directory
    forecastDirectory = os.path.normpath(pathString)
    forecastExtension = ['fcst']
    forecastFiles = [fn for fn in os.listdir(forecastDirectory) if any(fn.endswith(ext) for ext in forecastExtension)]
    for file in forecastFiles:
        fname = file
        pyCast.updateStatusMessage('Loading forecast file ' + fname)
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

        forceUpdate(pyCast, fname, 'Forecast file loaded!')
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
            time.sleep(2)

        forceUpdate(pyCast, fname, 'Updated data downloaded!')
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
                forceUpdate(pyCast, fname, 'Generating model...')
                ithModel.generate() #Regenerate Model
                if endYear not in ithModel.x.index:
                    print('Forecast cannot be issued -- missing data...')
                    ithOutListEntry = outListEntry + 'MISSING DATA ModelId=' + str(ithModelEntry.name) + ',nan,nan,nan,nan,nan,nan'
                    print('----- FAIL!')
                else:
                    try:
                        # JR - BREAKPOINT GOES ON THE NEXT LINE
                        forceUpdate(pyCast, fname, 'Generating forecast...')
                        ithModel.predict(ithModel.x.loc[endYear]) #Make a prediction
                        # Build model output strings
                        equationString = ithModel.modelReport[ithModel.modelReport.index("----- MODEL EQUATION -----") + 1]
                        equationVariables = ithModel.modelReport[(ithModel.modelReport.index("----- MODEL VARIABLES -----") + 1):(ithModel.modelReport.index("----- MODEL EQUATION -----") - 1)]
                        equationVariables = [w.replace(',', ';') for w in equationVariables]
                        equationVariablesString = ','.join([' '.join(ithString.split()) for ithString in equationVariables])
                        xValues = pandas.concat([ithModel.x.loc[endYear], pyCast.datasetTable], axis=1, join="inner").iloc[:, [4, 2, 5, 3, 0]]
                        xStrings = xValues.to_string(header=False, index=False, index_names=False).split('\n')
                        xString = ','.join([' '.join(ithString.split()) for ithString in xStrings])
                        # Build model output row
                        ithOutListEntry = outListEntry + 'OK ModelId=' + str(ithModelEntry.name) + ',' + str(ithModel.prediction) + ',' + str(','.join(map(str, ithModel.predictionRange.values[[10,25,50,75,90],0]))) + ',' + equationString + ',' + equationVariablesString + ',' + xString
                        print('----- OK!')
                    except:
                        ithOutListEntry = outListEntry + 'FAILED ModelId=' + str(ithModelEntry.name) + ',nan,nan,nan,nan,nan,nan'
                        print('----- FAIL!')
            except:
                ithOutListEntry = outListEntry + 'FAILED regenerating model - potential model and/or data errors...'
                print('----- FAIL!')

            # Add output row to output array
            outList.append(ithOutListEntry.replace("[", "").replace("]", ""))

        print(' ')

    ######################################################
    # Write output file
    date_time = datetime.datetime.now()
    tsString = date_time.strftime("%d%b%YT%H%M%S")
    with open(forecastDirectory + r'\ForecastWrapperOutput-' + tsString.upper() + '.csv', 'w') as f:
        for item in outList:
            f.write("%s\n" % item)
