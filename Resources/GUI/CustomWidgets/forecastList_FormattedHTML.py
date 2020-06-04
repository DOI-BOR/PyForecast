from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime
import sys
import os
sys.path.append(r"C:\Users\KFoley\Documents\NextFlow")
from resources.modules.Miscellaneous.truncateHtml import truncate
import isodate

FF = """<style>
div {{
color: #003E51;
margin: 0px;
padding: 0px;
font-family: 'Open Sans', Arial, sans-serif, monospace;
font-size: 12px;
vertical-align: middle;
}}

</style>
<div>
<table border="0" width="100px">
	<tr >
	<td style="padding-top:5px">
    <img src="resources/GraphicalResources/icons/{magnitude}" width="18" height="18" style="vertical-align:top; top:4px;"/>
    </td>
	<td><p style="color: #007396; font-size: 15px; vertical-align: middle"><strong style="color: #007396; vertical-align: middle; font-size: 15px">{fcstMid} {units} </strong>({fcstLow} {units} to {fcstHigh} {units})</p></td>
	</tr>
	<tr>
	<td>
    <img src="resources/GraphicalResources/icons/flag_checkered-24px.svg" width="18" height="18"/>
	</td>
	<td><p style="vertical-align: bottom">{skill}</p></td>
	</tr>
    <tr>
	<td>
    <img src="resources/GraphicalResources/icons/build-24px.svg" width="18" height="18"/>
	</td>
	<td><p style="vertical-align: bottom">{pipe}</p></td>
	</tr>
    <tr>
	<td>
    <img style="vertical-align: top" src="resources/GraphicalResources/icons/target-24px.svg" width="18" height="18"/>
	</td>
	<td style="padding-top:4px"><p style="vertical-align: middle;">{target}</p></td>
	</tr>
    <tr >
	<td >
    <img src="resources/GraphicalResources/icons/bullseye-24px.svg" width="18" height="18"/>
	</td>
	<td ><p style="vertical-align: bottom">{predictors}</p></td>
	</tr>
    <tr>
    </tr>
    <tr>
    <td>{modelIDImg}</td>
    <td style="text-align:right; color: #8c9f9d">{modelIDNum}</td>
    </tr>

</table>
</div>"""


class forecastList_HTML(QtWidgets.QTreeWidget):

    def __init__(self, parent = None):

        QtWidgets.QTreeWidget.__init__(self)
        self.setColumnCount(1)
        self.setIndentation(14)
        self.parent = parent
        self.font_ = QtGui.QFont()
        self.font_.setBold(True)
        self.setHeaderLabels(["Forecasts"])
        self.setForecastTable()
        #self.setMaximumWidth(400)
        
        #self.expandAll()

    def expandTopLevel(self):
        return

    def setForecastTable(self):

        for i, (idx, forecastEquation) in enumerate(self.parent.forecastEquationsTable.iterrows()):

            # Get the target and predictor datasets
            predictand = self.parent.datasetTable.loc[forecastEquation['EquationPredictand']]
            predictors = [
                self.parent.datasetTable.loc[predictorID] for predictorID in forecastEquation['EquationPredictors']
            ]
            targetText1 = truncate('<strong style="vertical-align:middle">{0}</strong><br/>'.format(predictand['DatasetName']), 50, ellipsis='...')
            targetText2 = truncate('{0} {1}'.format(predictand['DatasetParameter'], forecastEquation['PredictandMethod'].title()), 50, ellipsis='...')
            targetText =  targetText1 + targetText2
            predictorsText = ", ".join([predictor['DatasetParameter'] for predictor in predictors])
            

            # Parse the source
            source = forecastEquation['EquationSource']
            if source == 'USACE':
                modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/USACE.png" width="20", height="20"/>'
                modelNumText = '<strong>USACE</strong>' + str(idx)
            elif source == 'NRCS':
                modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/NRCS.svg" width="20", height="20"/>'
                modelNumText = '<strong>NRCS</strong>' + str(idx)
            elif source == 'NOAA':
                modelImg = '<img style="vertical-align:bottom" src="resources/GraphicalResources/icons/NOAA.svg" width="20", height="20"/>'
                modelNumText = '<strong>NOAA</strong>' + str(idx)
            elif source != 'PyForecast':
                modelImg = ""
                modelNumText = '<strong>{0}</strong>'.format(source) + str(idx)
            
            else:
                modelImg = ""
                modelNumText = idx

            # Parse the equation method into human readable format
            equationMethod = forecastEquation['EquationMethod'].split('/')
            equationMethod[1] = self.parent.preprocessorsDict[equationMethod[1]]
            equationMethod[2] = self.parent.regressorsDict[equationMethod[2]]
            pipeText1 = "<strong>{0}</strong>".format(equationMethod[2]) 
            pipeText2 = "({0}, {1})".format(equationMethod[1], self.parent.crossValidators[equationMethod[3]]['name'] )

            # Get the forecasts
            if idx in self.parent.forecastsTable.index.get_level_values(0):
                fcstMid = int(round(self.parent.forecastsTable.loc[(idx, 2020, 0.5), "ForecastValues"]))
                fcstLow = int(round(self.parent.forecastsTable.loc[(idx, 2020, 0.9), "ForecastValues"]))
                fcstHigh= int(round(self.parent.forecastsTable.loc[(idx, 2020, 0.1), "ForecastValues"]))
                mag = self.parent.forecastsTable.loc[(idx, 2020, 0.5), "ForecastMagnitude"] + ".png"
            else:
                fcstMid = "[MISSING PREDICTOR DATA] ?"
                fcstLow = "?"
                fcstHigh= "?"
                mag = 'warning-24px.svg'
            
            # Skill
            skillText = []
            for key, value in forecastEquation['EquationSkill'].items():
                skillText.append("<strong>{0}</strong>&nbsp;:&nbsp;{1}".format(self.parent.scorers['info'][key]['HTML'], value)) 
            skillText = ', '.join(skillText)

            # Check if the period equals the last period
            if (i != 0) and (forecastEquation['PredictandPeriod'] == self.parent.forecastEquationsTable.iloc[i-1]['PredictandPeriod']):
                
                # check if the issue date equals the last issue date
                if forecastEquation['EquationIssueDate'] == issueDate:
                    forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
                    label = QtWidgets.QLabel(FF.format(
                            units= predictand['DatasetUnits'] if 'KAF' not in forecastEquation['PredictandMethod'] else 'KAF',
                            magnitude=mag,
                            fcstMid = fcstMid,
                            fcstLow = fcstLow,
                            fcstHigh= fcstHigh,
                            target = targetText,
                            pipe = truncate(pipeText1, 50, ellipsis = '...') + '<br>' + truncate(pipeText2, 50, ellipsis = '...'),
                            skill = truncate(skillText,50, ellipsis = '...'),
                            predictors = truncate(predictorsText, 50, ellipsis = '...'),
                            modelIDNum = modelNumText,
                            modelIDImg = modelImg
                        ))
                    forecastItem.setData(0, QtCore.Qt.UserRole, idx)       
                    label.setTextFormat(QtCore.Qt.RichText)  
                    self.setItemWidget(forecastItem,0, label)


                else:

                    issueDate = forecastEquation['EquationIssueDate']
                    issueDateItem = QtWidgets.QTreeWidgetItem(periodItem, ["Issued on {0}".format(issueDate.strftime("%B %d"))])
                    forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
                    label = QtWidgets.QLabel(FF.format(
                            units= predictand['DatasetUnits'] if 'KAF' not in forecastEquation['PredictandMethod'] else 'KAF',
                            magnitude=mag,
                            fcstMid = fcstMid,
                            fcstLow = fcstLow,
                            fcstHigh= fcstHigh,
                            target = targetText,
                            pipe = truncate(pipeText1, 50, ellipsis = '...') + '<br>' + truncate(pipeText2, 50, ellipsis = '...'),
                            skill = truncate(skillText,50, ellipsis = '...'),
                            predictors = truncate(predictorsText, 50, ellipsis = '...'),
                            modelIDNum = modelNumText,
                            modelIDImg = modelImg
                        ))
                    forecastItem.setData(0, QtCore.Qt.UserRole, idx)       
                    label.setTextFormat(QtCore.Qt.RichText)  
                    self.setItemWidget(forecastItem,0, label)


            # Create a new parent
            else:
                period = forecastEquation['PredictandPeriod'].split('/')
                periodStart = datetime.strptime(period[1], "%Y-%m-%d")
                duration = isodate.parse_duration(period[2])
                periodEnd = periodStart + duration - isodate.duration.Duration(1)
                issueDate = forecastEquation['EquationIssueDate']
                periodItem = QtWidgets.QTreeWidgetItem(self, ["Forecast Period {0} - {1}".format(periodStart.strftime("%B %d"), periodEnd.strftime("%B %d"))])
                periodItem.setFont(0,self.font_)
                issueDateItem = QtWidgets.QTreeWidgetItem(periodItem, ["Issued on {0}".format(issueDate.strftime("%B %d"))])
                forecastItem = QtWidgets.QTreeWidgetItem(issueDateItem, 0)
                label = QtWidgets.QLabel(FF.format(
                        units= predictand['DatasetUnits'] if 'KAF' not in forecastEquation['PredictandMethod'] else 'KAF',
                        magnitude=mag,
                        fcstMid = fcstMid,
                        fcstLow = fcstLow,
                        fcstHigh= fcstHigh,
                        target = targetText,
                        pipe = truncate(pipeText1, 50, ellipsis = '...') + '<br>' + truncate(pipeText2, 50, ellipsis = '...'),
                        skill = truncate(skillText,50),
                        predictors = truncate(predictorsText, 50),
                        modelIDNum = modelNumText,
                        modelIDImg = modelImg
                    ))
                forecastItem.setData(0, QtCore.Qt.UserRole, idx)       
                label.setTextFormat(QtCore.Qt.RichText)
                self.setItemWidget(forecastItem,0, label)           
     

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
    for file_ in os.listdir("resources/modules/StatisticalModelsTab/RegressionAlgorithms"):
        if '.py' in file_:
            mod = importlib.import_module("resources.modules.StatisticalModelsTab.RegressionAlgorithms.{0}".format(file_[:file_.index(".py")]))
            regr[file_[:file_.index(".py")]] = getattr(mod, "Regressor").NAME
    for file_ in os.listdir("resources/modules/StatisticalModelsTab/PreProcessingAlgorithms"):
        if '.py' in file_:
            mod = importlib.import_module("resources.modules.StatisticalModelsTab.PreProcessingAlgorithms.{0}".format(file_[:file_.index(".py")]))
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
    mod = importlib.import_module("resources.modules.StatisticalModelsTab.CrossValidationAlgorithms")
    for cv, class_ in inspect.getmembers(mod, inspect.isclass):
        widg.crossValidators[cv] = {}
        widg.crossValidators[cv]["module"] = class_
        widg.crossValidators[cv]["name"] = class_.NAME

    widg.scorers = {}
    mod = importlib.import_module("resources.modules.StatisticalModelsTab.ModelScoring")
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