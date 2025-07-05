from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QApplication
from PyQt5.QtCore import QTimer
from ui.components.json_viewer import JsonViewer
import json

class EditRecordDialog(QDialog):
    def __init__(self, value, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Editar Registro')
        self.resize(700, 600)
        self.edited_json = None
        layout = QVBoxLayout()
        
        # Usar el JsonViewer en lugar de QTextEdit
        self.json_viewer = JsonViewer()
        layout.addWidget(self.json_viewer)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
        buttons.accepted.connect(self.accept_changes)
        buttons.rejected.connect(self.reject)
        
        # Cargar el JSON en el editor después de que se haya cargado la página
        QTimer.singleShot(500, lambda: self.load_json_data(value))

    def load_json_data(self, value):
        """Cargar los datos JSON en el editor"""
        json_str = json.dumps(value, indent=2, ensure_ascii=False)
        # Pasar el JSON ya parseado directamente
        js_code = f"setJSON({json_str})"
        self.json_viewer.page().runJavaScript(js_code)

    def accept_changes(self):
        """Obtener el JSON editado antes de aceptar el diálogo"""
        def handle_json_result(result):
            try:
                if result is not None:
                    self.edited_json = json.dumps(result, indent=2, ensure_ascii=False)
                else:
                    self.edited_json = "{}"
                self.accept()
            except Exception as e:
                print(f"Error al obtener JSON: {e}")
                # Intentar obtener el texto directamente
                self.json_viewer.page().runJavaScript('getJSONText()', self.handle_text_result)
        
        def handle_text_result(text_result):
            try:
                self.edited_json = text_result if text_result else "{}"
                self.accept()
            except Exception as e:
                print(f"Error al obtener texto JSON: {e}")
                self.edited_json = "{}"
                self.accept()
        
        # Obtener el JSON del editor
        self.json_viewer.page().runJavaScript('getJSON()', handle_json_result)

    def handle_text_result(self, text_result):
        """Manejar el resultado del texto JSON como método de respaldo"""
        try:
            self.edited_json = text_result if text_result else "{}"
            self.accept()
        except Exception as e:
            print(f"Error al manejar texto JSON: {e}")
            self.edited_json = "{}"
            self.accept()

    def get_json(self):
        """Retornar el JSON editado"""
        return self.edited_json if self.edited_json is not None else "{}"
