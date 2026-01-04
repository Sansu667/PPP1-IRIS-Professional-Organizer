import sys
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QDateEdit, QMessageBox, QTextEdit, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QColor
from ui.components.progress_chart import ProgressChart
from core.habits import Tarea
from core.ai_engine import generar_reporte
from database.db_manager import guardar_tarea, cargar_tareas, actualizar_tarea, eliminar_tarea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IRIS - Professional Organizer")
        self.setGeometry(100, 100, 900, 600)
        
        # --- ESTILOS ---
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
                border-radius: 10px;
                border-left: 5px solid #bd93f9; /* Borde morado estilo Iris */
                padding: 20px;
                font-size: 15px;
                line-height: 1.5;
                color: #f8f8f2;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout_principal = QVBoxLayout(central_widget)

        # 1. SECCIÓN IA
        ia_section_layout = QHBoxLayout()
        
        ia_text_layout = QVBoxLayout()
        self.label_titulo = QLabel("🧠 ANÁLISIS DE IRIS")
        self.label_titulo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        ia_text_layout.addWidget(self.label_titulo)

        self.reporte_ia = QLabel("Cargando análisis...")
        self.reporte_ia.setObjectName("ai_report")
        self.reporte_ia.setWordWrap(True)
        ia_text_layout.addWidget(self.reporte_ia)

        ia_section_layout.addLayout(ia_text_layout, 2)


        # Aquí pongo el gráfico
        self.progress_chart = ProgressChart()
        ia_section_layout.addWidget(self.progress_chart, 1)
        
        self.layout_principal.addLayout(ia_section_layout)
        
        # 2. SECCIÓN DE INPUTS
        input_layout = QHBoxLayout()
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre de la tarea...")
        
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")

        self.btn_agregar = QPushButton("Crear Tarea")
        self.btn_agregar.clicked.connect(self.agregar_tarea)

        input_layout.addWidget(self.input_nombre, 2)
        input_layout.addWidget(self.input_fecha, 1)
        input_layout.addWidget(self.btn_agregar, 1)
        
        self.layout_principal.addLayout(input_layout)

        # 3. SECCIÓN TABLA
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Tarea", "Fecha Límite", "Estado", "Éxito"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(40)
        self.tabla.setColumnHidden(0, True) 
        self.layout_principal.addWidget(self.tabla)

        # --- 4. SECCIÓN BOTONES DE ACCIÓN ---
        botones_layout = QHBoxLayout()
        
        # Primero CREAMOS los botones
        self.btn_completar = QPushButton("✔️ Completar")
        self.btn_completar.setObjectName("btn_complete")
        
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setObjectName("btn_delete")

        # El botón agregar ya lo habías creado arriba en la sección de INPUTS, 
        # así que solo le actualizamos el texto aquí
        self.btn_agregar.setText("➕ Crear Tarea")

        # Definimos la función de sombra (la sacamos del bucle para que sea más limpio)
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor

        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(3)
            sombra.setColor(QColor(0, 0, 0, 150))
            widget.setGraphicsEffect(sombra)

        # Ahora que ya existen todos, aplicamos las sombras
        aplicar_sombra(self.btn_agregar)
        aplicar_sombra(self.btn_completar)
        aplicar_sombra(self.btn_eliminar)

        # Conectamos las funciones a los botones
        self.btn_completar.clicked.connect(self.completar_tarea_seleccionada)
        self.btn_eliminar.clicked.connect(self.eliminar_tarea_seleccionada)

        # Añadimos los botones al layout horizontal
        botones_layout.addStretch() # Esto los empuja a la derecha
        botones_layout.addWidget(self.btn_completar)
        botones_layout.addWidget(self.btn_eliminar)
        
        # Añadimos el layout de botones al layout principal
        self.layout_principal.addLayout(botones_layout)

        # --- 5. CONSOLA DE LOGS/FEEDBACK DE IRIS ---
        self.ai_log = QTextEdit()
        self.ai_log.setReadOnly(True)
        self.ai_log.setPlaceholderText("Iris te dará feedback y consejos aquí...")
        self.ai_log.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Monospace';
            }
        """)
        self.layout_principal.addWidget(self.ai_log)

        # Finalmente cargamos los datos
        self.cargar_datos()

    def cargar_datos(self):
        self.mis_tareas = cargar_tareas()
        self.tabla.setRowCount(0)
        
        # 1. Actualizar IA
        mensaje_ia = generar_reporte(self.mis_tareas)
        self.reporte_ia.setText(mensaje_ia)

        # 2. Actualizar Gráfico Circular (Donut Chart)
        if self.mis_tareas:
            suma_exito = sum(t.porcentaje_exito for t in self.mis_tareas)
            promedio_general = suma_exito / len(self.mis_tareas)
            self.progress_chart.update_chart(promedio_general)
        else:
            self.progress_chart.update_chart(0)

        hoy = datetime.now().date()

        # 3. Poblar la Tabla
        for row, tarea in enumerate(self.mis_tareas):
            self.tabla.insertRow(row)
            fecha_tarea = tarea.fecha_limite.date()
            
            # Lógica de colores de fondo para las celdas de texto
            color_fondo = None
            if tarea.completada:
                color_fondo = QColor("#2e7d32") # Verde
            elif fecha_tarea < hoy:
                color_fondo = QColor("#c62828") # Rojo
            
            def crear_celda(texto):
                item = QTableWidgetItem(str(texto))
                if color_fondo:
                    item.setBackground(color_fondo)
                    item.setForeground(Qt.GlobalColor.white)
                return item

            # Insertar datos en columnas 0 a 3
            self.tabla.setItem(row, 0, crear_celda(tarea.id))
            self.tabla.setItem(row, 1, crear_celda(tarea.nombre))
            self.tabla.setItem(row, 2, crear_celda(tarea.fecha_limite.strftime('%Y-%m-%d')))
            estado_texto = "Completada" if tarea.completada else "Pendiente"
            self.tabla.setItem(row, 3, crear_celda(estado_texto))
            
            # --- 4. COLUMNA DE ÉXITO (Solo la Barra de Progreso) ---
            # Eliminamos la línea self.tabla.setItem(row, 4, ...) para que no haya texto detrás de la barra
            
            progreso_bar = QProgressBar()
            
            # CORRECCIÓN DEL ERROR: Convertir float a int
            valor_entero = int(tarea.porcentaje_exito) 
            progreso_bar.setValue(valor_entero)
            
            progreso_bar.setTextVisible(True)
            progreso_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Estilo moderno para la barra
            progreso_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #3e3e3e;
                    border-radius: 5px;
                    background-color: #2d2d2d;
                    text-align: center;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 #007acc, stop:1 #00d4ff);
                    border-radius: 4px;
                }
            """)

            # Colocamos el Widget en la columna 4
            self.tabla.setCellWidget(row, 4, progreso_bar)

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
        self.ai_log.append(f"🤖 Iris: Tarea '{nombre}' creada. ¡A por ella!")

    def completar_tarea_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return 
        
        # Obtengo el ID de la columna oculta (columna 0)
        id_tarea = int(self.tabla.item(fila, 0).text())
        
        # Busco el objeto tarea correspondiente en la lista en memoria
        tarea_obj = next((t for t in self.mis_tareas if t.id == id_tarea), None)
        
        if tarea_obj:
            tarea_obj.marcar_como_completada()
            actualizar_tarea(tarea_obj.id, tarea_obj.completada, tarea_obj.porcentaje_exito)
            self.cargar_datos()
            QMessageBox.information(self, "¡Felicidades!", f"Tarea completada. Éxito: {tarea_obj.porcentaje_exito}%")
            self.ai_log.append(f"🤖 Iris: ¡Felicidades! Completaste '{tarea_obj.nombre}' con {tarea_obj.porcentaje_exito}% de éxito.")

    def eliminar_tarea_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return
        
        # 1. Identificamos la tarea antes de borrarla
        id_tarea = int(self.tabla.item(fila, 0).text())
        # Busco el objeto en nuestra lista para saber su nombre
        tarea_a_eliminar = next((t for t in self.mis_tareas if t.id == id_tarea), None)

        if not tarea_a_eliminar:
            return

        confirmacion = QMessageBox.question(self, "Borrar", f"¿Seguro que quieres borrar '{tarea_a_eliminar.nombre}'?", 
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            eliminar_tarea(id_tarea)
            
            nombre_borrado = tarea_a_eliminar.nombre
            
            self.cargar_datos()
            
            self.ai_log.append(f"🤖 Iris: '{nombre_borrado}' eliminada de tu lista.")

    def closeEvent(self, event):
        """Asegura que la base de datos y los gráficos se cierren correctamente"""
        # Aquí podrías añadir un mensaje de despedida en el log si quisieras
        print("Cerrando Iris de forma segura...")
        event.accept()