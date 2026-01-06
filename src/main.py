import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from core.habits import Tarea
from core.ai_engine import generar_reporte
from database.db_manager import crear_base_de_datos, guardar_tarea, cargar_tareas, actualizar_tarea, eliminar_tarea

# Punto de entrada de la aplicación
if __name__ == "__main__":
    # 1. Se asegura que la BD exista
    crear_base_de_datos()
    
    # 2. Se inicializa el motor gráfico
    app = QApplication(sys.argv)
    
    # 3. Creo y muestro la ventana
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    ventana = MainWindow()
    ventana.show()
    
    # 4. Entro en el bucle de eventos (esperar clics)
    sys.exit(app.exec())
