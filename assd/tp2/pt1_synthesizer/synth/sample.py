#!/usr/bin/env python3
"""
Sample-based synthesizer module.

Provides both:
 - an interactive script `sample_synthesis(midi_data)`
 - a programmatic function `sample_synth(track, sample_rate, instrument_dir, sample_files)`

Dependencies:
  - numpy
  - scipy
  - matplotlib
  - soundfile
  - librosa
  - mido
  - pretty_midi
  - sounddevice
  - os
"""

import numpy as np
# Fix for librosa compatibility with NumPy ≥1.24
if not hasattr(np, 'complex'):
    np.complex = complex

import os
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
import mido
import pretty_midi
import sounddevice as sd

from core.models import Track
from synth import register

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def note_name_to_midi(note_name: str) -> int:
    names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    if len(note_name) == 2:
        name = note_name[0]; octave = int(note_name[1])
    else:
        name = note_name[:2]; octave = int(note_name[2])
    return names.index(name) + 12 * (octave + 1)

def find_closest_sample(midi_note: int, sample_dict: dict[int, str]) -> int:
    available = np.array(list(sample_dict.keys()))
    idx = np.argmin(np.abs(available - midi_note))
    return int(available[idx])

def load_sample(filename: str,
                instrument_dir: str,
                sample_rate: int = 44100
               ) -> np.ndarray:
    path = os.path.join(instrument_dir, filename)
    data, sr = sf.read(path)
    if sr != sample_rate:
        data = librosa.resample(data, orig_sr=sr, target_sr=sample_rate)
    return data

def simple_time_stretch(y: np.ndarray, target_len: int) -> np.ndarray:
    """
    Linearly interpolate `y` to length `target_len`.
    """
    if len(y) == 0 or target_len <= 0:
        return np.zeros(target_len, dtype=y.dtype)
    x_old = np.linspace(0, 1, num=len(y))
    x_new = np.linspace(0, 1, num=target_len)
    return np.interp(x_new, x_old, y)

# -----------------------------------------------------------------------------
# Interactive sample synthesis
# -----------------------------------------------------------------------------

def sample_synthesis(midi_data: pretty_midi.PrettyMIDI) -> None:
    wav_files = ['F2.wav','A#2.wav','D#3.wav','G#3.wav',
                 'C#4.wav','F#4.wav','B4.wav','E5.wav']
    sample_files = { note_name_to_midi(f[:-4]): f for f in wav_files }

    print("Listado de pistas del archivo MIDI:\n")
    for i, inst in enumerate(midi_data.instruments):
        name = inst.name or "Sin nombre"
        print(f"Pista {i}: Instrumento: {name}")

    total = len(midi_data.instruments)
    while True:
        try:
            sel = int(input(f"Ingrese número de pista (0–{total-1}): "))
            if 0 <= sel < total: break
        except:
            pass
        print("Entrada inválida. Intente de nuevo.")
    inst = midi_data.instruments[sel]

    while True:
        choice = input("Seleccione instrumento: G/E/S: ").strip().upper()
        if choice in ('G','E','S'): break
    instr_dir = {'G':'guitarra','E':'guitarra-electrica','S':'strings'}[choice]
    print(f"Sintetizando pista {sel} como {instr_dir}...")

    sr = 44100
    total_dur = midi_data.get_end_time()
    out = np.zeros(int(total_dur * sr))

    for note in inst.notes:
        ref = find_closest_sample(note.pitch, sample_files)
        fname = sample_files[ref]
        samp = load_sample(fname, instr_dir, sr)
        # pitch-shift
        steps = note.pitch - ref
        samp = librosa.effects.pitch_shift(samp, sr=sr, n_steps=steps)
        # time-stretch
        target_len = int((note.end - note.start) * sr)
        samp = simple_time_stretch(samp, target_len)
        # mix
        st = int(note.start * sr)
        en = st + len(samp)
        if en > len(out):
            out = np.pad(out, (0, en - len(out)))
        out[st:en] += samp * (note.velocity / 127.0)

    max_val = np.max(np.abs(out)) or 1.0
    out /= max_val

    filename = f'Pista-{sel}-{instr_dir}.wav'
    sf.write(filename, out, sr)
    print(f"Archivo generado: {filename}")

# -----------------------------------------------------------------------------
# Programmatic sample synth (for main.py)
# -----------------------------------------------------------------------------

def sample_synth(
    track: Track,
    sample_rate: int,
    instrument_dir: str,
    sample_files: dict[int, str]
) -> np.ndarray:
    if not track.events:
        return np.zeros(0)

    total_t = max(e.start_time + e.duration for e in track.events)
    buf     = np.zeros(int(total_t * sample_rate))

    for e in track.events:
        ref = find_closest_sample(e.pitch, sample_files)
        fname = sample_files[ref]
        samp  = load_sample(fname, instrument_dir, sample_rate)
        # pitch-shift
        steps = e.pitch - ref
        samp  = librosa.effects.pitch_shift(samp, sr=sample_rate, n_steps=steps)
        # time-stretch
        target_len = int(e.duration * sample_rate)
        samp       = simple_time_stretch(samp, target_len)
        # mix
        st = int(e.start_time * sample_rate)
        en = st + len(samp)
        if en > buf.shape[0]:
            buf = np.pad(buf, (0, en - buf.shape[0]))
        buf[st:en] += samp * (e.velocity / 127.0)

    max_val = np.max(np.abs(buf)) if buf.size > 0 else 1.0
    return buf / max_val

# Register for main.py dispatch
register("sample", sample_synth)

# -----------------------------------------------------------------------------
# Allow running standalone
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    path = input("Ingrese ruta al archivo MIDI (.mid): ")
    midi = pretty_midi.PrettyMIDI(path)
    sample_synthesis(midi)
