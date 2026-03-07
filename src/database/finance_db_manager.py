import sqlite3
from datetime import datetime, timedelta
from core.finance import Transaccion, Deuda

DB_NAME = "iris_datos.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_tablas_finanzas():
    """Crea las tablas necesarias para el módulo de finanzas"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabla de transacciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            fecha TEXT
        )
    """)
    
    # Tabla de deudas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deudas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            monto_total REAL NOT NULL,
            monto_pagado REAL DEFAULT 0,
            acreedor TEXT,
            descripcion TEXT,
            fecha_limite TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# === TRANSACCIONES ===

def guardar_transaccion(transaccion):
    """Guarda una nueva transacción"""
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    fecha_str = transaccion.fecha.strftime("%Y-%m-%d") if hasattr(transaccion.fecha, 'strftime') else str(transaccion.fecha)
    
    cursor.execute("""
        INSERT INTO transacciones (titulo, valor, tipo, categoria, descripcion, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (transaccion.titulo, transaccion.valor, transaccion.tipo, 
          transaccion.categoria, transaccion.descripcion, fecha_str))
    
    conn.commit()
    conn.close()

def cargar_transacciones(tipo=None, mes=None, anio=None):
    """
    Carga transacciones con filtros opcionales
    
    Args:
        tipo: 'ingreso' o 'egreso' para filtrar por tipo
        mes: número del mes (1-12) para filtrar por mes
        anio: año para filtrar por año
    """
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    query = "SELECT id, titulo, valor, tipo, categoria, descripcion, fecha FROM transacciones"
    conditions = []
    params = []
    
    if tipo:
        conditions.append("tipo = ?")
        params.append(tipo)
    
    if mes and anio:
        conditions.append("strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?")
        params.append(f"{mes:02d}")
        params.append(str(anio))
    elif anio:
        conditions.append("strftime('%Y', fecha) = ?")
        params.append(str(anio))
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY fecha DESC"
    
    cursor.execute(query, params)
    filas = cursor.fetchall()
    
    transacciones = []
    for f in filas:
        t = Transaccion(
            titulo=f[1],
            valor=f[2],
            tipo=f[3],
            categoria=f[4],
            descripcion=f[5],
            fecha=f[6],
            id=f[0]
        )
        transacciones.append(t)
    
    conn.close()
    return transacciones

def eliminar_transaccion(id_transaccion):
    """Elimina una transacción"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacciones WHERE id = ?", (id_transaccion,))
    conn.commit()
    conn.close()

def actualizar_transaccion(id_transaccion, titulo, valor, tipo, categoria, descripcion, fecha):
    """Actualiza una transacción existente"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transacciones
        SET titulo = ?, valor = ?, tipo = ?, categoria = ?, descripcion = ?, fecha = ?
        WHERE id = ?
    """, (titulo, valor, tipo, categoria, descripcion, fecha, id_transaccion))
    conn.commit()
    conn.close()

# === DEUDAS ===

def guardar_deuda(deuda):
    """Guarda una nueva deuda"""
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    fecha_limite_str = None
    if deuda.fecha_limite:
        fecha_limite_str = deuda.fecha_limite.strftime("%Y-%m-%d") if hasattr(deuda.fecha_limite, 'strftime') else str(deuda.fecha_limite)
    
    cursor.execute("""
        INSERT INTO deudas (titulo, monto_total, monto_pagado, acreedor, descripcion, fecha_limite)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (deuda.titulo, deuda.monto_total, deuda.monto_pagado, 
          deuda.acreedor, deuda.descripcion, fecha_limite_str))
    
    conn.commit()
    conn.close()

def cargar_deudas(solo_pendientes=False):
    """Carga las deudas"""
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, titulo, monto_total, monto_pagado, acreedor, descripcion, fecha_limite
        FROM deudas
        ORDER BY fecha_limite ASC
    """)
    filas = cursor.fetchall()
    
    deudas = []
    for f in filas:
        d = Deuda(
            titulo=f[1],
            monto_total=f[2],
            monto_pagado=f[3],
            acreedor=f[4],
            descripcion=f[5],
            fecha_limite=f[6],
            id=f[0]
        )
        
        if solo_pendientes and d.esta_pagada():
            continue
        
        deudas.append(d)
    
    conn.close()
    return deudas

def actualizar_pago_deuda(id_deuda, nuevo_monto_pagado):
    """Actualiza el monto pagado de una deuda"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE deudas
        SET monto_pagado = ?
        WHERE id = ?
    """, (nuevo_monto_pagado, id_deuda))
    conn.commit()
    conn.close()

def eliminar_deuda(id_deuda):
    """Elimina una deuda"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM deudas WHERE id = ?", (id_deuda,))
    conn.commit()
    conn.close()

# === ESTADÍSTICAS ===

def obtener_balance():
    """Calcula el balance total (ingresos - egresos)"""
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    # Total ingresos
    cursor.execute("SELECT SUM(valor) FROM transacciones WHERE tipo = 'ingreso'")
    total_ingresos = cursor.fetchone()[0] or 0
    
    # Total egresos
    cursor.execute("SELECT SUM(valor) FROM transacciones WHERE tipo = 'egreso'")
    total_egresos = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'ingresos': total_ingresos,
        'egresos': total_egresos,
        'balance': total_ingresos - total_egresos
    }

def obtener_balance_mensual(mes=None, anio=None):
    """Obtiene el balance de un mes específico"""
    if not mes or not anio:
        hoy = datetime.now()
        mes = hoy.month
        anio = hoy.year
    
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    # Ingresos del mes
    cursor.execute("""
        SELECT SUM(valor) FROM transacciones 
        WHERE tipo = 'ingreso' 
        AND strftime('%m', fecha) = ? 
        AND strftime('%Y', fecha) = ?
    """, (f"{mes:02d}", str(anio)))
    ingresos = cursor.fetchone()[0] or 0
    
    # Egresos del mes
    cursor.execute("""
        SELECT SUM(valor) FROM transacciones 
        WHERE tipo = 'egreso' 
        AND strftime('%m', fecha) = ? 
        AND strftime('%Y', fecha) = ?
    """, (f"{mes:02d}", str(anio)))
    egresos = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'mes': mes,
        'anio': anio,
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': ingresos - egresos
    }

def obtener_gastos_por_categoria(mes=None, anio=None):
    """Obtiene el total de gastos agrupado por categoría"""
    crear_tablas_finanzas()
    conn = conectar()
    cursor = conn.cursor()
    
    query = """
        SELECT categoria, SUM(valor) 
        FROM transacciones 
        WHERE tipo = 'egreso'
    """
    
    params = []
    if mes and anio:
        query += " AND strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?"
        params = [f"{mes:02d}", str(anio)]
    elif anio:
        query += " AND strftime('%Y', fecha) = ?"
        params = [str(anio)]
    
    query += " GROUP BY categoria ORDER BY SUM(valor) DESC"
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    
    return {categoria: monto for categoria, monto in resultados}

def obtener_total_deudas():
    """Calcula el total de deudas pendientes"""
    deudas = cargar_deudas(solo_pendientes=True)
    total_pendiente = sum(d.get_monto_pendiente() for d in deudas)
    return total_pendiente