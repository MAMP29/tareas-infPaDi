#include <stdio.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>

#define MAX_SIZE (512*1024*1024)

int main()
{
    clock_t start, end;
    double cpu_time;
    int i = 0;
    int j = 0;

    /* MAX_SIZE array is too big for stack.This is an unfortunate rough edge of
     * the way the stack works.  It lives in a fixed-size buffer, set by the 
     * program executable's configuration according to the operating system, but
     * its actual size is seldom checked against the available space. */

    int *arr = (int*)malloc(MAX_SIZE * sizeof(int));

    if (arr == NULL) {
      printf("Asignacion de memoria a la variable 'arr' fallo");
      return 1;
    }

    // Third loop, performing the same operations as loop 2,
    // but only touching 16KB of memory
    printf("\nLoop 3\n");
    for (j = 1 ; j <= 1024 ; j <<= 1)
    {
        /* CPU clock ticks count start */
        start = clock();

        /* Loop 3 */
        for (i = 0; i < MAX_SIZE; i += j)
            arr[i & 0xfff] += 3;

        /* CPU clock ticks count stop */
        end = clock();

        cpu_time = ((double) (end - start)) / CLOCKS_PER_SEC;
        printf("\tCPU time for (j = %d) %.6f secs.\n", j, cpu_time);
    }
    free(arr);
    return 0;
}
