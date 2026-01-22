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


def startRetrain(pyCast, dirIN, dirOUT, retrainWY):
    ######################################################
    # Wrapper script inputs and outputs
    pathStringPRE = dirIN
    pathStringPOST = dirOUT
    #pathStringPRE = r"C:\Users\jrocha\Desktop\_TLWRK_STUFF\Forecasting\_AllPycastFiles"
    #pathStringPOST = r"C:\Users\jrocha\Desktop\_TLWRK_STUFF\Forecasting\_AllPycastFilesWY2023"
    wyInput = retrainWY #2022
    outListORIG = []
    outListMOD = []

    ######################################################
    # Start PyForecast in the background
    print('#########################################')
    # Begin loading the application
    #pyCast.hide()
    print('----- OK!')
    print(' ')

    ######################################################
    # Loop through all the forecast files in the input directory
    forecastDirectoryPRE = os.path.normpath(pathStringPRE)
    forecastDirectoryPOST = os.path.normpath(pathStringPOST)
    forecastExtension = ['fcst']
    forecastFiles = [fn for fn in os.listdir(forecastDirectoryPRE) if any(fn.endswith(ext) for ext in forecastExtension)]
    for file in forecastFiles:
        fname = file
        fnameFQ = forecastDirectoryPRE + "\\" + fname

        ######################################################
        # Load data and populate all the PyForecast tables
        print(fnameFQ + '#########################################')
        print('Loading forecast file...')
        pyCast.updateStatusMessage('Loading forecast file ' + fname)
        with open(fnameFQ, 'rb') as readfile:
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


        forceUpdate(pyCast, fname, 'Forecast file loaded!')
        print('----- OK!')
        print(' ')

        ######################################################
        # Download and update data to the user defined WY
        print(fnameFQ + '#########################################')
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
        pyCast.downloadData()

        while pyCast.threadPool.activeThreadCount() > 0:
            print('  still downloading data - active threads=' + str(pyCast.threadPool.activeThreadCount()))
            time.sleep(2)

        forceUpdate(pyCast, fname, 'Updated data downloaded!')
        print('----- OK!')
        print(' ')

        ######################################################
        # Loop through each model in the forecast file
        print(fname + '#########################################')
        print('Generating original and retrained model equations...')
        for modelIdx in range(len(pyCast.savedForecastEquationsTable)):
            outListOrigString = "ORIGINAL;" + file + ";"
            outListModString = "RETRAINED;" + file + ";"
            try:
                ithModelEntry = pyCast.savedForecastEquationsTable.iloc[modelIdx]
                ithModel = Model(parent=pyCast, forecastEquationTableEntry=ithModelEntry)
                # JR - BREAKPOINT GOES ON THE NEXT LINE
                forceUpdate(pyCast, fname, 'Generating Original Model...')
                ithModel.generate()  # Regenerate Model
                outListOrigString = outListOrigString + ';'.join(ithModel.modelReport)
                # Set new training period end
                trainingPeriodString = ithModelEntry.ModelTrainingPeriod
                ithModelEntry.ModelTrainingPeriod = '/'.join(
                    [trainingPeriodString.split('/')[0], str(wyInput), trainingPeriodString.split('/')[2]]
                )
                ithModel = Model(parent=pyCast, forecastEquationTableEntry=ithModelEntry)
                # JR - BREAKPOINT GOES ON THE NEXT LINE
                forceUpdate(pyCast, fname, 'Generating Updated Model...')
                ithModel.generate()  # Regenerate Model
                outListModString = outListModString + ';'.join(ithModel.modelReport)

            except:
                print('----- FAIL!')
                outListOrigString = outListOrigString + 'FAILED'
                outListModString = outListModString + 'FAILED'

            # Add output row to output array
            outListORIG.append(outListOrigString.replace("[", "").replace("]", ""))
            outListMOD.append(outListModString.replace("[", "").replace("]", ""))

        print('----- OK!')
        print(' ')

        ######################################################
        # Save forecast file
        forceUpdate(pyCast, fname, 'Saving retrained file...')
        fnameFQ = forecastDirectoryPOST + "\\" + fname
        print(fnameFQ + '#########################################')
        print('Saving retrained file...')
        with open(fnameFQ, 'wb') as writefile:
            pickle.dump(pyCast.datasetTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(pyCast.dataTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(pyCast.datasetOperationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(pyCast.modelRunsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(pyCast.forecastEquationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(pyCast.savedForecastEquationsTable, writefile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(pyCast.forecastsTable, writefile, pickle.HIGHEST_PROTOCOL)

        print('----- OK!')
        print(' ')

    ######################################################
    # Write output file
    print(fnameFQ + '#########################################')
    print('Writing output files...')
    forceUpdate(pyCast, fname, 'Writing output files...')
    date_time = datetime.datetime.now()
    tsString = date_time.strftime("%d%b%YT%H%M%S")
    with open(forecastDirectoryPRE + r'\RetrainingOutput-ORIGINAL-' + tsString.upper() + '.txt', 'w') as f:
        for item in outListORIG:
            f.write("%s\n" % item)
    with open(forecastDirectoryPOST + r'\RetrainingOutput-RETRAINED-' + tsString.upper() + '.txt', 'w') as f:
        for item in outListMOD:
            f.write("%s\n" % item)

    print('----- OK!')
    print(' ')
