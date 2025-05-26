La implemetación de la FFT está en fft.c con su respectivo header. 
Luego para testear la función se usa el main_test.c, donde se harcodea una secuencia y printea su DFT a stdout. main_test tiene su proprio Makefile.

Después, para probar con secuencias más grandes, por ejemplo n = 4096, está el jupyter notebook en donde llama a la función escrita en C y grafica en matplotlib la señal y su espectro. 
Cambiar "signal" y "n" a su parecer. Por ejemplo:

    # ——— generate a test signal ———
    n = 4096 # (change to test)
    t = np.linspace(0, 10, n, endpoint=False)
    # e.g.: 
    signal = 1*np.sin(2*np.pi*50*t) + 2*np.sin(2*np.pi*125*t) # (change to test)
    signal = signal.astype(np.complex64)  # imaginary part = 0

