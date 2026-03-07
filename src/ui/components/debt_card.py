from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DebtCard(QFrame):
    """Tarjeta visual para mostrar una deuda"""
    
    def __init__(self, deuda, on_pay, on_delete, parent=None):
        super().__init__(parent)
        self.deuda = deuda
        self.on_pay = on_pay
        self.on_delete = on_delete
        
        self.setObjectName("debt_card")
        
        # ALTURA FIJA - NO CAMBIAR
        self.setMinimumHeight(140)
        self.setMaximumHeight(140)
        
        # Política de tamaño fija
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Fixed
        )
        
        # Color según estado
        border_color = deuda.get_estado_color()
        
        if deuda.esta_pagada():
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a2e2a, stop:1 #16161e)"
        elif deuda.get_porcentaje_pagado() >= 50:
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e261a, stop:1 #16161e)"
        else:
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e1a1a, stop:1 #16161e)"
        
        self.setStyleSheet(f"""
            QFrame#debt_card {{
                background: {bg_gradient};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel {{ background: transparent; color: #e0e0e0; }}
            QPushButton {{
                background: transparent;
                border: 1px solid #444;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                border-color: #bb86fc; 
                background: rgba(187, 134, 252, 0.1); 
            }}
            QPushButton#btn_delete {{
                border-color: #ff5252;
                color: #ff5252;
            }}
            QPushButton#btn_delete:hover {{
                background: #ff525220;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # TOP: Título y estado
        top_row = QHBoxLayout()
        
        title = QLabel(f"💳 {deuda.titulo}")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        top_row.addWidget(title, 1)
        
        # Badge de estado
        if deuda.esta_pagada():
            estado_badge = QLabel("✅ PAGADA")
            estado_badge.setStyleSheet("""
                background: #03dac620;
                color: #03dac6;
                border: 1px solid #03dac6;
                border-radius: 8px;
                padding: 3px 8px;
                font-size: 9px;
                font-weight: bold;
            """)
        else:
            estado_badge = QLabel("🔴 PENDIENTE")
            estado_badge.setStyleSheet("""
                background: #ff525220;
                color: #ff5252;
                border: 1px solid #ff5252;
                border-radius: 8px;
                padding: 3px 8px;
                font-size: 9px;
                font-weight: bold;
            """)
        estado_badge.setFixedSize(90, 20)
        estado_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(estado_badge)
        
        layout.addLayout(top_row)
        
        # MIDDLE: Información de montos
        info_layout = QHBoxLayout()
        
        # Columna izquierda: Acreedor y fecha
        left_col = QVBoxLayout()
        left_col.setSpacing(2)
        
        if deuda.acreedor:
            acreedor_label = QLabel(f"👤 {deuda.acreedor}")
            acreedor_label.setStyleSheet("color: #808090; font-size: 10px;")
            left_col.addWidget(acreedor_label)
        
        if deuda.fecha_limite:
            dias = deuda.get_dias_restantes()
            if dias is not None:
                if dias < 0:
                    fecha_text = f"⚠️ Venció hace {abs(dias)} días"
                    fecha_color = "#ff5252"
                elif dias == 0:
                    fecha_text = "⚡ Vence HOY"
                    fecha_color = "#ffb74d"
                elif dias <= 7:
                    fecha_text = f"⚡ Vence en {dias} días"
                    fecha_color = "#ffb74d"
                else:
                    fecha_text = f"📅 Vence en {dias} días"
                    fecha_color = "#808090"
                
                fecha_label = QLabel(fecha_text)
                fecha_label.setStyleSheet(f"color: {fecha_color}; font-size: 10px; font-weight: bold;")
                left_col.addWidget(fecha_label)
        
        info_layout.addLayout(left_col, 1)
        
        # Columna derecha: Montos
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.setSpacing(2)
        
        pagado_label = QLabel(f"Pagado: ${deuda.monto_pagado:,.0f}")
        pagado_label.setStyleSheet("color: #03dac6; font-size: 10px; font-weight: bold;")
        pagado_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(pagado_label)
        
        pendiente_label = QLabel(f"Pendiente: ${deuda.get_monto_pendiente():,.0f}")
        pendiente_label.setStyleSheet("color: #ff5252; font-size: 10px; font-weight: bold;")
        pendiente_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(pendiente_label)
        
        info_layout.addLayout(right_col)
        
        layout.addLayout(info_layout)
        
        # PROGRESS BAR
        progress = QProgressBar()
        progress.setValue(int(deuda.get_porcentaje_pagado()))
        progress.setFixedHeight(6)
        progress.setTextVisible(False)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background: #2d2d36;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {border_color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        # Info de progreso
        progreso_text = QLabel(f"{deuda.get_porcentaje_pagado():.1f}% completado")
        progreso_text.setStyleSheet("color: #b0b0b0; font-size: 9px;")
        progreso_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(progreso_text)
        
        # BOTTOM: Botones
        if not deuda.esta_pagada():
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            
            btn_pay = QPushButton("💵 Pagar")
            btn_pay.setFixedHeight(26)
            btn_pay.clicked.connect(lambda: self.on_pay(deuda))
            btn_row.addWidget(btn_pay)
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setObjectName("btn_delete")
            btn_delete.setFixedWidth(35)
            btn_delete.setFixedHeight(26)
            btn_delete.clicked.connect(lambda: self.on_delete(deuda))
            btn_row.addWidget(btn_delete)
            
            layout.addLayout(btn_row)