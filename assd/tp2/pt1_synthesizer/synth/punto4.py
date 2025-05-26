#!/usr/bin/env python3
"""
Combined Karplus-Strong synthesis, analysis, and noise-response comparison for original and percussion models.

Dependencies:
  - numpy
  - scipy (signal, io.wavfile)
  - matplotlib
Usage:
  python karplus_strong_full.py

Sections:
 1) Karplus-Strong synthesis (string, percussion, harp arpeggio)
 2) Filter analysis (frequency response & pole-zero of original model)
 3) Noise response: compare uniform vs. Gaussian noise through both original and percussion KS models
 4) Save audio outputs
"""

# Hola test
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
import os

# --------------------------
# Karplus-Strong Functions
# --------------------------

# Punto 1: Modelo tiempo invariante y variante (Karplus Strong)
###########################################################################
def karplus_strong(freq, duration, fs=44100, R=0.99, uniform=True):
    L = int(fs/freq - 0.5)
    N = int(duration * fs)
    if N <= 0:
        return np.zeros(0)
    # generate initial noise of length L
    noise = (np.random.uniform if uniform else np.random.normal)(size=L)
    y = np.zeros(N)

    # only seed the first min(L, N) samples
    M = min(L, N)
    y[:M] = noise[:M]
    # optionally pre-filter that seed
    for n in range(1, M):
        y[n] = 0.5*(noise[n] + noise[n-1])

    # only run the main loop when L < N
    if L < N:
        for n in range(L, N):
            y[n] = R * 0.5 * (y[n - L] + y[n - L - 1])

    return y

def karplus_strong_percussion(freq, duration, b, fs=44100, R=0.99, uniform=True):
    """Percussion KS: random ±1 sign in feedback with probability b of +1."""
    # 1) Delay length
    L = int(fs / freq - 0.5)
    # 2) Output length
    N = int(duration * fs)
    # 3) Initial excitation
    if uniform:
        noise = np.random.uniform(-1, 1, size=L)
    else:
        noise = np.random.normal(0, 0.8, size=L)
    # 4) Output buffer
    y = np.zeros(N)
    # 5) Seed the buffer (pre-filter noise if desired)
    y[:L] = noise
    y[0] = noise[0]
    for n in range(1, L):
        y[n] = 0.5 * (noise[n] + noise[n-1])

    # 6) Main loop — FEEDBACK with a fresh random sign each sample
    for n in range(L, N):
        # Recompute sign *inside* the loop, with correct probability
        sign = 1 if np.random.rand() < b else -1
        y[n] = sign * R * 0.5 * (y[n - L] + y[n - L - 1])

    return y
##########################################################################################

# Funciones de Analisis y graficación
##########################################################################################
def generate_arpa_arpeggio(freqs, note_duration, fs=44100, R=0.98, unif=True):
    N_note = int(note_duration * fs)
    total = N_note * len(freqs)
    y = np.zeros(total)
    for i, f in enumerate(freqs):
        y_note = karplus_strong_percussion(f, note_duration, 0, fs, R=R, uniform=unif)
        y[i * N_note:(i + 1) * N_note] += y_note
    return y / np.max(np.abs(y))

# --------------------------
# Filter Analysis
# --------------------------
def compute_transfer(R, L):
    b = np.zeros(L+2)
    b[L] = 0.5 * R
    b[L+1] = 0.5 * R
    a = np.zeros(L+2)
    a[0] = 1.0
    a[L] = -0.5 * R
    a[L+1] = -0.5 * R
    return b, a

# --------------------------
# Noise Response Analysis
# --------------------------
def noise_response_original(b, a, fs, N=500000):
    uni = np.random.uniform(-1, 1, size=N)
    gauss = np.random.normal(0, 1, size=N)
    y_u = signal.lfilter(b, a, uni)
    y_g = signal.lfilter(b, a, gauss)
    f_u, P_u = signal.welch(y_u, fs=fs, nperseg=2048)
    f_g, P_g = signal.welch(y_g, fs=fs, nperseg=2048)
    return f_u, P_u, f_g, P_g

def noise_response_percussion(freq, fs, b_prob, N=500000):
    # Treat noise as initial buffer and iterate
    L = int(fs / freq - 0.5)
    uni = np.random.uniform(-1, 1, size=N)
    gauss = np.random.normal(0, 1, size=N)
    def run_perc(input_noise):
        buf = input_noise[:L].copy()
        out = np.zeros(N)
        for n in range(N):
            out[n] = buf[n % L]
            sign = 1 if np.random.rand() < b_prob else -1
            avg = 0.5 * (buf[n % L] + buf[(n - 1) % L])
            buf[n % L] = sign * avg
        return out
    y_u = run_perc(uni)
    y_g = run_perc(gauss)
    f_u, P_u = signal.welch(y_u, fs=fs, nperseg=2048)
    f_g, P_g = signal.welch(y_g, fs=fs, nperseg=2048)
    return f_u, P_u, f_g, P_g
##########################################################################################

if __name__ == '__main__':
# Punto 2: Analisis de Comportamiento con distintos tipos de ruido
###########################################################################################
    fs = 44100
    duration = 2.0
    string_freq = 440.0
    perc_freq = 440.0
    arpa_notes = [261.63, 329.63, 392.00, 523.25]
    R = 0.99
    b_prob = 0.5

    # Generación de Strings "Sonoros"
    y_string = karplus_strong(string_freq, duration, fs, R)
    y_string_normal = karplus_strong(string_freq, duration, fs, R, uniform=False)

    y_string_percussion = karplus_strong_percussion(string_freq, duration,1, fs=fs, R=0.99)
    y_string_percussion_normal = karplus_strong_percussion(string_freq, duration,1, fs=fs, R=0.99, uniform=False)

    y_perc = karplus_strong_percussion(perc_freq, duration, 0.5, fs=fs, R=0.99)
    y_perc_normal = karplus_strong_percussion(perc_freq, duration, 0.5, fs=fs, R=0.99, uniform=False)

    y_arpa = generate_arpa_arpeggio(arpa_notes, note_duration=0.5, fs=fs, R=0.99)
    y_arpa_normal = generate_arpa_arpeggio(arpa_notes, note_duration=0.5, fs=fs, R=0.99, unif=False)

    # Guardar Audio Generado
    def to_int16(x):
        return (x / np.max(np.abs(x)) * 32767).astype(np.int16)
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/uniform', exist_ok=True)
    os.makedirs('output/normal', exist_ok=True)

    wavfile.write('output/uniform/string.wav', fs, to_int16(y_string_percussion))
    wavfile.write('output/uniform/percussion.wav', fs, to_int16(y_perc))
    wavfile.write('output/uniform/harp_arpeggio.wav', fs, to_int16(y_arpa))

    wavfile.write('output/normal/string_normal.wav', fs, to_int16(y_string_percussion_normal))
    wavfile.write('output/normal/percussion_normal.wav', fs, to_int16(y_perc_normal))
    wavfile.write('output/normal/harp_arpeggio_normal.wav', fs, to_int16(y_arpa_normal))
###################################################################################################


    # Punto 3: Mapeo de Polos y ceros asociado al filtro tiempo invariante
    ###############################################################################################
    L = int(fs / string_freq - 0.5)
    b, a = compute_transfer(R, L)
    w, h = signal.freqz(b, a, worN=1024, fs=fs)
    plt.figure()
    plt.plot(w, 20 * np.log10(np.abs(h)))
    plt.title('Original KS Frequency Response (dB)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True)
    plt.show()
    zeros = np.roots(b)
    poles = np.roots(a)
    plt.figure()
    plt.scatter(np.real(zeros), np.imag(zeros), marker='o', label='Zeros')
    plt.scatter(np.real(poles), np.imag(poles), marker='x', label='Poles')
    plt.title('Original KS Pole-Zero Plot')
    plt.xlabel('Real')
    plt.ylabel('Imaginary')
    plt.legend()
    plt.axis('equal')
    plt.grid(True)
    plt.show()

    # Bonus de Punto 2: Comparacion de Respuesta al input de sonido
    f_u_o, P_u_o, f_g_o, P_g_o = noise_response_original(b, a, fs)
    f_u_p, P_u_p, f_g_p, P_g_p = noise_response_percussion(perc_freq, fs, b_prob)

    plt.figure()
    plt.semilogy(f_u_o, P_u_o, label='Original-Uni')
    plt.semilogy(f_g_o, P_g_o, label='Original-Gauss')
    plt.semilogy(f_u_p, P_u_p, label='Perc-Uni')
    plt.semilogy(f_g_p, P_g_p, label='Perc-Gauss')
    plt.title('PSD: Original vs Percussion KS Models')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('PSD')
    plt.legend()
    plt.grid(True)
    plt.show()
#####################################################################################

# Punto 5: Modelado de caja acustica de una guitarra
from scipy.signal import sosfilt, zpk2sos

def design_modal_resonator(fs, modes):
    sos = []
    for f0, r in modes:
        theta = 2 * np.pi * f0 / fs
        # poles
        p = [r * np.exp(1j * theta), r * np.exp(-1j * theta)]
        # zeros at origin (two)
        z = [0, 0]
        # compute k to normalize peak gain to 1
        k = 1 - 2 * r * np.cos(theta) + r**2
        sos_mode = zpk2sos(z, p, k)
        sos.append(sos_mode)
    return np.vstack(sos)

def apply_guitar_body(y, fs):
    modes = [
        (82,  0.98),
        (145, 0.985),
        (230, 0.99),
        (315, 0.985),
        (460, 0.98),
        (620, 0.975)
    ]
    sos = design_modal_resonator(fs, modes)
    return sosfilt(sos, y)

# Generate signals
fs = 44100
y_ks = karplus_strong(freq=110, duration=2.0, fs=fs)
y_body = apply_guitar_body(y_ks, fs)

# Plot time domain
plt.figure(figsize=(8, 3))
plt.plot(y_ks[:1000], label='KS only')
plt.plot(y_body[:1000], label='KS + Body (normalized)', alpha=0.7)
plt.title('Time Domain - Normalized Resonators')
plt.legend()
plt.tight_layout()
plt.show()

# Plot magnitude spectrum
Yks = np.abs(np.fft.rfft(y_ks))
Ybody = np.abs(np.fft.rfft(y_body))
f = np.fft.rfftfreq(len(y_ks), 1/fs)

plt.figure(figsize=(8, 3))
plt.semilogy(f, Yks+1e-6, label='KS only')
plt.semilogy(f, Ybody+1e-6, label='KS + Body (normalized)', alpha=0.7)
plt.title('Magnitude Spectrum - Normalized Resonators')
plt.xlabel('Frequency (Hz)')
plt.legend()
plt.tight_layout()
plt.show()
#############################################################################

# Section 5: Disadvantages and Limitations
# - Frequency quantization: since the delay-line length L must be an integer, only frequencies equal to fs/(L+Δ) can be synthesized exactly, leading to pitch inaccuracies especially at high registers.
# - Limited harmonic control: the basic KS model produces perfectly harmonic overtones; it cannot simulate inharmonic instruments (e.g., bells, drums) without extra filtering or dispersion.
# - Decay envelope rigidity: the loop-gain R fixes the overall decay time; independent control of attack and sustain requires additional envelopes.
# - Low-frequency challenges: for very low notes (e.g., below A2), the required buffer length grows large, increasing memory use and startup noise.
# - High-frequency constraints: at high pitches (e.g., above A5), the buffer becomes very short (few samples), producing coarse timbres and potential aliasing.
# - Physical realism limits: it omits detailed modeling of string stiffness, body resonance, and damping curves present in real instruments.
# Recommended use: optimal in mid-range octaves (around A2–A5) where buffer lengths and harmonic richness balance artifact minimization.

