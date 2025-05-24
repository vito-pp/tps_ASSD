#include "fft.h"
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

// don't know why it doesn't recognize the M_PI on math.h
const float PI = 3.141592653589793;

static bool isPowerOf2(size_t n){ return (n & (n - 1)) == 0; }

void fft(complex float *in, complex float *out, size_t n)
{
    // validation (TODO handle error)
    if(!isPowerOf2(n))
        return;

    // bit reverse ordering. writes the bit reverse on the out array so the in 
    // array remains untouched
    size_t bits = 0;
    for (size_t temp = n; temp > 1; temp >>= 1) 
    {
        bits++;
    }
    for (size_t i = 0; i < n; i++) 
    {
        size_t rev = 0;
        for (size_t b = 0; b < bits; b++) 
        {
            if (i & (1u << b)) 
            {
                rev |= 1u << (bits - 1 - b);
            }
        }
        out[rev] = in[i];
    }

    // FFT
    for (size_t len = 2; len <= n; len <<= 1) 
    {
        // angle = -2π/len
        float theta = -2.0f * PI / (float)len;
        // twiddle factor with Euler's formula
        complex float wlen = cosf(theta) + I * sinf(theta);
        for (size_t i = 0; i < n; i += len) 
        {
            complex float w = 1.0f + 0.0f * I;
            for (size_t j = 0; j < (len >> 1); j++)
            {
                complex float u = out[i + j];
                complex float v = w * out[i + j + (len >> 1)];
                out[i + j]             = u + v;
                out[i + j + (len >> 1)] = u - v;
                w *= wlen;
            }
        }
    }
}
