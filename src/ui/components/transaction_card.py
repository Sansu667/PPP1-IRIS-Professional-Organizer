from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

class TransactionCard(QFrame):
    """Tarjeta visual para mostrar una transacción"""
    
    def __init__(self, transaccion, on_delete, parent=None):
        super().__init__(parent)
        self.transaccion = transaccion
        self.on_delete = on_delete
        
        self.setObjectName("transaction_card")
        
        # ALTURA FIJA - NO CAMBIAR
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)
        
        # Política de tamaño fija
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Fixed
        )
        
        # Color según tipo
        if transaccion.tipo == "ingreso":
            border_color = "#00c853"
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a2e1a, stop:1 #16161e)"
        else:
            border_color = "#ff5252"
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e1a1a, stop:1 #16161e)"
        
        self.setStyleSheet(f"""
            QFrame#transaction_card {{
                background: {bg_gradient};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel {{ background: transparent; color: #e0e0e0; }}
            QPushButton {{
                background: transparent;
                border: 1px solid #ff5252;
                color: #ff5252;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #ff525220; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(5)
        
        # TOP: Título y valor
        top_row = QHBoxLayout()
        
        # Icono + Título
        title_layout = QHBoxLayout()
        icono = QLabel(transaccion.get_icono_categoria())
        icono.setStyleSheet("font-size: 18px;")
        icono.setFixedWidth(25)
        title_layout.addWidget(icono)
        
        title = QLabel(transaccion.titulo)
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        top_row.addLayout(title_layout, 1)
        
        # Valor
        signo = "+" if transaccion.tipo == "ingreso" else "-"
        valor_label = QLabel(f"{signo} ${transaccion.valor:,.0f}")
        valor_label.setStyleSheet(f"""
            color: {border_color};
            font-size: 16px;
            font-weight: bold;
        """)
        valor_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_row.addWidget(valor_label)
        
        layout.addLayout(top_row)
        
        # MIDDLE: Categoría y fecha
        mid_row = QHBoxLayout()
        
        categoria_label = QLabel(f"📁 {transaccion.categoria}")
        categoria_label.setStyleSheet("color: #808090; font-size: 10px;")
        mid_row.addWidget(categoria_label)
        
        mid_row.addStretch()
        
        fecha_label = QLabel(f"📅 {transaccion.fecha.strftime('%Y-%m-%d')}")
        fecha_label.setStyleSheet("color: #808090; font-size: 10px;")
        mid_row.addWidget(fecha_label)
        
        layout.addLayout(mid_row)
        
        # BOTTOM: Descripción y botón
        bottom_row = QHBoxLayout()
        
        if transaccion.descripcion:
            desc_label = QLabel(transaccion.descripcion[:50] + "..." if len(transaccion.descripcion) > 50 else transaccion.descripcion)
            desc_label.setStyleSheet("color: #b0b0b0; font-size: 9px; font-style: italic;")
            bottom_row.addWidget(desc_label, 1)
        else:
            bottom_row.addStretch(1)
        
        btn_delete = QPushButton("🗑️ Eliminar")
        btn_delete.setFixedWidth(90)
        btn_delete.setFixedHeight(24)
        btn_delete.clicked.connect(lambda: self.on_delete(transaccion))
        bottom_row.addWidget(btn_delete)
        
        layout.addLayout(bottom_row)