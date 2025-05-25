#!/usr/bin/env python3
import os
import numpy as np
import soundfile as sf

from core.midi_loader import MidiLoader
from synth.punto4 import karplus_strong  # KS string synth :contentReference[oaicite:1]{index=1}

def midi_to_ks(track, sr=44100):
    """
    Synthesize one Track of NoteEvent with Karplus-Strong.
    Returns a NumPy 1-D array of length = track duration * sr.
    """
    # total track length in seconds
    total_time = max((e.start_time + e.duration) for e in track.events)
    buf = np.zeros(int(total_time * sr))

    for e in track.events:
        # convert MIDI note → frequency in Hz
        freq = 440.0 * 2 ** ((e.pitch - 69) / 12)
        y = karplus_strong(freq=freq, duration=e.duration, fs=sr)
        start = int(e.start_time * sr)
        end   = start + len(y)
        # extend buffer if this note overruns
        if end > buf.shape[0]:
            buf = np.pad(buf, (0, end - buf.shape[0]))
        buf[start:end] += y

    # normalize track buffer
    mx = np.max(np.abs(buf))
    return buf / mx if mx > 0 else buf

def main():
    sr = 44100
    midi_path = os.path.join('midis', 'dontcry.mid')

    # 1) Load all tracks
    tracks = MidiLoader.load(midi_path, sample_rate=sr)
    if not tracks:
        print("❌ No tracks found in MIDI."); return

    # 2) Keep only tracks with note events
    playable = [t for t in tracks if t.events]
    if not playable:
        print("❌ No note events in any track."); return

    # 3) Synthesize each track
    buffers = []
    for t in playable:
        print(f"▶ Synthesizing track {t.id} (‘{t.name}’) with {len(t.events)} notes")
        buffers.append(midi_to_ks(t, sr=sr))

    # 4) Mix: pad to the longest buffer, then sum
    maxlen = max(b.shape[0] for b in buffers)
    mix   = np.zeros(maxlen)
    for b in buffers:
        mix[:b.shape[0]] += b

    # 5) Normalize full mix
    mx = np.max(np.abs(mix))
    if mx > 0:
        mix /= mx

    # 6) Write to output/
    os.makedirs('output', exist_ok=True)
    out_path = os.path.join('output', 'dontcry_full_ks.wav')
    sf.write(out_path, mix, sr)
    print(f"✅ Written full-mix KS to {out_path}")

if __name__ == "__main__":
    main()
