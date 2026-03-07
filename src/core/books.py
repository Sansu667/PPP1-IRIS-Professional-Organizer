from datetime import datetime, timedelta

class Libro:
    """Modelo para gestión de lectura de libros"""
    
    ESTADO_SIN_EMPEZAR = "sin_empezar"
    ESTADO_LEYENDO = "leyendo"
    ESTADO_TERMINADO = "terminado"
    ESTADO_PAUSADO = "pausado"
    
    def __init__(self, titulo, autor, total_paginas, paginas_leidas=0, 
                 genero="", editorial="", anio=None, estado=ESTADO_SIN_EMPEZAR,
                 fecha_inicio=None, fecha_fin=None, id=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.total_paginas = int(total_paginas)
        self.paginas_leidas = int(paginas_leidas)
        self.genero = genero
        self.editorial = editorial
        self.anio = anio
        self.estado = estado
        
        # Fechas
        if fecha_inicio:
            if isinstance(fecha_inicio, str):
                try:
                    self.fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                except ValueError:
                    self.fecha_inicio = None
            else:
                self.fecha_inicio = fecha_inicio
        else:
            self.fecha_inicio = None
        
        if fecha_fin:
            if isinstance(fecha_fin, str):
                try:
                    self.fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                except ValueError:
                    self.fecha_fin = None
            else:
                self.fecha_fin = fecha_fin
        else:
            self.fecha_fin = None
    
    def get_porcentaje_completado(self):
        """Calcula el porcentaje de lectura completado"""
        if self.total_paginas == 0:
            return 0
        return (self.paginas_leidas / self.total_paginas) * 100
    
    def get_paginas_restantes(self):
        """Calcula páginas que faltan por leer"""
        return max(0, self.total_paginas - self.paginas_leidas)
    
    def get_dias_leyendo(self):
        """Calcula cuántos días lleva leyendo el libro"""
        if not self.fecha_inicio:
            return 0
        
        fecha_fin = self.fecha_fin if self.fecha_fin else datetime.now()
        delta = fecha_fin - self.fecha_inicio
        return max(1, delta.days)
    
    def get_promedio_paginas_dia(self):
        """Calcula el promedio de páginas leídas por día"""
        dias = self.get_dias_leyendo()
        if dias == 0:
            return 0
        return self.paginas_leidas / dias
    
    def get_tiempo_estimado_finalizacion(self):
        """Estima cuántos días faltan para terminar el libro"""
        promedio = self.get_promedio_paginas_dia()
        if promedio == 0:
            return None
        
        paginas_faltantes = self.get_paginas_restantes()
        dias_estimados = paginas_faltantes / promedio
        return int(dias_estimados)
    
    def get_horas_estimadas_finalizacion(self, palabras_por_pagina=250, palabras_por_minuto=200):
        """
        Estima horas para terminar el libro
        
        Parámetros por defecto:
        - 250 palabras por página (promedio)
        - 200 palabras por minuto (velocidad de lectura promedio)
        """
        paginas_faltantes = self.get_paginas_restantes()
        total_palabras = paginas_faltantes * palabras_por_pagina
        minutos_totales = total_palabras / palabras_por_minuto
        horas_totales = minutos_totales / 60
        
        return round(horas_totales, 1)
    
    def get_fecha_estimada_finalizacion(self):
        """Calcula la fecha estimada de finalización"""
        dias_estimados = self.get_tiempo_estimado_finalizacion()
        if dias_estimados is None:
            return None
        
        fecha_estimada = datetime.now() + timedelta(days=dias_estimados)
        return fecha_estimada
    
    def get_color_estado(self):
        """Retorna color según el estado del libro"""
        colores = {
            self.ESTADO_SIN_EMPEZAR: "#9e9e9e",  # Gris
            self.ESTADO_LEYENDO: "#03dac6",       # Cyan
            self.ESTADO_TERMINADO: "#00c853",     # Verde
            self.ESTADO_PAUSADO: "#ffb74d"        # Naranja
        }
        return colores.get(self.estado, "#9e9e9e")
    
    def get_icono_estado(self):
        """Retorna icono según el estado"""
        iconos = {
            self.ESTADO_SIN_EMPEZAR: "📕",
            self.ESTADO_LEYENDO: "📖",
            self.ESTADO_TERMINADO: "✅",
            self.ESTADO_PAUSADO: "⏸️"
        }
        return iconos.get(self.estado, "📚")
    
    def get_texto_estado(self):
        """Retorna texto legible del estado"""
        textos = {
            self.ESTADO_SIN_EMPEZAR: "SIN EMPEZAR",
            self.ESTADO_LEYENDO: "LEYENDO",
            self.ESTADO_TERMINADO: "TERMINADO",
            self.ESTADO_PAUSADO: "PAUSADO"
        }
        return textos.get(self.estado, "DESCONOCIDO")
    
    def actualizar_progreso(self, paginas_leidas):
        """Actualiza el progreso de lectura"""
        self.paginas_leidas = min(paginas_leidas, self.total_paginas)
        
        # Actualizar estado automáticamente
        if self.paginas_leidas == 0:
            self.estado = self.ESTADO_SIN_EMPEZAR
        elif self.paginas_leidas >= self.total_paginas:
            self.estado = self.ESTADO_TERMINADO
            if not self.fecha_fin:
                self.fecha_fin = datetime.now()
        else:
            if self.estado == self.ESTADO_SIN_EMPEZAR:
                self.estado = self.ESTADO_LEYENDO
                if not self.fecha_inicio:
                    self.fecha_inicio = datetime.now()
    
    def marcar_como_terminado(self):
        """Marca el libro como terminado"""
        self.paginas_leidas = self.total_paginas
        self.estado = self.ESTADO_TERMINADO
        if not self.fecha_fin:
            self.fecha_fin = datetime.now()