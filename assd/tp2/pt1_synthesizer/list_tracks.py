#!/usr/bin/env python3
import argparse
from core.midi_loader import MidiLoader  # uses load(path, sample_rate) :contentReference[oaicite:0]{index=0}

def parse_args():
    p = argparse.ArgumentParser(
        description="List all tracks in a MIDI file with their IDs, names and" \
        "note counts"
    )
    p.add_argument(
        "midi_file",
        help="Path to the MIDI file (.mid) you want to inspect"
    )
    p.add_argument(
        "--sr", "-r",
        type=int,
        default=44100,
        help="Sample rate (Hz) for time → sample conversion (default: 44100)"
    )
    return p.parse_args()

def main():
    args = parse_args()
    tracks = MidiLoader.load(args.midi_file, sample_rate=args.sr)
    if not tracks:
        print("❌ No tracks found in that MIDI.")
        return

    print(f"\n🔍 Tracks in {args.midi_file}:")
    for t in tracks:
        name = t.name or "<unnamed>"
        print(f"  • ID={t.id:2}   name={name:12}   notes={len(t.events):3}")

if __name__ == "__main__":
    main()
