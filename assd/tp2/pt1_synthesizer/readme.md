# PT1 Sintetizador MIDI

Este repositorio contiene dos scripts principales para sintetizar archivos MIDI (.mid) donde cada pista puede ser sintetizada usando síntesis por frecuencia modulada (FM), por el algoritmo de Karplus–Strong (síntesis mediante modelos físicos) y síntesis mediante muestras para luego mezclar todas las pistas en un único archivo de audio (.wav).

---

## 1.venv y dependencias

### Linux / macOS

1. Crear y activar un entorno virtual:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Instalar dependencias:

    ```bash
    pip install -r requirements.txt
    ```

### Windows (PowerShell)

1. Crear y activar un entorno virtual:

    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

   o en CMD:

    ```cmd
    python -m venv venv
    venv\Scripts\activate.bat
    ```

2. Instalar dependencias:

    ```powershell
    pip install -r requirements.txt
    ```

---

## 2. ejecución del programa

1. Antes de sintetizar conviene saber qué tracks contienen notas. 
Por eso primero hay que ejecutar:

    ```
    python list_tracks.py midis/<name-of-midi>.mid 
    ```

Salida de ejemplo:

    ID= 0  name=untitled  notes=0
    ID= 1  name=Guitar Solo  notes=434
    ID= 2  name=Guitar Solo  notes=434
    ID= 3  name=Guitar Solo  notes=434
    ID= 4  name=Bass  notes=91
    ID= 5  name=Piano  notes=272
    ID= 6  name=Strings 2  notes=0
    ID= 7  name=Strings 1  notes=0
    ID= 8  name=Drums  notes=290
    ID= 9  name=Celli  notes=0
    ID=10  name=Gutar Acomp  notes=228
    ID=11  name=Contrabass  notes=0

2. Luego mediante CLI ejecutar el main.py con los siguientes posibles argumentos:

    ```
    python main.py \
            --midi midis/<name-of-midi>.mid \
            --track 1:<synth_type>,2:<synth_type>,3:<synth_type> \
            --instr-dir synth/guitarra \
            --outdir output
    ```

,donde en --track se indica el tipo de sintetizador que se va a utilizar para cada pista. Agregar tantos argumentos como pistas se quiera sintetizar (en el ejemplos sólo hay tres).

La salida entonces será:

    → Written output/track1_<synth_type>.wav
    → Written output/track2_<synth_type>.wav
    → Written output/track3_<synth_type>.wav
    → Written mixed output: output/final_mix.wav

Ejemplo de uso:

    ```
    python main.py \
            --midi midis/concierto-de-aranjuez.mid \
            --map 1:ks,3:ks \
            --instr-dir synth/guitarra \
            --outdir output
    ```