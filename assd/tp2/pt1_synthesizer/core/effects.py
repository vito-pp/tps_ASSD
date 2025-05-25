"""
/**
 * @file effects.py
 * @brief Applies audio effects to an existing .wav file.
 *
 * This script loads an input audio file in WAV format and applies a series of configurable effects
 * through console prompts. The available effects include:
 *
 * - Simple echo: delayed overlay with configurable delay time and attenuation.
 * - Flat reverb: multiple fixed-delay overlays simulating a basic reverberation.
 * - Low-pass filter: attenuates high frequencies with a user-defined cutoff.
 * - Flanger: sinusoidal delay modulation with adjustable depth and frequency.
 * - Vibrato: pitch modulation via time-varying sample offset.
 *
 * The processed audio is exported as a new WAV file. A spectrogram of the result is also displayed.
 *
 * @note This script does not handle MIDI-to-audio conversion and assumes a valid .wav file as input.
 *
 * @input Input .wav audio file.
 * @output Processed .wav file + spectrogram display.
 *
 * @date 2025
 */
"""

import os
from pydub import AudioSegment
import numpy as np
from scipy.signal import lfilter, butter

# --- FUNCIONES DE EFECTOS ---

def eco_simple(audio, delay_ms=150, attenuation_db=6):
   return audio.overlay(audio - attenuation_db, position=delay_ms)


def reverberacion_plana(audio, delays_ms=[300, 500], attenuations_db=[10, 15]):
    result = audio
    for d, a in zip(delays_ms, attenuations_db):
        result = result.overlay(audio - a, position=d)
    return result

def lowpass_filter(audio_segment, cutoff=2000):
    y = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sr = audio_segment.frame_rate
    b, a = butter(6, cutoff / (sr / 2), btype='low')
    y_filtered = lfilter(b, a, y)
    return AudioSegment(
        y_filtered.astype(np.int16).tobytes(),
        frame_rate=sr,
        sample_width=audio_segment.sample_width,
        channels=audio_segment.channels
    )

def flanger(audio_segment, depth=0.002, rate=0.25):
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sr = audio_segment.frame_rate
    max_delay = int(depth * sr)
    delay = (np.sin(2 * np.pi * rate * np.arange(len(samples)) / sr) + 1) / 2 * max_delay
    delayed = np.zeros_like(samples)
    for i in range(max_delay, len(samples)):
        delayed[i] = 0.5 * samples[i] + 0.5 * samples[int(i - delay[i])]
    return AudioSegment(
        delayed.astype(np.int16).tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width,
        channels=audio_segment.channels
    )

def vibrato(audio_segment, depth=0.002, rate=5):
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sr = audio_segment.frame_rate
    max_delay = int(depth * sr)
    delay = (np.sin(2 * np.pi * rate * np.arange(len(samples)) / sr) + 1) / 2 * max_delay
    vibratoed = np.zeros_like(samples)
    for i in range(max_delay, len(samples)):
        vibratoed[i] = samples[int(i - delay[i])]
    return AudioSegment(
        vibratoed.astype(np.int16).tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width,
        channels=audio_segment.channels
    )

# --- 1. ENTRADA DE AUDIO ---
wav_path = input("🔍 Ingresá el nombre del archivo WAV (ej: entrada.wav): ").strip()

if not os.path.exists(wav_path):
    raise FileNotFoundError(f"❌ No se encontró el archivo: {wav_path}")

audio = AudioSegment.from_wav(wav_path)

# --- 2. SELECCIÓN DE EFECTOS ---
print("\n🎛 ¿Qué efectos querés aplicar?")
apply_eco = input("¿Aplicar eco simple? (s/n): ").lower() == 's'
apply_rev = input("¿Aplicar reverberación plana? (s/n): ").lower() == 's'
apply_lowpass = input("¿Aplicar reverberador pasa-bajos? (s/n): ").lower() == 's'
apply_flang = input("¿Aplicar flanger? (s/n): ").lower() == 's'
apply_vibr = input("¿Aplicar vibrato? (s/n): ").lower() == 's'

# --- 3. APLICACIÓN DE EFECTOS ---
processed = audio

if apply_eco:
    delay = int(input("   ↪ Delay del eco (ms, por defecto 150): ") or "150")
    atten = int(input("   ↪ Atenuación del eco (dB, por defecto 6): ") or "6")
    processed = eco_simple(processed, delay, atten)

if apply_rev:
    processed = reverberacion_plana(processed)

if apply_lowpass:
    cutoff = int(input("   ↪ Frecuencia de corte (Hz, por defecto 2000): ") or "2000")
    processed = lowpass_filter(processed, cutoff)

if apply_flang:
    depth = float(input("   ↪ Profundidad flanger (s, por defecto 0.002): ") or "0.002")
    rate = float(input("   ↪ Frecuencia flanger (Hz, por defecto 0.25): ") or "0.25")
    processed = flanger(processed, depth, rate)

if apply_vibr:
    depth = float(input("   ↪ Profundidad vibrato (s, por defecto 0.002): ") or "0.002")
    rate = float(input("   ↪ Frecuencia vibrato (Hz, por defecto 5): ") or "5")
    processed = vibrato(processed, depth, rate)

# --- 4. EXPORTAR AUDIO ---
output_name = input("\n💾 Nombre del archivo de salida (ej: salida.wav): ").strip()
if not output_name.endswith(".wav"):
    output_name += ".wav"

processed.export(output_name, format="wav")
print(f"✅ Audio procesado guardado como: {output_name}")


