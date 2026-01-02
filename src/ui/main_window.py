import sys
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QColor

# Importamos tu lógica existente
from core.habits import Tarea
from core.ai_engine import generar_reporte
from database.db_manager import guardar_tarea, cargar_tareas, actualizar_tarea, eliminar_tarea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IRIS - Professional Organizer")
        self.setGeometry(100, 100, 900, 600) # Tamaño inicial
        
        # --- ESTILOS (CSS) ---
        # Aquí definimos el look "Dark Professional"
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #ffffff; font-size: 14px; }
            QLineEdit, QDateEdit { 
                padding: 8px; 
                background-color: #2d2d2d; 
                color: white; 
                border: 1px solid #3e3e3e; 
                border-radius: 4px;
            }
            QTableWidget {
                background-color: #252526;
                color: #dcdcdc;
                gridline-color: #3e3e3e;
                border: none;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: 1px solid #3e3e3e;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton#btn_delete { background-color: #d32f2f; }
            QPushButton#btn_delete:hover { background-color: #f44336; }
            QPushButton#btn_complete { background-color: #388e3c; }
            QPushButton#btn_complete:hover { background-color: #4caf50; }
            
            QLabel#ai_report {
                background-color: #2d2d2d;
                border-left: 5px solid #bd93f9; /* Borde morado estilo Iris */
                padding: 15px;
                font-style: italic;
                color: #f8f8f2;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout_principal = QVBoxLayout(central_widget)

        # 1. SECCIÓN IA (Cerebro)
        self.label_titulo = QLabel("🧠 ANÁLISIS DE IRIS")
        self.label_titulo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.layout_principal.addWidget(self.label_titulo)

        self.reporte_ia = QLabel("Cargando análisis...")
        self.reporte_ia.setObjectName("ai_report") # Para aplicar el estilo especial
        self.reporte_ia.setWordWrap(True) # Para que el texto baje si es muy largo
        self.layout_principal.addWidget(self.reporte_ia)

        # 2. SECCIÓN DE INPUTS (Crear Tarea)
        input_layout = QHBoxLayout()
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre de la tarea...")
        
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True) # Muestra calendario al hacer clic
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")

        self.btn_agregar = QPushButton("Crear Tarea")
        self.btn_agregar.clicked.connect(self.agregar_tarea)

        input_layout.addWidget(self.input_nombre, 2) # El 2 significa que ocupa el doble de espacio
        input_layout.addWidget(self.input_fecha, 1)
        input_layout.addWidget(self.btn_agregar, 1)
        
        self.layout_principal.addLayout(input_layout)

        # 3. SECCIÓN TABLA (Lista de Tareas)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Tarea", "Fecha Límite", "Estado", "Éxito"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # Ajusta columnas
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Selecciona fila completa
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection) # Solo una a la vez
        self.tabla.verticalHeader().setVisible(False) # Ocultar números de fila feos
        
        # Ocultamos la columna ID (columna 0) porque al usuario no le interesa ver el número técnico
        self.tabla.setColumnHidden(0, True) 

        self.layout_principal.addWidget(self.tabla)

        # 4. SECCIÓN BOTONES DE ACCIÓN
        botones_layout = QHBoxLayout()
        
        self.btn_completar = QPushButton("✅ Marcar Completada")
        self.btn_completar.setObjectName("btn_complete")
        self.btn_completar.clicked.connect(self.completar_tarea_seleccionada)
        
        self.btn_eliminar = QPushButton("🗑️ Eliminar Tarea")
        self.btn_eliminar.setObjectName("btn_delete")
        self.btn_eliminar.clicked.connect(self.eliminar_tarea_seleccionada)

        botones_layout.addStretch() # Empuja los botones a la derecha
        botones_layout.addWidget(self.btn_completar)
        botones_layout.addWidget(self.btn_eliminar)
        
        self.layout_principal.addLayout(botones_layout)

        # Cargar datos al iniciar
        self.cargar_datos()

    def cargar_datos(self):
        self.mis_tareas = cargar_tareas()
        
        # Actualizar IA
        mensaje_ia = generar_reporte(self.mis_tareas)
        self.reporte_ia.setText(mensaje_ia)

        # Actualizar Tabla
        self.tabla.setRowCount(0)
        
        hoy = datetime.now().date() # Fecha de hoy para comparar

        for row, tarea in enumerate(self.mis_tareas):
            self.tabla.insertRow(row)
            
            # Convertimos fecha de tarea a objeto date de Python para comparar
            fecha_tarea = tarea.fecha_limite.date()
            
            # --- LÓGICA DE COLORES ---
            color_fondo = None
            if tarea.completada:
                color_fondo = QColor("#2e7d32") # Verde oscuro (éxito)
            elif fecha_tarea < hoy:
                color_fondo = QColor("#c62828") # Rojo oscuro (vencida)
            
            # Función auxiliar para crear celdas coloreadas
            def crear_celda(texto):
                item = QTableWidgetItem(str(texto))
                if color_fondo:
                    item.setBackground(color_fondo)
                    item.setForeground(Qt.GlobalColor.white) # Texto blanco para contraste
                return item

            # Insertamos los datos usando la celda coloreada
            self.tabla.setItem(row, 0, crear_celda(tarea.id))
            self.tabla.setItem(row, 1, crear_celda(tarea.nombre))
            self.tabla.setItem(row, 2, crear_celda(tarea.fecha_limite.strftime('%Y-%m-%d')))
            
            estado_texto = "Completada" if tarea.completada else "Pendiente"
            self.tabla.setItem(row, 3, crear_celda(estado_texto))
            
            self.tabla.setItem(row, 4, crear_celda(f"{tarea.porcentaje_exito}%"))

    def agregar_tarea(self):
        nombre = self.input_nombre.text()
        fecha = self.input_fecha.date().toString("yyyy-MM-dd")
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío")
            return

        nueva_tarea = Tarea(nombre, fecha)
        guardar_tarea(nueva_tarea)
        
        self.input_nombre.clear()
        self.cargar_datos() # Refrescar interfaz

    def completar_tarea_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return 
        
        # Obtenemos el ID de la columna oculta (columna 0)
        id_tarea = int(self.tabla.item(fila, 0).text())
        
        # Buscamos el objeto tarea correspondiente en la lista en memoria
        tarea_obj = next((t for t in self.mis_tareas if t.id == id_tarea), None)
        
        if tarea_obj:
            tarea_obj.marcar_como_completada()
            actualizar_tarea(tarea_obj.id, tarea_obj.completada, tarea_obj.porcentaje_exito)
            self.cargar_datos()
            QMessageBox.information(self, "¡Felicidades!", f"Tarea completada. Éxito: {tarea_obj.porcentaje_exito}%")

    def eliminar_tarea_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return
        
        confirmacion = QMessageBox.question(self, "Borrar", "¿Estás seguro?", 
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            id_tarea = int(self.tabla.item(fila, 0).text())
            eliminar_tarea(id_tarea)
            self.cargar_datos()