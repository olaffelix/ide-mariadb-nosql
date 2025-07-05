from PyQt5.QtWidgets import QToolBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from ui.components.toolbar_button import ToolBarButton

class TopMenu(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(20, 20))
        # Botón + (agregar)
        self.add_btn = ToolBarButton(text="🞡", tooltip="Agregar conexión")
        self.addWidget(self.add_btn)
        # Botón - (eliminar)
        self.del_btn = ToolBarButton(text="—", tooltip="Eliminar conexión")
        self.addWidget(self.del_btn)
        # Botón lápiz (editar)
        self.edit_btn = ToolBarButton(text="✎", tooltip="Editar conexión")
        self.addWidget(self.edit_btn)
        # Botón conectar
        self.connect_btn = ToolBarButton(text="🔌", tooltip="Conectar")
        self.addWidget(self.connect_btn)
        # Botón desconectar
        self.disconnect_btn = ToolBarButton(text="⛔", tooltip="Desconectar")
        self.addWidget(self.disconnect_btn)
        # Botón recargar
        self.reload_btn = ToolBarButton(text="⟳", tooltip="Recargar conexión")
        self.addWidget(self.reload_btn)
