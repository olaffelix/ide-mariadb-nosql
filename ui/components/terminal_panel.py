from PyQt5.QtWidgets import QTextEdit

class TerminalPanel(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(180)
        self.setMinimumHeight(80)
        self.hide()
