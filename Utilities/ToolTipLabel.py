import sys

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout,
                               QProxyStyle, QStyle)
from pyqtgraph.examples.MultiDataPlot import widget

app = QApplication.instance()

class ToolTipLabel(QLabel):

    def __init__(self, parent=None, text='', tip=''):
        text = f"""<html>
        &#9432;&nbsp;&nbsp;{text}</html>
        """

        super().__init__(parent, text=text)
        self.setToolTip(tip)


class ToolTipLabel2(QWidget):

    def __init__(self, parent=None, text='', tip=''):
        super().__init__(parent)

        IconSize = QSize(16, 16)
        HorizontalSpacing = 2

        self.setStyle(proxyStyle())

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.icon = QLabel()
        self.icon.setPixmap(qta.icon('fa5.question-circle').pixmap(IconSize))
        self.icon.setToolTip(tip)
        self.text = QLabel(text)
        hlayout.addWidget(self.icon)
        hlayout.addSpacing(HorizontalSpacing)
        hlayout.addWidget(self.text)
        self.setLayout(hlayout)


class proxyStyle(QProxyStyle):

    def __init__(self, parent=None):
        super().__init__(parent)

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return 0
        return super().styleHint(hint, option, widget, returnData)


if __name__ == '__main__':
    app.setStyleSheet("""QLabel {font-size: 24px}""")

    w = ToolTipLabel(None, 'Hello World', '<strong>This</strong> is an example')
    w.show()
    sys.exit(app.exec())
