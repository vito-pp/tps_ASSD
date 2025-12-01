#include "fft.h"
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
//#include <stdio.h>

static complex float W[FFT_LEN];

// don't know why it doesn't recognize the M_PI on math.h
const double PI = 3.141592653589793;

// static bool isPowerOf2(size_t n){ return (n & (n - 1)) == 0; }

// bit reverse ordering. writes the bit reverse on the out array so the in 
// array remains untouched
static void bitReverse(const complex float *in, complex float *out, size_t n) 
{
    size_t j = 0;
    for (size_t i = 0; i < n; ++i) 
    {
        out[j] = in[i];
        size_t bit = n >> 1;
        while (j & bit) 
        {
            j ^= bit;
            bit >>= 1;
        }
        j |= bit;
    }
}

void fft(complex float *in, complex float *out)
{
    // validation 
    // if(!isPowerOf2(n))
    // {
    //     //fprintf(stderr, "n is not a power of 2. Returning...");
    //     return;
    // }

    // reorder input by bit reversal
    if (in != out) 
    {
        bitReverse(in, out, FFT_LEN);
    } else 
    {
        // in-place (if in = out): need temp array for bit reversal
        size_t bits = 0;
        for (size_t temp = FFT_LEN; temp > 1; temp >>= 1) 
            bits++;
        for (size_t i = 0; i < FFT_LEN; i++) 
        {
            size_t rev = 0;
            for (size_t b = 0; b < bits; b++) 
            {
                if (i & (1u << b)) 
                    rev |= 1u << (bits - 1 - b);
            }
            if (i < rev) 
            {
                complex float t = out[i];
                out[i]          = out[rev];
                out[rev]        = t;
            }
        }
    }

    // precomputes the twiddle factors
    //complex float *W = malloc(sizeof *W * (n/2));
    // if (W == NULL) 
    // {
    //     fprintf(stderr, "Failed to allocate %zu bytes.\n", 
    //            sizeof *W * (n/2));    
    //     return;
    // }
    for (size_t k = 0; k < FFT_LEN/2; k++) 
    {
        float angle = -2.0f * PI * k / (float)FFT_LEN;
        W[k] = cosf(angle) + I * sinf(angle);
    }
    
    // FFT
    for (size_t len = 2; len <= FFT_LEN; len <<= 1) 
    {
        size_t half = len >> 1;
        // how far apart in W[] successive twiddles are
        size_t step = FFT_LEN / len;

        for (size_t i = 0; i < FFT_LEN; i += len) 
        {
            for (size_t j = 0; j < half; j++) 
            {
                // FFT equations
                complex float u = out[i + j];
                complex float v = W[j * step] * out[i + j + half];
                out[i + j]           = u + v;
                out[i + j + half]    = u - v;
            }
        }
    }
    // normalizing the gain
    for (size_t i = 0; i < FFT_LEN; i++)
    {
        out[i] /= (complex float)FFT_LEN;
    }

    //free(W);
}
