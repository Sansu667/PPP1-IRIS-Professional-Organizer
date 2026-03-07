import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, 
    QTextEdit, QProgressBar, QFrame, QGraphicsDropShadowEffect, QMenu, QSpinBox, QTabWidget,
    QDialog, QDialogButtonBox, QScrollArea, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QDate, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QAction

# Componentes existentes
try:
    from ui.components.progress_chart import ProgressChart
    from ui.components.heatmap_widget import HeatmapWidget
    from ui.components.bar_chart import BarChart
    
    # NUEVOS: Componentes de Finanzas
    from ui.components.pie_chart import PieChart
    from ui.components.transaction_card import TransactionCard
    from ui.components.debt_card import DebtCard
    
    # NUEVOS: Componentes de Libros
    from ui.components.progress_ring import ProgressRing
    from ui.components.book_card import BookCard
    
    # Modelos existentes
    from core.habits import Tarea
    from core.ai_engine import generar_reporte
    
    # NUEVOS: Modelos de Finanzas y Libros
    from core.finance import Transaccion, Deuda
    from core.books import Libro
    
    # Managers existentes
    from database.db_manager import (guardar_tarea, cargar_tareas, actualizar_tarea, 
                                     eliminar_tarea, obtener_historial_heatmap, obtener_kpis, 
                                     obtener_actividad_semanal, actualizar_tarea_completa)
    
    # NUEVOS: Managers de Finanzas y Libros
    from database.finance_db_manager import (
        guardar_transaccion, cargar_transacciones, eliminar_transaccion,
        guardar_deuda, cargar_deudas, actualizar_pago_deuda, eliminar_deuda,
        obtener_balance, obtener_balance_mensual, obtener_gastos_por_categoria,
        obtener_total_deudas
    )
    from database.books_db_manager import (
        guardar_libro, cargar_libros, actualizar_progreso_libro,
        marcar_libro_como_terminado, eliminar_libro, cambiar_estado_libro,
        obtener_estadisticas_lectura, obtener_libro_actual
    )
    
except ImportError as e:
    print(f"Error cargando módulos: {e}")
    print(f"Python path: {sys.path}")

# --- BADGE ---
class StatusBadge(QLabel):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            background-color: {color}20; 
            color: {color}; 
            border: 1px solid {color}; 
            border-radius: 10px; 
            padding: 2px 8px; 
            font-weight: bold; 
            font-size: 10px;
        """)
        self.setFixedSize(100, 22)

# --- BADGE DE PRIORIDAD ---
class PriorityBadge(QLabel):
    def __init__(self, tarea, parent=None):
        icono = tarea.get_prioridad_icono()
        texto = tarea.get_prioridad_texto()
        color = tarea.get_prioridad_color()
        
        super().__init__(f"{icono} {texto}", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            background-color: {color}25; 
            color: {color}; 
            border: 1px solid {color}; 
            border-radius: 8px; 
            padding: 3px 10px; 
            font-weight: bold; 
            font-size: 10px;
            letter-spacing: 0.5px;
        """)
        self.setFixedSize(90, 24)

# --- KPI CARD ---
class StatCard(QFrame):
    def __init__(self, title, value, color, icon="📊"):
        super().__init__()
        self.setObjectName("stat_card")
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16161e);
                border: 1px solid #2f2f45; border-radius: 12px;
            }}
            QLabel {{ background: transparent; }}
        """)
        self.setFixedSize(220, 100)
        l = QVBoxLayout(self)
        t = QLabel(f"{icon} {title}"); t.setStyleSheet("color: #808090; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        self.v = QLabel(str(value)); self.v.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 800;")
        self.v.setAlignment(Qt.AlignmentFlag.AlignRight)
        l.addWidget(t); l.addWidget(self.v)

    def update_value(self, val):
        self.v.setText(str(val))

# --- TARJETA DE TAREA VISUAL CON PRIORIDAD ---
class TaskCard(QFrame):
    def __init__(self, tarea, on_complete, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.tarea = tarea
        self.on_complete = on_complete
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.setObjectName("task_card")
        self.setMinimumHeight(100)
        self.setMaximumHeight(140)
        
        # Estado visual - Color según prioridad si está activa
        hoy = datetime.now().date()
        fecha_limite = tarea.fecha_limite.date() if hasattr(tarea.fecha_limite, 'date') else tarea.fecha_limite
        
        if tarea.completada:
            border_color = "#03dac6"
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a2e2a, stop:1 #16161e)"
        elif fecha_limite < hoy:
            border_color = "#ff5252"
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e1a1a, stop:1 #16161e)"
        else:
            # Usar color de prioridad para tareas activas
            border_color = tarea.get_prioridad_color()
            if tarea.prioridad == "alta":
                bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e1a1a, stop:1 #16161e)"
            elif tarea.prioridad == "media":
                bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e261a, stop:1 #16161e)"
            else:
                bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a252e, stop:1 #16161e)"
        
        self.setStyleSheet(f"""
            QFrame#task_card {{
                background: {bg_gradient};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{ background: transparent; color: #e0e0e0; }}
            QPushButton {{ 
                background: transparent; 
                border: 1px solid #444; 
                border-radius: 4px; 
                padding: 8px 14px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ border-color: #bb86fc; background: rgba(187, 134, 252, 0.1); }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(6)
        
        # TOP ROW: Título y Badges
        top_row = QHBoxLayout()
        
        title = QLabel(tarea.nombre)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        title.setWordWrap(True)
        top_row.addWidget(title, 1)
        
        # Badge de prioridad (solo si no está completada)
        if not tarea.completada:
            priority_badge = PriorityBadge(tarea)
            top_row.addWidget(priority_badge)
        
        # Badge de estado
        if tarea.completada:
            badge = StatusBadge("COMPLETED", "#03dac6")
        elif fecha_limite < hoy:
            badge = StatusBadge("OVERDUE", "#ff5252")
        else:
            badge = StatusBadge("PENDING", "#ffb74d")
        top_row.addWidget(badge)
        
        main_layout.addLayout(top_row)
        
        # MIDDLE ROW: Fecha y Progreso
        mid_row = QHBoxLayout()
        
        # Calcular días restantes/vencidos
        dias_diff = (fecha_limite - hoy).days
        if dias_diff < 0:
            fecha_text = f"📅 {tarea.fecha_limite.strftime('%Y-%m-%d')}  🔥 Vencido hace {abs(dias_diff)} días"
            fecha_color = "#ff5252"
        elif dias_diff == 0:
            fecha_text = f"📅 {tarea.fecha_limite.strftime('%Y-%m-%d')}  ⚡ Vence HOY"
            fecha_color = "#ffb74d"
        elif dias_diff <= 3:
            fecha_text = f"📅 {tarea.fecha_limite.strftime('%Y-%m-%d')}  ⚡ Vence en {dias_diff} días"
            fecha_color = "#ffb74d"
        else:
            fecha_text = f"📅 {tarea.fecha_limite.strftime('%Y-%m-%d')}  ✨ Vence en {dias_diff} días"
            fecha_color = "#808090"
        
        fecha_label = QLabel(fecha_text)
        fecha_label.setStyleSheet(f"color: {fecha_color}; font-size: 11px; font-weight: bold;")
        mid_row.addWidget(fecha_label)
        
        mid_row.addStretch()
        
        progress_label = QLabel(f"XP: {int(tarea.porcentaje_exito)}%")
        progress_label.setStyleSheet(f"color: {border_color}; font-weight: bold; font-size: 12px;")
        mid_row.addWidget(progress_label)
        
        main_layout.addLayout(mid_row)
        
        # PROGRESS BAR
        progress_bar = QProgressBar()
        progress_bar.setValue(int(tarea.porcentaje_exito))
        progress_bar.setFixedHeight(6)
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: #2d2d36;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {border_color};
                border-radius: 3px;
            }}
        """)
        main_layout.addWidget(progress_bar)
        
        # BOTTOM ROW: Botones de acción
        if not tarea.completada:
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            
            btn_edit = QPushButton("✏️ Edit")
            btn_edit.setMinimumWidth(80)
            btn_edit.setMinimumHeight(32)
            btn_edit.clicked.connect(lambda: self.on_edit(tarea))
            btn_row.addWidget(btn_edit)
            
            btn_complete = QPushButton("✓ Complete")
            btn_complete.setMinimumWidth(120)
            btn_complete.setMinimumHeight(32)
            btn_complete.setStyleSheet("""
                QPushButton { 
                    background: #03dac6; 
                    color: black; 
                    border: none;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #00ffaa; }
            """)
            btn_complete.clicked.connect(lambda: self.on_complete(tarea))
            btn_row.addWidget(btn_complete)
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setFixedWidth(40)
            btn_delete.setMinimumHeight(32)
            btn_delete.setStyleSheet("""
                QPushButton { 
                    background: transparent; 
                    border: 1px solid #ff5252;
                    color: #ff5252;
                    font-size: 14px;
                }
                QPushButton:hover { background: #ff525220; }
            """)
            btn_delete.clicked.connect(lambda: self.on_delete(tarea))
            btn_row.addWidget(btn_delete)
            
            main_layout.addLayout(btn_row)
        
        # Efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

# --- DIÁLOGO DE EDICIÓN CON PRIORIDAD ---
class EditTaskDialog(QDialog):
    def __init__(self, tarea, parent=None):
        super().__init__(parent)
        self.tarea = tarea
        self.setWindowTitle("Editar Tarea")
        self.setModal(True)
        self.setFixedWidth(450)
        
        self.setStyleSheet("""
            QDialog { background: #16161e; }
            QLabel { color: #e0e0e0; font-size: 13px; }
            QLineEdit, QDateEdit, QComboBox { 
                padding: 10px; 
                background: #20202a; 
                color: white; 
                border: 1px solid #333340; 
                border-radius: 6px; 
                font-size: 13px; 
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus { border: 1px solid #7c4dff; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border: none; }
            QPushButton {
                background: #6200ea;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover { background: #7c4dff; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Nombre
        layout.addWidget(QLabel("Nombre de la tarea:"))
        self.txt_nombre = QLineEdit(tarea.nombre)
        layout.addWidget(self.txt_nombre)
        
        # Fecha
        layout.addWidget(QLabel("Fecha límite:"))
        self.date_limite = QDateEdit()
        fecha = tarea.fecha_limite.date() if hasattr(tarea.fecha_limite, 'date') else tarea.fecha_limite
        self.date_limite.setDate(QDate(fecha.year, fecha.month, fecha.day))
        layout.addWidget(self.date_limite)
        
        # Prioridad
        layout.addWidget(QLabel("Prioridad:"))
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItem("🔥 ALTA", "alta")
        self.combo_prioridad.addItem("⚡ MEDIA", "media")
        self.combo_prioridad.addItem("📌 BAJA", "baja")
        
        # Seleccionar prioridad actual
        if tarea.prioridad == "alta":
            self.combo_prioridad.setCurrentIndex(0)
        elif tarea.prioridad == "media":
            self.combo_prioridad.setCurrentIndex(1)
        else:
            self.combo_prioridad.setCurrentIndex(2)
        
        layout.addWidget(self.combo_prioridad)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self):
        return {
            'nombre': self.txt_nombre.text(),
            'fecha': self.date_limite.date().toString("yyyy-MM-dd"),
            'prioridad': self.combo_prioridad.currentData()
        }

# --- ESTILOS VISUALES ---
STYLE_SHEET = """
    * { font-family: 'Segoe UI', sans-serif; }
    QMainWindow { background-color: #0d0d12; } 
    QLabel { color: #e0e0e0; font-size: 14px; }
    
    QTabWidget::pane { border: 1px solid #252530; background: #0d0d12; border-radius: 8px; top: -1px; }
    QTabBar::tab { background: #16161e; color: #808090; padding: 10px 25px; margin-right: 5px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-weight: bold; }
    QTabBar::tab:selected { background: #252530; color: #bb86fc; border-bottom: 2px solid #bb86fc; }

    QFrame#card { background: #16161e; border-radius: 12px; border: 1px solid #252530; }
    QFrame#dashboard_card { 
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #131325); 
        border-radius: 12px; border: 1px solid #2f2f45; 
    }
    
    QLineEdit, QDateEdit, QComboBox { padding: 10px; background: #20202a; color: white; border: 1px solid #333340; border-radius: 6px; font-size: 13px; }
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus { border: 1px solid #7c4dff; background-color: #252530; }
    
    QComboBox::drop-down { border: none; width: 25px; }
    QComboBox::down-arrow { image: none; border: none; }
    
    QSpinBox { background: #20202a; border: 1px solid #333340; border-radius: 6px; color: #03dac6; font-weight: bold; padding: 8px; font-size: 14px; }
    QSpinBox::up-button, QSpinBox::down-button { width: 0px; }
    
    QPushButton { background: #6200ea; color: white; border-radius: 6px; font-weight: bold; border: none; padding: 10px 20px; font-size: 13px; }
    QPushButton:hover { background: #7c4dff; }
    QPushButton#btn_complete { background-color: #03dac6; color: #000; }
    QPushButton#btn_delete { background-color: transparent; color: #ff5252; border: 1px solid #ff5252; }
    
    QPushButton#btn_action { background-color: #252530; border: 1px solid #444; color: #ccc; }
    QPushButton#btn_action:hover { border: 1px solid #fff; color: white; }

    QScrollArea { border: none; background: transparent; }
    
    QTextEdit { background: #0f0f13; border: 1px solid #333; border-radius: 8px; color: #00ffaa; font-family: Consolas; font-size: 11px; padding: 5px; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IRIS - Neural Task Organizer v2.0 🔥")
        self.resize(1250, 880) 
        self.setStyleSheet(STYLE_SHEET)

        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(25,25,25,25); main_layout.setSpacing(20)

        # HEADER
        h_layout = QHBoxLayout()
        lbl = QLabel("🧠  IRIS ORGANIZER"); lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: white; letter-spacing: 1.5px;")
        h_layout.addWidget(lbl); h_layout.addStretch()
        main_layout.addLayout(h_layout)

        # TABS PRINCIPALES
        # TABS PRINCIPALES
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.tab_dash = QWidget(); self.setup_dashboard(); self.tabs.addTab(self.tab_dash, "📊 Dashboard")
        self.tab_tasks = QWidget(); self.setup_tasks(); self.tabs.addTab(self.tab_tasks, "📝 Tasks")
        
        # NUEVAS PESTAÑAS DE FINANZAS Y LIBROS
        self.tab_finance = QWidget(); self.setup_finance(); self.tabs.addTab(self.tab_finance, "💰 Finanzas")
        self.tab_books = QWidget(); self.setup_books(); self.tabs.addTab(self.tab_books, "📚 Libros")
        
        self.tab_analytics = QWidget(); self.setup_analytics(); self.tabs.addTab(self.tab_analytics, "📈 Analytics")

        # LOG
        self.ai_log = QTextEdit(); self.ai_log.setReadOnly(True); self.ai_log.setFixedHeight(50)
        self.ai_log.setPlaceholderText("System initialized...")
        main_layout.addWidget(self.ai_log)

        # VARS
        self.tiempo_restante = 25 * 60; self.timer_pausado = False
        self.timer = QTimer(); self.timer.timeout.connect(self.tick)
        
        self.cargar_datos()
        self.tabs.currentChanged.connect(self.tab_changed)

    def setup_dashboard(self):
        layout = QVBoxLayout(self.tab_dash); layout.setContentsMargins(10,20,10,10); layout.setSpacing(25)
        
        # --- TOP CARD ---
        self.top_card = QFrame(); self.top_card.setObjectName("dashboard_card")
        self.top_card.setFixedHeight(340) 
        
        tc_layout = QHBoxLayout(self.top_card); tc_layout.setContentsMargins(40, 30, 40, 30); tc_layout.setSpacing(50)

        # 1. IA
        ia_l = QVBoxLayout(); ia_l.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.lbl_ia_title = QLabel("ANALYSIS"); self.lbl_ia_title.setStyleSheet("color: #bb86fc; font-weight: bold; font-size: 12px; letter-spacing: 1.2px; margin-bottom: 8px;")
        self.lbl_feedback = QLabel("Conectando con el núcleo..."); 
        self.lbl_feedback.setWordWrap(True)
        self.lbl_feedback.setStyleSheet("color: #e0e0e0; font-size: 15px; line-height: 1.6; font-weight: 400;")
        ia_l.addWidget(self.lbl_ia_title); ia_l.addWidget(self.lbl_feedback)
        tc_layout.addLayout(ia_l, 4)

        # 2. TIMER
        tm_l = QVBoxLayout(); 
        tm_l.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        tm_l.setSpacing(20)
        tm_l.addStretch()

        self.lbl_time = QLabel("25:00")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 72px; font-weight: bold; color: white;")
        
        self.time_ctrl = QWidget()
        h_selector = QHBoxLayout(self.time_ctrl)
        h_selector.setContentsMargins(0,0,0,0)
        h_selector.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.spin = QSpinBox(); self.spin.setRange(1, 180); self.spin.setValue(25); self.spin.setSuffix(" min"); self.spin.setFixedWidth(100)
        self.spin.valueChanged.connect(self.update_timer_label_init)
        
        h_selector.addWidget(QLabel("Focus:", styleSheet="color:#808090; font-size:13px; font-weight:bold; margin-right:10px;"))
        h_selector.addWidget(self.spin)
        
        btns_wrapper = QWidget()
        h_btns = QHBoxLayout(btns_wrapper)
        h_btns.setContentsMargins(0,0,0,0)
        h_btns.setSpacing(15)
        h_btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_focus = QPushButton("START FOCUS")
        self.btn_focus.setFixedSize(150, 45)
        self.btn_focus.clicked.connect(self.toggle_timer)
        
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setObjectName("btn_action")
        self.btn_reset.setFixedSize(100, 45)
        self.btn_reset.clicked.connect(self.reset_timer)

        h_btns.addWidget(self.btn_focus)
        h_btns.addWidget(self.btn_reset)

        tm_l.addWidget(self.lbl_time)
        tm_l.addWidget(self.time_ctrl)
        tm_l.addWidget(btns_wrapper)
        tm_l.addStretch()
        
        tc_layout.addLayout(tm_l, 3)

        # 3. CHART
        ch_l = QVBoxLayout()
        ch_l.addStretch() 
        lbl_disc = QLabel("DISCIPLINE"); lbl_disc.setStyleSheet("color: #bb86fc; font-weight: bold; font-size: 12px; letter-spacing: 1.2px; margin-bottom: 5px;")
        lbl_disc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ch_l.addWidget(lbl_disc)
        self.chart = ProgressChart(); ch_l.addWidget(self.chart, 0, Qt.AlignmentFlag.AlignCenter) 
        ch_l.addStretch()
        tc_layout.addLayout(ch_l, 3)
        
        layout.addWidget(self.top_card)
        self.shadow(self.top_card)

    def setup_tasks(self):
        """Nueva pestaña de tareas mejorada con tarjetas visuales y prioridades"""
        layout = QVBoxLayout(self.tab_tasks)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)
        
        # INPUT PARA NUEVA TAREA
        input_card = QFrame()
        input_card.setObjectName("card")
        input_card.setFixedHeight(130)
        
        ic_layout = QVBoxLayout(input_card)
        ic_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_input = QLabel("➕ Nueva Misión")
        lbl_input.setStyleSheet("font-weight: bold; color: #bb86fc; font-size: 13px;")
        ic_layout.addWidget(lbl_input)
        
        # Primera fila: Nombre
        in_row1 = QHBoxLayout()
        self.txt_task = QLineEdit()
        self.txt_task.setPlaceholderText("✨ Describe tu próxima misión...")
        self.txt_task.setMinimumHeight(35)
        in_row1.addWidget(self.txt_task)
        ic_layout.addLayout(in_row1)
        
        # Segunda fila: Fecha + Prioridad + Botón
        in_row2 = QHBoxLayout()
        
        self.date_task = QDateEdit()
        self.date_task.setDate(QDate.currentDate())
        self.date_task.setFixedWidth(140)
        self.date_task.setMinimumHeight(45)
        in_row2.addWidget(self.date_task)
        
        self.combo_priority = QComboBox()
        self.combo_priority.addItem("🔥 ALTA", "alta")
        self.combo_priority.addItem("⚡ MEDIA", "media")
        self.combo_priority.addItem("📌 BAJA", "baja")
        self.combo_priority.setCurrentIndex(1)  # Media por defecto
        self.combo_priority.setFixedWidth(140)
        self.combo_priority.setMinimumHeight(45)
        in_row2.addWidget(self.combo_priority)
        
        btn_add = QPushButton("ADD MISSION")
        btn_add.setMinimumHeight(45)
        btn_add.setMinimumWidth(150)
        btn_add.clicked.connect(self.add_task)
        in_row2.addWidget(btn_add)
        
        ic_layout.addLayout(in_row2)
        
        layout.addWidget(input_card)
        self.shadow(input_card)
        
        # SUB-TABS PARA ACTIVAS Y COMPLETADAS
        self.task_tabs = QTabWidget()
        layout.addWidget(self.task_tabs)
        
        # TAB: TAREAS ACTIVAS
        self.active_tab = QWidget()
        active_layout = QVBoxLayout(self.active_tab)
        active_layout.setContentsMargins(0, 10, 0, 0)
        
        active_scroll = QScrollArea()
        active_scroll.setWidgetResizable(True)
        active_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        active_scroll.setMaximumHeight(500)
        
        self.active_container = QWidget()
        self.active_layout = QVBoxLayout(self.active_container)
        self.active_layout.setSpacing(12)
        self.active_layout.setContentsMargins(5, 5, 5, 5)
        self.active_layout.addStretch()
        
        active_scroll.setWidget(self.active_container)
        active_layout.addWidget(active_scroll)
        
        self.task_tabs.addTab(self.active_tab, f"🎯 Active (0)")
        
        # TAB: TAREAS COMPLETADAS
        self.completed_tab = QWidget()
        completed_layout = QVBoxLayout(self.completed_tab)
        completed_layout.setContentsMargins(0, 10, 0, 0)
        
        completed_scroll = QScrollArea()
        completed_scroll.setWidgetResizable(True)
        completed_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        completed_scroll.setMaximumHeight(500)
        
        self.completed_container = QWidget()
        self.completed_layout = QVBoxLayout(self.completed_container)
        self.completed_layout.setSpacing(12)
        self.completed_layout.setContentsMargins(5, 5, 5, 5)
        self.completed_layout.addStretch()
        
        completed_scroll.setWidget(self.completed_container)
        completed_layout.addWidget(completed_scroll)
        
        self.task_tabs.addTab(self.completed_tab, f"✅ Completed (0)")

    def setup_analytics(self):
        main_l = QVBoxLayout(self.tab_analytics)
        main_l.setContentsMargins(20, 20, 20, 20)
        main_l.setSpacing(20)
        
        # KPI CARDS
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        self.card_total = StatCard("TOTAL COMPLETED", "0", "white", "🏆")
        self.card_streak = StatCard("CURRENT STREAK", "0 Days", "#03dac6", "🔥")
        self.card_rate = StatCard("SUCCESS RATE", "0%", "#bb86fc", "📈")
        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_streak)
        kpi_layout.addWidget(self.card_rate)
        main_l.addLayout(kpi_layout)

        # HEATMAP
        try:
            self.hm_w = HeatmapWidget()
            hm_frame = QFrame(); hm_frame.setObjectName("card")
            l = QVBoxLayout(hm_frame); l.addWidget(self.hm_w)
            main_l.addWidget(hm_frame)
            self.shadow(hm_frame)
        except: pass

        # BAR CHART
        try:
            bar_frame = QFrame(); bar_frame.setObjectName("card")
            l_bar = QVBoxLayout(bar_frame)
            
            lbl_bar = QLabel("📊 Actividad Semanal")
            lbl_bar.setStyleSheet("color: white; font-weight: bold; font-size: 13px; margin-bottom: 10px;")
            l_bar.addWidget(lbl_bar)
            
            self.bar_chart = BarChart()
            l_bar.addWidget(self.bar_chart)
            
            main_l.addWidget(bar_frame)
            self.shadow(bar_frame)
        except: pass
        
        main_l.addStretch()

    def shadow(self, w):
        eff = QGraphicsDropShadowEffect(); eff.setBlurRadius(20); eff.setColor(QColor(0,0,0,80)); eff.setYOffset(4)
        w.setGraphicsEffect(eff)

    # --- TASK MANAGEMENT ---
    def clear_layout(self, layout):
        """Limpia un layout de todos sus widgets"""
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def render_tasks(self):
        """Renderiza las tareas en sus respectivas pestañas"""
        self.clear_layout(self.active_layout)
        self.clear_layout(self.completed_layout)
        
        active_count = 0
        completed_count = 0
        
        for tarea in self.tasks:
            card = TaskCard(
                tarea,
                on_complete=self.complete_task,
                on_edit=self.edit_task,
                on_delete=self.delete_task
            )
            
            if tarea.completada:
                self.completed_layout.addWidget(card)
                completed_count += 1
            else:
                self.active_layout.addWidget(card)
                active_count += 1
        
        self.task_tabs.setTabText(0, f"🎯 Active ({active_count})")
        self.task_tabs.setTabText(1, f"✅ Completed ({completed_count})")
        
        if active_count == 0:
            empty_label = QLabel("No hay tareas activas. ¡Crea una nueva misión!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.active_layout.addWidget(empty_label)
        
        if completed_count == 0:
            empty_label = QLabel("Aún no has completado ninguna tarea.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.completed_layout.addWidget(empty_label)

    def complete_task(self, tarea):
        """Completa una tarea"""
        actualizar_tarea(tarea.id, True, 100)
        self.ai_log.append(f"🏆 [{datetime.now().strftime('%H:%M')}] Complete: {tarea.nombre}")
        self.cargar_datos()
    
    def edit_task(self, tarea):
        """Abre diálogo para editar tarea"""
        dialog = EditTaskDialog(tarea, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            actualizar_tarea_completa(tarea.id, data['nombre'], data['fecha'], data['prioridad'])
            self.ai_log.append(f"✏️ [{datetime.now().strftime('%H:%M')}] Edited: {tarea.nombre}")
            self.cargar_datos()
    
    def delete_task(self, tarea):
        """Elimina una tarea con confirmación"""
        reply = QMessageBox.question(
            self, 
            'Confirmar eliminación',
            f'¿Estás seguro de eliminar "{tarea.nombre}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            eliminar_tarea(tarea.id)
            self.ai_log.append(f"🗑️ [{datetime.now().strftime('%H:%M')}] Deleted: {tarea.nombre}")
            self.cargar_datos()

    # --- LOGIC ---
    def tab_changed(self, i):
        """Se ejecuta al cambiar de pestaña principal"""
        if i == 2:  # Finanzas
            self.actualizar_dashboard_finanzas()
            self.cargar_transacciones()
            self.cargar_deudas()
        elif i == 3:  # Libros
            self.cargar_libro_actual()
            self.cargar_libros()
        elif i == 4:  # Analytics (antes era índice 2, ahora es 4)
            try: 
                self.hm_w.update_heatmap(obtener_historial_heatmap())
                stats = obtener_kpis()
                self.card_total.update_value(stats["total"])
                self.card_streak.update_value(f"{stats['streak']} Days")
                self.card_rate.update_value(f"{stats['promedio']:.1f}%")
                semana = obtener_actividad_semanal()
                self.bar_chart.update_data(semana)
            except Exception as e: 
                print(f"Error actualizando analytics: {e}")

    def cargar_datos(self):
        self.tasks = cargar_tareas()
        
        try: 
            self.lbl_feedback.setText(generar_reporte(self.tasks))
        except: 
            self.lbl_feedback.setText("Sistemas listos. Esperando misiones...")

        if self.tasks:
            avg = sum(t.porcentaje_exito for t in self.tasks) / len(self.tasks)
            self.chart.update_chart(avg)
        else: 
            self.chart.update_chart(0)
        
        self.render_tasks()

    # --- TIMER LOGIC ---
    def update_timer_label_init(self):
        if not self.timer.isActive() and not self.timer_pausado:
            self.lbl_time.setText(f"{self.spin.value():02d}:00")

    def toggle_timer(self):
        if not self.timer.isActive():
            if not self.timer_pausado:
                self.tiempo_restante = self.spin.value() * 60
                self.ai_log.append(f"⚡ [{datetime.now().strftime('%H:%M')}] Focus session started: {self.spin.value()} min")
            else: 
                self.ai_log.append(f"▶️ [{datetime.now().strftime('%H:%M')}] Session resumed")
            
            self.time_ctrl.hide()
            self.timer.start(1000)
            self.btn_focus.setText("PAUSE")
            self.btn_focus.setStyleSheet("background: #ff5252; color: white;")
            self.timer_pausado = False
        else:
            self.timer.stop()
            self.timer_pausado = True
            self.btn_focus.setText("RESUME")
            self.btn_focus.setStyleSheet("background: #03dac6; color: black;")
            self.ai_log.append(f"⏸ [{datetime.now().strftime('%H:%M')}] Session paused")

    def reset_timer(self):
        self.timer.stop()
        self.timer_pausado = False
        self.tiempo_restante = self.spin.value() * 60
        self.time_ctrl.show()
        self.update_timer_label_init()
        self.btn_focus.setText("START FOCUS")
        self.btn_focus.setStyleSheet("background: #6200ea; color: white;")
        self.ai_log.append(f"↺ [{datetime.now().strftime('%H:%M')}] Timer reset")

    def tick(self):
        self.tiempo_restante -= 1
        if self.tiempo_restante <= 0:
            self.timer.stop()
            self.timer_pausado = False
            self.time_ctrl.show()
            self.update_timer_label_init()
            self.btn_focus.setText("START FOCUS")
            self.btn_focus.setStyleSheet("background: #6200ea; color: white;")
            self.ai_log.append(f"🎉 [{datetime.now().strftime('%H:%M')}] Session completed!")
        else: 
            m, s = divmod(self.tiempo_restante, 60)
            self.lbl_time.setText(f"{m:02d}:{s:02d}")

    # ACTIONS
    def add_task(self):
        if self.txt_task.text().strip():
            prioridad = self.combo_priority.currentData()
            tarea = Tarea(self.txt_task.text(), self.date_task.date().toString("yyyy-MM-dd"), prioridad=prioridad)
            guardar_tarea(tarea)
            self.ai_log.append(f"✨ [{datetime.now().strftime('%H:%M')}] New mission added: {self.txt_task.text()} [{prioridad.upper()}]")
            self.txt_task.clear()
            self.cargar_datos()

    # ==================== MÓDULO DE FINANZAS ====================
    
    def setup_finance(self):
        """Configura la pestaña de Finanzas"""
        main_layout = QVBoxLayout(self.tab_finance)
        main_layout.setContentsMargins(10, 20, 10, 10)
        main_layout.setSpacing(20)
        
        # Sub-tabs: Dashboard, Transacciones, Deudas
        self.finance_tabs = QTabWidget()
        main_layout.addWidget(self.finance_tabs)
        
        # Dashboard de Finanzas
        self.finance_dashboard_tab = QWidget()
        self.setup_finance_dashboard()
        self.finance_tabs.addTab(self.finance_dashboard_tab, "📊 Dashboard")
        
        # Transacciones
        self.transactions_tab = QWidget()
        self.setup_transactions()
        self.finance_tabs.addTab(self.transactions_tab, "💸 Transacciones")
        
        # Deudas
        self.debts_tab = QWidget()
        self.setup_debts()
        self.finance_tabs.addTab(self.debts_tab, "🔴 Deudas")
        
        # Listener para actualizar al cambiar de tab
        self.finance_tabs.currentChanged.connect(self.on_finance_tab_changed)
    
    def setup_finance_dashboard(self):
        """Dashboard de finanzas con balance y gráficos"""
        layout = QVBoxLayout(self.finance_dashboard_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)
        
        # Cards de Balance
        balance_row = QHBoxLayout()
        balance_row.setSpacing(20)
        
        self.card_balance = StatCard("BALANCE", "$0", "white", "💰")
        self.card_ingresos = StatCard("INGRESOS", "$0", "#00c853", "📈")
        self.card_egresos = StatCard("EGRESOS", "$0", "#ff5252", "📉")
        
        balance_row.addWidget(self.card_balance)
        balance_row.addWidget(self.card_ingresos)
        balance_row.addWidget(self.card_egresos)
        layout.addLayout(balance_row)
        
        # Gráfico de distribución
        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_chart = QLabel("📊 Distribución de Gastos por Categoría")
        lbl_chart.setStyleSheet("color: white; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        chart_layout.addWidget(lbl_chart)
        
        self.pie_chart = PieChart()
        chart_layout.addWidget(self.pie_chart)
        
        layout.addWidget(chart_frame)
        self.shadow(chart_frame)
        
        layout.addStretch()
    
    def setup_transactions(self):
        """Pestaña de transacciones"""
        layout = QVBoxLayout(self.transactions_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)
        
        # Formulario para nueva transacción
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_frame.setFixedHeight(200)
        
        form_layout = QVBoxLayout(input_frame)
        form_layout.setContentsMargins(20, 15, 20, 15)
        form_layout.setSpacing(12)
        
        lbl_titulo = QLabel("➕ Nueva Transacción")
        lbl_titulo.setStyleSheet("font-weight: bold; color: #bb86fc; font-size: 13px;")
        form_layout.addWidget(lbl_titulo)
        
        # Primera fila: Título
        self.txt_trans_titulo = QLineEdit()
        self.txt_trans_titulo.setPlaceholderText("Título de la transacción...")
        self.txt_trans_titulo.setMinimumHeight(40)
        form_layout.addWidget(self.txt_trans_titulo)
        
        # Segunda fila: Valor, Tipo, Categoría
        row2 = QHBoxLayout()
        
        self.txt_trans_valor = QLineEdit()
        self.txt_trans_valor.setPlaceholderText("Valor (ej: 50000)")
        self.txt_trans_valor.setMinimumHeight(40)
        self.txt_trans_valor.setFixedWidth(180)
        row2.addWidget(self.txt_trans_valor)
        
        self.combo_trans_tipo = QComboBox()
        self.combo_trans_tipo.addItem("💚 Ingreso", "ingreso")
        self.combo_trans_tipo.addItem("💔 Egreso", "egreso")
        self.combo_trans_tipo.setMinimumHeight(40)
        self.combo_trans_tipo.setFixedWidth(150)
        self.combo_trans_tipo.currentIndexChanged.connect(self.actualizar_categorias_transaccion)
        row2.addWidget(self.combo_trans_tipo)
        
        self.combo_trans_categoria = QComboBox()
        self.combo_trans_categoria.setMinimumHeight(40)
        self.actualizar_categorias_transaccion()
        row2.addWidget(self.combo_trans_categoria)
        
        form_layout.addLayout(row2)
        
        # Tercera fila: Descripción y botón
        row3 = QHBoxLayout()
        
        self.txt_trans_desc = QLineEdit()
        self.txt_trans_desc.setPlaceholderText("Descripción (opcional)")
        self.txt_trans_desc.setMinimumHeight(40)
        row3.addWidget(self.txt_trans_desc)
        
        btn_add_trans = QPushButton("Agregar Transacción")
        btn_add_trans.setMinimumHeight(40)
        btn_add_trans.setMinimumWidth(180)
        btn_add_trans.clicked.connect(self.agregar_transaccion)
        row3.addWidget(btn_add_trans)
        
        form_layout.addLayout(row3)
        
        layout.addWidget(input_frame)
        self.shadow(input_frame)
        
        # Lista de transacciones
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.transactions_container = QWidget()
        self.transactions_layout = QVBoxLayout(self.transactions_container)
        self.transactions_layout.setSpacing(15)
        self.transactions_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(self.transactions_container)
        layout.addWidget(scroll)
    
    def setup_debts(self):
        """Pestaña de deudas"""
        layout = QVBoxLayout(self.debts_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)
        
        # Formulario para nueva deuda
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_frame.setFixedHeight(200)
        
        form_layout = QVBoxLayout(input_frame)
        form_layout.setContentsMargins(20, 15, 20, 15)
        form_layout.setSpacing(12)
        
        lbl_titulo = QLabel("➕ Nueva Deuda")
        lbl_titulo.setStyleSheet("font-weight: bold; color: #bb86fc; font-size: 13px;")
        form_layout.addWidget(lbl_titulo)
        
        # Primera fila: Título
        self.txt_debt_titulo = QLineEdit()
        self.txt_debt_titulo.setPlaceholderText("Título de la deuda...")
        self.txt_debt_titulo.setMinimumHeight(40)
        form_layout.addWidget(self.txt_debt_titulo)
        
        # Segunda fila: Monto total, Acreedor
        row2 = QHBoxLayout()
        
        self.txt_debt_monto = QLineEdit()
        self.txt_debt_monto.setPlaceholderText("Monto total")
        self.txt_debt_monto.setMinimumHeight(40)
        row2.addWidget(self.txt_debt_monto)
        
        self.txt_debt_acreedor = QLineEdit()
        self.txt_debt_acreedor.setPlaceholderText("Acreedor")
        self.txt_debt_acreedor.setMinimumHeight(40)
        row2.addWidget(self.txt_debt_acreedor)
        
        form_layout.addLayout(row2)
        
        # Tercera fila: Fecha límite y botón
        row3 = QHBoxLayout()
        
        self.date_debt_limite = QDateEdit()
        self.date_debt_limite.setDate(QDate.currentDate().addMonths(1))
        self.date_debt_limite.setMinimumHeight(40)
        self.date_debt_limite.setDisplayFormat("yyyy-MM-dd")
        row3.addWidget(QLabel("Fecha límite:"))
        row3.addWidget(self.date_debt_limite)
        
        row3.addStretch()
        
        btn_add_debt = QPushButton("Agregar Deuda")
        btn_add_debt.setMinimumHeight(40)
        btn_add_debt.setMinimumWidth(150)
        btn_add_debt.clicked.connect(self.agregar_deuda)
        row3.addWidget(btn_add_debt)
        
        form_layout.addLayout(row3)
        
        layout.addWidget(input_frame)
        self.shadow(input_frame)
        
        # Lista de deudas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.debts_container = QWidget()
        self.debts_layout = QVBoxLayout(self.debts_container)
        self.debts_layout.setSpacing(40)
        self.debts_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll.setWidget(self.debts_container)
        layout.addWidget(scroll)
    
    # --- MÉTODOS AUXILIARES DE FINANZAS ---
    
    def actualizar_categorias_transaccion(self):
        """Actualiza las categorías según el tipo de transacción"""
        self.combo_trans_categoria.clear()
        
        tipo = self.combo_trans_tipo.currentData()
        
        if tipo == "ingreso":
            categorias = Transaccion.CATEGORIAS_INGRESO
        else:
            categorias = Transaccion.CATEGORIAS_EGRESO
        
        for cat in categorias:
            trans_temp = Transaccion("", 0, tipo, cat)
            icono = trans_temp.get_icono_categoria()
            self.combo_trans_categoria.addItem(f"{icono} {cat}", cat)
    
    def agregar_transaccion(self):
        """Agrega una nueva transacción"""
        titulo = self.txt_trans_titulo.text().strip()
        valor_text = self.txt_trans_valor.text().strip()
        
        if not titulo or not valor_text:
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos requeridos")
            return
        
        try:
            valor = float(valor_text.replace(",", "").replace("$", ""))
        except ValueError:
            QMessageBox.warning(self, "Error", "Valor inválido")
            return
        
        tipo = self.combo_trans_tipo.currentData()
        categoria = self.combo_trans_categoria.currentData()
        descripcion = self.txt_trans_desc.text().strip()
        
        transaccion = Transaccion(titulo, valor, tipo, categoria, descripcion)
        guardar_transaccion(transaccion)
        
        # Limpiar formulario
        self.txt_trans_titulo.clear()
        self.txt_trans_valor.clear()
        self.txt_trans_desc.clear()
        
        # Recargar
        self.cargar_transacciones()
        self.actualizar_dashboard_finanzas()
        
        self.ai_log.append(f"💰 [{datetime.now().strftime('%H:%M')}] Transacción registrada: {titulo}")
    
    def agregar_deuda(self):
        """Agrega una nueva deuda"""
        titulo = self.txt_debt_titulo.text().strip()
        monto_text = self.txt_debt_monto.text().strip()
        acreedor = self.txt_debt_acreedor.text().strip()
        
        if not titulo or not monto_text:
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos requeridos")
            return
        
        try:
            monto = float(monto_text.replace(",", "").replace("$", ""))
        except ValueError:
            QMessageBox.warning(self, "Error", "Monto inválido")
            return
        
        fecha_limite = self.date_debt_limite.date().toString("yyyy-MM-dd")
        
        deuda = Deuda(titulo, monto, 0, acreedor, "", fecha_limite)
        guardar_deuda(deuda)
        
        # Limpiar formulario
        self.txt_debt_titulo.clear()
        self.txt_debt_monto.clear()
        self.txt_debt_acreedor.clear()
        self.date_debt_limite.setDate(QDate.currentDate().addMonths(1))
        
        # Recargar
        self.cargar_deudas()
        
        self.ai_log.append(f"🔴 [{datetime.now().strftime('%H:%M')}] Deuda registrada: {titulo}")
    
    def cargar_transacciones(self):
        """Carga y muestra las transacciones"""
        # Limpiar
        while self.transactions_layout.count() > 0:
            item = self.transactions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Cargar
        transacciones = cargar_transacciones()
        
        if not transacciones:
            empty_label = QLabel("No hay transacciones registradas")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.transactions_layout.addWidget(empty_label)
            return
        
        for trans in transacciones[:50]:  # Máximo 50 más recientes
            card = TransactionCard(trans, on_delete=self.eliminar_transaccion)
            self.transactions_layout.addWidget(card)
    
    def cargar_deudas(self):
        """Carga y muestra las deudas"""
        # Limpiar
        while self.debts_layout.count() > 0:
            item = self.debts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Cargar
        deudas = cargar_deudas()
        
        if not deudas:
            empty_label = QLabel("No hay deudas registradas")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.debts_layout.addWidget(empty_label)
            return
        
        for deuda in deudas:
            card = DebtCard(deuda, on_pay=self.pagar_deuda, on_delete=self.eliminar_deuda)
            self.debts_layout.addWidget(card)
    
    def eliminar_transaccion(self, transaccion):
        """Elimina una transacción"""
        reply = QMessageBox.question(
            self, 
            'Confirmar eliminación',
            f'¿Eliminar la transacción "{transaccion.titulo}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            eliminar_transaccion(transaccion.id)
            self.cargar_transacciones()
            self.actualizar_dashboard_finanzas()
            self.ai_log.append(f"🗑️ [{datetime.now().strftime('%H:%M')}] Transacción eliminada")
    
    def pagar_deuda(self, deuda):
        """Registra un pago en una deuda"""
        from PyQt6.QtWidgets import QInputDialog
        
        monto, ok = QInputDialog.getDouble(
            self,
            "Registrar Pago",
            f"¿Cuánto pagaste de '{deuda.titulo}'?\nPendiente: ${deuda.get_monto_pendiente():,.0f}",
            0, 0, deuda.monto_total, 0
        )
        
        if ok and monto > 0:
            nuevo_total = min(deuda.monto_pagado + monto, deuda.monto_total)
            actualizar_pago_deuda(deuda.id, nuevo_total)
            self.cargar_deudas()
            self.ai_log.append(f"💵 [{datetime.now().strftime('%H:%M')}] Pago registrado: ${monto:,.0f}")
    
    def eliminar_deuda(self, deuda):
        """Elimina una deuda"""
        reply = QMessageBox.question(
            self,
            'Confirmar eliminación',
            f'¿Eliminar la deuda "{deuda.titulo}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            eliminar_deuda(deuda.id)
            self.cargar_deudas()
            self.ai_log.append(f"🗑️ [{datetime.now().strftime('%H:%M')}] Deuda eliminada")
    
    def actualizar_dashboard_finanzas(self):
        """Actualiza el dashboard de finanzas"""
        balance = obtener_balance()
        
        self.card_balance.update_value(f"${balance['balance']:,.0f}")
        self.card_ingresos.update_value(f"${balance['ingresos']:,.0f}")
        self.card_egresos.update_value(f"${balance['egresos']:,.0f}")
        
        # Actualizar gráfico
        gastos = obtener_gastos_por_categoria()
        if gastos:
            colors = {}
            for cat in gastos.keys():
                trans_temp = Transaccion("", 0, "egreso", cat)
                colors[cat] = trans_temp.get_color_categoria()
            
            self.pie_chart.update_data(gastos, colors)
    
    def on_finance_tab_changed(self, index):
        """Se ejecuta al cambiar de tab en finanzas"""
        if index == 0:  # Dashboard
            self.actualizar_dashboard_finanzas()
        elif index == 1:  # Transacciones
            self.cargar_transacciones()
        elif index == 2:  # Deudas
            self.cargar_deudas()

    # ==================== MÓDULO DE LIBROS ====================
    
    def setup_books(self):
        """Configura la pestaña de Libros"""
        main_layout = QVBoxLayout(self.tab_books)
        main_layout.setContentsMargins(10, 20, 10, 10)
        main_layout.setSpacing(20)
        
        # Sub-tabs: Libro Actual, Biblioteca
        self.books_tabs = QTabWidget()
        main_layout.addWidget(self.books_tabs)
        
        # Libro Actual
        self.current_book_tab = QWidget()
        self.setup_current_book()
        self.books_tabs.addTab(self.current_book_tab, "📖 Libro Actual")
        
        # Biblioteca
        self.library_tab = QWidget()
        self.setup_library()
        self.books_tabs.addTab(self.library_tab, "📚 Biblioteca")
        
        # Listener
        self.books_tabs.currentChanged.connect(self.on_books_tab_changed)
    
    def setup_current_book(self):
        """Pestaña del libro actual"""
        layout = QVBoxLayout(self.current_book_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)
        
        # Card del libro actual
        current_frame = QFrame()
        current_frame.setObjectName("dashboard_card")
        current_frame.setFixedHeight(400)
        
        current_layout = QHBoxLayout(current_frame)
        current_layout.setContentsMargins(40, 30, 40, 30)
        current_layout.setSpacing(40)
        
        # Izquierda: Información
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.lbl_current_title = QLabel("Ningún libro en lectura")
        self.lbl_current_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.lbl_current_title.setWordWrap(True)
        info_layout.addWidget(self.lbl_current_title)
        
        self.lbl_current_author = QLabel("")
        self.lbl_current_author.setStyleSheet("color: #808090; font-size: 14px; margin-bottom: 10px;")
        info_layout.addWidget(self.lbl_current_author)
        
        info_layout.addSpacing(20)
        
        self.lbl_current_stats = QLabel("")
        self.lbl_current_stats.setStyleSheet("color: #e0e0e0; font-size: 13px; line-height: 2.0;")
        self.lbl_current_stats.setWordWrap(True)
        info_layout.addWidget(self.lbl_current_stats)
        
        info_layout.addStretch()
        
        current_layout.addLayout(info_layout, 2)
        
        # Derecha: Progreso circular
        ring_container = QVBoxLayout()
        ring_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_ring = ProgressRing()
        ring_container.addWidget(self.progress_ring)
        
        current_layout.addLayout(ring_container, 1)
        
        layout.addWidget(current_frame)
        self.shadow(current_frame)
        
        layout.addStretch()
    
    def setup_library(self):
        """Pestaña de biblioteca"""
        layout = QVBoxLayout(self.library_tab)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(20)
        
        # Formulario para agregar libro
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_frame.setFixedHeight(230)
        
        form_layout = QVBoxLayout(input_frame)
        form_layout.setContentsMargins(20, 15, 20, 15)
        form_layout.setSpacing(12)
        
        lbl_titulo = QLabel("➕ Agregar Libro")
        lbl_titulo.setStyleSheet("font-weight: bold; color: #bb86fc; font-size: 13px;")
        form_layout.addWidget(lbl_titulo)
        
        # Primera fila: Título y Autor
        row1 = QHBoxLayout()
        
        self.txt_book_titulo = QLineEdit()
        self.txt_book_titulo.setPlaceholderText("Título del libro")
        self.txt_book_titulo.setMinimumHeight(40)
        row1.addWidget(self.txt_book_titulo)
        
        self.txt_book_autor = QLineEdit()
        self.txt_book_autor.setPlaceholderText("Autor")
        self.txt_book_autor.setMinimumHeight(40)
        row1.addWidget(self.txt_book_autor)
        
        form_layout.addLayout(row1)
        
        # Segunda fila: Páginas, Género, Editorial
        row2 = QHBoxLayout()
        
        self.txt_book_paginas = QLineEdit()
        self.txt_book_paginas.setPlaceholderText("Total de páginas")
        self.txt_book_paginas.setMinimumHeight(40)
        self.txt_book_paginas.setFixedWidth(150)
        row2.addWidget(self.txt_book_paginas)
        
        self.txt_book_genero = QLineEdit()
        self.txt_book_genero.setPlaceholderText("Género")
        self.txt_book_genero.setMinimumHeight(40)
        row2.addWidget(self.txt_book_genero)
        
        self.txt_book_editorial = QLineEdit()
        self.txt_book_editorial.setPlaceholderText("Editorial")
        self.txt_book_editorial.setMinimumHeight(40)
        row2.addWidget(self.txt_book_editorial)
        
        form_layout.addLayout(row2)
        
        # Tercera fila: Año y botón
        row3 = QHBoxLayout()
        
        self.txt_book_anio = QLineEdit()
        self.txt_book_anio.setPlaceholderText("Año")
        self.txt_book_anio.setMinimumHeight(40)
        self.txt_book_anio.setFixedWidth(100)
        row3.addWidget(self.txt_book_anio)
        
        row3.addStretch()
        
        btn_add_book = QPushButton("Agregar Libro")
        btn_add_book.setMinimumHeight(40)
        btn_add_book.setMinimumWidth(150)
        btn_add_book.clicked.connect(self.agregar_libro)
        row3.addWidget(btn_add_book)
        
        form_layout.addLayout(row3)
        
        layout.addWidget(input_frame)
        self.shadow(input_frame)
        
        # Filtros
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filtrar por estado:"))
        
        self.combo_book_filter = QComboBox()
        self.combo_book_filter.addItem("📚 Todos", None)
        self.combo_book_filter.addItem("📖 Leyendo", Libro.ESTADO_LEYENDO)
        self.combo_book_filter.addItem("✅ Terminados", Libro.ESTADO_TERMINADO)
        self.combo_book_filter.addItem("⏸️ Pausados", Libro.ESTADO_PAUSADO)
        self.combo_book_filter.addItem("📕 Sin empezar", Libro.ESTADO_SIN_EMPEZAR)
        self.combo_book_filter.currentIndexChanged.connect(self.cargar_libros)
        self.combo_book_filter.setFixedWidth(200)
        filter_row.addWidget(self.combo_book_filter)
        
        filter_row.addStretch()
        layout.addLayout(filter_row)
        
        # Lista de libros
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.books_container = QWidget()
        self.books_layout = QVBoxLayout(self.books_container)
        self.books_layout.setSpacing(15)
        self.books_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(self.books_container)
        layout.addWidget(scroll)
    
    # --- MÉTODOS AUXILIARES DE LIBROS ---
    
    def agregar_libro(self):
        """Agrega un nuevo libro"""
        titulo = self.txt_book_titulo.text().strip()
        autor = self.txt_book_autor.text().strip()
        paginas_text = self.txt_book_paginas.text().strip()
        
        if not titulo or not autor or not paginas_text:
            QMessageBox.warning(self, "Error", "Por favor completa título, autor y páginas")
            return
        
        try:
            total_paginas = int(paginas_text)
            if total_paginas <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Número de páginas inválido")
            return
        
        genero = self.txt_book_genero.text().strip()
        editorial = self.txt_book_editorial.text().strip()
        
        anio = None
        if self.txt_book_anio.text().strip():
            try:
                anio = int(self.txt_book_anio.text().strip())
            except ValueError:
                pass
        
        libro = Libro(
            titulo=titulo,
            autor=autor,
            total_paginas=total_paginas,
            genero=genero,
            editorial=editorial,
            anio=anio
        )
        
        guardar_libro(libro)
        
        # Limpiar formulario
        self.txt_book_titulo.clear()
        self.txt_book_autor.clear()
        self.txt_book_paginas.clear()
        self.txt_book_genero.clear()
        self.txt_book_editorial.clear()
        self.txt_book_anio.clear()
        
        # Recargar
        self.cargar_libros()
        self.cargar_libro_actual()
        
        self.ai_log.append(f"📚 [{datetime.now().strftime('%H:%M')}] Libro agregado: {titulo}")
    
    def cargar_libros(self):
        """Carga y muestra los libros"""
        # Limpiar
        while self.books_layout.count() > 0:
            item = self.books_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Obtener filtro
        estado = self.combo_book_filter.currentData()
        
        # Cargar
        libros = cargar_libros(estado=estado)
        
        if not libros:
            empty_label = QLabel("No hay libros en esta categoría")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.books_layout.addWidget(empty_label)
            return
        
        for libro in libros:
            card = BookCard(
                libro,
                on_update=self.actualizar_libro,
                on_edit=self.editar_libro,
                on_delete=self.eliminar_libro
            )
            self.books_layout.addWidget(card)
    
    def actualizar_libro(self, libro):
        """Actualiza el progreso de un libro"""
        from PyQt6.QtWidgets import QInputDialog
        
        paginas, ok = QInputDialog.getInt(
            self,
            "Actualizar Progreso",
            f"¿Cuántas páginas llevas leídas de '{libro.titulo}'?\n(Total: {libro.total_paginas})",
            libro.paginas_leidas,
            0,
            libro.total_paginas,
            1
        )
        
        if ok:
            actualizar_progreso_libro(libro.id, paginas)
            self.cargar_libros()
            self.cargar_libro_actual()
            self.ai_log.append(f"📖 [{datetime.now().strftime('%H:%M')}] Progreso actualizado: {libro.titulo}")
    
    def editar_libro(self, libro, complete=False):
        """Edita un libro o lo marca como terminado"""
        if complete:
            reply = QMessageBox.question(
                self,
                'Confirmar',
                f'¿Marcar "{libro.titulo}" como terminado?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                marcar_libro_como_terminado(libro.id)
                self.cargar_libros()
                self.cargar_libro_actual()
                self.ai_log.append(f"✅ [{datetime.now().strftime('%H:%M')}] Libro terminado: {libro.titulo}")
    
    def eliminar_libro(self, libro):
        """Elimina un libro"""
        reply = QMessageBox.question(
            self,
            'Confirmar eliminación',
            f'¿Eliminar "{libro.titulo}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            eliminar_libro(libro.id)
            self.cargar_libros()
            self.cargar_libro_actual()
            self.ai_log.append(f"🗑️ [{datetime.now().strftime('%H:%M')}] Libro eliminado")
    
    def cargar_libro_actual(self):
        """Carga el libro que se está leyendo actualmente"""
        libro = obtener_libro_actual()
        
        if libro:
            self.lbl_current_title.setText(libro.titulo)
            self.lbl_current_author.setText(f"✍️ {libro.autor}")
            
            # Estadísticas
            dias_est = libro.get_tiempo_estimado_finalizacion()
            horas_est = libro.get_horas_estimadas_finalizacion()
            promedio = libro.get_promedio_paginas_dia()
            
            stats_html = f"""
            <p style='line-height: 1.8; margin: 5px 0;'>
            <span style='color: #bb86fc;'>📄 Páginas:</span> {libro.paginas_leidas} / {libro.total_paginas}<br>
            <span style='color: #bb86fc;'>📊 Progreso:</span> {libro.get_porcentaje_completado():.1f}%<br>
            <span style='color: #bb86fc;'>📈 Promedio:</span> {promedio:.1f} páginas/día<br>
            """
            
            if dias_est:
                stats_html += f"<span style='color: #bb86fc;'>⏱️ Tiempo estimado:</span> {dias_est} días<br>"
            
            if horas_est:
                stats_html += f"<span style='color: #bb86fc;'>🕐 Horas restantes:</span> ~{horas_est:.1f}h<br>"
            
            fecha_est = libro.get_fecha_estimada_finalizacion()
            if fecha_est:
                stats_html += f"<span style='color: #bb86fc;'>📅 Estimación:</span> {fecha_est.strftime('%d %B %Y')}"
            
            stats_html += "</p>"
            
            self.lbl_current_stats.setText(stats_html)
            
            # Actualizar anillo de progreso
            self.progress_ring.update_progress(
                libro.get_porcentaje_completado(),
                f"{libro.paginas_leidas}/{libro.total_paginas}",
                f"{libro.get_paginas_restantes()} páginas"
            )
        else:
            self.lbl_current_title.setText("Ningún libro en lectura")
            self.lbl_current_author.setText("Agrega un libro en la Biblioteca y empieza a leer")
            self.lbl_current_stats.setText("")
            self.progress_ring.update_progress(0, "", "")
    
    def on_books_tab_changed(self, index):
        """Se ejecuta al cambiar de tab en libros"""
        if index == 0:  # Libro actual
            self.cargar_libro_actual()
        elif index == 1:  # Biblioteca
            self.cargar_libros()


# Para testing directo
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())