from core.habits import Tarea
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

while salir == False:
    print(""" ----- Bienvenido a Iris -----
          1. Crear nueva tarea
          2. Revisar tus tareas
          3. Marcar tarea como completada
          4. Borrar tarea
          5. Salir de Iris
          """)
    
    opcion_usuario = int(input("Introduce la opción que deseas: "))

    if opcion_usuario == 1:
        entrada = input("Ingresa el nombre de la tarea y la fecha límite (Ej: Tarea, AAAA-MM-DD): ")
        datos = entrada.split(",")
        nueva_tarea = Tarea(datos[0].strip(), datos[1].strip())
        mis_tareas.append(nueva_tarea) # Aquí busco, como ya lo había construido, guardar las tareas en la lista vacía.
        guardar_tarea(nueva_tarea) # Entonces con esta línea de código guardo la tarea en la base de datos "iris_datos.db"
        mis_tareas = cargar_tareas()
        print("¡Tarea guardada correctamente!")

    elif opcion_usuario == 2:
         if len(mis_tareas) == 0:
              print("No hay tareas registradas aún.")
         else:
              suma_exito = 0
              print("--- Tus tareas ---")
              for t in mis_tareas:
                print(f"- {t.nombre} (Éxito: {t.porcentaje_exito}%)")
                suma_exito = suma_exito + t.porcentaje_exito
              promedio = suma_exito/len(mis_tareas)
              print(f"Nivel de disciplina general: {promedio}%")
    elif opcion_usuario == 3:
         for index, t in enumerate(mis_tareas, start=1):
             print(f"{index}: {t.nombre}")
         opcion_usuario_completar = int(input("¿Cuál tarea quieres marcar como completada? "))
         indice_real = opcion_usuario_completar - 1
         if mostrar_tareas_numeradas(mis_tareas):
             tarea_elegida = mis_tareas[indice_real]
             tarea_elegida.marcar_como_completada()

             actualizar_tarea(tarea_elegida.id, tarea_elegida.completada, tarea_elegida.porcentaje_exito)

             print(f"¡Base de datos actualizada! Éxito actual: {tarea_elegida.porcentaje_exito}%")
         else:
             print("La tarea que seleccionaste no existe. Comprueba de nuevo")
    elif opcion_usuario == 4:
        if len(mis_tareas) == 0:
            print("No hay tareas para borrar.")
        else:
            print("--- Selecciona la tarea que deseas eliminar ---")
            for index, t in enumerate(mis_tareas, start=1):
                print(f"{index}: {t.nombre}")

            seleccion = int(input("Introduce el número de la tarea: "))
            indice_real = seleccion - 1

            if mostrar_tareas_numeradas(mis_tareas):
                tarea_a_eliminar = mis_tareas[indice_real]
                eliminar_tarea(tarea_a_eliminar.id)
                mis_tareas.pop(indice_real)

                print(f"¡'{tarea_a_eliminar.nombre}' ha sido eliminada")
            else:
                print("Selección inválida")
    elif opcion_usuario == 5:
         print("Saliendo de Iris...")
         break
    

