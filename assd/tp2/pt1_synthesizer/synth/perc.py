# synth/perc.py

import numpy as np
from synth import register
from core.models import Track
from synth.punto4 import karplus_strong_percussion

def perc_synth(
    track: Track,
    sample_rate: int,
    b: float = 0.5,
    R: float = 0.99,
    uniform: bool = True
) -> np.ndarray:
    """
    Synthesize one Track via Percussive KS.
    """
    total = max((e.start_time + e.duration) for e in track.events)
    buf   = np.zeros(int(total * sample_rate))

    for e in track.events:
        freq = 440.0 * 2 ** ((e.pitch - 69) / 12)
        y    = karplus_strong_percussion(
                   freq=freq,
                   duration=e.duration,
                   b=b,
                   fs=sample_rate,
                   R=R,
                   uniform=uniform
               )
        start = int(e.start_time * sample_rate)
        end   = start + len(y)
        if end > buf.shape[0]:
            buf = np.pad(buf, (0, end - buf.shape[0]))
        buf[start:end] += y

    mx = np.max(np.abs(buf)) or 1.0
    return buf / mx

# register under the key "perc"
register("perc", perc_synth)
