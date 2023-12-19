from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

app = QApplication.instance()

class LogViewer(QDialog):

  def __init__(self):

    QDialog.__init__(self)
    self.setModal(False)
    self.setWindowTitle('Application Log')
    self.setWindowIcon(QIcon(app.base_dir + '/Resources/Icons/AppIcon.ico'))
    self.setUI()
    self.log_area.setText(app.log_message)
    self.clear_button.pressed.connect(self.clear_log)
    self.refr_button.pressed.connect(self.refr)
    app.new_log_message.connect(lambda: self.log_area.setText(app.log_message))
    app.new_log_message.connect(lambda: self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum()))

  def refr(self):
    self.log_area.setText(app.log_message)

  def clear_log(self):
    app.log_message = ''
    app.new_log_message.emit()
    app.processEvents()

  def setUI(self):
    layout = QVBoxLayout()
    self.log_area = QTextEdit(objectName='monospace')
    self.log_area.setReadOnly(True)
    self.clear_button = QPushButton('Clear')
    self.refr_button = QPushButton('Refresh')
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(self.clear_button)
    hlayout.addWidget(self.refr_button)
    layout.addWidget(self.log_area)
    layout.addLayout(hlayout)
    self.setLayout(layout)
    self.log_area.setMinimumWidth(1100)