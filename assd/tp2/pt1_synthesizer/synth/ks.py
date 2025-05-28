import os
import numpy as np
import soundfile as sf
import librosa
import pretty_midi
from synth.punto4 import karplus_strong_percussion
from synth.punto4 import karplus_strong

def ks_synthesis(midi_data: pretty_midi.PrettyMIDI, track_idx: int):
    """
    Interactivo: sintetiza la pista `track_idx` usando Karplus-Strong
    y guarda el WAV en output/Pista-<idx>-KS.wav.
    """
    # Selección de parámetros
    ruido = input("Ruido uniforme? [S/N]:\n").strip().lower() != 'n'

    modelo_mod = input("Percusión [P], Guitarra [G] o" 
                        " Arpa [A]?\n").strip().lower()

    if modelo_mod == 'a':
        b = 0
    elif modelo_mod == 'g':
        b = 1
    elif modelo_mod == 'p':
        b = 0.5
    else:
        b = float(input("Easter egg!!! Elegí tu b:\nb = "))

    inst = midi_data.instruments[track_idx]
    sr = 44100
    dur = midi_data.get_end_time()
    buf = np.zeros(int(dur * sr))

    # Por cada nota, calculo frecuencia y pluck
    for note in inst.notes:
        freq = 440.0 * 2 ** ((note.pitch - 69) / 12)  
        y = karplus_strong_percussion(freq=freq,
                                        duration=note.end - note.start,
                                        b=b,
                                        fs=sr,
                                        R=0.99,
                                        uniform=ruido)
        start = int(note.start * sr)
        end   = start + len(y)
        if end > buf.shape[0]:
            buf = np.pad(buf, (0, end - buf.shape[0]))
        buf[start:end] += y

    # Normalizo
    peak = np.max(np.abs(buf)) or 1.0
    buf /= peak

    # Guardo en output/
    os.makedirs("output", exist_ok=True)
    nombre = f"Pista-{track_idx}-KS.wav"
    path   = os.path.join("output", nombre)
    sf.write(path, buf, sr)
    print(f"Archivo KS generado: {path}")

    return buf

# Registrar también si quisieras dispatch vía get_synth
from synth import register
register("ks_int", ks_synthesis)
