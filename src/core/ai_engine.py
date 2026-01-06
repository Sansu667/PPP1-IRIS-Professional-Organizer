from datetime import datetime
import random

# Frases motivacionales
FRASES = {
    "excelencia": [
        "\"Quien tiene un porqué para vivir, puede soportar casi cualquier cómo.\" - Nietzsche",
        "\"La excelencia no es un acto, es un hábito.\" - Aristóteles",
        "\"Amor fati: ama tu destino, que es en realidad tu propia vida.\" - Nietzsche",
        "\"Somos lo que hacemos repetidamente.\" - Aristóteles"
    ],
    "mejora": [
        "\"La disciplina es el puente entre metas y logros.\" - Jim Rohn",
        "\"No cuentes los días, haz que los días cuenten.\" - Muhammad Ali",
        "\"El dolor de la disciplina es temporal, el del arrepentimiento es para siempre.\"",
        "\"Un viaje de mil millas comienza con un solo paso.\" - Lao-Tse"
    ],
    "rescate": [
        "\"No es que tengamos poco tiempo, es que perdemos mucho.\" - Séneca",
        "\"Empieza donde estás. Usa lo que tienes. Haz lo que puedas.\" - Arthur Ashe",
        "\"El caos precede al orden. Organiza tu mente hoy.\"",
        "\"Tus hábitos deciden tu futuro. Cámbialos hoy.\""
    ]
}

def generar_reporte(lista_tareas):
    """
    Genera un reporte HTML con tipografía mejorada y diseño de bloques.
    """
    if not lista_tareas:
        return "<p style='color:#808090; font-size:14px;'>🌑 Base de datos vacía. Inicia el protocolo.</p>"
    
    # 1. Cálculos
    try:
        total = len(lista_tareas)
        completadas = sum(1 for t in lista_tareas if t.completada)
        promedio = (sum(t.porcentaje_exito for t in lista_tareas) / total) if total > 0 else 0.0
    except:
        promedio = 0.0

    # 2. Configuración de Estados (Colores e Iconos)
    if promedio >= 90:
        estado_texto = "MODO EXCELENCIA"
        icono = "💎"
        color_tema = "#03dac6" # Cyan
        cita = random.choice(FRASES["excelencia"])
    elif promedio >= 60:
        estado_texto = "EN PROGRESO"
        icono = "📈"
        color_tema = "#ffb74d" # Naranja
        cita = random.choice(FRASES["mejora"])
    else:
        estado_texto = "MODO RECUPERACIÓN"
        icono = "🛡️"
        color_tema = "#ff5252" # Rojo
        cita = random.choice(FRASES["rescate"])

    # 3. Mensaje de Urgencia
    pendientes = [t for t in lista_tareas if not t.completada]
    if pendientes:
        try:
            def get_date(t):
                if isinstance(t.fecha_limite, str):
                    return datetime.strptime(t.fecha_limite, "%Y-%m-%d").date()
                return t.fecha_limite.date() if hasattr(t.fecha_limite, 'date') else t.fecha_limite

            mas_proxima = min(pendientes, key=get_date)
            dias = (get_date(mas_proxima) - datetime.now().date()).days

            if dias < 0:
                msg_urgencia = f"⚠️ <span style='color:#ff5252'><b>CRÍTICO:</b></span> '{mas_proxima.nombre}' venció hace {abs(dias)} días."
            elif dias == 0:
                msg_urgencia = f"🔥 <span style='color:#ffb74d'><b>FOCO DE HOY:</b></span> '{mas_proxima.nombre}'."
            elif dias == 1:
                msg_urgencia = f"📅 <span style='color:#03dac6'><b>MAÑANA:</b></span> '{mas_proxima.nombre}'."
            else:
                msg_urgencia = f"📅 <b>Próximo objetivo:</b> '{mas_proxima.nombre}' en {dias} días."
        except:
            msg_urgencia = "Analizando cronograma temporal..."
    else:
        msg_urgencia = "✨ <span style='color:#03dac6'><b>Todo al día.</b></span> Eres libre para crear."

    # 4. Generación de HTML
    # - Encabezado grande
    # - Cuerpo legible
    # - Cita con estilo de bloque
    html = f"""
    <html>
    <head/>
    <body>
        <p style='margin-bottom: 8px;'>
            <span style='font-size: 20px; font-weight: 800; color: {color_tema}; letter-spacing: 1px;'>
                {estado_texto} {icono}
            </span>
        </p>
        
        <p style='font-size: 15px; color: #e0e0e0; line-height: 140%; margin-bottom: 15px;'>
            {msg_urgencia}
        </p>
        
        <p style='font-size: 14px; font-style: italic; color: #bb86fc; margin-left: 10px;'>
            <span style='color: {color_tema}; font-weight:bold;'>|</span>&nbsp; {cita}
        </p>
    </body>
    </html>
    """
    
    return html