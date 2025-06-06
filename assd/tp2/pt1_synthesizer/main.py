import numpy as np
import scipy
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
import mido
import pretty_midi
import sounddevice as sd
import os

from synth.sample import sample_synthesis
from synth.ks import ks_synthesis
from synth.fm import fm_synthesis
from core.mixer import mix_buffers
from core.espectograma import plot_spectrogram
from core.effects import apply_effects

def list_midi_files(midi_dir='midis'):
    """
    Lista en consola todos los archivos .mid en la carpeta especificada.
    """
    if not os.path.isdir(midi_dir):
        print(f"Directorio '{midi_dir}' no existe.")
        return []
    files = sorted(f for f in os.listdir(midi_dir) if f.lower().endswith('.mid'))
    if not files:
        print(f"No se encontraron archivos .mid en '{midi_dir}'.")
    else:
        print(f"Archivos MIDI disponibles en '/{midi_dir}':")
        for f in files:
            print(f"  - {f}")
    return 

def type_of_synthesis():
    #Choose type of synthesis
    while True:
        id_modelado = input(
            "\nSeleccione el tipo de síntesis que desea realizar:\n"
            "M - Por muestreo\n"
            "K - Por método de modelado físico (Karplus strong)\n"
            "F - Frecuencia modulada\n"
            "Ingrese M, K o F: "
        ).strip().upper()

        if id_modelado in ['M', 'K', 'F']:
            break
        else:
            print("Error: debe ingresar M, K o F.")
    return id_modelado

def select_track(midi_data):
    print("Listado de pistas del archivo MIDI:\n")
    for i, instrument in enumerate(midi_data.instruments):
        nombre = instrument.name or "Sin nombre"
        nota_count = len(instrument.notes)
        print(f"Pista {i}: Instrumento: {nombre} | Notas: {nota_count}")
    print("\n")

    total_pistas = len(midi_data.instruments)
    while True:
        try:
            track_idx_to_synthesize = int(input(
                f"Ingrese el número de pista que desea sintetizar [0–{total_pistas-1}]: "
            ))
            if 0 <= track_idx_to_synthesize < total_pistas:
                break
            else:
                print(f"Error: el número debe estar entre 0 y {total_pistas-1}.")
        except ValueError:
            print("Error: debe ingresar un número entero válido.")
    return track_idx_to_synthesize

def main():
    list_midi_files('midis')
    midi_file = input("Ingrese el nombre del archivo MIDI que desea sintetizar (incluyendo la extensión .mid).\n")
    midi_data = pretty_midi.PrettyMIDI("midis/" + midi_file)

    buffers = [] # to store each synthesized track

    flag_pista = 1
    while flag_pista:
        track_idx_to_synthesize = select_track(midi_data) #Selects track thats gonna be synthesized

        id_modelado = type_of_synthesis() #Selects type of instrument modeling

        if id_modelado== 'M': 
            print(f"Usted eligió sintetizar la pista mediante muestreo.")
            # Uploads MIDI file
            output_audio = sample_synthesis(midi_data, track_idx_to_synthesize)
            buffers.append(output_audio)

        elif id_modelado == 'K':
            print(f"Usted eligió sintetizar la pista mediante modelado físico (Karplus Strong).")
            output_audio = ks_synthesis(midi_data, track_idx_to_synthesize)
            buffers.append(output_audio)
            
        else:
            print(f"Usted eligió sintetizar la pista mediante frecuencia modulada.")
            output_audio = fm_synthesis(midi_data, track_idx_to_synthesize)
            buffers.append(output_audio)

        #Now you have a synthesized track

        #Do you wanna synthesize another track?
        while True:
            yes_or_no = input(
            "\n¿Desea sintetizar otra pista? [S/N]\n"
        ).strip().upper()
            if yes_or_no in ['S', 'N']:
                break
            else:
                print("Error: debe ingresar S o N")
        
        if yes_or_no == 'N':
            flag_pista = 0
    
    #Now you have N synthesized tracks

    if not buffers:
        print("No hay pistas sintetizadas; terminando...")
        return
    
    # Mix the tracks into a master
    master = mix_buffers(buffers)

    os.makedirs("output", exist_ok=True)
    final_name = "master_mix.wav"
    final_path = os.path.join("output", final_name)
    sf.write(final_path, master, 44100)
    print(f"→ Master guardado en: {final_path}")

    # Sound FX
    path_with_FX = apply_effects(final_path)

    # Spectrogram
    plot_spectrogram(path_with_FX)

    return

if __name__ == "__main__":
    main()