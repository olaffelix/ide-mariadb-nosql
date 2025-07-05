from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QTreeWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class SideDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Conexiones/Bases/Tablas", parent)
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        menu_widget = QWidget()
        menu_layout = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.del_btn = QPushButton("-")
        self.edit_btn = QPushButton("✎")
        menu_layout.addWidget(self.add_btn)
        menu_layout.addWidget(self.del_btn)
        menu_layout.addWidget(self.edit_btn)
        menu_layout.addStretch()
        menu_widget.setLayout(menu_layout)
        dock_main = QWidget()
        dock_layout = QVBoxLayout()
        dock_layout.addWidget(menu_widget)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Conexiones/Bases/Tablas"])
        dock_layout.addWidget(self.tree_widget)
        dock_main.setLayout(dock_layout)
        self.setWidget(dock_main)
