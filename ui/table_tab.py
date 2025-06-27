from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import json
from widgets.json_modal import JsonModal

class TableTab(QWidget):
    def __init__(self, conn, db, table, conn_manager):
        super().__init__()
        self.conn = conn
        self.db = db
        self.table = table
        self.conn_manager = conn_manager
        self.layout = QVBoxLayout()
        self.reload_btn = QPushButton('Recargar')
        self.reload_btn.clicked.connect(self.load_table_data)
        self.layout.addWidget(self.reload_btn)
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        self.setLayout(self.layout)
        self.load_table_data()

    def load_table_data(self):
        try:
            columns, rows = self.conn_manager.get_table_data(self.conn, self.db, self.table)
            self.table_widget.clear()
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)
            self.table_widget.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    if columns[col_idx] == 'value':
                        try:
                            json_obj = json.loads(value)
                            if isinstance(json_obj, dict):
                                value = json.dumps(json_obj, indent=2, ensure_ascii=False)
                        except Exception:
                            pass
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(row_idx, col_idx, item)
            self.table_widget.resizeColumnsToContents()
            self.table_widget.cellDoubleClicked.connect(lambda r, c: self.show_json_modal(columns, r, c))
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_json_modal(self, columns, row_idx, col_idx):
        if columns[col_idx] != 'value':
            return
        item = self.table_widget.item(row_idx, col_idx)
        if not item:
            return
        json_text = item.text()
        dlg = JsonModal(json_text, editable=False)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        self._json_modal = dlg

