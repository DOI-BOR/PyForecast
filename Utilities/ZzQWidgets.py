from PySide6.QtWidgets import QComboBox, QDateEdit

class ZzQDateEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event, /):
        event.ignore()


class ZzQComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event, /):
        event.ignore()