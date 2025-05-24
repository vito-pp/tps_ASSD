#include "fft.h"
#include <stdio.h>

#define N 8

int main(void)
{ 
    complex float in[N] = {1,2,3,4,4,3,2,1};
    complex float out[N];

    fft(in, out, N);

    for (size_t i = 0; i < N; i++)
        printf("%.6lf%+.6lfi\n", creal(out[i]), cimag(out[i]));
}