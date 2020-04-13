"""
Helper widget for SVG Icons
Allows you to resize and or re-color icons
"""
from PyQt5 import QtCore, QtWidgets, QtGui
from xml.dom import minidom
from io import StringIO

class SVGIcon(QtGui.QIcon):

    def __init__(self, path_to_icon, icon_color=None, icon_rotation=0, icon_size=(None, None)):
        """
        path_to_icon: icon system path
        icon_color: hex color code
        icon_rotation: 0-359 degrees
        icon_size: (width, height) in pixels
        """

        

        # Open the file
        with open(path_to_icon, 'r') as readFile:
            self.xmlDom = minidom.parseString(readFile.read())

        # First adjust the size and color
        # if the user supplied those arguments
        if icon_color:

            # Change any non-transparent paths to 
            # the new color
            for element in filter(lambda element_: element_.tagName in ['path', 'circle'], self.xmlDom.childNodes[0].childNodes):
                if element.hasAttribute('fill'):
                    if element.attributes['fill'].value != 'none':
                        element.attributes['fill'].value = icon_color
                else:
                    element.setAttribute("fill", icon_color)

        # Next adjust the size if necessarry
        if icon_size != (None, None):

            # Change the height and width attributes to the new size
            if self.xmlDom.childNodes[0].hasAttribute("width"):
                self.xmlDom.childNodes[0].attributes['width'].value = str(icon_size[0])
            else:
                self.xmlDom.childNodes[0].setAttribute("width", str(icon_size[0]))
            if self.xmlDom.childNodes[0].hasAttribute("height"):
                self.xmlDom.childNodes[0].attributes['height'].value = str(icon_size[1])
            else:
                self.xmlDom.childNodes[0].setAttribute("height", str(icon_size[0]))
            self.xmlDom.childNodes[0].attributes['height'].value = str(icon_size[1])
        
        # Read the xml into an image
        self.image = QtGui.QImage.fromData(bytearray(self.xmlDom.toxml(), encoding='utf-8'))
        self.pixmap = QtGui.QPixmap.fromImage(self.image)
        matrix_ = QtGui.QTransform()
        matrix_.rotate(icon_rotation)
        QtGui.QIcon.__init__(self, self.pixmap.transformed(matrix_))

        return

    def XML(self):
        return self.xmlDom.toxml()

if __name__ == '__main__':
    import sys
    import os
    app = QtWidgets.QApplication(sys.argv)
    widg = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    icon = SVGIcon(os.path.abspath("resources/graphicalResources/icons/search-24px.svg"), '#FF00FF', 173, icon_size=(50,50))
    button = QtWidgets.QPushButton("g")
    button.setIcon(icon)
    button.setIconSize(QtCore.QSize(300,300))
    layout.addWidget(button)
    widg.setLayout(layout)
    widg.show()
    sys.exit(app.exec_())



