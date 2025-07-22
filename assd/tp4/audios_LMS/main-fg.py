import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# --- LMS filter implementation ---
def apply_lms_filter(x, d, P, mu=0.01):
    w = np.zeros(P, dtype=np.float64)
    N = x.shape[0]
    y = np.zeros(N, dtype=np.float64)
    e = np.zeros(N, dtype=np.float64)
    buf = np.zeros(P, dtype=np.float64)
    for n in range(N):
        buf[1:] = buf[:-1]
        buf[0] = x[n]
        y[n] = np.dot(buf, w)
        e[n] = d[n] - y[n]
        w = w + mu * e[n] * buf
    return y, e

# --- SNR calculation ---
def calculate_snr(signal, reference):
    signal_power = np.mean(signal ** 2)
    noise = signal - reference
    noise_power = np.mean(noise ** 2)
    if noise_power == 0:
        return float('inf')  # Evitar división por cero
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def main():
    # Load and preprocess audio
    x, sr1 = sf.read('input.wav')  # Señal ruidosa
    d, sr2 = sf.read('desired.wav')  # Señal deseada (limpia)
    assert sr1 == sr2, 'Sampling rates must match'
    
    # Convertir a mono si es estéreo
    if x.ndim > 1:
        x = x.mean(axis=1)
    if d.ndim > 1:
        d = d.mean(axis=1)

    # Normalizar señales para evitar valores extremos
    x = x / np.max(np.abs(x))
    d = d / np.max(np.abs(d))

    # Asegurarse de que las señales tengan la misma longitud
    min_length = min(len(x), len(d))
    x = x[:min_length]
    d = d[:min_length]

    # Parámetros
    P = 15  # Orden del filtro
    mu = 0.01  # Tasa de aprendizaje

    # Aplicar filtro LMS
    y, e = apply_lms_filter(x, d, P, mu)

    # Guardar la señal filtrada
    sf.write('Filtered_W_LMS.wav', y, sr1)
    print('Filtered audio saved to filtered_bebe.wav')

    # Calcular MSE
    mse_d_y = np.mean((d - y) ** 2)
    print(f"MSE between desired and filtered output: {mse_d_y:.6f}")
    mse_x_y = np.mean((x - y) ** 2)
    print(f"MSE between input and filtered output: {mse_x_y:.6f}")

    # Calcular SNR
    snr_filtered = calculate_snr(y, d)
    snr_input = calculate_snr(x, d)
    print(f"SNR of input signal: {snr_input:.2f} dB")
    print(f"SNR of filtered signal: {snr_filtered:.2f} dB")

    # Visualización
    t =np.linspace(0, min_length/sr1, min_length)
    plt.figure(figsize=(10, 6))
    plt.plot(t, x, label='Señal Ruidosa', alpha=0.7)
    plt.plot(t, y, label='Señal Filtrada (LMS)', color='red')
    plt.legend()
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.title(f'Señal Ruidosa vs Filtrada (SNR Filtrada: {snr_filtered:.2f} dB)')
    plt.xlim(0, 0.02)
    plt.ylim(-2, 2)
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()