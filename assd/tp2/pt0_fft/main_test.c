#include "fft.h"
#include <stdio.h>

#define N 8

int main(void)
{ 
    complex float in[N] = {1, 2, 3, 4, 2, 1, 0, -1};
    complex float out[N];

    fft(in, out, N);

    for (size_t i = 0; i < N; i++)
        printf("%.lf%+.lfi\n", creal(out[i]), cimag(out[i]));
}