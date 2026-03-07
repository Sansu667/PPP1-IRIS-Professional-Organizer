from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt6.QtCore import Qt, QRectF
import math

class PieChart(QWidget):
    """Gráfico circular para mostrar distribución de gastos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}  # {categoria: valor}
        self.colors = {}  # {categoria: color}
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(300, 300)
    
    def update_data(self, data, colors):
        """
        Actualiza los datos del gráfico
        data: dict {categoria: valor}
        colors: dict {categoria: color_hex}
        """
        self.data = data
        self.colors = colors
        self.update()
    
    def paintEvent(self, event):
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Geometría del círculo
        side = min(self.width(), self.height()) - 100
        rect = QRectF(
            (self.width() - side) / 2,
            50,
            side,
            side
        )
        
        # Calcular total
        total = sum(self.data.values())
        if total == 0:
            return
        
        # Dibujar segmentos
        start_angle = 90 * 16  # Empezar desde arriba
        
        for categoria, valor in self.data.items():
            # Calcular ángulo del segmento
            span_angle = int((valor / total) * 360 * 16)
            
            # Color
            color = QColor(self.colors.get(categoria, "#9e9e9e"))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#16161e"), 2))
            
            # Dibujar segmento
            painter.drawPie(rect, start_angle, -span_angle)
            
            start_angle -= span_angle
        
        # Dibujar leyenda
        self.draw_legend(painter)
        
        painter.end()
    
    def draw_legend(self, painter):
        """Dibuja la leyenda del gráfico"""
        legend_x = 10
        legend_y = self.height() - 80
        
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        total = sum(self.data.values())
        x_offset = 0
        
        for i, (categoria, valor) in enumerate(self.data.items()):
            if i >= 5:  # Máximo 5 en la leyenda
                break
            
            # Cuadrado de color
            color = QColor(self.colors.get(categoria, "#9e9e9e"))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(legend_x + x_offset, legend_y, 12, 12)
            
            # Texto
            porcentaje = (valor / total) * 100 if total > 0 else 0
            texto = f"{categoria} ({porcentaje:.0f}%)"
            painter.setPen(QColor("#e0e0e0"))
            painter.drawText(legend_x + x_offset + 18, legend_y + 10, texto)
            
            x_offset += 160
            
            # Nueva línea cada 3 items
            if (i + 1) % 3 == 0:
                legend_y += 20
                x_offset = 0