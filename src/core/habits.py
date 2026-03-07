from datetime import datetime

class Tarea:
    # Constantes de prioridad
    PRIORIDAD_ALTA = "alta"
    PRIORIDAD_MEDIA = "media"
    PRIORIDAD_BAJA = "baja"
    
    PRIORIDADES_VALIDAS = [PRIORIDAD_ALTA, PRIORIDAD_MEDIA, PRIORIDAD_BAJA]
    
    def __init__(self, nombre, fecha_limite, id=None, prioridad="media"):
        self.id = id
        self.nombre = nombre
        
        # Validar y establecer prioridad
        if prioridad in self.PRIORIDADES_VALIDAS:
            self.prioridad = prioridad
        else:
            self.prioridad = self.PRIORIDAD_MEDIA
        
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
    
    def get_prioridad_valor(self):
        """Retorna un valor numérico para ordenar (mayor = más prioritario)"""
        if self.prioridad == self.PRIORIDAD_ALTA:
            return 3
        elif self.prioridad == self.PRIORIDAD_MEDIA:
            return 2
        else:
            return 1
    
    def get_prioridad_color(self):
        """Retorna el color asociado a la prioridad"""
        if self.prioridad == self.PRIORIDAD_ALTA:
            return "#ff5252"  # Rojo
        elif self.prioridad == self.PRIORIDAD_MEDIA:
            return "#ffb74d"  # Naranja
        else:
            return "#4fc3f7"  # Azul claro
    
    def get_prioridad_icono(self):
        """Retorna el icono asociado a la prioridad"""
        if self.prioridad == self.PRIORIDAD_ALTA:
            return "🔥"
        elif self.prioridad == self.PRIORIDAD_MEDIA:
            return "⚡"
        else:
            return "📌"
    
    def get_prioridad_texto(self):
        """Retorna el texto legible de la prioridad"""
        return self.prioridad.upper()