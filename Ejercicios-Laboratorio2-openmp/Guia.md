# Laboratorio OpenMP - Ejercicios en C

Este repositorio contiene la solución a dos ejercicios de laboratorio desarrollados en lenguaje C utilizando la biblioteca OpenMP para programación paralela. Cada ejercicio se encuentra en su respectiva carpeta con el código fuente, scripts de automatización y resultados obtenidos.

## Requisitos

-   Sistema operativo Linux
    
-   Compilador `gcc` con soporte para OpenMP
    
-   Bash (para ejecución de scripts)
    
-   Python 3 (solo para análisis del segundo ejercicio)
    
-   Entorno virtual (recomendado para análisis con Python)
    

----------

## Estructura del proyecto

### 🧮 **Ejercicio 1: Simulación Paralela de Lanzamiento de Dados**

**Ubicación:** Carpeta `Ejercicio1-lanzamiento-dados`

**Contenido:**

-   `ejc1-dados.c`: Código fuente principal.
    
-   `script-ejecucion`: Script en Bash que automatiza la ejecución del programa con múltiples hilos.
    
-   `resultados_dados/`: Carpeta que contiene los resultados de lanzamientos para configuraciones de hasta 12 hilos.
    
-   `tiempos-resultados/`: Carpeta con los tiempos de ejecución "puros", recolectados manualmente mediante bucles `for` desde la terminal (sin uso de script).
    

----------

### ⚙️ **Ejercicio 2:  Analizando la Escalabilidad con Diferentes Mecanismos de Control de Threads **

**Ubicación:** Carpeta `Ejercicio2-Mecanismos-de-control`

**Contenido:**

-   `ej2-limite.c`: Código fuente principal.
    
-   `times-script`: Script en Bash que automatiza la ejecución y recolección de tiempos.
    
-   `resultados/`: Carpeta que contiene los resultados generados por el script.
    
-   `analisis_tiempos.py`: Script en Python para el análisis de los tiempos obtenidos.
    
-   `resultados_analisis/`: Carpeta donde se guardan las gráficas y tablas generadas.
    
-   `requirements.txt`: Lista de dependencias necesarias para ejecutar el análisis en Python.
    

**Nota importante:**  
El script de ejecución guarda los resultados temporalmente en la carpeta `/tmp`, que reside en la RAM del sistema. Esto fue intencional, para evitar que la escritura en disco afectara los tiempos de medición.

----------

## 🔧 Configuración del entorno virtual (para análisis en Python)

Si desea generar las gráficas y tablas de análisis del segundo ejercicio, sigue estos pasos:

```bash
cd ejercicio2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python analisis_tiempos.py

```

----------

## 📌 Notas finales

-   Los scripts de ejecución están diseñados para entornos Linux. Asegúrese de otorgarles permisos de ejecución antes de correrlos:
    

```bash
chmod +x script-ejecucion
chmod +x times-script

```

-   Puedes modificar los scripts para adaptarlos a sus propios entornos o cantidades de hilos.
    

----------

¿Quieres que también te ayude a redactar una introducción más teórica o técnica para los ejercicios?
