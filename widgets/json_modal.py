from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class JsonModal(QWidget):
    def __init__(self, json_text, editable=False):
        super().__init__()
        self.setWindowTitle('Editor JSON' + ('' if not editable else ' (editable)'))
        self.setGeometry(200, 200, 600, 500)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setText(json_text)
        self.text_edit.setReadOnly(not editable)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

