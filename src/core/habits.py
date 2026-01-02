from datetime import datetime # Importo esta librería para manejar fechas y hacer los cálculos de tiempo.

class Tarea: # Esta será la clase para hacer el molde de la tarea
    def __init__(self, nombre, fecha_limite, id=None):
        self.id = id
        self.nombre = nombre
        
        if isinstance(fecha_limite, str):
            fecha_limpia = fecha_limite.strip()[:10] 
            self.fecha_limite = datetime.strptime(fecha_limpia, "%Y-%m-%d")
        else:
            self.fecha_limite = fecha_limite
        
        self.completada = False
        self.porcentaje_exito = 0

    def marcar_como_completada(self):
        self.completada = True
        self.fecha_finalizacion = datetime.now()
        self.calcular_metricas()

    def calcular_metricas(self):
        diferencia = self.fecha_finalizacion - self.fecha_limite
        dias_diferencia = diferencia.days 

        # Si terminas justo el día límite, tu éxito base es 100.
        # Si terminas antes, podrías tener un "bonus".
        # Si terminas tarde, restamos puntos por cada día de retraso.
        
        if dias_diferencia <= 0:
            # Éxito total por cumplir a tiempo
            self.porcentaje_exito = 100 
            print(f"✨ ¡Objetivo cumplido! {abs(dias_diferencia)} días de adelanto.")
        else:
            # Penalización: 100 menos 10 puntos por cada día de retraso
            # Usamos max(0, ...) para que el éxito no sea un número negativo
            penalizacion = dias_diferencia * 10
            self.porcentaje_exito = max(0, 100 - penalizacion)
            print(f"⚠️ Tarea completada con retraso de {dias_diferencia} días.")

    def para_db(self):
        return (self.nombre, str(self.fecha_limite, int(self.completada), self.porcentaje_exito)) # Con esto busco que retorne una tupla con los datos listos para SQL