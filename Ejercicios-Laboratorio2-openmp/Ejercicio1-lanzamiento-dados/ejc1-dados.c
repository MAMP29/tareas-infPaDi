#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

#define NUM_LANZAMIENTOS 1000000
#define MIN_SUMA 2
#define MAX_SUMA 12

int main() {
    int num_threads;
    double tiempo_inicio = omp_get_wtime(); // Tiempo inicio

    // Almacenaremos los conteos individuales aquí
    int conteos_individuales[128][MAX_SUMA + 1] = {0};  // Máximo 128 hilos

    // Región paralela
    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        int total_threads = omp_get_num_threads();

        // Solo un hilo imprime esto
        #pragma omp single
        {
            num_threads = total_threads;
            printf("Usando %d hilos...\n\n", num_threads);
        }

        // Semilla por hilo para aleatoriedad
        unsigned int semilla = time(NULL) ^ id;

        int lanzamientos_por_hilo = NUM_LANZAMIENTOS / total_threads;

        for (int i = 0; i < lanzamientos_por_hilo; ++i) {
            int dado1 = rand_r(&semilla) % 6 + 1;
            int dado2 = rand_r(&semilla) % 6 + 1;
            int suma = dado1 + dado2;
            conteos_individuales[id][suma]++;
        }
    }

    // Mostrar conteos individuales
    for (int t = 0; t < num_threads; ++t) {
        printf("Hilo %d:\n", t);
        for (int suma = MIN_SUMA; suma <= MAX_SUMA; ++suma) {
            printf("  Suma %2d: %d veces\n", suma, conteos_individuales[t][suma]);
        }
        printf("\n");
    }

    // Combinar todos los conteos en uno global
    int conteo_global[MAX_SUMA + 1] = {0};

    for (int t = 0; t < num_threads; ++t) {
        for (int suma = MIN_SUMA; suma <= MAX_SUMA; ++suma) {
            conteo_global[suma] += conteos_individuales[t][suma];
        }
    }

    // Mostrar resultado total combinado
    printf("Conteo global total:\n");
    for (int suma = MIN_SUMA; suma <= MAX_SUMA; ++suma) {
        printf("  Suma %2d: %d veces\n", suma, conteo_global[suma]);
    }

    // Medir tiempo final y mostrar duración
    double tiempo_final = omp_get_wtime();
    printf("\nTiempo total de ejecución: %.6f segundos\n", tiempo_final - tiempo_inicio);

    return 0;
}
