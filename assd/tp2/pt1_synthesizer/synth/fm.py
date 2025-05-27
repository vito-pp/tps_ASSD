import os
import numpy as np
import soundfile as sf
import pretty_midi

# teoría basada en: "The Synthesis of Complex Audio Spectra
# by Means of Frequency Modulation", Chowning

def A_adsr(t: np.ndarray, dur: float, A_peak: float = 1.0) -> np.ndarray:
    '''
    Envolvente ADSR vectorizada para un array de tiempos t.
    '''
    A = 0.01 * dur    # 1% attack
    D = 0.1 * dur     # 10% decay
    S = 0.7           # sustain level
    R = 0.2 * dur     # 20% release

    env = np.zeros_like(t)
    # Attack
    env = np.where(t < A, (t / A) * A_peak, env)
    # Decay
    mask = (t >= A) & (t < A + D)
    env = np.where(mask, A_peak - (A_peak - S) * (t - A) / D, env)
    # Sustain
    mask = (t >= A + D) & (t < dur - R)
    env = np.where(mask, S, env)
    # Release
    mask = t >= (dur - R)
    env = np.where(mask, S * (1 - (t - (dur - R)) / R), env)
    return env

def I_woodwind(t: np.ndarray, dur: float, I_max: float) -> np.ndarray:
    '''
    Índice de modulación decreciente exponencial para woodwind.
    '''
    tau = 0.05 * dur  # 5% de la duración
    I = I_max * np.exp(-t / tau)
    return I

def I_brass(t: np.ndarray, dur: float, I_max: float) -> np.ndarray:
    '''
    Índice de modulación lineal para brass.
    '''
    I = I_max * (t / dur)
    return I

def fm_synthesis(midi_data: pretty_midi.PrettyMIDI, track_id: int, sr: int = 44100):
    """
    Sintetiza la pista `track_id` de midi_data usando FM synthesis.
    Pregunta al usuario por timbre “brass” o “woodwind”, luego:
      • brass: índice de modulación I(t) crece lineal en el ataque
      • woodwind: I(t) decae exponencial
    Genera un buffer por nota y los mezcla, normaliza, y guarda en:
        output/track{track_id}_fm.wav
    """
    # 1) Selección de timbre
    while True:
        choice = input("Síntesis FM: Metal (brass) (B) o Viento-Madera"
                       " (woodwind) (W)? ").strip().lower()
        if choice in ('b','w'):
            break
    is_brass = (choice == 'b')
    print("→ Sintetizando como", "BRASS" if is_brass else "WOODWIND")

    # Parámetros fijos
    I_max = 3.0            # índice pico de modulación
    ratio = 3.0 if is_brass else 1.5   # fc/fm ratio típico
    # para woodwind vamos a decaer con tau = 50% de la nota
    # para brass el índice se rampa lineal en [0..I_max]

    # 2) Prepara el buffer de mezcla total
    inst      = midi_data.instruments[track_id]
    total_dur = midi_data.get_end_time()
    N_total   = int(total_dur * sr)
    mix_buf   = np.zeros(N_total, dtype=float)

    # 3) Recorre cada nota del track
    for note in inst.notes:
        start_s = note.start
        dur     = note.end - note.start
        if dur <= 0:
            continue
        N = int(dur * sr)
        t = np.linspace(0, dur, N, endpoint=False)

        # 3.1) frecuencia carrier & modulator
        fc = 440.0 * 2**((note.pitch - 69)/12)
        fm = fc / ratio

        # Envolventes vectorizadas
        I = I_brass(t, dur, I_max) if is_brass else I_woodwind(t, dur, I_max)
        A = A_adsr(t, dur, A_peak=1.0)

        # 3.3) cálculo de la señal FM
        modulator = np.sin(2 * np.pi * fm * t - np.pi/2)
        phase     = 2 * np.pi * fc * t + I * modulator - np.pi/2
        y_note    = A * np.sin(phase)

        # 3.4) agregar al buffer maestro
        i0 = int(start_s * sr)
        i1 = i0 + N
        if i1 > mix_buf.shape[0]:
            mix_buf = np.pad(mix_buf, (0, i1 - mix_buf.shape[0]))
        mix_buf[i0:i1] += y_note

    # 4) Normaliza mezcla final
    peak = np.max(np.abs(mix_buf))
    if peak > 0:
        mix_buf /= peak

    # 5) Escribe WAV en output/
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"track{track_id}_fm.wav")
    sf.write(out_path, mix_buf, sr)
    print(f"→ FM generado en output/: {out_path}")

    return mix_buf
