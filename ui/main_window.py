from PyQt5.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QMessageBox,
    QVBoxLayout,
    QTextEdit,
    QSplitter,
)
from PyQt5.QtCore import Qt
from db.connection_manager import ConnectionManager
from ui.table_tab import TableTab
from widgets.connection_modal import load_config, save_config


class MainWindow(QMainWindow):
    def __init__(self, connections=None):
        super().__init__()
        self.setWindowTitle("IDE MariaDB JSON")
        self.setGeometry(100, 100, 1600, 900)
        self.showMaximized()
        if connections is None:
            config = load_config()
            self.connections = config.get("connections", [])
        else:
            self.connections = connections
        self.conn_manager = ConnectionManager(self.connections)
        # Panel central con splitter para terminal
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.tab_widget = QTabWidget()
        self.splitter.addWidget(self.tab_widget)
        # Terminal/log inferior
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMaximumHeight(180)
        self.terminal.setMinimumHeight(80)
        self.terminal.hide()  # Oculto por defecto
        self.splitter.addWidget(self.terminal)
        self.setCentralWidget(self.splitter)
        # Dock lateral derecho
        self.dock = QDockWidget("Conexiones/Bases/Tablas", self)
        self.dock.setAllowedAreas(Qt.RightDockWidgetArea)
        # Menú superior con botones +, -, ✎
        menu_widget = QWidget()
        menu_layout = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.del_btn = QPushButton("-")
        self.edit_btn = QPushButton("✎")
        menu_layout.addWidget(self.add_btn)
        menu_layout.addWidget(self.del_btn)
        menu_layout.addWidget(self.edit_btn)
        menu_layout.addStretch()
        menu_widget.setLayout(menu_layout)
        # Widget principal del dock
        dock_main = QWidget()
        dock_layout = QVBoxLayout()
        dock_layout.addWidget(menu_widget)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Conexiones/Bases/Tablas"])
        dock_layout.addWidget(self.tree_widget)
        dock_main.setLayout(dock_layout)
        self.dock.setWidget(dock_main)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.populate_connections()
        self.tree_widget.itemExpanded.connect(self.handle_tree_expand)
        self.tree_widget.itemDoubleClicked.connect(self.handle_tree_double_click)
        self.add_btn.clicked.connect(self.add_connection)
        self.del_btn.clicked.connect(self.delete_connection)
        self.edit_btn.clicked.connect(self.edit_connection)
        # Barra de estado
        self.statusBar().showMessage("Listo")
        # Atajo para mostrar/ocultar terminal
        self.terminal_shortcut = QPushButton("Terminal")
        self.terminal_shortcut.clicked.connect(self.toggle_terminal)
        self.statusBar().addPermanentWidget(self.terminal_shortcut)

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
        save_config({"connections": self.connections})
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
        if data and data.get("type") == "table":
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

    def add_connection(self):
        from widgets.connection_modal import ConnectionModal

        dlg = ConnectionModal(self)
        if dlg.exec_():
            new_conn = dlg.get_connection()
            self.connections.append(new_conn)
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
            self.populate_connections()
