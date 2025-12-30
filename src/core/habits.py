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
        diferencia = self.fecha_finalizacion - self.fecha_limite # En este punto calculo la diferencia de días entre la fecha que se tenía propuesta (fecha_límite) y la fecha en la cual se completó la tarea
        dias_diferencia = diferencia.days # Entonces se pasa ese valor de la diferencia para que se pueda visualizar los números de días.
        if dias_diferencia <= 0: # Valido entonces si el número de días fue positivo o negativo, para así beneficiar la puntualidad o penalizar el atraso que se haya realizado.
            self.porcentaje_exito += 10
            print(f"Felicidades, terminaste con {abs(dias_diferencia)} días de adelanto.")
        else:
            self.porcentaje_exito -= 10
            print(f"Ánimo, te atrasaste {dias_diferencia} días. ¡A por la siguiente!")

    def para_db(self):
        return (self.nombre, str(self.fecha_limite, int(self.completada), self.porcentaje_exito)) # Con esto busco que retorne una tupla con los datos listos para SQL