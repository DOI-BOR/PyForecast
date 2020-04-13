from PyQt5 import QtCore, QtWidgets, QtGui
from pyqtgraph.widgets.RawImageWidget import RawImageWidget
from pyqtgraph import functions as fn
import numpy as np
import bitarray as ba


class ModelRunSummaryPage(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self)

        self.parent = parent
        self.layout = QtWidgets.QVBoxLayout()



class PredictorGrid(RawImageWidget):
    """
    """

    def __init__(self, parent=None):
        """
        """

        RawImageWidget.__init__(self, scaled=True)
        self.numPredictors = None
        self.accumulatedSwitch = False

    def paintEvent(self, ev):
        """
        Taken from original PyQtGraph source code. Only thing changed
        is that we invert the image before drawing it.
        """
        if self.opts is None:
            return
        if self.image is None:
            argb, alpha = fn.makeARGB(self.opts[0], *self.opts[1], **self.opts[2])
            self.image = fn.makeQImage(argb, alpha)
            # INVERT THE IMAGE PIXELS
            self.image.invertPixels()
            self.opts = ()
        #if self.pixmap is None:
            #self.pixmap = QtGui.QPixmap.fromImage(self.image)
        p = QtGui.QPainter(self)
        if self.scaled:
            rect = self.rect()
            ar = rect.width() / float(rect.height())
            imar = self.image.width() / float(self.image.height())
            if ar > imar:
                rect.setWidth(int(rect.width() * imar/ar))
            else:
                rect.setHeight(int(rect.height() * ar/imar))
            
            p.drawImage(rect, self.image)
            
        else:
            p.drawImage(QtCore.QPointF(), self.image)
        #p.drawPixmap(self.rect(), self.pixmap)
        p.end()

    def switch(self):
        self.accumulatedSwitch = not self.accumulatedSwitch
        print(self.modelAccum.max())

    def newModel(self, model):
        """
        """

        modelArray = np.array(list(model), dtype=np.uint32)

        # First check if we need to initalize the model size
        if self.numPredictors == None:
            
            self.numPredictors = len(model)
            self.modelAccum = modelArray
            print(self.modelAccum)
            self.square = int(np.ceil(np.sqrt(self.numPredictors)))
            self.imgArray_current = np.reshape(
                np.append(modelArray, np.full((self.square**2 - self.numPredictors, ), np.nan)),
                (self.square, self.square)
            )
            self.imgArray_accum = np.reshape(
                np.append(modelArray, np.full((self.square**2 - self.numPredictors, ), np.nan)),
                (self.square, self.square)
            )

        else:
            self.imgArray_current = np.reshape(
                    np.append(modelArray, np.full((self.square**2 - self.numPredictors, ), np.nan)),
                    (self.square, self.square)
                )
            self.modelAccum += modelArray
            self.imgArray_accum = np.reshape(
                np.append(self.modelAccum, np.full((self.square**2 - self.numPredictors, ), np.nan)),
                (self.square, self.square)
            )

        if self.accumulatedSwitch:
            self.setImage(self.imgArray_accum, levels=[np.nanmin(self.modelAccum), self.modelAccum.max()])  
        else:
            self.setImage(self.imgArray_current, levels=[0,1])    
        QtWidgets.QApplication.processEvents()


if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    widg = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout()

    from time import sleep

    
    img_widg = PredictorGrid()
    layout.addWidget(img_widg)

    def runRandom():
        for i in range(2**11):
            sleep(0.0051)
            img_widg.newModel(ba.bitarray(format(i, '0{0}b'.format(11))))
    
    def switch():
        img_widg.switch()


    button = QtWidgets.QPushButton("run")
    button.pressed.connect(runRandom)
    layout.addWidget(button)

    button2 = QtWidgets.QPushButton("switch")
    button2.pressed.connect(switch)
    layout.addWidget(button2)



    widg.setLayout(layout)
    widg.show()
    sys.exit(app.exec_())

