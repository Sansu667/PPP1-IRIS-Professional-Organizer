import sqlite3
from datetime import datetime
from core.books import Libro

DB_NAME = "iris_datos.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_tablas_libros():
    """Crea la tabla necesaria para el módulo de libros"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            total_paginas INTEGER NOT NULL,
            paginas_leidas INTEGER DEFAULT 0,
            genero TEXT,
            editorial TEXT,
            anio INTEGER,
            estado TEXT DEFAULT 'sin_empezar',
            fecha_inicio TEXT,
            fecha_fin TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def guardar_libro(libro):
    """Guarda un nuevo libro"""
    crear_tablas_libros()
    conn = conectar()
    cursor = conn.cursor()
    
    fecha_inicio_str = None
    if libro.fecha_inicio:
        fecha_inicio_str = libro.fecha_inicio.strftime("%Y-%m-%d") if hasattr(libro.fecha_inicio, 'strftime') else str(libro.fecha_inicio)
    
    fecha_fin_str = None
    if libro.fecha_fin:
        fecha_fin_str = libro.fecha_fin.strftime("%Y-%m-%d") if hasattr(libro.fecha_fin, 'strftime') else str(libro.fecha_fin)
    
    cursor.execute("""
        INSERT INTO libros (titulo, autor, total_paginas, paginas_leidas, genero, 
                           editorial, anio, estado, fecha_inicio, fecha_fin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (libro.titulo, libro.autor, libro.total_paginas, libro.paginas_leidas,
          libro.genero, libro.editorial, libro.anio, libro.estado,
          fecha_inicio_str, fecha_fin_str))
    
    conn.commit()
    conn.close()

def cargar_libros(estado=None):
    """
    Carga libros con filtro opcional por estado
    
    Args:
        estado: 'sin_empezar', 'leyendo', 'terminado', 'pausado'
    """
    crear_tablas_libros()
    conn = conectar()
    cursor = conn.cursor()
    
    if estado:
        cursor.execute("""
            SELECT id, titulo, autor, total_paginas, paginas_leidas, genero,
                   editorial, anio, estado, fecha_inicio, fecha_fin
            FROM libros
            WHERE estado = ?
            ORDER BY fecha_inicio DESC
        """, (estado,))
    else:
        cursor.execute("""
            SELECT id, titulo, autor, total_paginas, paginas_leidas, genero,
                   editorial, anio, estado, fecha_inicio, fecha_fin
            FROM libros
            ORDER BY fecha_inicio DESC
        """)
    
    filas = cursor.fetchall()
    
    libros = []
    for f in filas:
        libro = Libro(
            titulo=f[1],
            autor=f[2],
            total_paginas=f[3],
            paginas_leidas=f[4],
            genero=f[5],
            editorial=f[6],
            anio=f[7],
            estado=f[8],
            fecha_inicio=f[9],
            fecha_fin=f[10],
            id=f[0]
        )
        libros.append(libro)
    
    conn.close()
    return libros

def actualizar_progreso_libro(id_libro, paginas_leidas):
    """Actualiza el progreso de lectura de un libro"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Primero obtenemos el libro para actualizar su estado
    cursor.execute("SELECT total_paginas, estado, fecha_inicio FROM libros WHERE id = ?", (id_libro,))
    fila = cursor.fetchone()
    
    if not fila:
        conn.close()
        return
    
    total_paginas, estado_actual, fecha_inicio = fila
    
    # Determinar nuevo estado
    if paginas_leidas == 0:
        nuevo_estado = Libro.ESTADO_SIN_EMPEZAR
        nueva_fecha_inicio = None
        nueva_fecha_fin = None
    elif paginas_leidas >= total_paginas:
        nuevo_estado = Libro.ESTADO_TERMINADO
        nueva_fecha_inicio = fecha_inicio if fecha_inicio else datetime.now().strftime("%Y-%m-%d")
        nueva_fecha_fin = datetime.now().strftime("%Y-%m-%d")
    else:
        # Si estaba sin empezar, cambia a leyendo
        if estado_actual == Libro.ESTADO_SIN_EMPEZAR:
            nuevo_estado = Libro.ESTADO_LEYENDO
            nueva_fecha_inicio = datetime.now().strftime("%Y-%m-%d")
        else:
            nuevo_estado = estado_actual
            nueva_fecha_inicio = fecha_inicio
        nueva_fecha_fin = None
    
    # Actualizar
    cursor.execute("""
        UPDATE libros
        SET paginas_leidas = ?, estado = ?, fecha_inicio = ?, fecha_fin = ?
        WHERE id = ?
    """, (paginas_leidas, nuevo_estado, nueva_fecha_inicio, nueva_fecha_fin, id_libro))
    
    conn.commit()
    conn.close()

def actualizar_libro_completo(id_libro, titulo, autor, total_paginas, genero, editorial, anio):
    """Actualiza la información completa de un libro"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE libros
        SET titulo = ?, autor = ?, total_paginas = ?, genero = ?, editorial = ?, anio = ?
        WHERE id = ?
    """, (titulo, autor, total_paginas, genero, editorial, anio, id_libro))
    
    conn.commit()
    conn.close()

def marcar_libro_como_terminado(id_libro):
    """Marca un libro como terminado"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Obtener total de páginas
    cursor.execute("SELECT total_paginas, fecha_inicio FROM libros WHERE id = ?", (id_libro,))
    fila = cursor.fetchone()
    
    if fila:
        total_paginas, fecha_inicio = fila
        fecha_inicio_final = fecha_inicio if fecha_inicio else datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            UPDATE libros
            SET paginas_leidas = ?, estado = ?, fecha_inicio = ?, fecha_fin = ?
            WHERE id = ?
        """, (total_paginas, Libro.ESTADO_TERMINADO, fecha_inicio_final, 
              datetime.now().strftime("%Y-%m-%d"), id_libro))
    
    conn.commit()
    conn.close()

def eliminar_libro(id_libro):
    """Elimina un libro"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM libros WHERE id = ?", (id_libro,))
    conn.commit()
    conn.close()

def cambiar_estado_libro(id_libro, nuevo_estado):
    """Cambia el estado de un libro"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Si se cambia a leyendo y no tiene fecha inicio, asignarla
    if nuevo_estado == Libro.ESTADO_LEYENDO:
        cursor.execute("SELECT fecha_inicio FROM libros WHERE id = ?", (id_libro,))
        fecha_inicio = cursor.fetchone()[0]
        
        if not fecha_inicio:
            cursor.execute("""
                UPDATE libros
                SET estado = ?, fecha_inicio = ?
                WHERE id = ?
            """, (nuevo_estado, datetime.now().strftime("%Y-%m-%d"), id_libro))
        else:
            cursor.execute("UPDATE libros SET estado = ? WHERE id = ?", (nuevo_estado, id_libro))
    else:
        cursor.execute("UPDATE libros SET estado = ? WHERE id = ?", (nuevo_estado, id_libro))
    
    conn.commit()
    conn.close()

# === ESTADÍSTICAS ===

def obtener_estadisticas_lectura():
    """Obtiene estadísticas generales de lectura"""
    crear_tablas_libros()
    conn = conectar()
    cursor = conn.cursor()
    
    # Total de libros
    cursor.execute("SELECT COUNT(*) FROM libros")
    total_libros = cursor.fetchone()[0]
    
    # Libros terminados
    cursor.execute("SELECT COUNT(*) FROM libros WHERE estado = ?", (Libro.ESTADO_TERMINADO,))
    libros_terminados = cursor.fetchone()[0]
    
    # Libros leyendo actualmente
    cursor.execute("SELECT COUNT(*) FROM libros WHERE estado = ?", (Libro.ESTADO_LEYENDO,))
    libros_leyendo = cursor.fetchone()[0]
    
    # Total de páginas leídas
    cursor.execute("SELECT SUM(paginas_leidas) FROM libros")
    total_paginas_leidas = cursor.fetchone()[0] or 0
    
    # Promedio de páginas por libro terminado
    cursor.execute("""
        SELECT AVG(total_paginas) FROM libros 
        WHERE estado = ?
    """, (Libro.ESTADO_TERMINADO,))
    promedio_paginas = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_libros': total_libros,
        'terminados': libros_terminados,
        'leyendo': libros_leyendo,
        'total_paginas_leidas': int(total_paginas_leidas),
        'promedio_paginas_libro': round(promedio_paginas, 0)
    }

def obtener_libros_por_genero():
    """Obtiene la distribución de libros por género"""
    crear_tablas_libros()
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT genero, COUNT(*) 
        FROM libros 
        WHERE genero IS NOT NULL AND genero != ''
        GROUP BY genero
        ORDER BY COUNT(*) DESC
    """)
    
    resultados = cursor.fetchall()
    conn.close()
    
    return {genero: count for genero, count in resultados}

def obtener_libro_actual():
    """Obtiene el libro que se está leyendo actualmente"""
    libros_leyendo = cargar_libros(estado=Libro.ESTADO_LEYENDO)
    
    if libros_leyendo:
        # Retornar el más reciente
        return libros_leyendo[0]
    
    return None