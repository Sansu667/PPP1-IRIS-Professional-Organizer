from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt6.QtCore import Qt

class BarChart(QWidget):
    def __init__(self):
        super().__init__()
        self.data = [0] * 7
        self.days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        self.setMinimumHeight(200)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def update_data(self, data_list):
        self.data = data_list
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Márgenes
        margin_bottom = 30
        margin_top = 20
        available_h = h - margin_bottom - margin_top
        
        # Encontrar el valor máximo para escalar las barras
        max_val = max(self.data) if max(self.data) > 0 else 1
        
        # Ancho de las barras y espacio
        bar_width = w / 9
        spacing = bar_width / 4
        
        # Dibujar Eje Base
        pen_axis = QPen(QColor("#333"))
        pen_axis.setWidth(2)
        painter.setPen(pen_axis)
        painter.drawLine(10, h - margin_bottom, w - 10, h - margin_bottom)

        start_x = spacing * 2
        
        for i, val in enumerate(self.data):
            # Calcular altura de la barra
            bar_h = (val / max_val) * available_h
            
            x = start_x + (i * (bar_width + spacing))
            y = h - margin_bottom - bar_h
            
            # Dibujar Barra
            # Color dinámico: Si hay datos, Cyan; si es 0, gris muy oscuro
            color = QColor("#6200ea") if val > 0 else QColor("#2d2d36")
            if val == max_val and val > 0: color = QColor("#03dac6") # Destacar el día más productivo
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            # Rectángulo de la barra
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_h), 4, 4)
            
            # Dibujar Etiqueta (Día)
            painter.setPen(QColor("#808090"))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(int(x), h - 5, int(bar_width), 20, Qt.AlignmentFlag.AlignCenter, self.days[i])
            
            # Dibujar Valor
            if val > 0:
                painter.setPen(QColor("white"))
                painter.drawText(int(x), int(y) - 15, int(bar_width), 20, Qt.AlignmentFlag.AlignCenter, str(val))
        
        painter.end()