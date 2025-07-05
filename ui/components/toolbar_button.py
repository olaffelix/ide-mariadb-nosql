from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class ToolBarButton(QToolButton):
    def __init__(self, icon=None, text=None, tooltip=None, parent=None, width=20, height=20):
        super().__init__(parent)
        self.setIconSize(QSize(width, height))
        if icon:
            self.setIcon(icon)
        if text:
            self.setText(text)
        if tooltip:
            self.setToolTip(tooltip)
