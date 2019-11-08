from PyQt5 import QtWidgets, QtCore, QtGui
import pandas as pd

class datasetEditorWindow(QtWidgets.QDialog):
    """
    This widget is the primary dataset editor window. It contains the 
    dataset's metadata as well as the dataset source information and any
    dataset computations.
    """

    def __init__(self, datasetTable, datasetInternalID = None):
        """
        Initialization function for the class. Set up the class GUI and 
        load the datasetTable. Optionally, initialize the editor to a 
        user-inputted datasetInternalID
        """

        self.datasetTable = datasetTable    # Create a refererence to the datasetTable
        
        self.loadDialogGUI()                # Load the dialog GUI

        self.selectDataset(datasetInternalID)

        self.dataChanged = False            # Initalize a variable to keep track of whether there are unsaved changes

        # Connect exit button to a dialog that reads ('you are about to exit without saving changes', continue?)

        # Connect Save button to the exit/save process

        return

    def checkSavedChangesBeforeSwitchingDatasets(self, selection):
        """
        Checks the current dataset to see if there are any changes that need to be saved. 
        If there are unsaved changes, prompt the user and resolve the changes before 
        proceeding. Then proceeds to change the selected dataset.
        """
        
        if self.dataChanged:
            # Create Message here and 

        return 

    def selectDataset(self, datasetID):
        """
        Sets the selected dataset in the dialog
        """

        return


    def loadDialogGUI(self):
        """
        Loads the GUI elements to the Dialog Window
        """

        # Layouts
        layout = QtWidgets.QHBoxLayout()
        formLayout = QtWidgets.QFormLayout()

        # Left Hand Sider Dataset Browser
        self.dataBrowser = 0#

        # Form fields
        self.form = QtWidgets.QWidget()
        self.DatasetTypeField =             QtWidgets.QLineEdit()
        self.DatasetExternalIDField =       QtWidgets.QLineEdit()
        self.DatasetNameField =             QtWidgets.QLineEdit()
        self.DatasetAgencyField =           QtWidgets.QLineEdit()
        self.DatsetParameterField =         QtWidgets.QLineEdit()
        self.DatasetUnitsField =            QtWidgets.QLineEdit()
        self.DefaultResamplingField =       QtWidgets.QLineEdit()
        self.DatasetDataLoaderField =       QtWidgets.QComboBox()
        self.DatasetHUC8Field =             QtWidgets.QLineEdit()
        self.DatasetLatitudeField =         QtWidgets.QLineEdit()
        self.DatasetLongitudeField =        QtWidgets.QLineEdit()
        self.DatasetElevationField =        QtWidgets.QLineEdit()
        self.DatasetPORFieldStart =         QtWidgets.QDateEdit()
        self.DatasetPORFieldEnd =           QtWidgets.QDateEdit()
        self.DatasetCompositeField =        QtWidgets.QLineEdit()
        self.DatasetImportFileField =       QtWidgets.QLineEdit()
        self.DatasetAddOptionsField =       QtWidgets.QTableWidget()

        # ToolTips
        
        

        # Labels
        DatasetTypeLabel =                  QtWidgets.QLabel("Dataset Type")
        DatasetExternalIDLabel =            QtWidgets.QLabel("Dataset External ID")
        DatasetNameLabel =                  QtWidgets.QLabel("Dataset Name")
        DatasetAgencyLabel =                QtWidgets.QLabel("Dataset Agency")
        DatasetParameterLabel =             QtWidgets.QLabel("Dataset Parameter")
        DatasetUnitsLabel =                 QtWidgets.QLabel("Dataset Units")
        DatasetResamplingLabel =            QtWidgets.QLabel("Dataset Resampling")
        DatasetDataLoaderLabel =            QtWidgets.QLabel("Dataset Dataloader")
        DatasetHUC8Label =                  QtWidgets.QLabel("Dataset HUC8")
        DatasetLatitudeLabel =              QtWidgets.QLabel("Dataset Latitude")
        DatasetLongitudeLabel =             QtWidgets.QLabel("Dataset Longitude")
        DatasetElevationLabel =             QtWidgets.QLabel("Dataset Elevation")
        DatasetPORStartLabel =              QtWidgets.QLabel("Dataset POR Start")
        DatasetPOREndLabel =                QtWidgets.QLabel("Dataset POR End")
        DatasetCompositeLabel =             QtWidgets.QLabel("Dataset Composite Equation")
        DatasetImportFileLabel =            QtWidgets.QLabel("Dataset original file (import)")
        DatasetAddOptionsLabel =            QtWidgets.QLabel("Dataset Additional Parameters")

        # Validators
        HUCValidator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{8}"), self.DatasetHUC8Field) # Matches 8 digit numbers like 01032241
        LatitudeValidator = QtGui.QDoubleValidator(-180,180,30,self.DatasetLatitudeField)
        LongitudeValidator = QtGui.QDoubleValidator(-180,180,30,self.DatasetLongitudeField)
        ElevationValidator = QtGui.QDoubleValidator(-100,100000,30,self.DatasetElevationField)
        CompositeValidator = QtGui.QRegExpValidator(QtCore.QRegExp("C/([0-9]{6},?)+/([0-9]+\.[0-9]+,?)+/([0-9]+,?)+"))
        
        # Drop-down combo boxes
        map(self.DatasetDataLoaderField.addItem, [file.split('.p')[0] for file in os.listdir('../../DataLoaders') if os.path.isfile(file)])

        
        # Add items to layout
        layout.addWidget(self.dataBrowser)
        formLayout.addRow(DatasetTypeLabel,         self.DatasetTypeField)
        formLayout.addRow(DatasetExternalIDLabel,   self.DatasetExternalIDField)
        formLayout.addRow(DatasetNameLabel,         self.DatasetNameField)
        formLayout.addRow(DatasetAgencyLabel,       self.DatasetAgencyField)
        formLayout.addRow(DatasetUnitsLabel,        self.DatasetUnitsField)
        formLayout.addRow(DatasetResamplingLabel,   self.DefaultResamplingField)
        formLayout.addRow(DatasetDataLoaderLabel,   self.DatasetDataLoaderField)
        formLayout.addRow(DatasetHUC8Label,         self.DatasetHUC8Field)
        formLayout.addRow(DatasetLatitudeLabel,     self.DatasetLatitudeField)
        formLayout.addRow(DatasetLongitudeLabel,    self.DatasetLongitudeField)
        formLayout.addRow(DatasetElevationLabel,    self.DatasetElevationField)
        formLayout.addRow(DatasetPORStartLabel,     self.DatasetPORFieldStart)
        formLayout.addRow(DatasetPOREndLabel,       self.DatasetPORFieldEnd)
        formLayout.addRow(DatasetCompositeLabel,    self.DatasetCompositeField)
        formLayout.addRow(DatasetImportFileLabel,   self.DatasetImportFileField)
        formLayout.addRow(DatasetAddOptionsLabel,   self.DatasetAddOptionsField)




        return
    
    

