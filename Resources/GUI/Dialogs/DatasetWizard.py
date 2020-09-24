# Import Statements
from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from resources.GUI.CustomWidgets.CombinedDatasetTable import CombinedDatasetTbl
from resources.modules.Miscellaneous import loggingAndErrors
import importlib
from csv import Sniffer
import os
import requests
import io


# Main Class Definition
class DatasetWizard(QtWidgets.QWizard):
    # Signal to return the custom dataset definition to the application
    returnDatasetSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, datasetID=None):
        """
        This dialog window handles adding custom dataset definitions
        into the forecast file.
        """

        QtWidgets.QWizard.__init__(self)

        self.parent = parent
        self.datasetID = datasetID
        self.setWindowTitle("User Defined Dataset")
        self.setWhatsThis(
            "Use this dialog to define a new dataset using an alternate data source (Import, composite, URL, etc).")
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        logo = QtGui.QPixmap("resources/GraphicalResources/icon.png")
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, logo.scaled(71, 61))

        # Load in the list of dataloaders
        self.dloaderNames = []
        for filename in os.listdir("resources/DataLoaders"):
            if '.py' in filename.lower() and not 'import' in filename.lower():
                self.dloaderNames.append(filename[:filename.index(".py")])
        self.dloaders = [importlib.import_module("resources.DataLoaders.{0}".format(fname)) for fname in
                         self.dloaderNames]

        # Set the User Interface
        self.setupUI()

        # Connect events
        self.fileButton.clicked.connect(self.loadImportFile)
        self.HTMLloadUrlButton.clicked.connect(self.loadHTMLFile)

        # Initialize an empty dataset
        self.loadDataset(self.datasetID)

        # Connect the page changed signal
        self.currentIdChanged.connect(self.updateDataset)
        self.accepted.connect(lambda: self.updateDataset(-100))

    def loadDataset(self, datasetID):
        """
        Loads the dataset information associated with the selected datasetID
        """

        if datasetID == None:
            if self.parent.datasetTable.empty:
                self.datasetID = 900000
            elif (max(self.parent.datasetTable.index) < 900000):
                self.datasetID = 900000
            else:
                self.datasetID = max(self.parent.datasetTable.index) + 1
            self.dataset = pd.Series()

        else:
            self.dataset = self.parent.datasetTable.loc[datasetID]
            self.datasetTypeField.setCurrentText(self.dataset['DatasetType'])
            self.datasetAgencyField.setText(self.dataset['DatasetAgency'])
            self.datasetNameField.setText(self.dataset['DatasetName'])
            self.datasetIDField.setText(self.dataset['DatasetExternalID'])
            self.parameterCodeField.setText(self.dataset["DatasetParameterCode"])
            self.parameterNameField.setText(self.dataset["DatasetParameter"])
            self.parameterUnitField.setText(self.dataset['DatasetUnits'])

        return

    def updateDataset(self, newID):

        if newID > self.metadataID:
            self.dataset["DatasetType"] = self.datasetTypeField.currentText()
            self.dataset["DatasetName"] = self.datasetNameField.text()
            self.dataset["DatasetParameter"] = self.parameterNameField.text()
            self.dataset["DatasetParameterCode"] = self.parameterCodeField.text()
            self.dataset["DatasetExternalID"] = self.datasetIDField.text()
            self.dataset["DatasetUnits"] = self.parameterUnitField.text()
            self.dataset["DatasetAgency"] = self.datasetAgencyField.text()

        if newID == -100:

            selection = self.sourceBox.checkedId()

            if selection == 1:
                self.dataset["DatasetDataloader"] = "IMPORTED_FILE"
                self.dataset[
                    "DatasetImportFileName"] = self.importFileName + "?" + self.dateColSelect.currentText() + "?" + self.fileDatasetSelect.currentText()

            self.dataset.name = self.datasetID
            self.returnDatasetSignal.emit(self.dataset)
            print("returning")

        return

    def nextId(self):
        """
        Function to tell the dialog window which screen to advance to
        when the user clicks next. Additionally, updates the dataset
        table row on the backend
        """

        currentID = self.currentId()

        if currentID == self.metadataID:
            nextID_ = self.dataSourceID

        # Page 2: Data Source
        elif currentID == self.dataSourceID:

            # Data Source Select Box
            selection = self.sourceBox.checkedId()

            # PyForecast Dataloader
            if selection == 0:
                nextID_ = self.dataLoaderID

            # File Import
            elif selection == 1:
                nextID_ = self.importID

            # From URL
            elif selection == 2:
                nextID_ = self.urlID

            # Composite
            elif selection == 3:
                nextID_ = self.compositeID

        elif currentID in [self.importID]:

            nextID_ = -1

        elif currentID == self.urlID:
            selection = self.URLButtonGroup.checkedId()
            if selection == 0:
                nextID_ = self.urlHTMLID

        else:
            nextID_ = -1

        return nextID_

    def loadHTMLFile(self):
        """

        """
        pd.set_option('max_colwidth', 200)
        self.HTMLtablePreview.setLineWrapMode(QtWidgets.QTextEdit.FixedPixelWidth)
        response = requests.get(self.HTMLurlEntry.text())
        if response.status_code != 200:
            self.HTMLnumTablesLabel.setText("ERROR {0}: Couldn't get page".format(response.status_code))
            return
        if "<table" not in response.text:
            self.HTMLnumTablesLabel.setText("No Tables found at this webpage...")
            return
        rawdata = pd.read_html(io.StringIO(response.text))
        if len(rawdata) == 0:
            self.HTMLnumTablesLabel.setText("No Tables found at this webpage...")
            return
        self.HTMLtablePreview.setLineWrapColumnOrWidth(50 * (rawdata[0].shape[1] + 1))
        self.HTMLnumTablesLabel.setText("{0} tables found".format(len(rawdata)))

        rawHtml = rawdata[0].to_html(justify='center', col_space=50)
        rawHtml = rawHtml.replace("<th ", '<th bgcolor="oldlace" ')
        rawHtml = rawHtml.replace("<th>", '<th bgcolor="dimgrey" style="color: white">')
        self.HTMLtablePreview.setHtml(rawHtml)

        self.HTMLdateColSelect.addItems(rawdata[0].columns)
        self.HTMLfileDatasetSelect.addItems(rawdata[0].columns)

        for col in rawdata[0].columns:
            if 'date' in col.lower() or 'time' in col.lower():
                self.HTMLdateColSelect.setCurrentText(col)

        self.HTMLfileDatasetSelect.setCurrentIndex(1 if len(rawdata[0].columns) > 0 else 0)

    def loadImportFile(self):

        self.dateColSelect.clear()
        self.fileDatasetSelect.clear()

        self.importFileName = \
        QtWidgets.QFileDialog.getOpenFileName(self, "Import Flat File", "", "Flat Files (*.csv *.xlsx *.txt)")[0]
        if self.importFileName == "":
            return

        self.fname.setText(self.importFileName)

        # if the file is an xlsx file, load it with pandas
        if '.xlsx' in self.importFileName.lower():
            rawdata = pd.read_excel(self.importFileName, nrows=500, )

        # use the CSV library to sniff out the delimiter of the file if it's a csv or txt file
        else:
            with open(self.importFileName, 'r') as readfile:
                try:
                    dialect = Sniffer().sniff(readfile.read(1024))
                except:
                    loggingAndErrors.showErrorMessage(self,
                                                      "Could not parse the file. Make sure the file is a proper flat file.")
                    return
            rawdata = pd.read_csv(self.importFileName, nrows=500, sep=dialect.delimiter, quotechar=dialect.quotechar,
                                  lineterminator=dialect.lineterminator.replace('\r', ''), skipinitialspace=True)
        pd.set_option('max_colwidth', 200)
        self.filePreviewBox.setLineWrapMode(QtWidgets.QTextEdit.FixedPixelWidth)
        self.filePreviewBox.setLineWrapColumnOrWidth(50 * (rawdata.shape[1] + 1))

        rawHtml = rawdata.to_html(justify='center', col_space=50)
        rawHtml = rawHtml.replace("<th ", '<th bgcolor="oldlace" ')
        rawHtml = rawHtml.replace("<th>", '<th bgcolor="dimgrey" style="color: white">')
        self.filePreviewBox.setHtml(rawHtml)

        self.dateColSelect.addItems(rawdata.columns)
        self.fileDatasetSelect.addItems(rawdata.columns)

        for col in rawdata.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                self.dateColSelect.setCurrentText(col)

        self.fileDatasetSelect.setCurrentIndex(1 if len(rawdata.columns) > 0 else 0)

    def setupUI(self):
        """
        Initializes the wizard GUI
        """

        # Create Pages
        self.metadataPage = QtWidgets.QWizardPage()
        self.dataSourcePage = QtWidgets.QWizardPage()
        self.dataLoaderPage = QtWidgets.QWizardPage()
        self.importPage = QtWidgets.QWizardPage()
        self.compositePage = QtWidgets.QWizardPage()
        self.urlPage = QtWidgets.QWizardPage()
        self.urlPageHTML = QtWidgets.QWizardPage()

        # Set up the metadata page's GUI
        self.metadataPage.setTitle("Step 1: Dataset Metadata")
        self.metadataPage.setSubTitle(
            "Provide general information about this dataset. Information provided here will be referenced in other areas of the software.")
        layout = QtWidgets.QFormLayout()

        self.datasetTypeField = QtWidgets.QComboBox()
        datasetTypes = list(set(self.parent.searchableDatasetsTable['DatasetType'])) + list(
            set(self.parent.additionalDatasetsTable['DatasetType'])) + ['OTHER']
        self.datasetTypeField.addItems(datasetTypes)
        self.datasetTypeField.setCurrentText("OTHER")
        self.datasetNameField = QtWidgets.QLineEdit()
        self.datasetNameField.setPlaceholderText("Enter Dataset Name here (e.g. Lower Creek Gauge)")
        self.datasetIDField = QtWidgets.QLineEdit()
        self.datasetIDField.setPlaceholderText("Enter the dataset ID (used in dataloaders)")
        self.parameterNameField = QtWidgets.QLineEdit()
        self.parameterNameField.setPlaceholderText("Enter the parameter name (e.g. Canal Flow)")
        self.parameterCodeField = QtWidgets.QLineEdit()
        self.parameterCodeField.setPlaceholderText("Enter the parameter code (used in dataloaders)")
        self.parameterUnitField = QtWidgets.QLineEdit()
        self.parameterUnitField.setPlaceholderText("Enter the units for this parameter (e.g. inches)")
        self.datasetAgencyField = QtWidgets.QLineEdit()
        self.datasetAgencyField.setPlaceholderText("E.g. USACE, USGS, NRCS, WYSEO, ...")

        layout.addRow("(required) Dataset Type", self.datasetTypeField)
        layout.addRow("(required) Dataset Name", self.datasetNameField)
        layout.addRow("(required) Parameter Name", self.parameterNameField)
        layout.addRow("(required) Parameter Unit", self.parameterUnitField)
        layout.addRow("Dataset ID", self.datasetIDField)
        layout.addRow("Parameter ID", self.parameterCodeField)
        layout.addRow("Dataset Agency", self.datasetAgencyField)

        self.metadataPage.setLayout(layout)

        # Register metadata page's required fields
        self.metadataPage.registerField("datasetName*", self.datasetNameField)
        self.metadataPage.registerField("parameterName*", self.parameterNameField)
        self.metadataPage.registerField("parameterUnit*", self.parameterUnitField)

        # Setup the dataSource Page
        self.dataSourcePage.setTitle("Step 2: Data Source")
        self.dataSourcePage.setSubTitle("Tell the software where to find the data for this dataset.")
        layout = QtWidgets.QVBoxLayout()

        self.sourceBox = QtWidgets.QButtonGroup()
        self.sourceGroupBox = QtWidgets.QGroupBox("Data Source")
        self.infoBox = QtWidgets.QLabel()
        self.infoBox.setTextFormat(QtCore.Qt.RichText)
        self.infoBox.setWordWrap(True)
        self.dataLoaderButton = QtWidgets.QRadioButton("PyForecast Dataloader")
        self.importButton = QtWidgets.QRadioButton("File Import")
        self.urlButton = QtWidgets.QRadioButton("From URL")
        self.compositeButton = QtWidgets.QRadioButton("Composite")

        self.dataLoaderInfo = "Uses an existing PyForecast dataloader to load the dataset using the options you provided in the metadata."
        self.importInfo = "Imports the dataset from a flat file (csv, xlsx), using the dataset ID from the metadata to identify the correct column."
        self.urlInfo = "Imports data from a URL endpoint, as long as that data is in machine read-able JSON or CSV format."
        self.compositeInfo = "Creates a new dataset from 2 or more existing datasets, by adding/subtracting and/or lag shifting"

        self.infoDict = {
            "0": "<strong>Information:</strong><br>" + self.dataLoaderInfo,
            "1": "<strong>Information:</strong><br>" + self.importInfo,
            "2": "<strong>Information:</strong><br>" + self.urlInfo,
            "3": "<strong>Information:</strong><br>" + self.compositeInfo
        }

        self.sourceBox.addButton(self.dataLoaderButton, 0)
        self.sourceBox.addButton(self.importButton, 1)
        self.sourceBox.addButton(self.urlButton, 2)
        self.sourceBox.addButton(self.compositeButton, 3)
        self.sourceBox.setExclusive(True)
        self.dataLoaderButton.setChecked(True)
        self.infoBox.setText(self.infoDict['0'])
        self.sourceBox.buttonClicked[int].connect(lambda id_: self.infoBox.setText(self.infoDict[str(id_)]))

        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(self.dataLoaderButton)
        layout2.addWidget(self.importButton)
        layout2.addWidget(self.urlButton)
        layout2.addWidget(self.compositeButton)
        self.sourceGroupBox.setLayout(layout2)

        layout.addWidget(self.sourceGroupBox)
        layout.addWidget(self.infoBox)

        self.dataSourcePage.setLayout(layout)

        # Set up the dataloader page
        self.dataLoaderPage.setTitle("Step 3: Choose Dataloader")
        self.dataLoaderPage.setSubTitle(
            "Select the dataloader used to load this dataset. Make sure that the required metadata fields are filled in.")

        layout = QtWidgets.QVBoxLayout()
        self.dataLoaderSelect = QtWidgets.QComboBox()
        self.infoBoxDloader = QtWidgets.QTextEdit()
        self.infoBoxDloader.setReadOnly(True)
        self.dataLoaderSelect.addItems(self.dloaderNames)
        self.infoBoxDloader.setHtml(self.dloaders[0].dataLoaderInfo()[1].replace("\n", "<br>"))

        layout2 = QtWidgets.QFormLayout()
        layout2.addRow("Dataloader selection", self.dataLoaderSelect)
        layout.addLayout(layout2)
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText("<strong>Dataloader Information</strong>")
        layout.addWidget(label)
        layout.addWidget(self.infoBoxDloader)

        self.dataLoaderSelect.currentTextChanged.connect(lambda dloader: self.infoBoxDloader.setHtml(
            self.dloaders[self.dloaderNames.index(dloader)].dataLoaderInfo()[1].replace("\n", "<br>")))

        self.dataLoaderPage.setLayout(layout)

        # layout the import page
        self.importPage.setTitle("Step 3: Set Filename")
        self.importPage.setSubTitle(
            "Browse for the flat file (csv, xlsx) that you want to import and verify the data looks correct.")

        layout = QtWidgets.QVBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel("Filename:")
        label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.fname = QtWidgets.QLabel("No File Selected...")
        self.fname.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.fileButton = QtWidgets.QPushButton("Browse")
        self.fileButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        layout2.addWidget(label)
        layout2.addWidget(self.fname)
        layout2.addSpacerItem(
            QtWidgets.QSpacerItem(1000, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        layout2.addWidget(self.fileButton)

        layout.addLayout(layout2)
        label = QtWidgets.QLabel("<strong>File Preview</strong>")
        label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(label)

        self.filePreviewBox = QtWidgets.QTextEdit()
        self.filePreviewBox.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.filePreviewBox.setReadOnly(True)
        self.filePreviewBox.setHtml("No file selected...")
        layout.addWidget(self.filePreviewBox)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addSpacerItem(
            QtWidgets.QSpacerItem(1000, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        layout2.addWidget(QtWidgets.QLabel("Which column contains the datetime?"))
        self.dateColSelect = QtWidgets.QComboBox()
        self.dateColSelect.setFixedWidth(240)
        layout2.addWidget(self.dateColSelect)
        layout.addLayout(layout2)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addSpacerItem(
            QtWidgets.QSpacerItem(1000, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        layout2.addWidget(QtWidgets.QLabel("Which column contains the dataset?"))
        self.fileDatasetSelect = QtWidgets.QComboBox()
        self.fileDatasetSelect.setFixedWidth(240)
        layout2.addWidget(self.fileDatasetSelect)

        layout.addLayout(layout2)

        self.importPage.setLayout(layout)

        # Lay out the Composite Dataset page
        self.compositePage.setTitle("Step 3: Create Composite Dataset")
        self.compositePage.setSubTitle("Create a linear combination of up to 10 datasets.")

        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("")
        label.setTextFormat(QtCore.Qt.RichText)
        label.setWordWrap(True)

        label.setText("""
        <strong>Information</strong><br>
        Use the table below to specify which datasets to combine. The <img src="resources/GraphicalResources/icons/plusIcon.png" width="10" height="10"/> button 
        adds a new dataset to the list and the <img src="resources/GraphicalResources/icons/xIcon.png" width="10" height="10"/> button removes the dataset.
        The datasets are combined linearly using the provided coefficients, and individual datasets can be lag-shifted.
        """)
        layout.addWidget(label)
        self.combineDatasetTable = CombinedDatasetTbl(self.parent)
        layout.addWidget(self.combineDatasetTable)

        self.compositePage.setLayout(layout)

        # Lay out the URL Page 1
        self.urlPage.setTitle("Step 3: Specify URL options")
        self.urlPage.setSubTitle("What is the format of the data enpoint that we'll be retrieving?")

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        self.HTMLTableButton = QtWidgets.QRadioButton("HTML Tables")
        self.csvTableButton = QtWidgets.QRadioButton("Raw CSV")
        self.jsonButton = QtWidgets.QRadioButton("Raw JSON")
        self.URLButtonGroup = QtWidgets.QButtonGroup()
        self.URLButtonGroup.setExclusive(True)
        self.URLButtonGroup.addButton(self.HTMLTableButton, 0)
        self.HTMLTableButton.setChecked(True)
        self.URLButtonGroup.addButton(self.csvTableButton, 1)
        self.URLButtonGroup.addButton(self.jsonButton, 2)
        self.URLbox = QtWidgets.QGroupBox("URL Format Option")
        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(self.HTMLTableButton)
        layout2.addWidget(self.csvTableButton)
        layout2.addWidget(self.jsonButton)
        self.URLbox.setLayout(layout2)
        layout.addWidget(self.URLbox)

        self.URLInfoBox = QtWidgets.QLabel()
        self.URLInfoBox.setTextFormat(QtCore.Qt.RichText)
        self.URLInfoBox.setWordWrap(True)
        self.URLInfoBox.setText(
            "<strong>Information</strong><br>Check this box if the data you want to import resides in a HTML table somewhere at the URL you plan to specify.")
        self.URLInfoPic = QtWidgets.QLabel()
        self.URLInfoPic.setPixmap(QtGui.QPixmap("resources/GraphicalResources/HTML_import_pic.png"))

        def updateURLInfo(id_):
            if id_ == 0:
                info = "<strong>Information</strong><br>Check this box if the data you want to import resides in a HTML table somewhere at the URL you plan to specify."
                pic = QtGui.QPixmap("resources/GraphicalResources/HTML_import_pic.png")
            elif id_ == 1:
                info = "<strong>Information</strong><br>Check this box if the data you want to import is raw CSV located at the URL."
                pic = QtGui.QPixmap("resources/GraphicalResources/CSV_import_pic.png")
            elif id_ == 2:
                info = "<strong>Information</strong><br>Check this box if the data you want to import is raw JSON located at the URL."
                pic = QtGui.QPixmap("resources/GraphicalResources/JSON_import_pic.png")
            else:
                return
            self.URLInfoBox.setText(info)
            self.URLInfoPic.setPixmap(pic)

        self.URLButtonGroup.buttonClicked[int].connect(lambda id_: updateURLInfo(id_))
        layout.addWidget(self.URLInfoBox)
        layout.addWidget(self.URLInfoPic)

        self.urlPage.setLayout(layout)

        # Setup the extended URL options page
        self.urlPageHTML.setTitle("Step 4: Find HTML Table")
        self.urlPageHTML.setSubTitle(
            "Locate the HTML Table and specify the where the dataset of interest is in that table.")
        layout = QtWidgets.QVBoxLayout()

        self.HTMLurlEntry = QtWidgets.QLineEdit()
        self.HTMLurlEntry.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.HTMLurlEntry.setPlaceholderText("Enter the URL here: (e.g. https://www.ncdc.noaa.gov/teleconnections/pna")
        self.HTMLloadUrlButton = QtWidgets.QPushButton("Load")
        self.HTMLnumTablesLabel = QtWidgets.QLabel("Enter a URL and press 'Load' to find tables.")
        self.HTMLtableSelect = QtWidgets.QComboBox()
        self.HTMLtablePreview = QtWidgets.QTextEdit()
        self.HTMLtablePreview.setHtml("No tables found")
        self.HTMLtablePreview.setReadOnly(True)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(QtWidgets.QLabel("URL:"))
        layout2.addWidget(self.HTMLurlEntry)
        layout2.addWidget(self.HTMLloadUrlButton)
        layout.addLayout(layout2)
        layout.addWidget(self.HTMLnumTablesLabel)
        layout.addWidget(self.HTMLtablePreview)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addSpacerItem(
            QtWidgets.QSpacerItem(1000, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        layout2.addWidget(QtWidgets.QLabel("Which column contains the datetime?"))
        self.HTMLdateColSelect = QtWidgets.QComboBox()
        self.HTMLdateColSelect.setFixedWidth(240)
        layout2.addWidget(self.HTMLdateColSelect)
        layout.addLayout(layout2)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addSpacerItem(
            QtWidgets.QSpacerItem(1000, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        layout2.addWidget(QtWidgets.QLabel("Which column contains the dataset?"))
        self.HTMLfileDatasetSelect = QtWidgets.QComboBox()
        self.HTMLfileDatasetSelect.setFixedWidth(240)
        layout2.addWidget(self.HTMLfileDatasetSelect)

        layout.addLayout(layout2)
        self.urlPageHTML.setLayout(layout)

        # Add pages to the wizard
        self.metadataID = self.addPage(self.metadataPage)
        self.dataSourceID = self.addPage(self.dataSourcePage)
        self.dataLoaderID = self.addPage(self.dataLoaderPage)
        self.importID = self.addPage(self.importPage)
        self.urlID = self.addPage(self.urlPage)
        self.compositeID = self.addPage(self.compositePage)
        self.urlHTMLID = self.addPage(self.urlPageHTML)

        #

        return

    def returnDataset(self):
        """
        This is going to be a logic nightmare!
        """

        return


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mw = DatasetWizard()
    mw.show()
    sys.exit(app.exec_())