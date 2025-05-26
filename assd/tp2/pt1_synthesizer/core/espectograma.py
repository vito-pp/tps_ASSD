"""
/**
 * @file espectrograma.py
 * @brief Carga y muestra el espectrograma de un archivo WAV.
 *
 * Este módulo proporciona la función `plot_spectrogram(wav_path)` que
 * carga un archivo WAV y despliega su espectrograma en escala logarítmica.
 *
 * @input Ruta al archivo WAV.
 * @output Ventana con el espectrograma.
 *
 * @author Tu Nombre
 * @date 2025
 */
"""

import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

def plot_spectrogram(wav_path: str):
    """
    Carga el WAV dado y muestra su espectrograma en escala log.
    """
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"❌ File not found: {wav_path}")

    # Carga audio completo (respetando la tasa original)
    y, sr = librosa.load(wav_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"✅ Loaded {wav_path} | Duration: {duration:.2f}s | Sample Rate: {sr}Hz")

    # Cálculo de STFT y conversión a dB
    S    = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    # Visualización
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(
        S_db,
        sr=sr,
        x_axis='time',
        y_axis='log',
        cmap='magma'
    )
    plt.colorbar(format="%+2.0f dB")
    plt.title(f'Spectrograma (escala log) de {os.path.basename(wav_path)}')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Modo interactivo: pide la ruta y muestra el espectrograma
    path = input("🎵 Ruta al archivo WAV: ").strip()
    plot_spectrogram(path)
