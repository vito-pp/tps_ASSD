# PT1 Sintetizador MIDI

Este repositorio contiene un scipt para sintetizar archivos MIDI (.mid) por CLI; donde cada pista puede ser sintetizada usando síntesis por frecuencia modulada (FM), por el algoritmo de Karplus–Strong (síntesis mediante modelos físicos) y síntesis mediante muestras para luego mezclar todas las pistas en un único archivo de audio (.wav).

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

    Luego ya se puede ejecutar :D
    
    ```
    python main.py
    ```
Todas las salidas del programa se guardan en la carpeta output/ y los midis a usar se encuentran en midis/ (agregar los midis que desee).