"""
Script Name:        DatasetsTab.py

Description:        'DatasetsTab.py' is a PyQt5 GUI for the NextFlow application. 
                    The GUI includes all the visual aspects of the Datasets Tab (menus,
                    plots, tables, buttons, webmaps, etc.) as well as the functionality
                    to add data to the plots, tables, and webmaps.
"""

from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui
from    resources.GUI.CustomWidgets     import  DatasetBoxView
from    resources.GUI.WebMap    import  webMapView
import  sys
import  os

class DatasetTab(QtWidgets.QWidget):
    """
    This subclass of QWidget describes the layout of the NextFlow
    applicaiton's Datasets Tab. For the functionality of the Datasets Tab, 
    see the 'DatasetTab' section of 'application.py'
    """
    def __init__(self, parent = None):
        self.infoIcon = QtGui.QPixmap(os.path.abspath('resources/GraphicalResources/icons/infoHover.png')).scaled(30,30, QtCore.Qt.KeepAspectRatio)
        """
        Initialization function for the DatasetTab class. Physically
        lays out the DatasetTab widget.

        Keyword Arguments:
        parent -- The parent widget of this tab. Not used.
        """
        QtWidgets.QWidget.__init__(self)

        # Layout Elements
        layout = QtWidgets.QVBoxLayout()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        tabPane = QtWidgets.QTabWidget()
        tabPane.setTabPosition(QtWidgets.QTabWidget.East)

        # Left hand side web view
        self.webMapView = webMapView.webMapView()
        splitter.addWidget(self.webMapView)

        # Right hand side tab pane - DatasetListTab
        DatasetListTab = QtWidgets.QWidget()
        layout_ = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('<b style="font-size: 20px">Selected Datasets</b>')
        label.setTextFormat(QtCore.Qt.RichText)
        self.selectedDatasetsLabel = QtWidgets.QLabel("0 datasets have been selected:")
        self.selectedDatasetsWidget = DatasetBoxView.DatasetBoxView()
        self.selectedDatasetsWidget.setContextMenu(options=['remove', 'edit'])
        layout_.addWidget(label)
        layout_.addWidget(self.selectedDatasetsLabel)
        layout_.addWidget(self.selectedDatasetsWidget)
        DatasetListTab.setLayout(layout_)
        icon = QtGui.QPixmap(os.path.abspath("resources/graphicalResources/icons/datasetListTab.png"))
        matrix_ = QtGui.QTransform()
        matrix_.rotate(270)
        icon = QtGui.QIcon(icon.transformed(matrix_))
        tabPane.addTab(DatasetListTab, icon, "")
        tabPane.setTabToolTip(0, "Selected Dataset List")

        # Right hand side tab pane - SearchTab
        SearchTab = QtWidgets.QWidget()
        layout_ = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('<b style="font-size: 20px">Search Datasets</b>')
        label.setTextFormat(QtCore.Qt.RichText)
        keywordLabel = QtWidgets.QLabel("Search for Keyword:")
        self.keywordSearchBox = QtWidgets.QLineEdit()
        self.keywordSearchBox.setPlaceholderText("e.g. Alpine Meadow")
        self.keywordSearchButton = QtWidgets.QPushButton("Search")
        self.searchResultsBox = DatasetBoxView.DatasetBoxView(searchBoxView=True)
        layout_.addWidget(label)
        layout_.addWidget(keywordLabel)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.keywordSearchBox)
        layout2.addWidget(self.keywordSearchButton)
        layout_.addLayout(layout2)
        layout_.addWidget(self.searchResultsBox)
        SearchTab.setLayout(layout_)
        icon = QtGui.QPixmap(os.path.abspath("resources/graphicalResources/icons/searchTab.png"))
        matrix_ = QtGui.QTransform()
        matrix_.rotate(270)
        icon = QtGui.QIcon(icon.transformed(matrix_))
        tabPane.addTab(SearchTab, icon, "")
        tabPane.setTabToolTip(1, "Dataset Search")

        # Right hand side tab pane - box/huc search
        boxHucSearchTab = QtWidgets.QWidget()
        layout_ = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('<b style="font-size: 20px">Browse Map</b><p>Search for stations within watersheds or a bounding box</p>')
        label.setTextFormat(QtCore.Qt.RichText)
        layout_.addWidget(label)
        self.boundingBoxButton = QtWidgets.QPushButton("Draw Bounding Box")
        self.hucSelectionButton = QtWidgets.QPushButton("Select Watersheds")
        self.boxHucSearchButton = QtWidgets.QPushButton("Search Selected Areas")
        self.boxHucSearchButton.setEnabled(False)
        self.boxHucResultsBox = DatasetBoxView.DatasetBoxView(searchBoxView=True)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.boundingBoxButton)
        layout2.addWidget(self.hucSelectionButton)
        layout_.addLayout(layout2)
        layout_.addWidget(self.boxHucSearchButton)
        layout_.addWidget(self.boxHucResultsBox)
        boxHucSearchTab.setLayout(layout_)
        icon = QtGui.QPixmap(os.path.abspath("resources/graphicalResources/icons/hucBoxTab.png"))
        matrix_ = QtGui.QTransform()
        matrix_.rotate(270)
        icon = QtGui.QIcon(icon.transformed(matrix_))
        tabPane.addTab(boxHucSearchTab, icon, "")
        tabPane.setTabToolTip(1, "Area Search")


        # Right hand side tab pane - AdditionalDatasetTab
        AdditionalDatasetTab = QtWidgets.QWidget()
        layout_ = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('<b style="font-size: 20px">Additional Datasets</b>')
        label.setTextFormat(QtCore.Qt.RichText)
        prismLabel = QtWidgets.QLabel("PRISM Temperature/Precipitation")
        prismInfo = QtWidgets.QLabel()
        prismInfo.setPixmap(self.infoIcon)
        prismInfo.setToolTip("Returns watershed averaged temperature and precipitation data from the PRISM dataset")
        self.prismInput = QtWidgets.QLineEdit()
        self.prismInput.setPlaceholderText("Enter HUC8:")
        self.prismButton = QtWidgets.QPushButton("Add")
        self.prismButton.setFixedWidth(100)

        nrccLabel = QtWidgets.QLabel("NRCC Temperature/Precipitation")
        nrccInfo = QtWidgets.QLabel()
        nrccInfo.setPixmap(self.infoIcon)
        nrccInfo.setToolTip("Returns watershed averaged temperature and precipitation data from the NRCC dataset")
        self.nrccInput = QtWidgets.QLineEdit()
        self.nrccInput.setPlaceholderText("Enter HUC8:")
        self.nrccButton = QtWidgets.QPushButton("Add")
        self.nrccButton.setFixedWidth(100)

        pdsiLabel = QtWidgets.QLabel("Palmer Drought Severity Index")
        pdsiInfo = QtWidgets.QLabel()
        pdsiInfo.setPixmap(self.infoIcon)
        pdsiInfo.setToolTip("Returns climate-division averaged Palmer Drought Severity Index data from the CPC.")
        self.pdsiInput = QtWidgets.QComboBox()
        self.pdsiButton = QtWidgets.QPushButton("Add")
        self.pdsiButton.setFixedWidth(100)

        climLabel = QtWidgets.QLabel("Climate Indices")
        climInfo = QtWidgets.QLabel()
        climInfo.setPixmap(self.infoIcon)
        climInfo.setToolTip("Returns various climate indices data from the CPC.")
        self.climInput = QtWidgets.QComboBox()
        self.climButton = QtWidgets.QPushButton("Add")
        self.climButton.setFixedWidth(100)

        addiLabel = QtWidgets.QLabel("User Defined Dataset")
        addiInfo = QtWidgets.QLabel()
        addiInfo.setPixmap(self.infoIcon)
        addiInfo.setToolTip("")
        self.addiButton = QtWidgets.QPushButton("Add Dataset")
        self.addiButton.setFixedWidth(100)
        
        blank = QtWidgets.QLabel()
        blank.setMinimumHeight(10000)
        layout_.addWidget(label)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(prismInfo)
        layout2.addWidget(prismLabel)
        layout2.addSpacerItem(QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        layout_.addLayout(layout2)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.prismInput)
        layout2.addWidget(self.prismButton)
        layout_.addLayout(layout2)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(nrccInfo)
        layout2.addWidget(nrccLabel)
        layout2.addSpacerItem(QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        layout_.addLayout(layout2)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.nrccInput)
        layout2.addWidget(self.nrccButton)
        layout_.addLayout(layout2)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(pdsiInfo)
        layout2.addWidget(pdsiLabel)
        layout2.addSpacerItem(QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        layout_.addLayout(layout2)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.pdsiInput)
        layout2.addWidget(self.pdsiButton)
        layout_.addLayout(layout2)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(climInfo)
        layout2.addWidget(climLabel)
        layout2.addSpacerItem(QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        layout_.addLayout(layout2)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.climInput)
        layout2.addWidget(self.climButton)
        layout_.addLayout(layout2)

        layout_.addSpacerItem(QtWidgets.QSpacerItem(40, 1000, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(addiInfo)
        layout2.addWidget(addiLabel)
        layout2.addSpacerItem(QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        layout2.addWidget(self.addiButton)
        layout_.addLayout(layout2)

        #layout_.addWidget(blank)
        AdditionalDatasetTab.setLayout(layout_)
        icon = QtGui.QPixmap(os.path.abspath("resources/graphicalResources/icons/additionalTab.png"))
        matrix_ = QtGui.QTransform()
        matrix_.rotate(270)
        icon = QtGui.QIcon(icon.transformed(matrix_))
        tabPane.addTab(AdditionalDatasetTab, icon, "")
        tabPane.setTabToolTip(2, "Additional Datasets")

        self.webMapView.sizePolicy().setHorizontalStretch(4)
        tabPane.sizePolicy().setHorizontalStretch(0)
        splitter.addWidget(tabPane)
        layout.addWidget(splitter)
        self.setLayout(layout)
