import numpy as np
import matplotlib.pyplot as plt

# Parámetros de la simulación
OSR = 64               # Oversampling Ratio
fs = 1e6               # Frecuencia de muestreo [Hz]
fo = 1e3               # Frecuencia de la señal de entrada [Hz]
N = OSR * 1024         # Número total de muestras
t = np.arange(N) / fs  # Vector de tiempo
x = 0.5 * np.sin(4 * np.pi * fo * t)  # Señal de entrada (senoidal)

# ---------------------------
# Modulador Sigma-Delta 
# ---------------------------
y = np.zeros(N)  # Salida del integrador
q = np.zeros(N)  # Salida del cuantizador (+1 o -1)
for n in range(1, N):
    y[n] = y[n-1] + (x[n] - q[n-1])
    q[n] = 1.0 if y[n] >= 0 else -1.0

# ---------------------------
# Decimación
# ---------------------------
h = np.ones(OSR) / OSR
v = np.convolve(q, h, mode='same')
v_dec = v[::OSR]             # Señal decimada
fs_dec = fs / OSR            # Frecuencia tras decimar
N_dec = len(v_dec)           # Número de muestras decimadas

# ---------------------------
# Cálculo de THD, SNDR y ENOB
# ---------------------------
# FFT de la señal decimada
V = np.fft.fft(v_dec)
f_dec = np.fft.fftfreq(N_dec, d=1/fs_dec)

# Identificar armónicos hasta Nyquist
max_harm = int((fs_dec/2) // fo)
idxs = [np.argmin(np.abs(f_dec - k*fo)) for k in range(1, max_harm+1)]

# Potencia de fundamental y de armónicos
P1 = np.abs(V[idxs[0]])**2
P_harm = sum(np.abs(V[i])**2 for i in idxs[1:])

# THD
THD = np.sqrt(P_harm / P1)
THD_dB = 20 * np.log10(THD)

# SNDR (excluye DC, fundamental y armónicos)
P_total = np.sum(np.abs(V)**2)
P_noise = P_total - P1 - P_harm - np.abs(V[0])**2
SNDR = 10 * np.log10(P1 / P_noise)

# ENOB y ganancia de resolución sobre 1 bit
ENOB = (SNDR - 1.76) / 6.02
resolution_gain = ENOB - 1.0

print(f"THD   = {THD_dB:.2f} dB")
print(f"SNDR  = {SNDR:.2f} dB")
print(f"ENOB  = {ENOB:.2f} bits (ganancia ≈ {resolution_gain:.2f} bits)")

# ---------------------------
# Gráficos (idénticos a la versión anterior)
# ---------------------------
# 1) Señal de entrada vs. salida del cuantizador (primeros 200 puntos)
plt.figure()
plt.plot(t[:200], x[:200], label='Entrada')
plt.plot(t[:200], q[:200], label='Salida cuantizador', alpha=0.7)
plt.legend()
plt.title('Sigma-Delta 1er Orden (tiempo)')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid()

# 2) Salida tras decimación vs. señal original sobremuestreada
plt.figure()
plt.plot(t[::OSR][:200], x[::OSR][:200], label='Entrada (sobremuestreada)', alpha=0.7)
plt.plot(t[::OSR][:200], v_dec[:200], label='Salida decimada')
plt.legend()
plt.title('Salida tras Decimación')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid()

# 3) PSD del ruido (Noise Shaping)
noise = q - x
Noise_fft = np.abs(np.fft.fft(noise))**2
f = np.fft.fftfreq(N, d=1/fs)

plt.figure()
plt.semilogy(f[:N//2], Noise_fft[:N//2])
plt.title('PSD del Ruido (Noise Shaping)')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('PSD')
plt.grid()
plt.tight_layout()

plt.show()

# CONCLUSIONES:
# En la simulación con un modulador sigma-delta de primer orden y OSR=64 se confirma que el integrador acumula correctamente la diferencia entre la señal de 
# entrada senoidal y la salida del cuantizador 1-bit, cuyo tren de pulsos ±1 sigue fielmente la envolvente del seno; la PSD del error muestra un crecimiento 
# de ruido con la frecuencia (≈+20 dB/década), evidenciando el efecto de noise shaping que desplaza el ruido fuera de banda base; tras aplicar un filtro de 
# promedio móvil y decimar, la señal reconstruida en fs/OSR coincide muy bien en amplitud y fase con la original, demostrando la eficacia del proceso de decimación 
# para atenuar el ruido de alta frecuencia; sin embargo, el cálculo cuantitativo arroja un THD de –34,93 dB y un SNDR (Relacion Senal-Ruido y Distorcion) 
# de –5,24 dB, lo que se traduce en una ENOB (numero efectivo de bits) de –1,16 bits (ganancia de resolución ≈–2,16 bits sobre el cuantizador de 1 bit), valores
# negativos atribuibles al filtrado demasiado sencillo que no elimina suficiente ruido fuera de banda; por tanto, aunque el OSR elevado mejora teóricamente 
# la resolución (≈3 dB extra por duplicar OSR), para materializar esa ganancia en bits efectivos es imprescindible emplear un filtro de decimación más 
# selectivo (por ejemplo, un FIR de mayor orden) o un modulador de orden superior.
