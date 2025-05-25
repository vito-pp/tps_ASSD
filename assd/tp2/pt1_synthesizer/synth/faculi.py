import numpy as np
import scipy
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
import mido
import pretty_midi
import sounddevice as sd
import os


#Defino nombre de todas las notas
def note_name_to_midi(note_name):
    every_note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    #Extraigo nota y octava
    #Si tiene dos caracters (Ejemplo C4 --> name = "C", octave = 4)
    if len(note_name) == 2:
        name = note_name[0]
        octave = int(note_name[1])
    #Si tiene tres caracters (Ejemplo D#4 --> name = "D#", octave = 4)
    else:
        name = note_name[0:2]
        octave = int(note_name[2])

    #Calcula la nota en formato MIDI
    return every_note_name.index(name) + 12 * (octave + 1)

#Lista de archivos muestra
wav_files = ['G4.wav']

#Clave: número MIDI, Valor: nombre del archivo
sample_files = {}
for file in wav_files:
    note = file.replace('.wav', '')
    midi_num = note_name_to_midi(note)
    sample_files[midi_num] = file


def find_closest_sample(midi_note, sample_dict):
    #Convierte claves a array
    available_notes = np.array(list(sample_dict.keys())) 
    #Encuentro índice de la nota mas cercana(En caso de equidistancia se queda con la mas grave).
    closest_note = available_notes[np.argmin(np.abs(available_notes - midi_note))] 
    return closest_note

# Cargar el archivo MIDI
midi_data = pretty_midi.PrettyMIDI('../midis/dontcry.mid')

print("Listado de pistas del archivo MIDI:\n")
for i, instrument in enumerate(midi_data.instruments):
    nombre = instrument.name if instrument.name else "Sin nombre"
    print(f"Pista {i}: Instrumento: {nombre}")


# Elegir la pista
total_pistas = len(midi_data.instruments) # Cantidad total de pistas
# Loop para pedir y validar el número
while True:
    try:
        track_idx_to_synthesize = int(input(f"Ingrese el número de pista que desea sintetizar: "))
        if 0 <= track_idx_to_synthesize <= total_pistas - 1:
            break  # sale del loop si está dentro del rango
        else:
            print(f"Error: el número debe estar entre 0 y {total_pistas - 1}.")
    except ValueError:
        print("Error: debe ingresar un número entero válido.")

instrument = midi_data.instruments[track_idx_to_synthesize]

#Elegir el instrumento
while True:
    id_instrumento = input(
        "\nSeleccione el instrumento que desea sintetizar:\n"
        "P - Piano\n"
        "G - Guitarra\n"
        "S - Strings\n"
        "Ingrese P, G o S: "
    ).strip().upper()

    if id_instrumento in ['P', 'G', 'S']:
        break
    else:
        print("Error: debe ingresar P, G o S.")

if id_instrumento== 'G':
    instrumento = "guitarra"
elif id_instrumento == 'P':
    instrumento = "piano"
else:
    instrumento = "strings"

print(f"Usted eligió sintetizar la pista {track_idx_to_synthesize} como {instrumento}.")


# Configuración de audio
sample_rate = 44100  # Frecuencia de muestreo: 44,100 muestras por segundo para el audio de salida
total_duration = midi_data.get_end_time()  # Duración total del MIDI en segundos
output_audio = np.zeros(int(total_duration * sample_rate))  # Buffer de audio (arreglo de ceros)

# Cargar la muestra
def load_sample(filename):
    # filename: Nombre del archivo WAV (por ejemplo, 'C4.wav')
    # Construir la ruta completa al archivo dentro del subdirectorio del instrumento correspondiente.
    filepath = os.path.join(instrumento, filename)
    sample, sr = sf.read(filepath)  # Lee el WAV, devuelve el arreglo de audio y su frecuencia de muestreo
    if sr != sample_rate:  # Si la frecuencia del WAV no es 44.1 kHz, la ajustamos
        sample = librosa.resample(sample, orig_sr=sr, target_sr=sample_rate)
    return sample

# Procesar las notas
for note in instrument.notes:
    #Busco la nota mas cercana
    ref_pitch = find_closest_sample(note.pitch, sample_files)
    #Busco el sample de la nota correspondiente.
    sample = load_sample(sample_files[ref_pitch]) 

    pitch_shift_semitones = note.pitch - ref_pitch  # Calcula el cambio de tono (en semitonos)
    shifted_sample = librosa.effects.pitch_shift(sample, sr=sample_rate, n_steps=pitch_shift_semitones)  #Pitchea el sample original
    note_duration = note.end - note.start  # Duración de la nota en segundos
    sample_duration = len(sample) / sample_rate  # Duración de la muestra en segundos
    rate = sample_duration / note_duration if note_duration > 0 else 1  # Factor de estiramiento
    stretched_sample = librosa.effects.time_stretch(shifted_sample, rate=rate)  # Ajusta la duración
    start_sample = int(note.start * sample_rate)  # Convierte el tiempo de inicio a índice de muestra
    end_sample = start_sample + len(stretched_sample)  # Índice de fin
    if end_sample > len(output_audio):  # Amplía el buffer si es necesario
        output_audio = np.pad(output_audio, (0, end_sample - len(output_audio)))
    output_audio[start_sample:end_sample] += stretched_sample * (note.velocity / 127.0)  # Mezcla la nota

# Normalizar y guardar
if np.max(np.abs(output_audio)) > 0:
    output_audio = output_audio / np.max(np.abs(output_audio))  # Normaliza para evitar distorsión
sf.write('pista_gf.wav', output_audio, sample_rate)  # Guarda el WAV
print("Archivo WAV generado: pista_gf.wav")