from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

class ProgressRing(QWidget):
    """Anillo de progreso circular para mostrar porcentaje de lectura"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percentage = 0.0
        self.label_text = ""
        self.sub_text = ""
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(250, 250)
    
    def update_progress(self, percentage, label="", sub_label=""):
        """Actualiza el progreso y las etiquetas"""
        self.percentage = float(percentage)
        self.label_text = label
        self.sub_text = sub_label
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Geometría
        side = min(self.width(), self.height()) - 40
        rect = QRectF(
            (self.width() - side) / 2,
            (self.height() - side) / 2,
            side,
            side
        )
        
        line_width = 18
        
        # Fondo del anillo
        pen_bg = QPen(QColor("#2d2d36"))
        pen_bg.setWidth(line_width)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)
        
        # Progreso
        if self.percentage > 0:
            # Color según porcentaje
            if self.percentage >= 75:
                color = "#00c853"  # Verde
            elif self.percentage >= 50:
                color = "#03dac6"  # Cyan
            elif self.percentage >= 25:
                color = "#ffb74d"  # Naranja
            else:
                color = "#ff5252"  # Rojo
            
            pen_progress = QPen(QColor(color))
            pen_progress.setWidth(line_width)
            pen_progress.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_progress)
            
            startAngle = 90 * 16
            spanAngle = -int((self.percentage / 100) * 360 * 16)
            painter.drawArc(rect, startAngle, spanAngle)
        
        # Texto central
        painter.setPen(QColor("white"))
        
        # Porcentaje
        font_size = int(side * 0.15)
        painter.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
        painter.drawText(
            rect.adjusted(0, -20, 0, -20),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.percentage:.0f}%"
        )
        
        # Label
        if self.label_text:
            painter.setFont(QFont("Segoe UI", int(font_size * 0.35), QFont.Weight.Normal))
            painter.setPen(QColor("#808090"))
            painter.drawText(
                rect.adjusted(0, 30, 0, 30),
                Qt.AlignmentFlag.AlignCenter,
                self.label_text
            )
        
        # Sub-label
        if self.sub_text:
            painter.setFont(QFont("Segoe UI", int(font_size * 0.3), QFont.Weight.Bold))
            painter.setPen(QColor("#bb86fc"))
            painter.drawText(
                rect.adjusted(0, 50, 0, 50),
                Qt.AlignmentFlag.AlignCenter,
                self.sub_text
            )
        
        painter.end()