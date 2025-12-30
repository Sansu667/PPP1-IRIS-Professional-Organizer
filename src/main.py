from core.habits import Tarea
from database.db_manager import crear_base_de_datos, guardar_tarea, cargar_tareas, actualizar_tarea

crear_base_de_datos() # Aquí aseguro que la tabla exista al iniciar
mis_tareas = cargar_tareas()
salir = False
while salir == False:
    print(""" ----- Bienvenido a Iris -----
          1. Crear nueva tarea
          2. Revisar tus tareas
          3. Marcar tarea como completada
          4. Salir de Iris
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
         if indice_real >= 0 and indice_real < len(mis_tareas):
             tarea_elegida = mis_tareas[indice_real]
             tarea_elegida.marcar_como_completada()

             actualizar_tarea(tarea_elegida.id, tarea_elegida.completada, tarea_elegida.porcentaje_exito)

             print(f"¡Base de datos actualizada! Éxito actual: {tarea_elegida.porcentaje_exito}%")
         else:
             print("La tarea que seleccionaste no existe. Comprueba de nuevo")

    elif opcion_usuario == 4:
         print("Saliendo de Iris...")
         break
