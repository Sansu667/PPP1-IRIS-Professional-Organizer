from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, 
    QTextEdit, QProgressBar, QFrame, QGraphicsDropShadowEffect, QMenu, QSpinBox, QTabWidget)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor, QAction

# --- IMPORTACIONES ---
try:
    from ui.components.progress_chart import ProgressChart
    from ui.components.heatmap_widget import HeatmapWidget
    from ui.components.bar_chart import BarChart
    from core.habits import Tarea
    from core.ai_engine import generar_reporte
    from database.db_manager import (guardar_tarea, cargar_tareas, actualizar_tarea, 
                                     eliminar_tarea, obtener_historial_heatmap, obtener_kpis, obtener_actividad_semanal)
except ImportError as e:
    print(f"Error cargando módulos: {e}")

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
    
    QLineEdit, QDateEdit { padding: 10px; background: #20202a; color: white; border: 1px solid #333340; border-radius: 6px; font-size: 13px; }
    QLineEdit:focus, QDateEdit:focus { border: 1px solid #7c4dff; background-color: #252530; }
    
    QSpinBox { background: #20202a; border: 1px solid #333340; border-radius: 6px; color: #03dac6; font-weight: bold; padding: 8px; font-size: 14px; }
    QSpinBox::up-button, QSpinBox::down-button { width: 0px; }
    
    QPushButton { background: #6200ea; color: white; border-radius: 6px; font-weight: bold; border: none; padding: 10px 20px; font-size: 13px; }
    QPushButton:hover { background: #7c4dff; }
    QPushButton#btn_complete { background-color: #03dac6; color: #000; }
    QPushButton#btn_delete { background-color: transparent; color: #ff5252; border: 1px solid #ff5252; }
    
    /* Estilo botón secundario (Reset) */
    QPushButton#btn_action { background-color: #252530; border: 1px solid #444; color: #ccc; }
    QPushButton#btn_action:hover { border: 1px solid #fff; color: white; }

    QTableWidget { background: transparent; border: none; gridline-color: transparent; color: #eee; }
    QHeaderView::section { background: #16161e; color: #bb86fc; border: none; border-bottom: 2px solid #333; font-weight: bold; padding: 10px; font-size: 11px; letter-spacing: 1px; }
    QTableWidget::item { border-bottom: 1px solid #252530; padding-left: 10px; }
    
    QTextEdit { background: #0f0f13; border: 1px solid #333; border-radius: 8px; color: #00ffaa; font-family: Consolas; font-size: 11px; padding: 5px; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IRIS - Neural Task Organizer v1.6")
        self.resize(1250, 880) 
        self.setStyleSheet(STYLE_SHEET)

        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(25,25,25,25); main_layout.setSpacing(20)

        # HEADER
        h_layout = QHBoxLayout()
        lbl = QLabel("🧠  IRIS ORGANIZER"); lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: white; letter-spacing: 1.5px;")
        h_layout.addWidget(lbl); h_layout.addStretch()
        main_layout.addLayout(h_layout)

        # TABS
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.tab_dash = QWidget(); self.setup_dashboard(); self.tabs.addTab(self.tab_dash, "📊 Dashboard")
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

        # Etiqueta de Tiempo
        self.lbl_time = QLabel("25:00")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 72px; font-weight: bold; color: white;")
        
        # Selector de Tiempo
        self.time_ctrl = QWidget()
        h_selector = QHBoxLayout(self.time_ctrl)
        h_selector.setContentsMargins(0,0,0,0)
        h_selector.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.spin = QSpinBox(); self.spin.setRange(1, 180); self.spin.setValue(25); self.spin.setSuffix(" min"); self.spin.setFixedWidth(100)
        self.spin.valueChanged.connect(self.update_timer_label_init)
        
        h_selector.addWidget(QLabel("Focus:", styleSheet="color:#808090; font-size:13px; font-weight:bold; margin-right:10px;"))
        h_selector.addWidget(self.spin)
        
        # Contenedor de Botones (Start + Reset)
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

        # Añado todo a la columna central
        tm_l.addWidget(self.lbl_time)
        tm_l.addWidget(self.time_ctrl)
        tm_l.addWidget(btns_wrapper)
        
        # Stretch abajo para equilibrar
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

        # --- BOTTOM CARD ---
        self.btm_card = QFrame(); self.btm_card.setObjectName("card")
        bc_layout = QVBoxLayout(self.btm_card); bc_layout.setContentsMargins(25,25,25,25); bc_layout.setSpacing(20)

        in_l = QHBoxLayout()
        self.txt_task = QLineEdit(); self.txt_task.setPlaceholderText("✨ Nueva misión..."); self.txt_task.setMinimumHeight(45)
        self.date_task = QDateEdit(); self.date_task.setDate(QDate.currentDate()); self.date_task.setFixedWidth(130); self.date_task.setMinimumHeight(45)
        btn_add = QPushButton("ADD MISSION"); btn_add.setMinimumHeight(45); btn_add.clicked.connect(self.add_task)
        in_l.addWidget(self.txt_task); in_l.addWidget(self.date_task); in_l.addWidget(btn_add)
        bc_layout.addLayout(in_l)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "TASK", "DEADLINE", "STATUS", "XP"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed); h.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed); h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 120); self.table.setColumnWidth(3, 130); self.table.setColumnWidth(4, 100)
        self.table.setColumnHidden(0, True) 
        self.table.verticalHeader().setVisible(False); self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        bc_layout.addWidget(self.table)

        ac_l = QHBoxLayout(); ac_l.addStretch()
        btn_del = QPushButton("Delete"); btn_del.setObjectName("btn_delete"); btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok = QPushButton("✓ COMPLETE MISSION"); btn_ok.setObjectName("btn_complete"); btn_ok.setCursor(Qt.CursorShape.PointingHandCursor); btn_ok.setMinimumWidth(180)
        btn_del.clicked.connect(lambda: self.manage_task(False)); btn_ok.clicked.connect(lambda: self.manage_task(True))
        ac_l.addWidget(btn_del); ac_l.addWidget(btn_ok)
        bc_layout.addLayout(ac_l)

        layout.addWidget(self.btm_card)
        self.shadow(self.btm_card)

    def setup_analytics(self):
        # Layout Principal de la pestaña con Scroll por si la pantalla es chica
        main_l = QVBoxLayout(self.tab_analytics)
        main_l.setContentsMargins(20, 20, 20, 20)
        main_l.setSpacing(20)
        
        # 1. KPI CARDS
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        self.card_total = StatCard("TOTAL COMPLETED", "0", "white", "🏆")
        self.card_streak = StatCard("CURRENT STREAK", "0 Days", "#03dac6", "🔥")
        self.card_rate = StatCard("SUCCESS RATE", "0%", "#bb86fc", "📈")
        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_streak)
        kpi_layout.addWidget(self.card_rate)
        main_l.addLayout(kpi_layout)

        # 2. CONTENEDOR CENTRAL
        # Uso un Splitter o simplemente dos Frames verticales
        
        # -- A. HEATMAP --
        try:
            self.hm_w = HeatmapWidget()
            # Envuelvo en un Frame con estilo
            hm_frame = QFrame(); hm_frame.setObjectName("card")
            l = QVBoxLayout(hm_frame); l.addWidget(self.hm_w)
            main_l.addWidget(hm_frame)
            self.shadow(hm_frame)
        except: pass

        # -- B. BAR CHART --
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

    # --- LOGIC ---
    def tab_changed(self, i):
        if i == 1: 
            try: 
                # Heatmap
                self.hm_w.update_heatmap(obtener_historial_heatmap())
                # Stats
                stats = obtener_kpis()
                self.card_total.update_value(stats["total"])
                self.card_streak.update_value(f"{stats['streak']} Days")
                self.card_rate.update_value(f"{stats['promedio']:.1f}%")
                # Bar Chart
                semana = obtener_actividad_semanal()
                self.bar_chart.update_data(semana)
            except Exception as e: 
                print(f"Error actualizando analytics: {e}")

    def cargar_datos(self):
        self.tasks = cargar_tareas()
        try: self.lbl_feedback.setText(generar_reporte(self.tasks))
        except: self.lbl_feedback.setText("Sistemas listos. Esperando misiones...")

        if self.tasks:
            avg = sum(t.porcentaje_exito for t in self.tasks) / len(self.tasks)
            self.chart.update_chart(avg)
        else: self.chart.update_chart(0)

        self.table.setRowCount(0)
        hoy = datetime.now().date()
        for r, t in enumerate(self.tasks):
            self.table.insertRow(r); self.table.setRowHeight(r, 60)
            if t.completada: st, cl = "COMPLETED", "#03dac6"
            elif t.fecha_limite.date() < hoy: st, cl = "OVERDUE", "#ff5252"
            else: st, cl = "PENDING", "#ffb74d"

            self.table.setItem(r, 0, QTableWidgetItem(str(t.id)))
            nm = QTableWidgetItem(t.nombre); nm.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold)); self.table.setItem(r, 1, nm)
            dt = QTableWidgetItem(t.fecha_limite.strftime("%Y-%m-%d")); dt.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.table.setItem(r, 2, dt)
            
            w = QWidget(); hl = QHBoxLayout(w); hl.setAlignment(Qt.AlignmentFlag.AlignCenter); hl.setContentsMargins(0,0,0,0); hl.addWidget(StatusBadge(st, cl))
            self.table.setCellWidget(r, 3, w)
            
            pb = QProgressBar(); pb.setValue(int(t.porcentaje_exito)); pb.setFixedHeight(6); pb.setTextVisible(False)
            pb.setStyleSheet(f"background:#333; border-radius:3px; QProgressBar::chunk{{background:{cl}; border-radius:3px;}}")
            wp = QWidget(); wl = QVBoxLayout(wp); wl.setContentsMargins(15,0,15,0); wl.setAlignment(Qt.AlignmentFlag.AlignCenter); wl.addWidget(pb)
            self.table.setCellWidget(r, 4, wp)

    # --- TIMER LOGIC CON RESET ---
    def update_timer_label_init(self):
        if not self.timer.isActive() and not self.timer_pausado:
            self.lbl_time.setText(f"{self.spin.value():02d}:00")

    def toggle_timer(self):
        if not self.timer.isActive():
            if not self.timer_pausado:
                self.tiempo_restante = self.spin.value() * 60
                self.ai_log.append(f"⚡ [{datetime.now().strftime('%H:%M')}] Focus session started: {self.spin.value()} min")
            else: self.ai_log.append(f"▶️ [{datetime.now().strftime('%H:%M')}] Session resumed")
            
            self.time_ctrl.hide() # Ocultar selector al iniciar
            self.timer.start(1000)
            self.btn_focus.setText("PAUSE"); self.btn_focus.setStyleSheet("background: #ff5252; color: white;")
            self.timer_pausado = False
        else:
            self.timer.stop(); self.timer_pausado = True
            self.btn_focus.setText("RESUME"); self.btn_focus.setStyleSheet("background: #03dac6; color: black;")
            self.ai_log.append(f"⏸ [{datetime.now().strftime('%H:%M')}] Session paused")

    def reset_timer(self):
        """Reinicia el cronómetro al estado original y muestra el selector"""
        self.timer.stop()
        self.timer_pausado = False
        self.tiempo_restante = self.spin.value() * 60
        
        # Restaurar UI
        self.time_ctrl.show() # Mostrar selector de nuevo
        self.update_timer_label_init()
        
        self.btn_focus.setText("START FOCUS")
        self.btn_focus.setStyleSheet("background: #6200ea; color: white;")
        
        self.ai_log.append(f"↺ [{datetime.now().strftime('%H:%M')}] Timer reset")

    def tick(self):
        self.tiempo_restante -= 1
        if self.tiempo_restante <= 0:
            self.timer.stop(); self.timer_pausado = False; self.time_ctrl.show()
            self.update_timer_label_init()
            self.btn_focus.setText("START FOCUS"); self.btn_focus.setStyleSheet("background: #6200ea; color: white;")
            self.ai_log.append(f"🎉 [{datetime.now().strftime('%H:%M')}] Session completed!")
        else: m, s = divmod(self.tiempo_restante, 60); self.lbl_time.setText(f"{m:02d}:{s:02d}")

    # ACTIONS
    def add_task(self):
        if self.txt_task.text().strip():
            guardar_tarea(Tarea(self.txt_task.text(), self.date_task.date().toString("yyyy-MM-dd")))
            self.ai_log.append(f"✨ [{datetime.now().strftime('%H:%M')}] New mission added: {self.txt_task.text()}")
            self.txt_task.clear(); self.cargar_datos()

    def manage_task(self, complete):
        r = self.table.currentRow()
        if r >= 0:
            tid = int(self.table.item(r, 0).text()); t_name = self.table.item(r, 1).text()
            if complete: actualizar_tarea(tid, True, 100); self.ai_log.append(f"🏆 [{datetime.now().strftime('%H:%M')}] Complete: {t_name}")
            else: eliminar_tarea(tid); self.ai_log.append(f"🗑️ [{datetime.now().strftime('%H:%M')}] Deleted: {t_name}")
            self.cargar_datos()