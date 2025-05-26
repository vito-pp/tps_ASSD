#!/usr/bin/env python3
import os
import numpy as np
import soundfile as sf

from core.midi_loader import MidiLoader
from synth.punto4 import karplus_strong  # make sure you applied the guard above

def midi_to_ks(track, sr=44100):
    total_time = max((e.start_time + e.duration) for e in track.events)
    buf = np.zeros(int(total_time * sr))

    for e in track.events:
        # MIDI→Hz
        freq = 440.0 * 2**((e.pitch - 69)/12)
        # skip notes shorter than a period
        if e.duration < 1/freq:
            continue

        y = karplus_strong(freq=freq, duration=e.duration, fs=sr)
        start = int(e.start_time * sr)
        end   = start + len(y)
        if end > buf.shape[0]:
            buf = np.pad(buf, (0, end - buf.shape[0]))
        buf[start:end] += y

    # normalize full track
    mx = np.max(np.abs(buf))
    return buf/mx if mx>0 else buf

def main():
    sr = 44100
    midi_path = os.path.join("midis","dontcry.mid")

    tracks = MidiLoader.load(midi_path, sample_rate=sr)
    playable = [t for t in tracks if t.events]
    if not playable:
        print("No playable tracks."); return

    # synth each track
    mix = np.zeros(1)
    for t in playable:
        print(f"▶ Synthesizing track {t.id} with {len(t.events)} notes")
        tr_buf = midi_to_ks(t, sr=sr)
        if tr_buf.shape[0] > mix.shape[0]:
            mix = np.pad(mix, (0, tr_buf.shape[0]-mix.shape[0]))
        mix[:tr_buf.shape[0]] += tr_buf

    # normalize and write
    mx = np.max(np.abs(mix))
    mix = mix/mx if mx>0 else mix
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output","dontcry_full_ks.wav")
    sf.write(out_path, mix, sr)
    print(f"✅ Written {out_path}")

if __name__=="__main__":
    main()
