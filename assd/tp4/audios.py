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