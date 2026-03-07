from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BookCard(QFrame):
    """Tarjeta visual para mostrar un libro"""
    
    def __init__(self, libro, on_update, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.libro = libro
        self.on_update = on_update
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.setObjectName("book_card")
        
        # ALTURA FIJA - NO CAMBIAR
        self.setMinimumHeight(150)
        self.setMaximumHeight(150)
        
        # Política de tamaño fija
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Fixed
        )
        
        # Color según estado
        border_color = libro.get_color_estado()
        
        if libro.estado == "terminado":
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a2e1a, stop:1 #16161e)"
        elif libro.estado == "leyendo":
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a2e2e, stop:1 #16161e)"
        elif libro.estado == "pausado":
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e261a, stop:1 #16161e)"
        else:
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a2a2a, stop:1 #16161e)"
        
        self.setStyleSheet(f"""
            QFrame#book_card {{
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
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                border-color: #bb86fc; 
                background: rgba(187, 134, 252, 0.1); 
            }}
            QPushButton#btn_complete {{
                background: #03dac6;
                color: black;
                border: none;
            }}
            QPushButton#btn_complete:hover {{
                background: #00ffaa;
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
        layout.setSpacing(5)
        
        # TOP: Título y estado
        top_row = QHBoxLayout()
        
        title = QLabel(f"{libro.get_icono_estado()} {libro.titulo}")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        top_row.addWidget(title, 1)
        
        # Badge de estado
        estado_badge = QLabel(libro.get_texto_estado())
        estado_badge.setStyleSheet(f"""
            background: {border_color}25;
            color: {border_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 3px 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        estado_badge.setFixedSize(90, 20)
        estado_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(estado_badge)
        
        layout.addLayout(top_row)
        
        # MIDDLE: Información del libro
        info_layout = QHBoxLayout()
        
        # Autor y género
        left_col = QVBoxLayout()
        left_col.setSpacing(2)
        
        autor_label = QLabel(f"✍️ {libro.autor}")
        autor_label.setStyleSheet("color: #808090; font-size: 10px;")
        left_col.addWidget(autor_label)
        
        if libro.genero:
            genero_label = QLabel(f"📚 {libro.genero}")
            genero_label.setStyleSheet("color: #808090; font-size: 10px;")
            left_col.addWidget(genero_label)
        
        info_layout.addLayout(left_col, 1)
        
        # Páginas
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.setSpacing(2)
        
        paginas_label = QLabel(f"{libro.paginas_leidas} / {libro.total_paginas} pág")
        paginas_label.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
        paginas_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(paginas_label)
        
        porcentaje_label = QLabel(f"{libro.get_porcentaje_completado():.0f}%")
        porcentaje_label.setStyleSheet(f"color: {border_color}; font-size: 10px; font-weight: bold;")
        porcentaje_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(porcentaje_label)
        
        info_layout.addLayout(right_col)
        
        layout.addLayout(info_layout)
        
        # PROGRESS BAR
        if libro.estado != "sin_empezar":
            progress = QProgressBar()
            progress.setValue(int(libro.get_porcentaje_completado()))
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
        
        # Estadísticas de lectura (solo si está leyendo)
        if libro.estado == "leyendo" and libro.paginas_leidas > 0:
            stats_text = ""
            
            dias_est = libro.get_tiempo_estimado_finalizacion()
            horas_est = libro.get_horas_estimadas_finalizacion()
            
            if dias_est:
                stats_text = f"⏱️ ~{dias_est}d"
            if horas_est:
                if stats_text:
                    stats_text += f" ({horas_est:.1f}h)"
                else:
                    stats_text = f"⏱️ ~{horas_est:.1f}h"
            
            if stats_text:
                stats_label = QLabel(stats_text)
                stats_label.setStyleSheet("color: #bb86fc; font-size: 9px; font-style: italic;")
                stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(stats_label)
        
        # BOTTOM: Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        if libro.estado != "terminado":
            btn_update = QPushButton("📝 Actualizar")
            btn_update.setFixedHeight(26)
            btn_update.clicked.connect(lambda: self.on_update(libro))
            btn_row.addWidget(btn_update)
            
            if libro.estado != "sin_empezar":
                btn_complete = QPushButton("✓ Terminar")
                btn_complete.setObjectName("btn_complete")
                btn_complete.setFixedHeight(26)
                btn_complete.clicked.connect(lambda: self.on_edit(libro, complete=True))
                btn_row.addWidget(btn_complete)
        
        btn_delete = QPushButton("🗑️")
        btn_delete.setObjectName("btn_delete")
        btn_delete.setFixedWidth(35)
        btn_delete.setFixedHeight(26)
        btn_delete.clicked.connect(lambda: self.on_delete(libro))
        btn_row.addWidget(btn_delete)
        
        layout.addLayout(btn_row)