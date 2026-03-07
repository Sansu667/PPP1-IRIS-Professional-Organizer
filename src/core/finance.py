from datetime import datetime

class Transaccion:
    """Modelo para transacciones financieras (ingresos/egresos)"""
    
    TIPO_INGRESO = "ingreso"
    TIPO_EGRESO = "egreso"
    
    # Categorías predefinidas
    CATEGORIAS_INGRESO = [
        "Salario", "Freelance", "Inversiones", "Regalos", "Ventas", "Otros"
    ]
    
    CATEGORIAS_EGRESO = [
        "Alimentación", "Transporte", "Vivienda", "Servicios", 
        "Entretenimiento", "Salud", "Educación", "Ropa", 
        "Tecnología", "Otros"
    ]
    
    def __init__(self, titulo, valor, tipo, categoria, descripcion="", fecha=None, id=None):
        self.id = id
        self.titulo = titulo
        self.valor = float(valor)
        self.tipo = tipo  # "ingreso" o "egreso"
        self.categoria = categoria
        self.descripcion = descripcion
        
        if fecha:
            if isinstance(fecha, str):
                try:
                    self.fecha = datetime.strptime(fecha, "%Y-%m-%d")
                except ValueError:
                    self.fecha = datetime.now()
            else:
                self.fecha = fecha
        else:
            self.fecha = datetime.now()
    
    def get_color_categoria(self):
        """Retorna color según la categoría"""
        colores = {
            # Ingresos (tonos verdes)
            "Salario": "#00c853",
            "Freelance": "#00e676",
            "Inversiones": "#69f0ae",
            "Regalos": "#b9f6ca",
            "Ventas": "#00e676",
            
            # Egresos (tonos naranjas/rojos)
            "Alimentación": "#ff6f00",
            "Transporte": "#ff9100",
            "Vivienda": "#ffa726",
            "Servicios": "#ffb74d",
            "Entretenimiento": "#f57c00",
            "Salud": "#ff5252",
            "Educación": "#7c4dff",
            "Ropa": "#e91e63",
            "Tecnología": "#2196f3",
            "Otros": "#9e9e9e"
        }
        return colores.get(self.categoria, "#9e9e9e")
    
    def get_icono_categoria(self):
        """Retorna icono según la categoría"""
        iconos = {
            # Ingresos
            "Salario": "💼",
            "Freelance": "💻",
            "Inversiones": "📈",
            "Regalos": "🎁",
            "Ventas": "🛒",
            
            # Egresos
            "Alimentación": "🍔",
            "Transporte": "🚗",
            "Vivienda": "🏠",
            "Servicios": "💡",
            "Entretenimiento": "🎮",
            "Salud": "🏥",
            "Educación": "📚",
            "Ropa": "👔",
            "Tecnología": "💻",
            "Otros": "📌"
        }
        return iconos.get(self.categoria, "💵")


class Deuda:
    """Modelo para deudas pendientes"""
    
    def __init__(self, titulo, monto_total, monto_pagado=0, acreedor="", 
                 descripcion="", fecha_limite=None, id=None):
        self.id = id
        self.titulo = titulo
        self.monto_total = float(monto_total)
        self.monto_pagado = float(monto_pagado)
        self.acreedor = acreedor
        self.descripcion = descripcion
        
        if fecha_limite:
            if isinstance(fecha_limite, str):
                try:
                    self.fecha_limite = datetime.strptime(fecha_limite, "%Y-%m-%d")
                except ValueError:
                    self.fecha_limite = None
            else:
                self.fecha_limite = fecha_limite
        else:
            self.fecha_limite = None
    
    def get_monto_pendiente(self):
        """Calcula el monto que falta por pagar"""
        return self.monto_total - self.monto_pagado
    
    def get_porcentaje_pagado(self):
        """Calcula el porcentaje pagado"""
        if self.monto_total == 0:
            return 0
        return (self.monto_pagado / self.monto_total) * 100
    
    def esta_pagada(self):
        """Verifica si la deuda está completamente pagada"""
        return self.monto_pagado >= self.monto_total
    
    def get_estado_color(self):
        """Color según el estado de la deuda"""
        if self.esta_pagada():
            return "#03dac6"  # Verde
        elif self.get_porcentaje_pagado() >= 50:
            return "#ffb74d"  # Naranja
        else:
            return "#ff5252"  # Rojo
    
    def get_dias_restantes(self):
        """Calcula días restantes hasta la fecha límite"""
        if not self.fecha_limite:
            return None
        
        hoy = datetime.now().date()
        limite = self.fecha_limite.date() if hasattr(self.fecha_limite, 'date') else self.fecha_limite
        return (limite - hoy).days