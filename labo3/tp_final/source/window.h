#ifndef WINDOW_H
#define WINDOW_H

#include "stdint.h"
#include "fft.h"

extern double window[FFT_SIZE]; 

void fill_rectangular_window(void);
void fill_hann_window(void);
void fill_hamming_window(void);
void fill_blackman_window(void);
void fill_blackman_harris_window(void);

#endif