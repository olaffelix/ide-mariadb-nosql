from PyQt5.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow

if __name__ == '__main__':
    connections = []
    app = QApplication(sys.argv)
    window = MainWindow(connections)
    window.show()
    sys.exit(app.exec_())

