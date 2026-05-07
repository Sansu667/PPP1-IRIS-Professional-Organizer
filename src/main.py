import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from database.db_manager import crear_base_de_datos

if __name__ == "__main__":
    crear_base_de_datos()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())
