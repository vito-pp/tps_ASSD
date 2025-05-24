/**
 * @file fft.h
 * @brief Implementation of the Radix-2 decimation in time Cooley-Tukey FFT 
 * algorithm with normalized output for ASSD
 * @authors Grupo 3
 */

#ifndef FFT_H
#define FFT_H

#include <stddef.h>
#include <complex.h>

/**
 * @brief Computes the FFT of a complex array
 * 
 * @param in Complex float pointer to an input array of lenght n which 
 *              represents a time domain signal
 * @param out Complex float pointer to an input array of lenght n which 
 *              represents the DFT of the input signal
 * @param n Unsigned integer which is the size of the signal. It has to be a 
 *              power of 2 
 * @return void
 */
void fft(complex float *in, complex float *out, size_t n);

#endif // FFT_H