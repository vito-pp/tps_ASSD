"""
/**
 * @file espectrograma.py
 * @brief Carga un archivo WAV y guarda su espectrograma como imagen PNG.
 *
 * Este módulo proporciona la función `plot_spectrogram(wav_path)` que
 * carga un archivo WAV y guarda su espectrograma en escala logarítmica como imagen.
 *
 * @input Ruta al archivo WAV.
 * @output Archivo PNG con el espectrograma.
 *
 * @author Grupo 3
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
    Carga el WAV dado y guarda su espectrograma en escala log como imagen PNG.
    """
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"❌ Archivo no encontrado: {wav_path}")

    # Carga audio completo (respetando la tasa original)
    y, sr = librosa.load(wav_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)


    # Cálculo de STFT y conversión a dB
    S    = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    # Visualización y guardado
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(
        S_db,
        sr=sr,
        x_axis='time',
        y_axis='log',
        cmap='magma'
    )
    plt.colorbar(format="%+2.0f dB")
    plt.title(f'Espectrograma (escala log) de {os.path.basename(wav_path)}')
    plt.tight_layout()

    # Nombre de salida basado en el nombre del archivo WAV
    output_file = os.path.splitext(wav_path)[0] + "_spectrogram.png"
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"📸 Espectrograma guardado como: {output_file}")

if __name__ == "__main__":
    # Modo interactivo: pide la ruta y guarda el espectrograma
    path = input("🎵 Ruta al archivo WAV: ").strip()
    plot_spectrogram(path)
