import numpy as np
import scipy
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
import mido
import pretty_midi
import sounddevice as sd
import os

'''
/**
* @brief Converts a note name written in format Name + octave, to MIDI id. (Example: C4 --> 60)
* @param in String that contains de note name
* @return MIDI id of note
*/
'''

def note_name_to_midi(note_name):
    every_note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    #Extract note and octave
    #If it has two characters (Example: C4 --> name = "C", octave = 4)
    if len(note_name) == 2:
        name = note_name[0]
        octave = int(note_name[1])
    #If it has three characters (Example: D#4 --> name = "D#", octave = 4)
    else:
        name = note_name[0:2]
        octave = int(note_name[2])

    #Calculate the note in MIDI format
    return every_note_name.index(name) + 12 * (octave + 1)

#
#  @brief Finds closets sample to the note that is trying to reproduce
 ## 
# @param in midi_note: note id from MIDI.
#           sample_dict: MAP whose key is the note's name in american notation withc value of MIDI id.
#  @return closest note in MIDI notation 
def find_closest_sample(midi_note, sample_dict):
    #Convert keys to array
    available_notes = np.array(list(sample_dict.keys())) 
    #Find the index of the closest note (If equidistant, it chooses the lower one)
    closest_note = available_notes[np.argmin(np.abs(available_notes - midi_note))] 
    return closest_note

#
#  @brief Loads sample that's used to represent de note
 ## 
# @param in filename: string that contains the sound of the closest note.
#           instrumento: string that contains the instrument whose sample the program is using.
#  @return sample of the closest note in the corresponding instrument.
def load_sample(filename, instrumento):
    # filename: Name of the WAV file (e.g., 'C4.wav')
    # Build the full path to the file inside the corresponding instrument subdirectory
    sample_rate = 44100
    # __file__ es la ruta a este módulo: synth/sample.py
    base_dir = os.path.join(os.path.dirname(__file__), instrumento)
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error. No se encontró el sample: {filepath}")
    sample, sr = sf.read(filepath)
    if sr != sample_rate:
        sample = librosa.resample(sample, orig_sr=sr, target_sr=sample_rate)
    return sample

#
#  @brief Synthesizes a midi track with a desired instrument sound.
#          It asks for several user inputs so as to decide which
#            track has to be synthesized and with which instrument.
## 
# @param in midi_data: map containing the midi information
#   @output: .wav file of the track with the sound of the desired instrument.
#  @return the .wav file with the synthesized track
def sample_synthesis(midi_data, track_idx_to_synthesize):
    #File list
    wav_files = ['F2.wav','A#2.wav', 'D#3.wav','G#3.wav', 'C#4.wav', 'F#4.wav', 'B4.wav', 'E5.wav']

    #Key: MIDI id, Value: file name.
    sample_files = {}
    for file in wav_files:
        note = file.replace('.wav', '')
        midi_num = note_name_to_midi(note)
        sample_files[midi_num] = file


    instrument = midi_data.instruments[track_idx_to_synthesize]

    #Choose instrument
    while True:
        id_instrumento = input(
            "\nSeleccione el instrumento que desea sintetizar:\n"
            "G - Guitarra\n"
            "E - Guitarra eléctrica\n"
            "S - Strings\n"
            "Ingrese G, E o S: "
        ).strip().upper()

        if id_instrumento in ['G', 'S', 'E']:
            break
        else:
            print("Error: debe ingresar G; E o S.")

    if id_instrumento == 'G':
        instrumento = "guitarra"
    elif id_instrumento == 'E':
        instrumento = "guitarra-electrica"
    else:
        instrumento = "strings"

    print(f"Usted eligió sintetizar la pista {track_idx_to_synthesize} como {instrumento}.")

    # Audio configuration
    sample_rate = 44100  # Sampling rate: 44,100 samples per second for the output audio
    total_duration = midi_data.get_end_time()  # Total duration of the MIDI in seconds
    output_audio = np.zeros(int(total_duration * sample_rate))  # Audio buffer (array of zeros)

    # Process the notes
    for note in instrument.notes:
        #Find the closest note
        ref_pitch = find_closest_sample(note.pitch, sample_files)
        #Load the sample for the corresponding note
        sample = load_sample(sample_files[ref_pitch], instrumento)

        pitch_shift_semitones = note.pitch - ref_pitch  # Calculate pitch shift in semitones
        shifted_sample = librosa.effects.pitch_shift(sample, sr=sample_rate, n_steps=pitch_shift_semitones)  # Apply pitch shift to the original sample
        note_duration = note.end - note.start  # Note duration in seconds
        sample_duration = len(sample) / sample_rate  # Sample duration in seconds
        rate = sample_duration / note_duration if note_duration > 0 else 1  # Stretching factor
        stretched_sample = librosa.effects.time_stretch(shifted_sample, rate=rate)  # Adjust duration
        start_sample = int(note.start * sample_rate)  # Convert start time to sample index
        end_sample = start_sample + len(stretched_sample)  # End index
        if end_sample > len(output_audio):  # Expand buffer if necessary
            output_audio = np.pad(output_audio, (0, end_sample - len(output_audio)))
        output_audio[start_sample:end_sample] += stretched_sample * (note.velocity / 127.0)  # Mix the note

    # Normalize and save
    if np.max(np.abs(output_audio)) > 0:
        output_audio = output_audio / np.max(np.abs(output_audio))  # Normaliza para evitar distorsión
    
    # ensure the output folder exists
    os.makedirs("output", exist_ok=True)

    # build path inside output/
    nombre_archivo = os.path.join(
        "output",
        f'Pista-{track_idx_to_synthesize}({instrumento}).wav'
    )

    # Saves file into output/
    sf.write(nombre_archivo, output_audio, sample_rate)

    print(f"Archivo WAV generado en output/: 'Pista-{track_idx_to_synthesize}({instrumento}).wav'")
    return output_audio
