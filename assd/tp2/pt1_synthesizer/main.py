#!/usr/bin/env python3
import os
import argparse
import soundfile as sf
import numpy as np

from core.midi_loader import MidiLoader
from core.mixer      import mix_buffers
from synth           import get_synth

# Force registration of synth modules
import synth.ks
import synth.perc
import synth.sample

from synth.sample import note_name_to_midi

def build_sample_files_dict(instrument_dir: str) -> dict[int, str]:
    """
    Scan instrument_dir for .wav files named like 'C4.wav','D#3.wav',…
    and return a dict mapping MIDI note number → filename.
    """
    sample_files: dict[int, str] = {}
    for fname in os.listdir(instrument_dir):
        if not fname.lower().endswith(".wav"):
            continue
        note = fname[:-4]  # drop ".wav"
        midi = note_name_to_midi(note)
        sample_files[midi] = fname
    return sample_files

def parse_args():
    p = argparse.ArgumentParser("MIDI → multi-synth pipeline")
    p.add_argument("--midi",     required=True,
                   help="Path to your .mid file")
    p.add_argument("--outdir",   default="output",
                   help="Directory to write per-track and final WAVs")
    p.add_argument("--sr",       type=int, default=44100,
                   help="Sample rate in Hz")
    p.add_argument("--track",      required=True,
                   help="Comma-separated list of trackID:synthName, e.g. 0:ks,1:perc,2:sample")
    p.add_argument("--instr-dir",
                   help="For sample synth: path to folder of sample WAVs")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    # 1) Load MIDI file into Track objects
    tracks = MidiLoader.load(args.midi, sample_rate=args.sr)
    if not tracks:
        print("❌ No tracks found in MIDI.")
        return

    bufs = []
    # 2) Iterate over each mapping entry and synthesize
    for part in args.map.split(","):
        tid_str, synth_name = part.split(":")
        tid = int(tid_str)

        # Find the Track with matching ID
        track = next((t for t in tracks if t.id == tid), None)
        if track is None:
            print(f"⚠️  Track {tid} not in MIDI; skipping.")
            continue

        synth_fn = get_synth(synth_name)
        synth_kwargs = {}

        if synth_name == "sample":
            if not args.instr_dir:
                print("❌ --instr-dir is required for sample synth.")
                return
            sample_files = build_sample_files_dict(args.instr_dir)
            synth_kwargs = {
                "instrument_dir": args.instr_dir,
                "sample_files": sample_files
            }

        # Call the synth function: returns a NumPy array
        buf = synth_fn(track, sample_rate=args.sr, **synth_kwargs)
        bufs.append(buf)

        # Write per-track WAV
        out1 = os.path.join(args.outdir, f"track{tid}_{synth_name}.wav")
        sf.write(out1, buf, args.sr)
        print(f"→ Written {out1}")

    if not bufs:
        print("⚠️ No buffers synthesized; exiting.")
        return

    # 3) Mix buffers into a master track (or use single buffer)
    if len(bufs) > 1:
        master = mix_buffers(bufs)
    else:
        master = bufs[0]

    # 4) Write master WAV if non-empty
    if master.size > 0:
        out_mix = os.path.join(args.outdir, "final_mix.wav")
        sf.write(out_mix, master, args.sr)
        print(f"→ Written mixed output: {out_mix}")
    else:
        print("⚠️ Master buffer is empty; skipping final mix.")

if __name__ == "__main__":
    main()
