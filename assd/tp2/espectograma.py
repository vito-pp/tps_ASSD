"""
/**
 * @file plot_spectrogram.py
 * @brief Plots the spectrogram of a given .wav audio file.
 *
 * This script prompts the user to provide the path to a WAV file,
 * loads the audio using librosa, computes the Short-Time Fourier Transform (STFT),
 * and visualizes the spectrogram in decibel scale using matplotlib.
 *
 * @input A .wav audio file path.
 * @output A spectrogram plot displayed in a window.
 *
 * @author [Your Name]
 * @date 2025
 */
"""

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Prompt user for WAV file ---
wav_path = input("🎵 Enter the path to the .wav file: ").strip()

if not os.path.exists(wav_path):
    raise FileNotFoundError(f"❌ File not found: {wav_path}")

# --- Load audio ---
y, sr = librosa.load(wav_path)
print(f"✅ Loaded {wav_path} | Duration: {librosa.get_duration(y=y, sr=sr):.2f}s | Sample Rate: {sr}Hz")

# --- Compute spectrogram ---
S = librosa.stft(y)
S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

# --- Plot spectrogram ---
plt.figure(figsize=(10, 4))
librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', cmap='magma')
plt.colorbar(format="%+2.0f dB")
plt.title('Spectrogram (log scale)')
plt.tight_layout()
plt.show()
