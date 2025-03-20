import time
import multiprocessing
from multiprocessing import Process
import matplotlib.pyplot as plt
import numpy as np


def tarea_paralelizable(delay, id_proceso=None):
    """
    Función que simula una tarea paralelizable con un retraso específico
    """
    inicio = time.time()
    # Simulamos trabajo con un bucle de cálculos
    resultado = 0
    for i in range(10000000):
        resultado += i * i % 10

    # Añadimos un retraso controlado para simular la carga
    time.sleep(delay)
    fin = time.time()

    if id_proceso is not None:
        print(f"Proceso {id_proceso} terminado en {fin - inicio:.4f} segundos")

    return resultado


def tarea_secuencial(delay):
    """
    Función que simula una tarea secuencial con un retraso específico
    """
    inicio = time.time()
    # Simulamos trabajo con un bucle de cálculos
    resultado = 0
    for i in range(10000000):
        resultado += i * (i + 1) % 10

    # Añadimos un retraso controlado para simular la carga
    time.sleep(delay)
    fin = time.time()

    print(f"Tarea secuencial terminada en {fin - inicio:.4f} segundos")
    return resultado


def ejecutar_paralelo(delay_total, num_workers):
    """
    Ejecuta la parte paralelizable usando multiprocessing.Process
    """
    # Calculamos el delay para cada proceso
    delay_por_proceso = delay_total / num_workers

    inicio = time.time()
    workers = []

    for i in range(num_workers):
        p = multiprocessing.Process(target=tarea_paralelizable, args=(delay_por_proceso, i))
        p.daemon = True  # Para asegurar que terminen si el principal termina
        p.start()
        workers.append(p)

    for p in workers:
        p.join()

    fin = time.time()
    tiempo_paralelo = fin - inicio

    print(f"Tiempo total en paralelo con {num_workers} procesos: {tiempo_paralelo:.4f} segundos")
    return tiempo_paralelo


def calcular_speedup_teorico(parte_secuencial, num_procesadores):
    """
    Calcula el speedup teórico según la Ley de Amdahl
    """
    return 1 / (parte_secuencial + (1 - parte_secuencial) / num_procesadores)


def calcular_speedup_real(tiempo_base, tiempo_paralelo):
    """
    Calcula el speedup real
    """
    return tiempo_base / tiempo_paralelo


def main():
    # Parámetros del programa
    TIEMPO_TOTAL = 10  # Tiempo total en segundos
    FRACCION_SECUENCIAL = 0.3  # 30% del tiempo es secuencial
    MAX_PROCESOS = 16  # Máximo número de procesos a probar

    # Calculamos tiempos para cada sección
    tiempo_secuencial = TIEMPO_TOTAL * FRACCION_SECUENCIAL
    tiempo_paralelizable = TIEMPO_TOTAL * (1 - FRACCION_SECUENCIAL)

    print(f"Iniciando demostración de la Ley de Amdahl")
    print(f"Tiempo total base: {TIEMPO_TOTAL} segundos")
    print(f"Parte secuencial: {FRACCION_SECUENCIAL * 100}% ({tiempo_secuencial} segundos)")
    print(f"Parte paralelizable: {(1 - FRACCION_SECUENCIAL) * 100}% ({tiempo_paralelizable} segundos)")
    print("-" * 50)

    # Ejecutamos la parte secuencial
    inicio_total = time.time()
    tarea_secuencial(tiempo_secuencial)

    # Medimos el tiempo base para la parte paralelizable (con 1 proceso)
    tiempo_base_paralelo = ejecutar_paralelo(tiempo_paralelizable, 1)

    # Datos para la gráfica
    num_procesos_lista = list(range(1, MAX_PROCESOS + 1))
    speedups_reales = [1.0]  # El primer valor es el caso base (1 proceso)
    speedups_teoricos = [1.0]  # El primer valor es el caso base (1 proceso)
    tiempos_totales = [tiempo_secuencial + tiempo_base_paralelo]

    # Probamos con diferentes números de procesos
    for num_procesos in range(2, MAX_PROCESOS + 1):
        print("-" * 50)
        print(f"Ejecutando con {num_procesos} procesos:")

        # Reiniciamos para medir nuevamente
        inicio_total = time.time()
        tarea_secuencial(tiempo_secuencial)
        tiempo_paralelo = ejecutar_paralelo(tiempo_paralelizable, num_procesos)

        tiempo_total = tiempo_secuencial + tiempo_paralelo
        tiempos_totales.append(tiempo_total)
        # Calculamos speedup
        speedup_real = tiempo_base_paralelo / tiempo_paralelo
        speedup_teorico = calcular_speedup_teorico(FRACCION_SECUENCIAL, num_procesos)

        # Añadimos a las listas para la gráfica
        speedups_reales.append(speedup_real)
        speedups_teoricos.append(speedup_teorico)

        # Calculamos el speedup total (considerando parte secuencial)
        speedup_total_real = tiempos_totales[0] / tiempo_total
        speedup_total_teorico = calcular_speedup_teorico(FRACCION_SECUENCIAL, num_procesos)

        print(f"Tiempo total: {tiempo_total:.4f} segundos")
        print(f"Speedup real de la parte paralela: {speedup_real:.4f}")
        print(f"Speedup teórico según Amdahl: {speedup_teorico:.4f}")
        print(f"Speedup total real: {speedup_total_real:.4f}")
        print(f"Speedup total teórico: {speedup_total_teorico:.4f}")

    # Creamos una gráfica
    plt.figure(figsize=(10, 6))

    # Gráfica de speedup
    plt.subplot(1, 2, 1)
    plt.plot(num_procesos_lista, speedups_reales, 'bo-', label='Speedup Real')
    plt.plot(num_procesos_lista, speedups_teoricos, 'ro-', label='Speedup Teórico')
    plt.axhline(y=1 / FRACCION_SECUENCIAL, color='g', linestyle='--',
                label=f'Límite teórico: {1 / FRACCION_SECUENCIAL:.2f}')
    plt.xlabel('Número de Procesos')
    plt.ylabel('Speedup')
    plt.title('Speedup vs Número de Procesos')
    plt.legend()
    plt.grid(True)

    # Gráfica de tiempos
    plt.subplot(1, 2, 2)
    plt.plot(num_procesos_lista, tiempos_totales, 'go-', label='Tiempo Total')
    plt.axhline(y=tiempo_secuencial, color='r', linestyle='--', label=f'Límite teórico: {tiempo_secuencial:.2f} s')
    plt.xlabel('Número de Procesos')
    plt.ylabel('Tiempo (segundos)')
    plt.title('Tiempo Total vs Número de Procesos')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('amdahl_law_demo.png')
    plt.show()

    print("-" * 50)
    print("Demostración completada. Se ha guardado la gráfica en 'amdahl_law_demo.png'")


if __name__ == "__main__":
     main()
