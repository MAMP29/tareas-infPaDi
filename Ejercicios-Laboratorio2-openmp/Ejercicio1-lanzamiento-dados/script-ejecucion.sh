#!/bin/bash

# Lista de hilos a probar
hilos_list=(1 2 4 8 12)

# Nombre del ejecutable
ejecutable="./ejc1-dados"

# Carpeta para los resultados
mkdir -p resultados_dados

echo "Ejecutando $ejecutable con diferentes hilos..."

for hilos in "${hilos_list[@]}"; do
    echo "-> Ejecutando con $hilos hilo(s)..."
    OMP_NUM_THREADS=$hilos $ejecutable >> "resultados_dados/resultados${hilos}.txt"
done

echo "Ejecuciones completadas. Resultados en carpeta 'resultados-dados/'."
