#include "fft.h"
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

// don't know why it doesn't recognize the M_PI on math.h
const double PI = 3.141592653589793;

static bool isPowerOf2(size_t n){ return (n & (n - 1)) == 0; }

void fft(complex float *in, complex float *out, size_t n)
{
    // validation 
    if(!isPowerOf2(n))
    {
        fprintf(stderr, "n is not a power of 2. Returning...");
        return;
    }
        
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

    // precomputes the twiddle factors
    complex float *W = malloc(sizeof *W * (n/2));
    if (W == NULL) 
    {
        fprintf(stderr, "Failed to allocate %zu bytes.\n", 
                sizeof *W * (n/2));    
        return;
    }
    for (size_t k = 0; k < n/2; k++) 
    {
        float angle = -2.0f * PI * k / (float)n;
        W[k] = cosf(angle) + I * sinf(angle);
    }

    // FFT
    for (size_t len = 2; len <= n; len <<= 1) 
    {
        size_t half = len >> 1;
        // how far apart in W[] successive twiddles are
        size_t step = n / len;

        for (size_t i = 0; i < n; i += len) 
        {
            for (size_t j = 0; j < half; j++) 
            {
                complex float u = out[i + j];
                complex float v = W[j * step] * out[i + j + half];
                // FFT equations
                out[i + j]           = u + v;
                out[i + j + half]    = u - v;
            }
        }
    }
    // normalizing the gain
    for (size_t i = 0; i < n; i++)
    {
        out[i] /= (complex float)n;
    }

    free(W);
}
