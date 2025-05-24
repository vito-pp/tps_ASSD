La implemetaci'on de la FFT esta en fft.c con su respectivo header. 
Luego para testear la funci'on se usa el main_test.c, donde se harcodea una
secuencia y printea su DFT a stdout. main_test tiene su Makefile.

Despu'es, para probar con secuencias mas grandes, por ejemplo n = 4096, est'a
el jupyter notebook en donde llama a la funci'on escrita en C y grafica en
matplotlib la sen~al y su espectro. Cambiar "signal" y "n" a su parecer.