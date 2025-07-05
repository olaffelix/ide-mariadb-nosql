from PyQt5.QtWidgets import QSplitter, QVBoxLayout, QWidget
from ui.components.terminal_panel import TerminalPanel
from PyQt5.QtCore import Qt

class CentralPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.splitter = QSplitter()
        self.tab_widget = self._create_tab_widget()
        self.terminal = TerminalPanel()
        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.terminal)
        self.splitter.setSizes([800, 120])
        self.splitter.setOrientation(Qt.Vertical)  # Asegura orientación vertical
        self.splitter.setStretchFactor(0, 4)  # Tab widget ocupa más espacio
        self.splitter.setStretchFactor(1, 1)  # Terminal ocupa menos espacio
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def _create_tab_widget(self):
        from PyQt5.QtWidgets import QTabWidget
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(True)
        return tab_widget
