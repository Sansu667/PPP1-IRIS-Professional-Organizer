from datetime import datetime

def generar_reporte(lista_tareas):
    if not lista_tareas:
        return "Hola, soy Iris. Tu base de datos está vacía. ¿Empezamos a construir tu disciplina hoy?"
    
    # 1. Cálculo de Disciplina General
    promedio = sum(t.porcentaje_exito for t in lista_tareas) / len(lista_tareas)

    # 2. Búsqueda de Tarea Crítica
    pendientes = [t for t in lista_tareas if not t.completada]

    mensaje_urgencia = ""
    if pendientes:
        # BUsco la tarea con la fecha más cercana
        mas_proxima = min(pendientes, key=lambda t: t.fecha_limite)
        dias = (mas_proxima.fecha_limite - datetime.now()).days

        if dias < 0:
            mensaje_urgencia = f"\n Atención: '{mas_proxima.nombre}' está vencida"
        elif dias == 0:
            mensaje_urgencia = f"\n Hoy es el límite para: '{mas_proxima.nombre}'."
        else:
            mensaje_urgencia = f"\n Próximo foco: '{mas_proxima.nombre}' (en {dias} días)."

    # 3. Definición de Personalidad según promedio
    if promedio >= 80:
        estado = "Modo excelencia: Estás dominando tus hábitos."
    elif promedio >= 50:
        estado = "Modo mejora: Vas por buen camino, mantén el ritmo."
    else:
        estado = "Modo rescate: Necesitas retomar el control de tus tareas."

    return f"{estado}\nDisciplina actual: {promedio:1.f}%{mensaje_urgencia}"