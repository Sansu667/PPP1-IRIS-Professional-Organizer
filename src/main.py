from core.habits import Tarea
import math
from datetime import datetime

mis_tareas = []
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
        nueva_tarea = Tarea(datos[0], datos[1])
        mis_tareas.append(nueva_tarea)
        
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
         else:
             print("La tarea que seleccionaste no existe. Comprueba de nuevo")

    elif opcion_usuario == 4:
         print("Saliendo de Iris...")
         break
