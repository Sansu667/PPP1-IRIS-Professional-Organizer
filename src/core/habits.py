from datetime import datetime

class Tarea:
    def __init__(self, nombre, fecha_limite, id=None):
        self.id = id
        self.nombre = nombre
        
        # Manejo robusto de fechas
        if isinstance(fecha_limite, str):
            try:
                # Intentamos cortar por si viene con hora "2026-01-01 12:00:00"
                fecha_limpia = fecha_limite.strip()[:10] 
                self.fecha_limite = datetime.strptime(fecha_limpia, "%Y-%m-%d")
            except ValueError:
                self.fecha_limite = datetime.now() # Fallback por seguridad
        else:
            self.fecha_limite = fecha_limite
        
        self.completada = False
        self.porcentaje_exito = 0

    def marcar_como_completada(self):
        self.completada = True
        self.fecha_finalizacion = datetime.now()
        self.calcular_metricas()

    def calcular_metricas(self):
        # Aseguro que fecha_finalizacion exista
        if not hasattr(self, 'fecha_finalizacion'):
            self.fecha_finalizacion = datetime.now()
            
        diferencia = self.fecha_finalizacion - self.fecha_limite
        dias_diferencia = diferencia.days 
        
        if dias_diferencia <= 0:
            self.porcentaje_exito = 100 
        else:
            # Penalización: 10 puntos por día de retraso
            penalizacion = dias_diferencia * 10
            self.porcentaje_exito = max(0, 100 - penalizacion)