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
    A = 0.16 * dur    # 16% attack
    D = 0.16 * dur     # 16% decay
    S = 0.5           # sustain level
    R = 0.16 * dur     # 16% release

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

def A_woodwind(t: np.ndarray, dur: float, A_max: float = 1.0) -> np.ndarray:
        # Punto en el que termina la fase de subida (20% de la duración)
    ramp_end = 0.2 * dur
    # Constante de tiempo elegida para que I(t) alcance I_max a t = ramp_end
    tau = ramp_end / (np.log(A_max+1))

    # Vectorizado: para t <= ramp_end usamos subida exponencial, luego A_max
    I = np.where(
        t <= ramp_end,
        np.exp(t / tau) - 1,
        A_max
    )
    return I

def I_woodwind(t: np.ndarray, dur: float, I_max: float) -> np.ndarray:
    """
    Índice de modulación para woodwind:
    - Crece exponencialmente desde 0 hasta casi I_max durante el 20% inicial de la nota.
    - Luego se mantiene constante = I_max.
    
    Parámetros:
      t      : array de tiempos (segundos) desde el inicio de la nota, length N
      dur    : duración total de la nota (segundos)
      I_max  : índice máximo de modulación
    
    Devuelve:
      I : array de long N con el índice I(t) en cada instante
    """
    # Punto en el que termina la fase de subida (20% de la duración)
    ramp_end = 0.2 * dur
    # Constante de tiempo elegida para que I(t) alcance I_max a t = ramp_end
    tau = ramp_end / (np.log(I_max+1))

    # Vectorizado: para t <= ramp_end usamos subida exponencial, luego I_max
    I = np.where(
        t <= ramp_end,
        np.exp(t / tau) - 1,
        I_max
    )
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
    Devuelve el .wav en "mix_buf"
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
        A = A_adsr(t, dur, A_peak=1.0) if is_brass else A_woodwind(t, dur,
                                                                    A_max=1.0)

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
    out_path = os.path.join("output", f"Pista-{track_id}-fm.wav")
    sf.write(out_path, mix_buf, sr)
    print(f"→ FM generado en output/: {out_path}")

    return mix_buf
