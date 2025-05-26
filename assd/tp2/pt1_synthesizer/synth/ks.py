import numpy as np
from synth import register
from core.models import Track
from synth.punto4 import karplus_strong

def ks_synth(
    track: Track,
    sample_rate: int,
    R: float = 0.99,
    uniform: bool = True
) -> np.ndarray:
    """
    Synthesize one Track via Karplus-Strong.
    """
    # find total track length in seconds
    total = max((e.start_time + e.duration) for e in track.events)
    buf   = np.zeros(int(total * sample_rate))

    for e in track.events:
        freq = 440.0 * 2 ** ((e.pitch - 69) / 12)
        y    = karplus_strong(
                   freq=freq,
                   duration=e.duration,
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

# register under the key "ks"
register("ks", ks_synth)
