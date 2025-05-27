import os
import numpy as np
import soundfile as sf
import pretty_midi

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
    I_max = 5.0            # índice pico de modulación
    ratio = 2.0 if is_brass else 1.5   # fc/fm ratio típico
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

        # 3.2) envolvente de índice I(t)
        if is_brass:
            I = I_max * (t / dur)           # lineal desde 0 hasta I_max
        else:
            tau = dur * 0.5
            I   = I_max * np.exp(-t / tau)  # decaimiento exponencial

        # 3.3) cálculo de la señal FM
        modulator = np.sin(2 * np.pi * fm * t)
        phase     = 2 * np.pi * fc * t + I * modulator
        y_note    = np.sin(phase)

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
