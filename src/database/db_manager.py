import sqlite3
from datetime import datetime, timedelta
from core.habits import Tarea

DB_NAME = "iris_datos.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_base_de_datos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha_limite TEXT,
            completada INTEGER,
            porcentaje_exito REAL
        )
    """)
    try: cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_completada TEXT")
    except sqlite3.OperationalError: pass
    conn.commit()
    conn.close()

def guardar_tarea(tarea):
    crear_base_de_datos()
    conn = conectar()
    cursor = conn.cursor()
    fecha_limite = tarea.fecha_limite.strftime("%Y-%m-%d") if hasattr(tarea.fecha_limite, 'strftime') else str(tarea.fecha_limite)
    cursor.execute("""
        INSERT INTO tareas (nombre, fecha_limite, completada, porcentaje_exito, fecha_completada)
        VALUES (?, ?, ?, ?, ?)
    """, (tarea.nombre, fecha_limite, int(tarea.completada), tarea.porcentaje_exito, None))
    conn.commit()
    conn.close()

def cargar_tareas():
    crear_base_de_datos()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, fecha_limite, completada, porcentaje_exito FROM tareas")
    filas = cursor.fetchall()
    tareas = []
    for f in filas:
        t = Tarea(f[1], f[2], id=f[0])
        t.completada = bool(f[3])
        t.porcentaje_exito = f[4]
        tareas.append(t)
    conn.close()
    return tareas

def actualizar_tarea(id_tarea, completada, exito):
    conn = conectar()
    cursor = conn.cursor()
    fecha_comp = datetime.now().strftime("%Y-%m-%d") if completada else None
    cursor.execute("""
        UPDATE tareas
        SET completada = ?, porcentaje_exito = ?, fecha_completada = ?
        WHERE id = ?
    """, (1 if completada else 0, exito, fecha_comp, id_tarea))
    conn.commit()
    conn.close()

def eliminar_tarea(id_tarea):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (id_tarea,))
    conn.commit()
    conn.close()

def obtener_historial_heatmap():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha_completada, COUNT(*) FROM tareas 
        WHERE completada = 1 AND fecha_completada IS NOT NULL
        GROUP BY fecha_completada
    """)
    datos = cursor.fetchall()
    conn.close()
    return {fila[0]: fila[1] for fila in datos}

# --- ESTADÍSTICAS AVANZADAS ---
def obtener_kpis():
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Total Completadas
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE completada = 1")
    total_completadas = cursor.fetchone()[0]
    
    # 2. Promedio Global
    cursor.execute("SELECT AVG(porcentaje_exito) FROM tareas WHERE completada = 1")
    promedio = cursor.fetchone()[0]
    promedio = promedio if promedio else 0.0
    
    # 3. Cálculo de Racha (Streak)
    # Obtengo todas las fechas únicas completadas ordenadas descendente
    cursor.execute("""
        SELECT DISTINCT fecha_completada FROM tareas 
        WHERE completada = 1 AND fecha_completada IS NOT NULL 
        ORDER BY fecha_completada DESC
    """)
    fechas = [f[0] for f in cursor.fetchall()]
    conn.close()
    
    streak = 0
    if fechas:
        hoy = datetime.now().date()
        # Convierto strings a date objects
        fechas_obj = [datetime.strptime(f, "%Y-%m-%d").date() for f in fechas]
        
        # Chequeo si la última fue hoy o ayer para mantener la racha viva
        if fechas_obj[0] == hoy or fechas_obj[0] == (hoy - timedelta(days=1)):
            streak = 1
            fecha_actual = fechas_obj[0]
            
            for i in range(1, len(fechas_obj)):
                # Si el siguiente en la lista es exactamente un día antes
                if fechas_obj[i] == (fecha_actual - timedelta(days=1)):
                    streak += 1
                    fecha_actual = fechas_obj[i]
                else:
                    break
        else:
            streak = 0 # Se rompió la racha hace más de un día

    return {
        "total": total_completadas,
        "promedio": promedio,
        "streak": streak
    }

def obtener_actividad_semanal():
    """
    Retorna una lista de 7 enteros con la cantidad de tareas completadas por día de la semana.
    Índice 0 = Lunes, ..., 6 = Domingo.
    """
    conn = conectar()
    cursor = conn.cursor()
    
    # SQLite strftime('%w') retorna 0=Domingo, 1=Lunes... 6=Sábado.
    # Vamos a mapearlo a nuestro formato (0=Lunes... 6=Domingo) en python.
    cursor.execute("""
        SELECT strftime('%w', fecha_completada), COUNT(*) 
        FROM tareas 
        WHERE completada = 1 AND fecha_completada IS NOT NULL
        GROUP BY strftime('%w', fecha_completada)
    """)
    rows = cursor.fetchall()
    conn.close()
    
    # Inicializo contadores [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
    semana = [0] * 7
    
    for dia_str, cuenta in rows:
        dia_idx = int(dia_str) # 0=Dom, 1=Lun
        
        # Convertir de (0=Dom...6=Sab) a (0=Lun...6=Dom)
        if dia_idx == 0: idx_final = 6 # Domingo
        else: idx_final = dia_idx - 1  # Lunes(1)->0
        
        semana[idx_final] = cuenta
        
    return semana