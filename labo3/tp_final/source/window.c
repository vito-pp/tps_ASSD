#include "window.h"
#include <math.h>

#define PI 3.14159265358979323846

double window[WINDOW_SIZE]; 

void fill_hanning_window(uint16_t N) {
    if (N > WINDOW_SIZE) 
        return; 
    
    for (int n = 0; n < N; n++) {
        window[n] = 0.5 - 0.5 * cosf(2 * PI * (((double)n) / (N - 1)));
    }
}

void fill_hamming_window(uint16_t N) {
    if (N > WINDOW_SIZE) 
        return;

    const double a0 = 0.53836f;   
    const double a1 = 0.46164f;   // = 1 - a0

    for (int n = 0; n < N; n++) {
        window[n] = a0 - a1 * cosf(2 * PI * (((double)n) / (N - 1)));
    }
}

void fill_blackman_window(uint16_t N) {
    if (N > WINDOW_SIZE)  
        return;

    const double a0 = 0.42f;
    const double a1 = 0.50f;
    const double a2 = 0.08f;

    for (int n = 0; n < N; n++) {
        double angle = 2.0 * PI * (((double)n) / (N - 1));
        window[n] = a0 - a1 * cosf(angle) + a2 * cosf(2 * angle);
    }
}

void fill_blackman_harris_window(uint16_t N)
{
    if ( N > WINDOW_SIZE)  
        return;

    const double a0 = 0.35875;
    const double a1 = 0.48829;
    const double a2 = 0.14128;
    const double a3 = 0.01168;

    for (int n = 0; n < N; n++)
    {
        double x = 2.0f * PI * (((double)n) / (N - 1));

        window[n] = a0 
                  - a1 * cosf(x) 
                  + a2 * cosf(2 * x) 
                  - a3 * cosf(3 * x);
    }
}