
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define MAX_ENTEROS 100000000LL

enum MetodoControl {
    USAR_VARIABLE_ENTORNO = 1,
    USAR_FUNCION_SET,
    USAR_CLAUSULA_NUM_THREADS
};

// Función para obtener el nombre del método
const char* obtener_nombre_metodo(int metodo) {
    switch (metodo) {
        case USAR_VARIABLE_ENTORNO: return "Variable de Entorno (OMP_NUM_THREADS)";
        case USAR_FUNCION_SET: return "omp_set_num_threads()";
        case USAR_CLAUSULA_NUM_THREADS: return "Cláusula num_threads()";
        default: return "Desconocido";
    }
}

// Función principal para sumar números del 1 a MAX_ENTEROS usando el método elegido
long long suma_paralela(int metodo, int num_threads) {
    long long suma_total = 0;

    // Si el método es omp_set_num_threads(), lo aplicamos antes de entrar a la región paralela
    if (metodo == USAR_FUNCION_SET) {
        omp_set_num_threads(num_threads);
    }

    // Dependiendo del método, se usa la directiva adecuada
    if (metodo == USAR_VARIABLE_ENTORNO || metodo == USAR_FUNCION_SET) {
        #pragma omp parallel
        {
            long long suma_local = 0;
            #pragma omp for
            for (long long i = 1; i <= MAX_ENTEROS; i++) {
                suma_local += i;
            }

            // Sección crítica para acumular la suma local en la suma total
            #pragma omp atomic
            suma_total += suma_local;
        }
    } else if (metodo == USAR_CLAUSULA_NUM_THREADS) {
        #pragma omp parallel num_threads(num_threads)
        {
            long long suma_local = 0;
            #pragma omp for
            for (long long i = 1; i <= MAX_ENTEROS; i++) {
                suma_local += i;
            }

            #pragma omp atomic
            suma_total += suma_local;
        }
    }

    return suma_total;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Uso: %s <metodo> <num_threads>\n", argv[0]);
        printf("Métodos:\n");
        printf("  1: Variable de Entorno (OMP_NUM_THREADS)\n");
        printf("  2: omp_set_num_threads()\n");
        printf("  3: #pragma omp parallel num_threads()\n");
        return 1;
    }

    int metodo = atoi(argv[1]);
    int num_threads = atoi(argv[2]);

    double inicio = omp_get_wtime();
    long long resultado = suma_paralela(metodo, num_threads);
    double fin = omp_get_wtime();

    printf("Método: %s\n", obtener_nombre_metodo(metodo));
    printf("Threads solicitados: %d\n", num_threads);
    printf("Suma total = %lld\n", resultado);
    printf("Tiempo de ejecución = %.6f segundos\n", fin - inicio);

    return 0;
}
