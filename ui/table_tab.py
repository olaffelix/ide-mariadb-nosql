from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLineEdit, QLabel, QComboBox, QTextEdit
from PyQt5.QtCore import Qt
import json
from widgets.json_modal import JsonModal

class TableTab(QWidget):
    def __init__(self, conn, db, table, conn_manager):
        super().__init__()
        self.conn = conn
        self.db = db
        self.table = table
        self.conn_manager = conn_manager
        self.mode = 'Tabla'  # o 'JSON'
        self.data = []
        self.columns = []
        self.filtered_data = []
        self.init_ui()
        self.load_table_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # Campo de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Buscar registros...')
        self.search_input.textChanged.connect(self.apply_search)
        search_layout.addWidget(QLabel('Buscar:'))
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        # Barra de botones
        btn_layout = QHBoxLayout()
        self.new_btn = QPushButton('🞡')
        self.del_btn = QPushButton('—')
        self.edit_btn = QPushButton('✎')
        self.reload_btn = QPushButton('⟳')
        self.view_mode = QComboBox()
        self.view_mode.addItems(['Tabla', 'JSON'])
        self.view_mode.currentTextChanged.connect(self.change_view_mode)
        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.reload_btn)
        btn_layout.addWidget(QLabel('Modo:'))
        btn_layout.addWidget(self.view_mode)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        # Tabla y JSON viewer
        self.table_widget = QTableWidget()
        self.json_viewer = QTextEdit()
        self.json_viewer.setReadOnly(True)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(self.json_viewer)
        self.setLayout(main_layout)
        self.reload_btn.clicked.connect(self.load_table_data)
        self.new_btn.clicked.connect(self.add_record)
        self.del_btn.clicked.connect(self.delete_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.table_widget.cellDoubleClicked.connect(self.show_json_modal_from_table)
        self.json_viewer.hide()

    def load_table_data(self):
        try:
            columns, rows = self.conn_manager.get_table_data(self.conn, self.db, self.table)
            self.columns = columns
            self.data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                if 'value' in row_dict:
                    try:
                        value_json = json.loads(row_dict['value'])
                        self.data.append({'_pk': row_dict.get(columns[0]), 'value': value_json, '_raw': row_dict})
                    except Exception:
                        self.data.append({'_pk': row_dict.get(columns[0]), 'value': row_dict['value'], '_raw': row_dict})
            self.apply_search()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def apply_search(self):
        text = self.search_input.text().lower()
        if not text:
            self.filtered_data = self.data
        else:
            self.filtered_data = [d for d in self.data if text in json.dumps(d['value'], ensure_ascii=False).lower()]
        self.update_view()

    def update_view(self):
        if self.mode == 'Tabla':
            self.json_viewer.hide()
            self.table_widget.show()
            self.show_table_view()
        else:
            self.table_widget.hide()
            self.json_viewer.show()
            self.show_json_view()

    def show_table_view(self):
        # Mostrar solo los campos de primer nivel del JSON value
        if not self.filtered_data:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return
        keys = set()
        for d in self.filtered_data:
            if isinstance(d['value'], dict):
                keys.update(d['value'].keys())
        keys = sorted(list(keys))
        self.table_widget.setColumnCount(len(keys))
        self.table_widget.setHorizontalHeaderLabels(keys)
        self.table_widget.setRowCount(len(self.filtered_data))
        for row_idx, d in enumerate(self.filtered_data):
            for col_idx, key in enumerate(keys):
                value = d['value'].get(key, '') if isinstance(d['value'], dict) else ''
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row_idx, col_idx, item)

    def show_json_view(self):
        # Mostrar todos los registros como JSON
        json_list = [d['value'] for d in self.filtered_data]
        self.json_viewer.setText(json.dumps(json_list, indent=2, ensure_ascii=False))

    def change_view_mode(self, mode):
        self.mode = mode
        self.update_view()

    def show_json_modal_from_table(self, row, col):
        if row < len(self.filtered_data):
            dlg = JsonModal(json.dumps(self.filtered_data[row]['value'], indent=2, ensure_ascii=False), editable=False)
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()
            self._json_modal = dlg

    def add_record(self):
        # Modal para ingresar un nuevo registro JSON
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle('Nuevo Registro')
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlaceholderText('Introduce el JSON del nuevo registro')
        layout.addWidget(text_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec_():
            try:
                value_json = json.loads(text_edit.toPlainText())
                # Insertar en la base de datos
                import pymysql
                connection = pymysql.connect(
                    host=self.conn['host'], user=self.conn['user'], password=self.conn['password'], port=self.conn['port'], database=self.db
                )
                with connection.cursor() as cursor:
                    # Solo insertamos el campo 'value' como JSON
                    cursor.execute(f"INSERT INTO `{self.table}` (value) VALUES (%s)", (json.dumps(value_json, ensure_ascii=False),))
                    connection.commit()
                connection.close()
                self.load_table_data()
                QMessageBox.information(self, 'Éxito', 'Registro agregado correctamente.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al agregar registro: {e}')

    def delete_record(self):
        # Eliminar el registro seleccionado (por _pk)
        row = self.table_widget.currentRow()
        if row < 0 or row >= len(self.filtered_data):
            QMessageBox.warning(self, 'Eliminar Registro', 'Selecciona un registro para eliminar.')
            return
        pk = self.filtered_data[row]['_pk']
        if pk is None:
            QMessageBox.warning(self, 'Eliminar Registro', 'No se puede eliminar: no se encontró la llave primaria.')
            return
        reply = QMessageBox.question(self, 'Eliminar Registro', '¿Estás seguro de eliminar este registro?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                import pymysql
                connection = pymysql.connect(
                    host=self.conn['host'], user=self.conn['user'], password=self.conn['password'], port=self.conn['port'], database=self.db
                )
                with connection.cursor() as cursor:
                    pk_col = self.columns[0]
                    cursor.execute(f"DELETE FROM `{self.table}` WHERE `{pk_col}`=%s", (pk,))
                    connection.commit()
                connection.close()
                self.load_table_data()
                QMessageBox.information(self, 'Éxito', 'Registro eliminado correctamente.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al eliminar registro: {e}')

    def edit_record(self):
        # Editar el registro seleccionado (solo campo value)
        row = self.table_widget.currentRow()
        if row < 0 or row >= len(self.filtered_data):
            QMessageBox.warning(self, 'Editar Registro', 'Selecciona un registro para editar.')
            return
        pk = self.filtered_data[row]['_pk']
        if pk is None:
            QMessageBox.warning(self, 'Editar Registro', 'No se puede editar: no se encontró la llave primaria.')
            return
        # Modal para editar JSON
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle('Editar Registro')
        dlg.resize(600, 500)  # Igual que Editor JSON
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setText(json.dumps(self.filtered_data[row]['value'], indent=2, ensure_ascii=False))
        layout.addWidget(text_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec_():
            try:
                value_json = json.loads(text_edit.toPlainText())
                import pymysql
                connection = pymysql.connect(
                    host=self.conn['host'], user=self.conn['user'], password=self.conn['password'], port=self.conn['port'], database=self.db
                )
                with connection.cursor() as cursor:
                    pk_col = self.columns[0]
                    cursor.execute(f"UPDATE `{self.table}` SET value=%s WHERE `{pk_col}`=%s", (json.dumps(value_json, ensure_ascii=False), pk))
                    connection.commit()
                connection.close()
                self.load_table_data()
                QMessageBox.information(self, 'Éxito', 'Registro editado correctamente.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al editar registro: {e}')
