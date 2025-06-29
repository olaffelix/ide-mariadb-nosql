from PyQt5.QtWidgets import QSplitter, QTabWidget, QTextEdit
from PyQt5.QtCore import Qt

class CentralPanel(QSplitter):
    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMaximumHeight(180)
        self.terminal.setMinimumHeight(80)
        self.terminal.hide()
        self.addWidget(self.tab_widget)
        self.addWidget(self.terminal)
