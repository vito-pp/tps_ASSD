/**
 * @file fft.h
 * @brief Implementation of the Radix-2 decimation in time Cooley-Tukey FFT 
 * algorithm with normalized output
 * @authors Grupo 3
 */

#ifndef FFT_H
#define FFT_H

#include <stddef.h>
#include <complex.h>

#define FFT_SIZE 1024

/**
 * @brief Computes the FFT of a complex array. Normalized gain as 1/n. 
 * If in = out, then the in array is overwritten with its DFT
 * 
 * @param in Complex float pointer to an input array of lenght n which 
 * represents a time domain signal
 * @param out Complex float pointer to an input array of lenght n which 
 * represents the DFT of the input signal
 */
void fft(complex float *in, complex float *out);

#endif // FFT_H
