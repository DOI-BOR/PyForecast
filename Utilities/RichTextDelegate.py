from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys

class HTMLDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__()
        self.doc = QTextDocument(self)

    def paint(self, painter, option, index):

        option = QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        text = index.data(Qt.UserRole + 3)
        option.text = text

        style = QApplication.style() if option.widget is None \
            else option.widget.style()
        
        #textOption = QTextOption()
        #textOption.setTextDirection(option.direction)

        doc = QTextDocument()
        #doc.setDefaultTextOption(textOption)
        doc.setHtml(option.text)
        doc.setDefaultFont(option.font)
        doc.setDocumentMargin(10)
        #doc.setTextWidth(option.rect.width())
        #doc.adjustSize()
        option.text = ''

        style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)
        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, option)
        documentSize = QSize(int(doc.size().width()), int(doc.size().height()))
        layoutRect = QStyle.alignedRect(Qt.LayoutDirectionAuto, option.displayAlignment, documentSize, textRect)

        painter.save()

        painter.translate(layoutRect.topLeft())
        doc.drawContents(painter, QRectF(textRect.translated(-textRect.topLeft())));
        #painter.drawRect(QRectF(textRect.translated(-textRect.topLeft())))

        painter.restore()


    def sizeHint(self, option, index):
        option = QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        text = index.data(Qt.UserRole + 3)
        option.text = text
        if option.text == '':
            return QStyledItemDelegate.sizeHint(self, option, index)
        doc = QTextDocument()
        doc.setHtml(option.text)
        doc.setDefaultFont(option.font)
        doc.setDocumentMargin(10)
        #sdoc.setTextWidth(option.rect.width())
        #doc.adjustSize()
        return QSize(int(doc.size().width()), int(doc.size().height()))

        