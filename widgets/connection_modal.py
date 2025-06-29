from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configurations.json')
print("CONFIG_FILE", CONFIG_FILE)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'connections': []}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

class ConnectionModal(QDialog):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.setWindowTitle('Agregar/Editar Conexión')
        self.setGeometry(300, 300, 350, 220)
        layout = QVBoxLayout()
        self.inputs = {}
        fields = [
            ('name', 'Nombre'),
            ('host', 'Host'),
            ('user', 'Usuario'),
            ('password', 'Contraseña'),
            ('port', 'Puerto')
        ]
        for key, label in fields:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            edit = QLineEdit()
            if key == 'password':
                edit.setEchoMode(QLineEdit.Password)
            if conn and key in conn:
                edit.setText(str(conn[key]))
            row.addWidget(edit)
            layout.addLayout(row)
            self.inputs[key] = edit
        btns = QHBoxLayout()
        ok_btn = QPushButton('OK')
        cancel_btn = QPushButton('Cancelar')
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

    def get_connection(self):
        return {
            'name': self.inputs['name'].text(),
            'host': self.inputs['host'].text(),
            'user': self.inputs['user'].text(),
            'password': self.inputs['password'].text(),
            'port': int(self.inputs['port'].text()) if self.inputs['port'].text().isdigit() else 3306
        }
