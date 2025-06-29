from PyQt5.QtWidgets import QToolBar, QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt

class TopMenu(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(20, 20))
        # Botón + (agregar)
        self.add_btn = QToolButton()
        self.add_btn.setIcon(QIcon.fromTheme('list-add') or QIcon.fromTheme('plus') or QIcon.fromTheme('add') or QIcon.fromTheme('document-new'))
        self.add_btn.setText("🞡")
        self.add_btn.setToolTip("Agregar conexión")
        self.addWidget(self.add_btn)
        # Botón - (eliminar)
        self.del_btn = QToolButton()
        self.del_btn.setIcon(QIcon.fromTheme('list-remove') or QIcon.fromTheme('minus') or QIcon.fromTheme('edit-delete'))
        self.del_btn.setText("—")
        self.del_btn.setToolTip("Eliminar conexión")
        self.addWidget(self.del_btn)
        # Botón lápiz (editar)
        self.edit_btn = QToolButton()
        self.edit_btn.setText("✎")
        self.edit_btn.setToolTip("Editar conexión")
        self.addWidget(self.edit_btn)
        # Botón conectar
        self.connect_btn = QToolButton()
        self.connect_btn.setText("🔌")
        self.connect_btn.setToolTip("Conectar")
        self.addWidget(self.connect_btn)
        # Botón desconectar
        self.disconnect_btn = QToolButton()
        self.disconnect_btn.setText("⛔")
        self.disconnect_btn.setToolTip("Desconectar")
        self.addWidget(self.disconnect_btn)
        # Botón recargar
        self.reload_btn = QToolButton()
        self.reload_btn.setText("⟳")
        self.reload_btn.setToolTip("Recargar conexión")
        self.addWidget(self.reload_btn)
