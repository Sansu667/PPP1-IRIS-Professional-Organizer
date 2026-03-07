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
    
    # Agregar columnas nuevas si no existen
    try: 
        cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_completada TEXT")
    except sqlite3.OperationalError: 
        pass
    
    try:
        cursor.execute("ALTER TABLE tareas ADD COLUMN prioridad TEXT DEFAULT 'media'")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

def guardar_tarea(tarea):
    crear_base_de_datos()
    conn = conectar()
    cursor = conn.cursor()
    fecha_limite = tarea.fecha_limite.strftime("%Y-%m-%d") if hasattr(tarea.fecha_limite, 'strftime') else str(tarea.fecha_limite)
    
    # Asegurar que la tarea tenga prioridad
    prioridad = getattr(tarea, 'prioridad', 'media')
    
    cursor.execute("""
        INSERT INTO tareas (nombre, fecha_limite, completada, porcentaje_exito, fecha_completada, prioridad)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tarea.nombre, fecha_limite, int(tarea.completada), tarea.porcentaje_exito, None, prioridad))
    conn.commit()
    conn.close()

def cargar_tareas():
    crear_base_de_datos()
    conn = conectar()
    cursor = conn.cursor()
    
    # Verificar si existe la columna prioridad
    cursor.execute("PRAGMA table_info(tareas)")
    columnas = [col[1] for col in cursor.fetchall()]
    tiene_prioridad = 'prioridad' in columnas
    
    if tiene_prioridad:
        cursor.execute("SELECT id, nombre, fecha_limite, completada, porcentaje_exito, prioridad FROM tareas")
    else:
        cursor.execute("SELECT id, nombre, fecha_limite, completada, porcentaje_exito FROM tareas")
    
    filas = cursor.fetchall()
    tareas = []
    
    for f in filas:
        if tiene_prioridad and len(f) >= 6:
            prioridad = f[5] if f[5] else 'media'
        else:
            prioridad = 'media'
        
        t = Tarea(f[1], f[2], id=f[0], prioridad=prioridad)
        t.completada = bool(f[3])
        t.porcentaje_exito = f[4]
        tareas.append(t)
    
    conn.close()
    
    # Ordenar por prioridad (alta primero) y luego por fecha
    tareas.sort(key=lambda x: (-x.get_prioridad_valor(), x.fecha_limite))
    
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

def actualizar_tarea_completa(id_tarea, nombre, fecha_limite, prioridad):
    """Actualiza todos los campos de una tarea"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tareas 
        SET nombre = ?, fecha_limite = ?, prioridad = ?
        WHERE id = ?
    """, (nombre, fecha_limite, prioridad, id_tarea))
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
        fechas_obj = [datetime.strptime(f, "%Y-%m-%d").date() for f in fechas]
        
        if fechas_obj[0] == hoy or fechas_obj[0] == (hoy - timedelta(days=1)):
            streak = 1
            fecha_actual = fechas_obj[0]
            
            for i in range(1, len(fechas_obj)):
                if fechas_obj[i] == (fecha_actual - timedelta(days=1)):
                    streak += 1
                    fecha_actual = fechas_obj[i]
                else:
                    break
        else:
            streak = 0

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
    
    cursor.execute("""
        SELECT strftime('%w', fecha_completada), COUNT(*) 
        FROM tareas 
        WHERE completada = 1 AND fecha_completada IS NOT NULL
        GROUP BY strftime('%w', fecha_completada)
    """)
    rows = cursor.fetchall()
    conn.close()
    
    semana = [0] * 7
    
    for dia_str, cuenta in rows:
        dia_idx = int(dia_str)
        if dia_idx == 0: 
            idx_final = 6
        else: 
            idx_final = dia_idx - 1
        semana[idx_final] = cuenta
        
    return semana