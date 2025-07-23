import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from IPython.display import Audio, display

#Generación de audios
fs = 16000
duration = 5
t = np.linspace(0, duration, int(fs*duration), endpoint=False)

clean = 1 * np.sin(2 * np.pi * 220 * t)
noise = 0.3 * np.random.normal(0, 1, clean.shape)

noisy = clean + noise

reference = noise

sf.write("input.wav", noisy, fs)
sf.write("noise.wav", noise, fs)
sf.write("desired.wav", clean, fs) 

"""""
#Activar el siguiente código para usar una nota de guitarra como señal deseada.


import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from IPython.display import Audio, display

# Leer archivo G.wav como señal limpia
clean, fs = sf.read("G.wav")

# Si es estéreo, convertir a mono
if clean.ndim > 1:
    clean = clean.mean(axis=1)

# Generar ruido blanco con misma forma
noise = 0.1 * np.random.normal(0, 1, clean.shape)

# Señal ruidosa
noisy = clean + noise

# Guardar archivos de salida
sf.write("desired.wav", clean, fs)  # Señal limpia
sf.write("noise.wav", noise, fs)    # Solo ruido
sf.write("input.wav", noisy, fs)    # Señal ruidosa (entrada al sistema)

# (Opcional) Mostrar un fragmento
print("Archivos generados:")
display(Audio("input.wav"))
 """