import numpy as np

def mix_buffers(buffers: list[np.ndarray]) -> np.ndarray:
    L = max(b.shape[0] for b in buffers)
    mix = np.zeros(L)
    for b in buffers:
        mix[:b.shape[0]] += b
    mx = np.max(np.abs(mix)) or 1
    return mix / mx