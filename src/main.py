from core.habits import Tarea
from core.ai_engine import generar_reporte
from database.db_manager import crear_base_de_datos, guardar_tarea, cargar_tareas, actualizar_tarea, eliminar_tarea

crear_base_de_datos() # Aquí aseguro que la tabla exista al iniciar
mis_tareas = cargar_tareas()
salir = False

def mostrar_tareas_numeradas(lista_tareas):
    if not lista_tareas:
        print("\n📭 No hay tareas en la lista.")
        return False
    
    print("\n--- Lista de Tareas ---")
    for index, t in enumerate(lista_tareas, start=1):
        estado = "✅" if t.completada else "⏳"
        print(f"{index}. {estado} {t.nombre} (Plazo: {t.fecha_limite.strftime('%d-%m-%Y')})")
    print("-----------------------\n")
    return True

while not salir:
    # --- CAPA DE INTELIGENCIA: REPORTE DE IRIS ---
    print("\n" + "═" * 45)
    print(" 🧠 ANALISIS DE DESEMPEÑO (IRIS AI)")
    # Llamamos a la función de tu ai_engine.py
    print(generar_reporte(mis_tareas)) 
    print("═" * 45)

    print("""
    1. Crear nueva tarea
    2. Revisar tus tareas
    3. Marcar tarea como completada
    4. Borrar tarea
    5. Salir de Iris
    """)
    
    try:
        opcion_usuario = int(input("Introduce la opción que deseas: "))
    except ValueError:
        print("❌ Por favor, introduce un número válido.")
        continue

    if opcion_usuario == 1:
        entrada = input("Nombre y fecha límite (Ej: Estudiar, 2025-12-30): ")
        if "," in entrada:
            nombre, fecha = entrada.split(",")
            nueva_tarea = Tarea(nombre.strip(), fecha.strip())
            guardar_tarea(nueva_tarea)
            mis_tareas = cargar_tareas() # Recargamos para obtener el ID de la DB
            print("✅ ¡Tarea guardada y sincronizada!")
        else:
            print("❌ Formato incorrecto. Usa la coma para separar.")

    elif opcion_usuario == 2:
        # Usamos tu función optimizada
        mostrar_tareas_numeradas(mis_tareas)
        if mis_tareas:
            suma_exito = sum(t.porcentaje_exito for t in mis_tareas)
            print(f"📊 Nivel de disciplina general: {suma_exito/len(mis_tareas):.1f}%")

    elif opcion_usuario == 3:
        if mostrar_tareas_numeradas(mis_tareas):
            seleccion = int(input("¿Cuál tarea quieres completar?: "))
            indice_real = seleccion - 1
            if 0 <= indice_real < len(mis_tareas):
                tarea_elegida = mis_tareas[indice_real]
                tarea_elegida.marcar_como_completada()
                actualizar_tarea(tarea_elegida.id, tarea_elegida.completada, tarea_elegida.porcentaje_exito)
                print(f"⭐ ¡Excelente! Éxito obtenido: {tarea_elegida.porcentaje_exito}%")
            else:
                print("❌ Número de tarea no válido.")

    elif opcion_usuario == 4:
        if mostrar_tareas_numeradas(mis_tareas):
            seleccion = int(input("Introduce el número de la tarea a borrar: "))
            indice_real = seleccion - 1
            if 0 <= indice_real < len(mis_tareas):
                tarea_a_eliminar = mis_tareas[indice_real]
                eliminar_tarea(tarea_a_eliminar.id)
                mis_tareas.pop(indice_real)
                print(f"🗑️ '{tarea_a_eliminar.nombre}' ha sido eliminada.")

    elif opcion_usuario == 5:
        print("👋 Saliendo de Iris... ¡Vuelve pronto para seguir mejorando!")
        break

