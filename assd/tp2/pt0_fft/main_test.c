#include "fft.h"
#include <stdio.h>

#define N 8

int main(void)
{ 
    // sequence with known DFT
    complex float in[N] = {1,2,3,4,4,3,2,1};
    complex float out[N];

    fft(in, out, N);

    for (size_t i = 0; i < N; i++)
        printf("X(%zu) = %.6lf%+.6lfi\n", i, creal(out[i]), cimag(out[i]));

    // if want to test in = out, try:
    /*
        fft(in, in, N);

        for (size_t i = 0; i < N; i++)
            printf("X(%zu) = %.6lf%+.6lfi\n", i, creal(in[i]), cimag(in[i]));
    */
}
