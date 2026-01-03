
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class ProgressChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.figure = Figure(facecolor='#1e1e1e') # Fondo del gráfico oscuro
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111, facecolor='#252526') # Área de dibujo oscura
        
        # Estilos para el texto y los ejes
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['bottom'].set_color('#3e3e3e')
        self.ax.spines['left'].set_color('#3e3e3e')
        self.ax.spines['top'].set_color('#3e3e3e')
        self.ax.spines['right'].set_color('#3e3e3e')
        self.ax.yaxis.label.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.title.set_color('white')

        self.update_chart(0) # Inicializar con 0%

    def update_chart(self, percentage):
        self.ax.clear()
        
        if percentage > 0:
            sizes = [percentage, 100 - percentage]
            colors = ['#007acc', '#444444']
            labels = [f'{percentage:.1f}%', '']
            # Aquí autopct SÍ genera autotexts
            resultado = self.ax.pie(sizes, colors=colors, startangle=90, 
                                   autopct='%1.1f%%', pctdistance=0.85, 
                                   wedgeprops=dict(width=0.4, edgecolor='#1e1e1e'))
            
            # Desempaquetamos con cuidado:
            wedges, texts, autotexts = resultado
            
            # Estilo de los textos internos
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(12)
                autotext.set_fontweight('bold')
        else:
            # Caso 0%: No usamos autopct, por lo que pie() solo devuelve 2 valores
            sizes = [100]
            colors = ['#444444']
            resultado = self.ax.pie(sizes, colors=colors, startangle=90,
                                   wedgeprops=dict(width=0.4, edgecolor='#1e1e1e'))
            # Aquí solo hay wedges y texts
            wedges, texts = resultado

        self.ax.set_title("Disciplina General", color='white', fontsize=14, pad=20)
        self.ax.axis('equal')
        self.figure.tight_layout()
        self.canvas.draw()
        self.canvas.flush_events()
        