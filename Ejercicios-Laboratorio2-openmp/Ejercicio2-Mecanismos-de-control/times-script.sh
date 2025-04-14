#!/bin/bash

# ========== Función: mostrar ayuda ==========
mostrar_ayuda() {
    echo "Uso:"
    echo "  ./benchmark.sh --hilos              Ejecuta benchmarks para distintos hilos (100 veces por modo)"
    echo "  ./benchmark.sh --limite             Ejecuta benchmarks variando OMP_THREAD_LIMIT (20 veces por modo)"
    echo "  ./benchmark.sh --help               Muestra esta ayuda"
    exit 1
}

# ========== Función auxiliar para extraer tiempo ==========
# Extrae número del formato "Tiempo de ejecución = 0.273552 segundos"
extraer_tiempo() {
    echo "$1" | sed -n 's/.*= \([0-9.]*\) segundos/\1/p'
}

# ========== Modo: por número de hilos ==========
benchmark_hilos() {
    HILOS_LISTA=(1 2 4 8 16 24 64 128)

    for hilos in "${HILOS_LISTA[@]}"; do
        archivo="/tmp/tiempos${hilos}.txt"
        {
            echo "Forma 1: Usando OMP_NUM_THREADS (ignora el segundo argumento)"
            for i in {1..100}; do
                output=$(OMP_NUM_THREADS=$hilos ./ejc2-limite 1 $hilos)
                extraer_tiempo "$output"
            done
            echo ""

            echo "Forma 2: Usando omp_set_num_threads()"
            for i in {1..100}; do
                output=$(./ejc2-limite 2 $hilos)
                extraer_tiempo "$output"
            done
            echo ""

            echo "Forma 3: Usando num_threads()"
            for i in {1..100}; do
                output=$(./ejc2-limite 3 $hilos)
                extraer_tiempo "$output"
            done
            echo ""
        } >> "$archivo"
        echo "Resultados guardados en $archivo"
    done
}

# ========== Modo: por límite de hilos ==========
benchmark_limite() {
    LIMITES=(8 4)

    for limite in "${LIMITES[@]}"; do
        archivo="/tmp/limite${limite}.txt"
        {
            echo "Usando OMP_THREAD_LIMIT=$limite con modo 1 (OMP_NUM_THREADS)"
            for i in {1..20}; do
                output=$(OMP_THREAD_LIMIT=$limite ./ejc2-limite 1 128)
                extraer_tiempo "$output"
            done
            echo ""

            echo "Usando OMP_THREAD_LIMIT=$limite con modo 2 (omp_set_num_threads)"
            for i in {1..20}; do
                output=$(OMP_THREAD_LIMIT=$limite ./ejc2-limite 2 128)
                extraer_tiempo "$output"
            done
            echo ""

            echo "Usando OMP_THREAD_LIMIT=$limite con modo 3 (num_threads)"
            for i in {1..20}; do
                output=$(OMP_THREAD_LIMIT=$limite ./ejc2-limite 3 128)
                extraer_tiempo "$output"
            done
            echo ""
        } >> "$archivo"
        echo "Resultados guardados en $archivo"
    done
}

# ========== Entrada principal ==========
case "$1" in
    --hilos)
        benchmark_hilos
        ;;
    --limite)
        benchmark_limite
        ;;
    --help | -h)
        mostrar_ayuda
        ;;
    *)
        echo "Opción no válida: $1"
        mostrar_ayuda
        ;;
esac
