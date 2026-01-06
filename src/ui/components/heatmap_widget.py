from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QDate

class HeatmapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10,10,10,10)
        
        # Header
        h_layout = QHBoxLayout()
        title = QLabel("🔥 Historial de Productividad (6 Meses)")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        h_layout.addWidget(title); h_layout.addStretch()
        self.layout.addLayout(h_layout)
        
        # Grid Wrapper (Para centrar)
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper) # Uso HBox para centrar el Grid
        wrapper_layout.addStretch() # Resorte izquierda
        
        # Grid Container
        grid_container = QWidget()
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(3)
        wrapper_layout.addWidget(grid_container)
        
        wrapper_layout.addStretch() # Resorte derecha
        
        self.layout.addWidget(wrapper)
        
        self.cells = {}
        self.init_grid()
        self.init_legend()

    def init_grid(self):
        hoy = QDate.currentDate()
        weeks = 26
        start_date = hoy.addDays(-(weeks * 7) + (7 - hoy.dayOfWeek()))
        
        days = ["", "M", "", "W", "", "F", ""]
        for i, d in enumerate(days):
            l = QLabel(d); l.setStyleSheet("color: #555; font-size: 9px;")
            self.grid_layout.addWidget(l, i + 1, 0)

        current_month = -1
        for col in range(weeks):
            d_check = start_date.addDays(col * 7)
            if d_check.month() != current_month:
                l = QLabel(d_check.toString("MMM"))
                l.setStyleSheet("color: #555; font-size: 9px; font-weight: bold;")
                self.grid_layout.addWidget(l, 0, col + 1)
                current_month = d_check.month()

            for row in range(7):
                date_str = start_date.addDays((col * 7) + row).toString("yyyy-MM-dd")
                cell = QFrame(); cell.setFixedSize(13, 13)
                cell.setStyleSheet("background-color: #2d2d36; border-radius: 2px;")
                cell.setToolTip(f"{date_str}: 0")
                self.grid_layout.addWidget(cell, row + 1, col + 1)
                self.cells[date_str] = cell

    def init_legend(self):
        l = QHBoxLayout(); l.addStretch()
        l.addWidget(QLabel("Less", styleSheet="color: #555; font-size: 9px;"))
        for c in ["#2d2d36", "#00600f", "#00a152", "#00e676"]:
            b = QFrame(); b.setFixedSize(10,10); b.setStyleSheet(f"background: {c}; border-radius: 2px;")
            l.addWidget(b)
        l.addWidget(QLabel("More", styleSheet="color: #555; font-size: 9px;"))
        self.layout.addLayout(l)

    def update_heatmap(self, data):
        for d, c in data.items():
            if d in self.cells:
                color = "#00e676" if c>=4 else "#00a152" if c>=2 else "#00600f"
                self.cells[d].setStyleSheet(f"background: {color}; border-radius: 2px;")
                self.cells[d].setToolTip(f"{d}: {c} completed")