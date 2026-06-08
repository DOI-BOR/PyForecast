from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QPushButton)

app = QApplication.instance()


class LogViewer(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Application Log')
        self.setWindowIcon(app.icon)
        self.setUI()
        self.log_area.setText(app.log_message)
        self.clear_button.pressed.connect(self.clear_log)
        app.log_handler.signaler.new_log_message.connect(
            lambda:
            self.log_area.setText(app.log_message)
        )
        app.log_handler.signaler.new_log_message.connect(
            lambda:
            self.log_area.verticalScrollBar().setValue(
                self.log_area.verticalScrollBar().maximum()
            )
        )

    def clear_log(self):
        app.log_message = ''
        self.log_area.setText('')
        app.processEvents()

    def setUI(self):
        layout = QVBoxLayout()
        self.log_area = QTextEdit()
        self.log_area.setObjectName('monospace')
        self.log_area.setReadOnly(True)
        self.clear_button = QPushButton('Clear')
        self.refr_button = QPushButton('Refresh')
        hlayout = QHBoxLayout()
        hlayout.addStretch(1)
        hlayout.addWidget(self.clear_button)
        layout.addWidget(self.log_area)
        layout.addLayout(hlayout)
        self.setLayout(layout)
        self.log_area.setMinimumWidth(1100)
        self.log_area.setMinimumHeight(400)
