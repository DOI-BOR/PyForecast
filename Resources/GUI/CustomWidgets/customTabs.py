
"""
Script Name:    CustomTabs.py
Descriptoin:    This script contains a custom tab widget
                that emulates the look and feel of modern 
                software tabs (e.g. visual studio, microsoft teams, etc)
"""

from PyQt5 import QtCore, QtWidgets, QtGui
import os
import sys
sys.path.append(os.getcwd())
from resources.GUI.CustomWidgets.SVGIcon import SVGIcon

ICON_ORIENTATION = {
    "above":QtWidgets.QBoxLayout.TopToBottom,
    "left":QtWidgets.QBoxLayout.LeftToRight,
    "right":QtWidgets.QBoxLayout.RightToLeft,
    "below":QtWidgets.QBoxLayout.BottomToTop
}

STYLE = """
QWidget#TabLabel {
    padding: 0px;
    margin: 0px;
    color: #b6b6b6;
    border: 0px solid darkblue;
    border-color: darkblue;
}
QLabel#LabelText {
    padding: 0px;
    border-width: 0px;
    font-size: 9px;
    color: #b6b6b6;
}
QLabel#LabelIcon {
    padding: 0px;
    border-width: 0px;
    color: #b6b6b6;
}
QWidget#EnhancedTabWidget {
    background: darkblue;
}

"""

class HoverWidget(QtWidgets.QWidget):
    """
    Subclassed widget to create the actual tab headers.
    """
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent = None, objectName = None, orientation = None):
        QtWidgets.QWidget.__init__(self, objectName = objectName)
        self.parent = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.selected = False        

        return

    def mousePressEvent(self, event):
        if event != "":
            QtWidgets.QWidget.mousePressEvent(self, event)
        self.clicked.emit()
        self.selected = True
        self.setStyleSheet(
            """
            QWidget {
                border-color: #FFFFFF;
                background: #007396
            }
            QLabel {
                color: white;
            }
            """)
    
    def deselectEvent(self):
        self.selected = False
        if self.parent.tint:
            self.setStyleSheet(
                """
                QWidget {
                    background: #002b39;
                    border-color: #002b39;
                }
                QWidget QLabel{
                    color: #b6b6b6;
                }
                """
                )
        else:
            self.setStyleSheet(
                """
                QWidget {
                    background: #003E51;
                    border-color: #003E51;
                }
                QWidget QLabel{
                    color: #b6b6b6;
                }
                """
                )
    def enterEvent(self, event):
        if not self.selected:
            self.setStyleSheet(
                """
                QWidget {
                    background: #004f66;
                    border-color: #004f66;
                }
                QWidget QLabel{
                    color: white;
                    
                }
                """
                )

    def leaveEvent(self, event):
        if not self.selected:
            if self.parent.tint:
                self.setStyleSheet(
                    """
                    QWidget {
                        background: #002b39;
                        border-color: #002b39;
                    }
                    QWidget QLabel{
                        color: #b6b6b6;
                    }
                    """
                    )
            else:
                self.setStyleSheet(
                    """
                    QWidget {
                        background: #003E51;
                        border-color: #003E51;
                    }
                    QWidget QLabel{
                        color: #b6b6b6;
                    }
                    """
                    )


class EnhancedTabWidget(QtWidgets.QWidget):
    """
    """
    currentChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent = None, iconPosition = None, orientation = None, stretch = None, eastTab = None, tint = None):
        """
        Initialize the Enhanced Tab Widget. The initialization options are

        iconPosition => can be one of ["above", "left", "right", "below"]
                        Describes where the icon sits in relation to the HTML text
        oreintation  => can be on of ['horizontal', 'vertical']
                        Describes whether the tab bar goes from left to right 
                        or top to bottom
        stretch      => can be [True, False]
                        Describes whether to stretch the tab bar to cover the 
                        entire parent widget
        eastTab      => Can be [True, False]
                        specifies whether the vertical tab bar is 
                        on the right (true) or left (false) of the 
                        stackwidget.
        tint         => can be [True, False]
                        Causes the background colors to be tinted by 10%
        """

        

        # Parse the arguments
        self.parent = parent
        self.iconPosition = 'above' if iconPosition == None else iconPosition
        self.orientation = 'horizontal' if orientation == None else orientation
        self.stretch = False if stretch == None else stretch
        self.eastTab = False if eastTab == None else eastTab
        self.tint = False if tint == None else tint

        # Create an overall widget
        objectName_ = "EnhancedTabWidget" if not self.tint else "EnhancedTabWidget_tint"
        QtWidgets.QWidget.__init__(self, objectName=objectName_)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        # Configure the widget
        self.iconOrientation = ICON_ORIENTATION[self.iconPosition]
        if self.orientation == 'horizontal':
            self.overallLayout = QtWidgets.QVBoxLayout()
            self.tabLayout = QtWidgets.QHBoxLayout()

            self.setStyleSheet("""
                QWidget#TabLabel {
                    border-top-width: 3px;
                    border-bottom-width: 0px;
                    border-left-width: 0px;
                    border-right-width: 0px;
                }
                """
            )
            
            if not self.stretch:
                self.labelSizePolicyH = QtWidgets.QSizePolicy.Fixed
                self.labelSizePolicyV = QtWidgets.QSizePolicy.Minimum
                self.spacerItem = QtWidgets.QSpacerItem(10,10,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            
            else:
                self.labelSizePolicyH = QtWidgets.QSizePolicy.Minimum
                self.labelSizePolicyV = QtWidgets.QSizePolicy.Minimum

        elif self.orientation == 'vertical':
            self.overallLayout = QtWidgets.QHBoxLayout()
            self.tabLayout = QtWidgets.QVBoxLayout()
            if not self.eastTab:
                self.setStyleSheet("""
                    QWidget#TabLabel {
                        border-left-width: 3px;
                        border-bottom-width: 0px;
                        border-top-width: 0px;
                        border-right-width: 0px;
                    }
                    """
                )
            else:
                self.setStyleSheet("""
                    QWidget#TabLabel {
                        border-right-width: 3px;
                        border-bottom-width: 0px;
                        border-top-width: 0px;
                        border-left-width: 0px;
                    }
                    """
                )
            
            if not self.stretch:
                self.labelSizePolicyH = QtWidgets.QSizePolicy.Minimum
                self.labelSizePolicyV = QtWidgets.QSizePolicy.Fixed
                self.spacerItem = QtWidgets.QSpacerItem(10,10,QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            else:
                self.labelSizePolicyH = QtWidgets.QSizePolicy.Minimum
                self.labelSizePolicyV = QtWidgets.QSizePolicy.Minimum
        else:
            raise ValueError("Error: orientation must be 'horizontal' or 'vertical'.")
        
        
        # Store information about the widget
        self.numberOfTabs = 0
        self.currentIndex = 0
        self.TabList = []

        # Create a stackedWidget
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setContentsMargins(0,0,0,0)

        # Layout the overall Widget
        self.setContentsMargins(0,0,0,0)
        self.overallLayout.setContentsMargins(0,0,0,0)
        self.overallLayout.setSpacing(0)
        self.tabLayout.setContentsMargins(0,0,0,0)
        self.tabLayout.setSpacing(0)
        if not self.eastTab:
            self.overallLayout.addLayout(self.tabLayout)
            self.overallLayout.addWidget(self.stackedWidget)
        else:
            self.overallLayout.addWidget(self.stackedWidget)
            self.overallLayout.addLayout(self.tabLayout)
        self.setLayout(self.overallLayout)
        
        

    def switchTabs(self, idx):
        """
        switches to the tab at index idx
        """
        self.stackedWidget.setCurrentIndex(idx)
        self.currentIndex = idx
        for tab in self.TabList:
            tab.deselectEvent()

        # Emit a changed event to allow tab intercommunication
        self.currentChanged.emit(idx)
        return



    def addTab(self, widget, htmlText = None, icon = None, iconColor = None, color = None, iconSize = (None, None)):
        """
        """

        # Add the widget to the stacked widget
        self.stackedWidget.addWidget(widget)

        if not self.stretch:
            self.tabLayout.takeAt(self.numberOfTabs)

        # Create a new label for the tab bar
        icon = SVGIcon(icon, iconColor, 0, iconSize)
        iconLabel = QtWidgets.QLabel(objectName="LabelIcon")
        iconLabel.setPixmap(icon.pixmap)
        iconLabel.setContentsMargins(0,0,0,0)
        iconLabel.setAlignment(QtCore.Qt.AlignCenter)

        label = QtWidgets.QLabel(htmlText, objectName="LabelText")
        label.setContentsMargins(0,0,0,0)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setAlignment(QtCore.Qt.AlignCenter)

        widg = HoverWidget(self, objectName="TabLabel", orientation = self.orientation)
        widg.setContentsMargins(10,10,10,10)
        widg.setSizePolicy(self.labelSizePolicyH, self.labelSizePolicyV)
        layout = QtWidgets.QBoxLayout(self.iconOrientation)
        layout.setContentsMargins(0,0,0,0)

        if self.stretch and self.orientation == 'vertical':
            
            iconLabel.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
            label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
            layout.addWidget(iconLabel, QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
            layout.addWidget(label, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        else:
            layout.addWidget(iconLabel, QtCore.Qt.AlignCenter)
            layout.addWidget(label, QtCore.Qt.AlignCenter)

        

        widg.setLayout(layout)
        widg.tabNumber = self.numberOfTabs
        widg.clicked.connect(lambda: self.switchTabs(widg.tabNumber))
        self.TabList.append(widg)
        widg.leaveEvent("")
        if widg.tabNumber == 0:
            widg.mousePressEvent("")



        self.tabLayout.addWidget(widg, QtCore.Qt.AlignCenter)
        if not self.stretch:
            self.tabLayout.addSpacerItem(self.spacerItem)

        self.numberOfTabs += 1
        

        return
    
    def addTabBottom(self, widget, htmlText = None, icon = None, iconColor = None, color = None, iconSize = (None, None)):
        """
        Adds a tab to the bottom or right of the tab bar
        """

        if self.stretch:
            raise ValueError("Cannot add bottom tab in stretched EnhancedTabWidget")

        # Add the widget to the stacked widget
        self.stackedWidget.addWidget(widget)

        # Create a new label for the tab bar
        icon = SVGIcon(icon, iconColor, 0, iconSize)
        iconLabel = QtWidgets.QLabel(objectName="LabelIcon")
        iconLabel.setPixmap(icon.pixmap)
        iconLabel.setContentsMargins(0,0,0,0)
        iconLabel.setAlignment(QtCore.Qt.AlignCenter)

        label = QtWidgets.QLabel(htmlText, objectName="LabelText")
        label.setContentsMargins(0,0,0,0)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setAlignment(QtCore.Qt.AlignCenter)

        widg = HoverWidget(self, objectName="TabLabel", orientation = self.orientation)
        widg.setContentsMargins(10,10,10,10)
        widg.setSizePolicy(self.labelSizePolicyH, self.labelSizePolicyV)
        layout = QtWidgets.QBoxLayout(self.iconOrientation)
        layout.setContentsMargins(0,0,0,0)


        
        layout.addWidget(iconLabel, QtCore.Qt.AlignCenter)
        layout.addWidget(label, QtCore.Qt.AlignCenter)

        
        widg.setLayout(layout)
        widg.tabNumber = self.numberOfTabs
        widg.clicked.connect(lambda: self.switchTabs(widg.tabNumber))
        self.TabList.append(widg)
        widg.leaveEvent("")
        if widg.tabNumber == 0:
            widg.mousePressEvent("")

        self.tabLayout.addWidget(widg, QtCore.Qt.AlignCenter)

        self.numberOfTabs += 1
        

        return
    

        





    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    mw = EnhancedTabWidget(app, orientation='horizontal', iconPosition='above', stretch=True)
    widg1 = QtWidgets.QTableWidget()
    widg2 = QtWidgets.QWidget()
    widg3 = QtWidgets.QWidget()
    widg3.setAttribute(QtCore.Qt.WA_StyledBackground, True)
    widg3.setStyleSheet("""QWidget {background-color: red}""")
    mw.addTab(widg1, '<p style="font-weight: bold;font-size: 16px; padding:0; margin:0; margin-bottom: 3px">Specify</p>FORECAST<br>TARGET', "resources/graphicalResources/icons/target-24px.svg", iconColor="#FFFFFF")
    mw.addTab(widg2, '<p style="font-weight: bold;font-size: 16px; padding:0; margin:0; margin-bottom: 3px">Choose</p>PREDICTORS', "resources/graphicalResources/icons/border_all-24px.svg", iconColor="#FFFFFF")
    mw.addTab(widg3, '<p style="font-weight: bold;font-size: 16px; padding:0; margin:0; margin-bottom: 3px">Set</p>OPTIONS', "resources/graphicalResources/icons/tune-24px.svg", iconColor="#FFFFFF")

    mw.show()
    sys.exit(app.exec_())
    print("")