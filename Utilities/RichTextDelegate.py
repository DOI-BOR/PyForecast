from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import (QApplication, QStyle, QStyleOptionViewItem,
                               QStyledItemDelegate)

app = QApplication.instance()


class HTMLDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument(self)
        self.w = None

    def paint(self, painter, option, index):
        option = QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        text = index.data(Qt.ItemDataRole.UserRole + 3)
        option.text = text

        style = app.style() if option.widget is None else option.widget.style()

        doc = QTextDocument(self)
        doc.setHtml(option.text)
        doc.setDefaultFont(option.font)
        doc.setDocumentMargin(15)
        doc.setTextWidth(option.rect.width())

        option.text = ''

        style.drawControl(
            QStyle.ControlElement.CE_ItemViewItem,
            option,
            painter,
            option.widget
        )
        textRect = style.subElementRect(
            QStyle.SubElement.SE_ItemViewItemText,
            option
        )
        documentSize = QSize(
            int(option.rect.width()),
            int(doc.size().height())
        )
        layoutRect = QStyle.alignedRect(
            Qt.LayoutDirection.LayoutDirectionAuto,
            option.displayAlignment,
            documentSize,
            textRect
        )

        painter.save()

        painter.translate(layoutRect.topLeft())
        doc.drawContents(
            painter,
            QRectF(textRect.translated(-textRect.topLeft()))
        )

        painter.restore()

    def sizeHint(self, option, index):
        option = QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        text = index.data(Qt.ItemDataRole.UserRole + 3)
        option.text = text
        doc = QTextDocument(self)
        doc.setHtml(option.text)
        doc.setDefaultFont(option.font)
        doc.setDocumentMargin(15)
        doc.setTextWidth(option.rect.width())
        return QSize(int(doc.size().width()), int(doc.size().height()))
