import sys

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout,
                               QProxyStyle, QStyle)

app = QApplication.instance()

class ToolTipLabel(QLabel):

    def __init__(self, text='', tip=''):
        text = f"""<html>
        &#9432;&nbsp;&nbsp;{text}</html>
        """

        QLabel.__init__(self, text)
        self.setToolTip(tip)


class ToolTipLabel2(QWidget):

    def __init__(self, text="", tip=""):
        IconSize = QSize(16, 16)
        HorizontalSpacing = 2

        QWidget.__init__(self)

        self.setStyle(proxyStyle(self.style()))

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

    def __init__(self, style):
        QProxyStyle.__init__(self, style)

    def styleHint(self, hint, option, widget, returnData):
        if (hint == QStyle.SH_ToolTip_WakeUpDelay):
            return 0
        return QProxyStyle.styleHint(self, hint, option, widget, returnData)


if __name__ == '__main__':
    app.setStyleSheet("""QLabel {font-size: 24px}""")

    w = ToolTipLabel('Hello World', '<strong>This</strong> is an example')
    w.show()
    sys.exit(app.exec())
