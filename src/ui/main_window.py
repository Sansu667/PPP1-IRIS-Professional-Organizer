from datetime import datetime
import sys
from pathlib import Path

# Agregar el directorio src al path para que funcionen los imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QTextEdit, QProgressBar, QFrame, QGraphicsDropShadowEffect, QMenu, QSpinBox, QTabWidget,
    QDialog, QDialogButtonBox, QScrollArea, QMessageBox, QComboBox, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QAction

# --- IMPORTACIONES ---
try:
    from ui.components.progress_chart import ProgressChart
    from ui.components.heatmap_widget import HeatmapWidget
    from ui.components.bar_chart import BarChart
    from core.habits import Tarea
    from core.ai_engine import generar_reporte
    from database.db_manager import (guardar_tarea, cargar_tareas, actualizar_tarea, 
                                     eliminar_tarea, obtener_historial_heatmap, obtener_kpis, 
                                     obtener_actividad_semanal, actualizar_tarea_completa)
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
        self.setMinimumWidth(85)

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
        self.setMinimumWidth(80)

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
        self.setMinimumSize(160, 90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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
        self.setMinimumWidth(380)
        
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
            QComboBox QAbstractItemView {
                background: #20202a;
                color: white;
                border: 1px solid #444455;
                selection-background-color: #6200ea;
                selection-color: white;
                outline: none;
            }
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
    QComboBox QAbstractItemView {
        background: #20202a;
        color: white;
        border: 1px solid #444455;
        selection-background-color: #6200ea;
        selection-color: white;
        outline: none;
        padding: 2px;
    }

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
        self.resize(1100, 750)
        self.setMinimumSize(900, 640)
        self.setStyleSheet(STYLE_SHEET)

        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(25,25,25,25); main_layout.setSpacing(20)

        # HEADER
        h_layout = QHBoxLayout()
        lbl = QLabel("🧠  IRIS ORGANIZER"); lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: white; letter-spacing: 1.5px;")
        h_layout.addWidget(lbl); h_layout.addStretch()
        main_layout.addLayout(h_layout)

        # TABS PRINCIPALES
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.tab_dash = QWidget(); self.setup_dashboard(); self.tabs.addTab(self.tab_dash, "📊 Dashboard")
        self.tab_tasks = QWidget(); self.setup_tasks(); self.tabs.addTab(self.tab_tasks, "📝 Tasks")
        self.tab_analytics = QWidget(); self.setup_analytics(); self.tabs.addTab(self.tab_analytics, "📈 Analytics")

        # LOG
        self.ai_log = QTextEdit(); self.ai_log.setReadOnly(True); self.ai_log.setMinimumHeight(45); self.ai_log.setMaximumHeight(65)
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
        self.top_card.setMinimumHeight(270)

        tc_layout = QHBoxLayout(self.top_card); tc_layout.setContentsMargins(25, 20, 25, 20); tc_layout.setSpacing(25)

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
        self.lbl_time.setStyleSheet("font-size: 58px; font-weight: bold; color: white;")
        
        self.time_ctrl = QWidget()
        h_selector = QHBoxLayout(self.time_ctrl)
        h_selector.setContentsMargins(0,0,0,0)
        h_selector.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.spin = QSpinBox(); self.spin.setRange(1, 180); self.spin.setValue(25); self.spin.setSuffix(" min"); self.spin.setMinimumWidth(85); self.spin.setMaximumWidth(115)
        self.spin.valueChanged.connect(self.update_timer_label_init)
        
        h_selector.addWidget(QLabel("Focus:", styleSheet="color:#808090; font-size:13px; font-weight:bold; margin-right:10px;"))
        h_selector.addWidget(self.spin)
        
        btns_wrapper = QWidget()
        h_btns = QHBoxLayout(btns_wrapper)
        h_btns.setContentsMargins(0,0,0,0)
        h_btns.setSpacing(15)
        h_btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_focus = QPushButton("START FOCUS")
        self.btn_focus.setMinimumSize(110, 42)
        self.btn_focus.clicked.connect(self.toggle_timer)

        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setObjectName("btn_action")
        self.btn_reset.setMinimumSize(85, 42)
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
        input_card.setMinimumHeight(130)
        
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
        self.date_task.setMinimumWidth(120)
        self.date_task.setMaximumWidth(165)
        self.date_task.setMinimumHeight(45)
        in_row2.addWidget(self.date_task)
        
        self.combo_priority = QComboBox()
        self.combo_priority.addItem("🔥 ALTA", "alta")
        self.combo_priority.addItem("⚡ MEDIA", "media")
        self.combo_priority.addItem("📌 BAJA", "baja")
        self.combo_priority.setCurrentIndex(1)  # Media por defecto
        self.combo_priority.setMinimumWidth(120)
        self.combo_priority.setMaximumWidth(165)
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
        active_scroll.viewport().setStyleSheet("background: #0d0d12;")

        self.active_container = QWidget()
        self.active_container.setStyleSheet("background: #0d0d12;")
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
        completed_scroll.viewport().setStyleSheet("background: #0d0d12;")

        self.completed_container = QWidget()
        self.completed_container.setStyleSheet("background: #0d0d12;")
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
        while layout.count() > 1:
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
                self.completed_layout.insertWidget(self.completed_layout.count() - 1, card)
                completed_count += 1
            else:
                self.active_layout.insertWidget(self.active_layout.count() - 1, card)
                active_count += 1
        
        self.task_tabs.setTabText(0, f"🎯 Active ({active_count})")
        self.task_tabs.setTabText(1, f"✅ Completed ({completed_count})")
        
        if active_count == 0:
            empty_label = QLabel("No hay tareas activas. ¡Crea una nueva misión!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.active_layout.insertWidget(0, empty_label)
        
        if completed_count == 0:
            empty_label = QLabel("Aún no has completado ninguna tarea.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #808090; font-size: 14px; padding: 40px;")
            self.completed_layout.insertWidget(0, empty_label)

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
        if i == 2:
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


# Para testing directo
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())