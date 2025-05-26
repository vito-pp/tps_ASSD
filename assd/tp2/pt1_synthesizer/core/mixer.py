import numpy as np
from typing import List

def mix_buffers(buffers: list[np.ndarray]) -> np.ndarray:
    if not buffers:
            return np.array([], dtype=float)

    # 1) Longitud máxima
    max_len = max(buf.shape[0] for buf in buffers)

    # 2) Rellenar y sumar
    mix = np.zeros(max_len, dtype=float)
    for buf in buffers:
        mix[: buf.shape[0]] += buf

    # 3) Normalizar (si no es todo ceros)
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak

    return mix