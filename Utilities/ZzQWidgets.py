from PySide6.QtWidgets import QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox

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

class ZzQSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event, /):
        event.ignore()

class ZzQDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event, /):
        event.ignore()