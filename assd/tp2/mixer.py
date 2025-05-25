"""
/**
 * @file mix_wav_files.py
 * @brief Mixes multiple .wav files into a single output .wav file.
 *
 * This script prompts the user to enter the number of .wav files to mix,
 * then asks for each file path. It loads all the files, mixes their audio
 * content by summing them, and exports the result as a new .wav file.
 *
 * All files must have the same sample rate, number of channels, and duration.
 * If they differ, the shortest duration will be used as cutoff.
 *
 * @input Paths to multiple .wav files.
 * @output A single mixed .wav file: "mix_output.wav".
 *
 * @author [Your Name]
 * @date 2025
 */
"""

from pydub import AudioSegment
import os

def load_wav(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")
    return AudioSegment.from_wav(path)

def main():
    try:
        n = int(input("🔢 How many .wav files do you want to mix? "))
        if n < 2:
            print("⚠️ You must enter at least 2 files to mix.")
            return

        print("📂 Enter the full path of each .wav file:")
        audio_segments = []
        for i in range(n):
            path = input(f"  File {i+1}: ").strip()
            audio_segments.append(load_wav(path))

        # Trim all to the shortest duration to align lengths
        min_len = min(len(seg) for seg in audio_segments)
        trimmed_segments = [seg[:min_len] for seg in audio_segments]

        print("🔊 Mixing audio tracks...")
        mix = trimmed_segments[0]
        for seg in trimmed_segments[1:]:
            mix = mix.overlay(seg)

        mix.export("mix_output.wav", format="wav")
        print("✅ Mixed file saved as: mix_output.wav")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
