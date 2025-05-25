#!/usr/bin/env python3
import argparse
import os
import soundfile as sf

from synth.punto4 import (
    karplus_strong,
    karplus_strong_percussion,
    generate_arpa_arpeggio,
)

def parse_args():
    p = argparse.ArgumentParser(description="KS Synth CLI")
    p.add_argument(
        "--mode", "-m",
        choices=["ks", "ks_perc", "arpa"],
        required=True,
        help="Which Karplus-Strong variant to run"
    )
    p.add_argument(
        "--freq", "-f",
        type=float,
        default=440.0,
        help="Base frequency in Hz (for ks & ks_perc)"
    )
    p.add_argument(
        "--dur", "-d",
        type=float,
        default=2.0,
        help="Duration in seconds"
    )
    p.add_argument(
        "--sr", "-r",
        type=int,
        default=44100,
        help="Sample rate (Hz)"
    )
    return p.parse_args()

def main():
    args = parse_args()

    # Make sure output directory exists
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)

    # Choose synth & filename
    if args.mode == "ks":
        y = karplus_strong(freq=args.freq, duration=args.dur, fs=args.sr)
        fname = "ks_string.wav"
    elif args.mode == "ks_perc":
        y = karplus_strong_percussion(freq=args.freq, duration=args.dur, fs=args.sr)
        fname = "ks_percussion.wav"
    else:  # arpa
        # simple 4-note arpeggio spanning total duration
        freqs = [261.6, 329.6, 392.0, 523.3]
        note_dur = args.dur / len(freqs)
        y = generate_arpa_arpeggio(freqs, note_duration=note_dur, fs=args.sr)
        fname = "ks_arpeggio.wav"

    out_path = os.path.join(out_dir, fname)
    sf.write(out_path, y, args.sr)
    print(f"✅ Written {out_path}")

if __name__ == "__main__":
    main()


# ejemplos de como correr el codigo en la terminal:
# python main.py --mode ks        --freq 330 --dur 3
# python main.py --mode ks_perc   --freq 200 --dur 1
# python main.py --mode arpa      --dur 4