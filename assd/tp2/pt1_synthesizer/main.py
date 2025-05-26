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
            print("Error: debe ingresar M, K O F.")
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
    midi_file = input("Ingrese el nombre del archivo MIDI que desea sintetizar, incluyendo la extensión .mid.\n")
    midi_data = pretty_midi.PrettyMIDI("midis/" + midi_file)

    flag_pista = 1
    while flag_pista:
        track_idx_to_synthesize = select_track(midi_data) #Selects track thats gonna be synthesized
        id_modelado = type_of_synthesis() #Selects type of instrument modeling

        if id_modelado== 'M': 
            print(f"Usted eligió sintetizar la pista mediante muestreo.")
            # Uploads MIDI file
            sample_synthesis(midi_data, track_idx_to_synthesize)

        elif id_modelado == 'K':
            print(f"Usted eligió sintetizar la pista mediante Modelado físico (Karplus Strong).")
            #Call Karplus strong
        else:
            print(f"Usted eligió sintetizar la pista mediante Frecuencia modulada.")
            #Call FM
        
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
    
    #Here me out GONZA, this is your cue to stop being gay and mix the WAV files

    return

if __name__ == "__main__":
    main()