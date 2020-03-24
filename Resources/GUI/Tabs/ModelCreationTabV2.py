from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui

class ModelCreationTab(QtWidgets.QWidget):
    
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)

        # Set up the overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        summaryLayout = QtWidgets.QVBoxLayout()

        