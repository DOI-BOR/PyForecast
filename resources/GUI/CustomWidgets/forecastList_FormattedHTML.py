from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys
import os
import numpy as np
#sys.path.append(r"C:\Users\KFoley\Documents\NextFlow")
from resources.modules.Miscellaneous.truncateHtml import truncate
import isodate

FF = """<style>
div {{
table-layout: fixed;
width: 100%;
color: #003E51;
margin: 0px;
padding: 0px;
font-family: 'Open Sans', Arial, sans-serif, monospace;
font-size: 12px;
vertical-align: middle;
}}

</style>
<div>
<hr>
<table style="table-layout: fixed; width: 100%">
	<tr >
	<td style="padding-top:5px">
    
    </td>
	<td><p style="color: #007396; font-size: 15px; vertical-align: middle"><strong style="color: #007396; vertical-align: middle; font-size: 15px">
	{fcstMid} {units} </strong>({fcstLow} {units} to {fcstHigh} {units})</p><p><img src="resources/GraphicalResources/icons/{magnitude}" width="14" height="14" style="vertical-align:top; top:0px; right:10px;"/>&nbsp;&nbsp;{magExp}</p></td>
	</tr>
	<tr>
	<td>
    <img src="resources/GraphicalResources/icons/flag_checkered-24px.svg" width="18" height="18"/>
	</td>
	<td><p style="vertical-align: bottom">{skill}</p></td>
	</tr>
    <tr>
	<td><img src="resources/GraphicalResources/icons/build-24px.svg" width="18" height="18"/></td>
	<td><p style="vertical-align: bottom">{pipe}</p></td>
	</tr>
    <tr>
	<td><img style="vertical-align: top" src="resources/GraphicalResources/icons/target-24px.svg" width="18" height="18"/></td>
	<td style="padding-top:4px"><p style="vertical-align: middle;">{target}</p></td>
	</tr>
    <tr>
	<td><img src="resources/GraphicalResources/icons/bullseye-24px.svg" width="18" height="18"/></td>
	<td style="word-wrap: break-word"><p style="vertical-align: bottom">{predictors}</p></td>
	</tr>
    <tr>    
    <td style="text-align:left; color: #8c9f9d">{modelIDImg} Model ID: {modelIDNum}</td>
    </tr>
</table>
<hr>
</div>"""


class forecastList_HTML(QtWidgets.QTreeWidget):

    def __init__(self, parent = None):

        QtWidgets.QTreeWidget.__init__(self)
        self.parent = parent

        self.setColumnCount(1)
        self.setIndentation(0)
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.font_ = QtGui.QFont()
        self.font_.setBold(True)
        #self.setHeaderLabels(["Forecasts"])
        self.setHeaderHidden(True)
        self.setForecastTable()
        self.textTruncate = 70
        self.expandAll()

    def expandTopLevel(self):
        return

    def clearForecasts(self):
        self.clear()

    def setForecastTable(self):

        # Get all the years in the forecast equations
        years_w_forecasts = np.unique(self.parent.forecastsTable.index.get_level_values(1))

        for year in years_w_forecasts:

            # Add a new year to the tree widget
            yearItem = QtWidgets.QTreeWidgetItem(self, [f"{year} Forecasts"])
            yearItem.setFont(0, self.font_)

            # Get all the issue dates for this year
            issue_dates = np.unique(self.parent.forecastsTable.loc[(slice(None), year, slice(None), slice(None))].index.get_level_values(1))


            for date_ in issue_dates:

                # Add an issue date item
                issueDateItem = QtWidgets.QTreeWidgetItem(yearItem, [f'{date_.astype("datetime64[us]").astype(datetime).strftime("%Y-%b-%d")} Issue Date'])

                # Get all the models with this year and issue date
                models_list = np.unique(self.parent.forecastsTable.loc[(slice(None), year, date_, slice(None))].index.get_level_values(0))

                for model in models_list:

                    model_ref = self.parent.savedForecastEquationsTable.loc[model]
                    predictand = self.parent.datasetTable.loc[model_ref.EquationPredictand]
                    predictors = [self.parent.datasetTable.loc[predictorID] for predictorID in model_ref['EquationPredictors']]
                    targetText1 = truncate('<strong style="vertical-align:middle">{0}</strong><br/>'.format(predictand['DatasetName']), self.textTruncate, ellipsis='...')
                    targetText2 = truncate('{0}: {1}'.format(predictand['DatasetParameter'], model_ref['PredictandMethod'].replace("_", " ").upper()), self.textTruncate, ellipsis='...')
                    predictorsText = '<strong>{0} Predictors: </strong><br/>'.format(len(predictors))
                    allPreds = ", ".join([(f'({j + 1}) ' + predictor['DatasetName'] + '-' + predictor['DatasetParameter']) for j, predictor in enumerate(predictors)])
                    predBreaks = range(self.textTruncate, len(allPreds), self.textTruncate)
                    for ithBreak in reversed(predBreaks):
                        allPreds = allPreds[:ithBreak] + '<br/>' + allPreds[ithBreak:]
                    predictorsText += allPreds
                    source = model_ref['EquationSource']
                    if source == 'USACE':
                        modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/USACE.png" width="20", height="20"/>'
                        modelNumText = '<strong>USACE</strong>' + str(model)
                    elif source == 'NRCS':
                        modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/NRCS.svg" width="20", height="20"/>'
                        modelNumText = '<strong>NRCS</strong>' + str(model)
                    elif source == 'NOAA':
                        modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/NOAA.svg" width="20", height="20"/>'
                        modelNumText = '<strong>NOAA</strong>' + str(model)
                    elif source != 'PyForecast':
                        modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/icon.ico" width="20", height="20"/>'
                        modelNumText = '<strong>{0}</strong>'.format(source) + str(model)
                    else:
                        modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/icon.ico" width="20", height="20"/>'
                        modelNumText = model

                    # Parse the equation method into human readable format
                    equationMethod = model_ref['EquationMethod'].split('/')
                    equationMethod[1] = self.parent.preProcessors[equationMethod[1]]
                    equationMethod[2] = self.parent.regressors[equationMethod[2]]
                    pipeText1 = "<strong>{0}</strong>".format(equationMethod[2]['name'])
                    pipeText2 = "({0}, {1})".format(equationMethod[1]['name'], self.parent.crossValidators[equationMethod[3]]['name'])

                    # Get the forecasts
                    forecastValues = []

                    fcstMid = int(round(self.parent.forecastsTable.loc[(model, year, date_, 50), "ForecastValues"]))
                    fcstLow = int(round(self.parent.forecastsTable.loc[(model, year, date_, 10), "ForecastValues"]))
                    fcstHigh = int(round(self.parent.forecastsTable.loc[(model, year, date_, 90), "ForecastValues"]))
                    mag = str(self.parent.forecastsTable.loc[(model, year, date_, 50), "Magnitude"]) + ".png"
                    if mag == 'low.png':
                        magExp = "This forecast is lower than most years analyzed"
                    elif mag == 'high.png':
                        magExp = "This forecast is higher than most years analyzed"
                    else:
                        magExp = "This forecast is about normal for the years analyzed"


                    # Skill
                    skillText = []
                    for key, value in model_ref['EquationSkill'].items():
                        skillText.append("<strong>Scorer: {0}</strong>&nbsp;:&nbsp;{1}".format(self.parent.scorers['info'][key]['HTML'], round(value, 3)))
                    skillText = ', '.join(skillText)

                    label = QtWidgets.QLabel(FF.format(
                        units=predictand['DatasetUnits'] if 'KAF' not in model_ref['PredictandMethod'].upper() else 'KAF',
                        magnitude=mag,
                        fcstMid=fcstMid,
                        fcstLow=fcstLow,
                        fcstHigh=fcstHigh,
                        target=targetText1 + targetText2,
                        pipe=truncate(pipeText1, self.textTruncate, ellipsis='...') + '<br>' + truncate(pipeText2, self.textTruncate, ellipsis='...'),
                        skill=truncate(skillText, self.textTruncate),
                        predictors=predictorsText,
                        modelIDNum=modelNumText,
                        modelIDImg=modelImg,
                        magExp = magExp
                    ))

                    forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
                    forecastItem.forecastValues = self.parent.forecastsTable.loc[(model, year, date_, slice(None))]
                    forecastItem.modelID = modelNumText
                    forecastItem.setData(0, QtCore.Qt.UserRole, model)
                    label.setTextFormat(QtCore.Qt.RichText)
                    self.setItemWidget(forecastItem, 0, label)
        self.expandAll()

        # for i, (idx, forecastEquation) in enumerate(self.parent.savedForecastEquationsTable.iterrows()):
        #
        #     # Get the target and predictor datasets
        #     predictand = self.parent.datasetTable.loc[forecastEquation['EquationPredictand']]
        #     predictors = [
        #         self.parent.datasetTable.loc[predictorID] for predictorID in forecastEquation['EquationPredictors']
        #     ]
        #     targetText1 = truncate('<strong style="vertical-align:middle">{0}</strong><br/>'.format(predictand['DatasetName']), self.textTruncate, ellipsis='...')
        #     targetText2 = truncate('{0} {1}'.format(predictand['DatasetParameter'], forecastEquation['PredictandMethod'].title()), self.textTruncate, ellipsis='...')
        #     targetText =  targetText1 + targetText2
        #     predictorsText = '<strong>{0} Predictors: </strong><br/>'.format(len(predictors))
        #     allPreds = ", ".join([(f'({j+1}) '+predictor['DatasetName'] + '-' + predictor['DatasetParameter']) for j, predictor in enumerate(predictors)])
        #     predBreaks = range(self.textTruncate, len(allPreds), self.textTruncate)
        #     for ithBreak in reversed(predBreaks):
        #         allPreds = allPreds[:ithBreak] + '<br/>' + allPreds[ithBreak:]
        #     predictorsText += allPreds
        #
        #     # Parse the source43.64182962	-117.2425834
        #     source = forecastEquation['EquationSource']
        #     if source == 'USACE':
        #         modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/USACE.png" width="20", height="20"/>'
        #         modelNumText = '<strong>USACE</strong>' + str(idx)
        #     elif source == 'NRCS':
        #         modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/NRCS.svg" width="20", height="20"/>'
        #         modelNumText = '<strong>NRCS</strong>' + str(idx)
        #     elif source == 'NOAA':
        #         modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/NOAA.svg" width="20", height="20"/>'
        #         modelNumText = '<strong>NOAA</strong>' + str(idx)
        #     elif source != 'PyForecast':
        #         modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/icon_old.ico" width="20", height="20"/>'
        #         modelNumText = '<strong>{0}</strong>'.format(source) + str(idx)
        #     else:
        #         modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/icon_old.ico" width="20", height="20"/>'
        #         modelNumText = idx
        #
        #     # Parse the equation method into human readable format
        #     equationMethod = forecastEquation['EquationMethod'].split('/')
        #     equationMethod[1] = self.parent.preProcessors[equationMethod[1]]
        #     equationMethod[2] = self.parent.regressors[equationMethod[2]]
        #     pipeText1 = "<strong>{0}</strong>".format(equationMethod[2]['name'])
        #     pipeText2 = "({0}, {1})".format(equationMethod[1]['name'], self.parent.crossValidators[equationMethod[3]]['name'])
        #
        #     # Get the forecasts
        #     forecastValues = []
        #     if idx in self.parent.forecastsTable.index.get_level_values(0):
        #         fcstMid = int(round(self.parent.forecastsTable.loc[(idx, slice(None), 50), "ForecastValues"].iloc[-1]))
        #         fcstLow = int(round(self.parent.forecastsTable.loc[(idx, slice(None), 10), "ForecastValues"].iloc[-1]))
        #         fcstHigh= int(round(self.parent.forecastsTable.loc[(idx, slice(None), 90), "ForecastValues"].iloc[-1]))
        #         mag = str(self.parent.forecastsTable.loc[(idx, slice(None), 50), "Magnitude"].iloc[-1]) + ".png"
        #
        #     else:
        #         fcstMid = "[MISSING PREDICTOR DATA] ?"
        #         fcstLow = "?"
        #         fcstHigh= "?"
        #         mag = 'warning-24px.svg'
        #
        #     # Skill
        #     skillText = []
        #     for key, value in forecastEquation['EquationSkill'].items():
        #         skillText.append("<strong>Scorer: {0}</strong>&nbsp;:&nbsp;{1}".format(self.parent.scorers['info'][key]['HTML'], round(value, 3)))
        #     skillText = ', '.join(skillText)
        #
        #     # Check if the period equals the last period
        #     if (i != 0) and (forecastEquation['PredictandPeriod'] == self.parent.savedForecastEquationsTable.iloc[i-1]['PredictandPeriod']):
        #         # check if the issue date equals the last issue date
        #         if forecastEquation['EquationIssueDate'] == issueDate:
        #             forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
        #         else:
        #             issueDate = forecastEquation['EquationIssueDate']
        #             issueDateItem = QtWidgets.QTreeWidgetItem(periodItem, ["Issued on {0}".format(issueDate.strftime("%B %d"))])
        #             forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
        #     # Create a new parent
        #     else:
        #         period = forecastEquation['PredictandPeriod'].split('/')
        #         periodStart = datetime.strptime(period[1], "%Y-%m-%d")
        #         duration = isodate.parse_duration(period[2])
        #         periodEnd = periodStart + duration - isodate.duration.Duration(1)
        #         issueDate = forecastEquation['EquationIssueDate']
        #         periodItem = QtWidgets.QTreeWidgetItem(self, ["Forecast Period {0} - {1}".format(periodStart.strftime("%B %d"), periodEnd.strftime("%B %d"))])
        #         periodItem.setFont(0,self.font_)
        #         try:
        #             issueString = "Issued on {0}".format(issueDate.strftime("%B %d"))
        #         except:
        #             issueString = "No issued forecasts..."
        #         issueDateItem = QtWidgets.QTreeWidgetItem(periodItem, [issueString])
        #         forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
        #
        #     # Finalize object
        #     label = QtWidgets.QLabel(FF.format(
        #                 units= predictand['DatasetUnits'] if 'KAF' not in forecastEquation['PredictandMethod'] else 'KAF',
        #                 magnitude=mag,
        #                 fcstMid = fcstMid,
        #                 fcstLow = fcstLow,
        #                 fcstHigh= fcstHigh,
        #                 target = targetText,
        #                 pipe = truncate(pipeText1, self.textTruncate, ellipsis = '...') + '<br>' + truncate(pipeText2, self.textTruncate, ellipsis = '...'),
        #                 skill = truncate(skillText,self.textTruncate),
        #                 predictors = predictorsText,
        #                 modelIDNum = modelNumText,
        #                 modelIDImg = modelImg
        #             ))
        #
        #     forecastItem.forecastValues = forecastValues
        #     forecastItem.modelID = modelNumText
        #     forecastItem.setData(0, QtCore.Qt.UserRole, idx)
        #     label.setTextFormat(QtCore.Qt.RichText)
        #     self.setItemWidget(forecastItem,0, label)
     

if __name__ == '__main__':
    import sys
    import pandas as pd
    import pickle
    import importlib
    import os
    import inspect
    sys.path.append(r"C:\Users\KFoley\Documents\NextFlow")

    regr = {}
    cv = {}
    pp = {}
    for file_ in os.listdir("resources/modules/ModelCreationTab/RegressionAlgorithms"):
        if '.py' in file_:
            mod = importlib.import_module("resources.modules.ModelCreationTab.RegressionAlgorithms.{0}".format(file_[:file_.index(".py")]))
            regr[file_[:file_.index(".py")]] = getattr(mod, "Regressor").NAME
    for file_ in os.listdir("resources/modules/ModelCreationTab/PreProcessingAlgorithms"):
        if '.py' in file_:
            mod = importlib.import_module("resources.modules.ModelCreationTab.PreProcessingAlgorithms.{0}".format(file_[:file_.index(".py")]))
            pp[file_[:file_.index(".py")]] = getattr(mod, "preprocessor").NAME
    


    app = QtWidgets.QApplication(sys.argv)
    for fontFile in os.listdir("resources/GraphicalResources/fonts"):
            QtGui.QFontDatabase.addApplicationFont("resources/GraphicalResources/fonts/{0}".format(fontFile))
    widg = QtWidgets.QWidget()
    widg.datasetTable = pd.read_pickle("toyDatasets.pkl")
    widg.regressorsDict = regr
    widg.preprocessorsDict = pp
    layout = QtWidgets.QVBoxLayout()
    #widg.setFixedHeight(300)
    widg.setFixedWidth(500)
    widg.setMinimumHeight(700)

    widg.crossValidators = {}
    mod = importlib.import_module("resources.modules.ModelCreationTab.CrossValidationAlgorithms")
    for cv, class_ in inspect.getmembers(mod, inspect.isclass):
        widg.crossValidators[cv] = {}
        widg.crossValidators[cv]["module"] = class_
        widg.crossValidators[cv]["name"] = class_.NAME

    widg.scorers = {}
    mod = importlib.import_module("resources.modules.ModelCreationTab.ModelScoring")
    widg.scorers["class"] = getattr(mod, "Scorers")
    widg.scorers['info'] = widg.scorers["class"].INFO
    widg.scorers["module"] = mod
    for scorer, scorerFunc in inspect.getmembers(widg.scorers['class'], inspect.isfunction):
        widg.scorers[scorer] = scorerFunc

    widg.forecastEquationsTable = pd.DataFrame(
            index = pd.Index([], dtype=int, name='ForecastEquationID'),
            columns = [
                "EquationSource",       # e.g. 'PyForecast','NRCS', 'CustomImport'
                "EquationComment",      # E.g. 'Equation Used for 2000-2010 Forecasts'
                "EquationPredictand",   # E.g. 103011
                "PredictandPeriod",     # R/1978-03-01/P1M/F12M (starting in march of 1978, over a 1 month period, recurring once a year.)
                "PredictandMethod",      # E.g. Accumulation, Average, Max, etc
                "EquationCreatedOn",    # E.g. 2019-10-04
                "EquationIssueDate",    # E.g. 2019-02-01
                "EquationMethod",       # E.g. Pipeline string (e.g. PIPE/PreProc_Logistic/Regr_Gamma/KFOLD_5)
                "EquationSkill",        # E.g. Score metric dictionary (e.g. {"AIC_C": 433, "ADJ_R2":0.32, ...})
                "EquationPredictors",   # E.g. [100204, 100101, 500232]
                "PredictorPeriods",     # E.g. [R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M, R/1978-03-01/P1M/F12M]
                "PredictorMethods"      # E.g. ['Average', 'First', 'Max']
            ]
        )

    widg.forecastsTable = pd.DataFrame(
            index = pd.MultiIndex(
                levels=[[],[],[]],
                codes= [[],[],[]],
                names=[
                    'ForecastEquationID',   # E.g. 1010010 (999999 for user imported forecast)
                    'Year',                 # E.g. 2019
                    'ForecastExceedance'    # e.g. 0.30 (for 30% exceedence)
                    ]
            ),
            columns = [
                "ForecastValues",           # in order of 0-100% exceedance
                ],
        )
    widg.forecastEquationsTable.loc[10110] = [
        "PyForecast",
        "",
        106162,
        "R/1900-04-01/P4M/F12M",
        "accumulation",
        pd.to_datetime("2019-01-22"),
        pd.to_datetime("2019-02-01"),
        "PIPE/PreProc_NoPreProcessing/Regr_PCARegressor/KFOLD_10",
        {"AIC_C":422, "ADJ_R2":0.55},
        [100194, 14000, 106162, 14132],
        ["R/1900-02-01/P1D/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M" ],
        ["first", "average", "average", "average"]
    ]
    widg.forecastEquationsTable.loc[10033] = [
        "NOAA",
        "",
        106162,
        "R/1900-04-01/P4M/F12M",
        "accumulation",
        pd.to_datetime("2019-01-22"),
        pd.to_datetime("2019-02-01"),
        "PIPE/PreProc_YAware/Regr_ZScore/KFOLD_10",
        {"AIC_C":422, "ADJ_R2":0.55},
        [100194, 14000, 106162, 14132],
        ["R/1900-02-01/P1D/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M" ],
        ["first", "average", "average", "average"]
    ]
    
    widg.forecastEquationsTable.loc[10036] = [
        "USACE",
        "",
        106162,
        "R/1900-04-01/P4M/F12M",
        "accumulation",
        pd.to_datetime("2019-01-22"),
        pd.to_datetime("2019-03-01"),
        "PIPE/PreProc_Logarithmic_X/Regr_GammaGLM/KFOLD_10",
        {"AIC_C":422, "ADJ_R2":0.55},
        [100194, 14000, 106162, 14132],
        ["R/1900-02-01/P1D/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M" ],
        ["first", "average", "average", "average"]
    ]
    widg.forecastEquationsTable.loc[10026] = [
        "PyForecast",
        "",
        106162,
        "R/1900-05-01/P3M/F12M",
        "accumulation",
        pd.to_datetime("2019-01-22"),
        pd.to_datetime("2019-05-01"),
        "PIPE/PreProc_MinMaxScaler/Regr_SVM_RBF/KFOLD_5",
        {"AIC_C":422, "ADJ_R2":0.55},
        [100194, 14000, 106162, 14132],
        ["R/1900-02-01/P1D/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M", "R/1900-01-01/P1M/F12M" ],
        ["first", "average", "average", "average"]
    ]
    
    for i in range(1, 100):
        widg.forecastsTable.loc[(10110, 2020,i/100), "ForecastValues"] = (i+43)*100/(i+1)
        widg.forecastsTable.loc[(10033, 2020, i/100), "ForecastValues"] = (i)*88
        widg.forecastsTable.loc[(10026, 2020, i/100), "ForecastValues"] = (i)*88
    widg.forecastsTable.loc[(10110, 2020,.5), "ForecastMagnitude"] = 'high'
    widg.forecastsTable.loc[(10033, 2020,.5), "ForecastMagnitude"] = 'mid'
    widg.forecastsTable.loc[(10026, 2020,.5), "ForecastMagnitude"] = 'low'
    mm = forecastList_HTML(widg)
    layout.addWidget(mm)
    widg.setLayout(layout)
    widg.setStyleSheet("""
    QLabel {
        border: 0px solid darkgray;
        border-bottom-width: 1px;
        padding: 10px;
    }

QTreeView::branch:!has-children:selected{
        background: #FFFFFF;
}
QTreeView::item:!has-children:selected{
        background: #d1e1ed;
}
QTreeView::item:!has-children{
        background: #f4f1ec;
}


    """)
    widg.show()
    #mw = forecastList_HTML()
    sys.exit(app.exec_())