from core.habits import Tarea
import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("iris_datos.db")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha_limite TEXT,
            completada INTEGER, -- 0 para False, 1 para True
            porcentaje_exito REAL
                   )
""")
    
    conexion.commit()
    conexion.close()

def guardar_tarea(tarea):
    conexion = sqlite3.connect("iris_datos.db")
    cursor = conexion.cursor()

    fecha_texto = tarea.fecha_limite.strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO tareas (nombre, fecha_limite, completada, porcentaje_exito)
        VALUES (?, ?, ?, ?)
                   """, (tarea.nombre, fecha_texto, int(tarea.completada), tarea.porcentaje_exito))
    
    conexion.commit()
    conexion.close()

def cargar_tareas():
    conexion = sqlite3.connect("iris_datos.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, fecha_limite, completada, porcentaje_exito FROM tareas")
    filas = cursor.fetchall()

    tareas_cargadas = []
    for f in filas:
        objeto_tarea = Tarea(f[1], f[2], id=f[0]) # Creo el objeto con los datos básicos
        objeto_tarea.completada = bool(f[3])
        objeto_tarea.porcentaje_exito = f[4]
        tareas_cargadas.append(objeto_tarea)

    conexion.close()
    return tareas_cargadas

def actualizar_tarea(id_tarea, completada, exito):
    conexion = sqlite3.connect("iris_datos.db")
    cursor = conexion.cursor()

    valor_completada = 1 if completada else 0

    cursor.execute("""
        UPDATE tareas
        SET completada = ?, porcentaje_exito = ?
        WHERE id = ?
                   """, (valor_completada, exito, id_tarea))
    conexion.commit()
    conexion.close()

def eliminar_tarea(id_tarea):
    conexion = sqlite3.connect("iris_datos.db")
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM tareas WHERE id = ?", (id_tarea,))

    conexion.commit()
    conexion.close()