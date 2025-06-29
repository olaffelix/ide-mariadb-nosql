from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QMessageBox,
    QTreeWidgetItem,
)
from PyQt5.QtCore import Qt
from db.connection_manager import ConnectionManager
from ui.table_tab import TableTab
from widgets.connection_modal import load_config, save_config
from ui.central_panel import CentralPanel
from ui.terminal_panel import TerminalPanel
from ui.side_dock import SideDock
from ui.top_menu import TopMenu


class MainWindow(QMainWindow):
    def __init__(self, connections=None):
        super().__init__()
        self.setWindowTitle("IDE MariaDB JSON")
        self.setGeometry(100, 100, 1600, 900)
        self.showMaximized()
        if connections is None:
            config = load_config()
            self.connections = config.get('connections', [])
        else:
            self.connections = connections
            print(self.connections)
        self.conn_manager = ConnectionManager(self.connections)
        # Panel central con splitter para terminal
        self.central_panel = CentralPanel()
        self.tab_widget = self.central_panel.tab_widget
        self.terminal = self.central_panel.terminal
        self.setCentralWidget(self.central_panel)
        # Dock lateral derecho
        self.dock = SideDock(self)
        self.tree_widget = self.dock.tree_widget
        # Menú superior con botones +, -, ✎, conectar y desconectar
        self.top_menu = TopMenu()
        self.add_btn = self.top_menu.add_btn
        self.del_btn = self.top_menu.del_btn
        self.edit_btn = self.top_menu.edit_btn
        self.connect_btn = self.top_menu.connect_btn
        self.disconnect_btn = self.top_menu.disconnect_btn
        self.reload_btn = self.top_menu.reload_btn
        self.connect_btn.clicked.connect(self.open_selected_connection)
        self.disconnect_btn.clicked.connect(self.disconnect_selected_connection)
        self.reload_btn.clicked.connect(self.reload_selected_connection)
        # Widget principal del dock
        dock_main = self.dock.widget()
        dock_layout = dock_main.layout()
        # Elimina el menú duplicado del dock si existe
        if dock_layout.itemAt(0) and hasattr(dock_layout.itemAt(0).widget(), 'layout'):
            old_menu = dock_layout.itemAt(0).widget()
            dock_layout.removeWidget(old_menu)
            old_menu.deleteLater()
        dock_layout.insertWidget(0, self.top_menu)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.populate_connections()
        self.tree_widget.itemExpanded.connect(self.handle_tree_expand)
        self.tree_widget.itemDoubleClicked.connect(self.handle_tree_double_click)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.add_btn.clicked.connect(self.add_connection)
        self.del_btn.clicked.connect(self.delete_connection)
        self.edit_btn.clicked.connect(self.edit_connection)
        # Barra de estado
        self.statusBar().showMessage("Listo")
        # Atajo para mostrar/ocultar terminal
        self.terminal_shortcut = QPushButton("Terminal")
        self.terminal_shortcut.clicked.connect(self.toggle_terminal)
        self.statusBar().addPermanentWidget(self.terminal_shortcut)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

    def toggle_terminal(self):
        if self.terminal.isVisible():
            self.terminal.hide()
        else:
            self.terminal.show()

    def log(self, message):
        self.terminal.append(message)
        if not self.terminal.isVisible():
            self.terminal.show()

    def notify(self, message, error=False):
        self.statusBar().showMessage(message, 5000)
        self.log(("[ERROR] " if error else "[INFO] ") + message)

    def populate_connections(self):
        self.tree_widget.clear()
        for conn in self.connections:
            conn_item = QTreeWidgetItem([conn["name"]])
            conn_item.setData(0, Qt.UserRole, {"type": "connection", "conn": conn})
            self.tree_widget.addTopLevelItem(conn_item)
        self.tree_widget.expandAll()
        self.notify("Conexiones cargadas")

    def handle_tree_expand(self, item):
        data = item.data(0, Qt.UserRole)
        if data and data.get("type") == "connection" and item.childCount() == 0:
            conn = data["conn"]
            try:
                dbs = self.conn_manager.get_databases(conn)
                for db in dbs:
                    db_item = QTreeWidgetItem([db])
                    db_item.setData(
                        0, Qt.UserRole, {"type": "database", "conn": conn, "db": db}
                    )
                    item.addChild(db_item)
                self.notify(f'Conectado a {conn["name"]}')
            except Exception as e:
                db_item = QTreeWidgetItem([f"Error: {e}"])
                item.addChild(db_item)
                self.notify(f"Error de conexión: {e}", error=True)
        elif data and data.get("type") == "database" and item.childCount() == 0:
            conn = data["conn"]
            db = data["db"]
            try:
                tables = self.conn_manager.get_tables(conn, db)
                for table in tables:
                    table_item = QTreeWidgetItem([table])
                    table_item.setData(
                        0,
                        Qt.UserRole,
                        {"type": "table", "conn": conn, "db": db, "table": table},
                    )
                    item.addChild(table_item)
                self.notify(f"Tablas de {db} cargadas")
            except Exception as e:
                table_item = QTreeWidgetItem([f"Error: {e}"])
                item.addChild(table_item)
                self.notify(f"Error al cargar tablas: {e}", error=True)

    def handle_tree_double_click(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data and data.get("type") == "connection":
            self.expand_and_connect(item)
        elif data and data.get("type") == "database":
            self.expand_and_load_tables(item)
        elif data and data.get("type") == "table":
            conn = data["conn"]
            db = data["db"]
            table = data["table"]
            tab_name = f"{conn['name']}/{db}/{table}"
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == tab_name:
                    self.tab_widget.setCurrentIndex(i)
                    return
            tab = TableTab(conn, db, table, self.conn_manager)
            self.tab_widget.addTab(tab, tab_name)
            self.tab_widget.setCurrentWidget(tab)

    def expand_and_load_tables(self, item):
        # Expande y carga tablas si no está expandido
        if item.childCount() == 0:
            self.handle_tree_expand(item)
        self.tree_widget.expandItem(item)

    def expand_and_connect(self, item):
        # Expande y conecta si no está expandido
        if item.childCount() == 0:
            self.handle_tree_expand(item)
        self.tree_widget.expandItem(item)

    def open_selected_connection(self):
        item = self.tree_widget.currentItem()
        if item:
            data = item.data(0, Qt.UserRole)
            if data and data.get("type") == "connection":
                self.expand_and_connect(item)

    def show_tree_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        if data and data.get("type") == "connection":
            menu.addAction("Conectar", lambda: self.expand_and_connect(item))
            menu.addAction("Editar", self.edit_connection)
            menu.addAction("Desconectar", lambda: self.disconnect_connection(item))
            menu.addAction("Eliminar", self.delete_connection)
        elif data and data.get("type") == "database":
            menu.addAction("Desconectar", lambda: self.disconnect_connection(item))
        menu.exec_(self.tree_widget.viewport().mapToGlobal(pos))

    def disconnect_connection(self, item):
        # Simplemente colapsa el nodo y elimina hijos
        item.takeChildren()
        self.tree_widget.collapseItem(item)
        self.notify("Conexión desconectada")

    def add_connection(self):
        from widgets.connection_modal import ConnectionModal

        dlg = ConnectionModal(self)
        if dlg.exec_():
            new_conn = dlg.get_connection()
            self.connections.append(new_conn)
            save_config({"connections": self.connections})
            self.populate_connections()

    def delete_connection(self):
        item = self.tree_widget.currentItem()
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data or data.get("type") != "connection":
            return
        conn = data["conn"]
        reply = QMessageBox.question(
            self,
            "Eliminar conexión",
            f"¿Eliminar la conexión '{conn['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.connections = [
                c for c in self.connections if c["name"] != conn["name"]
            ]
            save_config({"connections": self.connections})
            self.populate_connections()

    def edit_connection(self):
        item = self.tree_widget.currentItem()
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data or data.get("type") != "connection":
            return
        conn = data["conn"]
        from widgets.connection_modal import ConnectionModal

        dlg = ConnectionModal(self, conn)
        if dlg.exec_():
            updated_conn = dlg.get_connection()
            for i, c in enumerate(self.connections):
                if c["name"] == conn["name"]:
                    self.connections[i] = updated_conn
                    break
            save_config({"connections": self.connections})
            self.populate_connections()

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def disconnect_selected_connection(self):
        item = self.tree_widget.currentItem()
        if item:
            data = item.data(0, Qt.UserRole)
            if data and data.get("type") == "connection":
                self.disconnect_connection(item)

    def reload_selected_connection(self):
        item = self.tree_widget.currentItem()
        if item:
            data = item.data(0, Qt.UserRole)
            if data and data.get("type") == "connection":
                # Desconecta y vuelve a conectar (recarga bases de datos)
                self.disconnect_connection(item)
                self.expand_and_connect(item)

