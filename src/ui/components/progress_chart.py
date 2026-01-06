from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

class ProgressChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percentage = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(200, 200) 

    def update_chart(self, value):
        self.percentage = float(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Geometría
        # Dejo un margen de 15px para que el pincel grueso no se corte
        side = min(self.width(), self.height()) - 30
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        
        line_width = 20

        # 2. Fondo
        pen_bg = QPen(QColor("#2d2d36"))
        pen_bg.setWidth(line_width)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)

        # 3. Progreso
        if self.percentage > 0:
            pen_progress = QPen(QColor("#03dac6"))
            pen_progress.setWidth(line_width)
            pen_progress.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_progress)
            
            startAngle = 90 * 16
            spanAngle = -int((self.percentage / 100) * 360 * 16)
            painter.drawArc(rect, startAngle, spanAngle)

        # 4. Texto
        painter.setPen(QColor("white"))
        # Ajusto la fuente para que sea grande pero no "coma" al anillo
        font_size = int(side * 0.10) 
        painter.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.percentage:.1f}%")
        
        painter.end()