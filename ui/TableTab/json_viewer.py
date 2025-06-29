from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os

class JsonViewer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        html_path = os.path.join(os.path.dirname(__file__), '../jsoneditor.html')
        html_path = os.path.abspath(html_path)
        if os.path.exists(html_path):
            self.load(QUrl.fromLocalFile(html_path))
        else:
            self.setHtml("<h3>jsoneditor.html no encontrado</h3>")

    def set_json(self, json_str):
        # Recibe un string JSON y lo pasa al editor
        self.page().runJavaScript(f"setJSON({json_str})")
