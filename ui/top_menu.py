from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

class TopMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.del_btn = QPushButton("-")
        self.edit_btn = QPushButton("✎")
        self.connect_btn = QPushButton("🔌")
        self.connect_btn.setToolTip("Conectar")
        self.disconnect_btn = QPushButton("⛔")
        self.disconnect_btn.setToolTip("Desconectar")
        self.reload_btn = QPushButton("⟳")
        self.reload_btn.setToolTip("Recargar conexión")
        layout.addWidget(self.add_btn)
        layout.addWidget(self.del_btn)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
        layout.addWidget(self.reload_btn)
        layout.addStretch()
        self.setLayout(layout)
