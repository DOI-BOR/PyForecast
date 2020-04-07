from PyQt5 import QtCore, QtGui, QtWidgets
def PLOTITEM_clear_(self):
        """
        Remove all items from the ViewBox.
        """
        for i in self.items[:]:
            self.removeItem(i)
            if hasattr(i, 'isActive'):
                i.isActive = False
        self.avgCurves = {}

def INFINITELINE_mouseDragEvent_(self, ev):
        if self.movable and ev.button() == QtCore.Qt.LeftButton:
            if ev.isStart():
                self.moving = True
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SplitHCursor)
                self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                self.startPosition = self.pos()
            ev.accept()

            if not self.moving:
                return

            self.setPos(self.cursorOffset + self.mapToParent(ev.pos()))
            self.sigDragged.emit(self)
            if ev.isFinish():
                self.moving = False
                QtWidgets.QApplication.restoreOverrideCursor()
                self.sigPositionChangeFinished.emit(self)
    
def INFINITELINE_setMouseHover_(self, hover):
        ## Inform the item that the mouse is (not) hovering over it
        if self.mouseHovering == hover:
            return
        self.mouseHovering = hover
        if hover:
            self.currentPen = self.hoverPen
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SplitHCursor)
        else:
            self.currentPen = self.pen
            QtWidgets.QApplication.restoreOverrideCursor()
        self.update()

def LINEARREGION_mouseDragEvent_(self, ev):
        if not self.movable or int(ev.button() & QtCore.Qt.LeftButton) == 0:
            return
        ev.accept()
        
        if ev.isStart():
            bdp = ev.buttonDownPos()
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ClosedHandCursor)
            self.cursorOffsets = [l.pos() - bdp for l in self.lines]
            self.startPositions = [l.pos() for l in self.lines]
            self.moving = True
            
        if not self.moving:
            return
            
        self.lines[0].blockSignals(True)  # only want to update once
        for i, l in enumerate(self.lines):
            l.setPos(self.cursorOffsets[i] + ev.pos())
        self.lines[0].blockSignals(False)
        self.prepareGeometryChange()
        
        if ev.isFinish():
            self.moving = False
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.OpenHandCursor)
            self.sigRegionChangeFinished.emit(self)
        else:
            self.sigRegionChanged.emit(self)
            
def LINEARREGION_mouseClickEvent_(self, ev):
    if self.moving and ev.button() == QtCore.Qt.RightButton:
        ev.accept()
        for i, l in enumerate(self.lines):
            l.setPos(self.startPositions[i])
        self.moving = False
        self.sigRegionChanged.emit(self)
        self.sigRegionChangeFinished.emit(self)

def LINEARREGION_hoverEvent_(self, ev):
    if self.movable and (not ev.isExit()) and ev.acceptDrags(QtCore.Qt.LeftButton):
        self.setMouseHover(True)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.OpenHandCursor)
        
    else:
        self.setMouseHover(False)
        QtWidgets.QApplication.restoreOverrideCursor()
        
        
def LINEARREGION_setMouseHover_(self, hover):
    ## Inform the item that the mouse is(not) hovering over it
    if self.mouseHovering == hover:
        return
    self.mouseHovering = hover
    if hover:
        self.currentBrush = self.hoverBrush
        
    else:
        self.currentBrush = self.brush
        
    self.update()