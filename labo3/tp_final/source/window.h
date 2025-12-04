#ifndef WINDOW_H
#define WINDOW_H

#include "stdint.h"

#define WINDOW_SIZE 1024

extern double window[WINDOW_SIZE]; 

void fill_hanning_window(uint16_t N);
void fill_hamming_window(uint16_t N);
void fill_blackman_window(uint16_t N);
void fill_blackman_harris_window(uint16_t N);

#endif