from dataclasses import dataclass

@dataclass
class NoteEvent:
    pitch: int         # MIDI note number
    velocity: int      # 0–127
    start_time: float  # seconds
    duration: float    # seconds
    channel: int
    track_id: int

@dataclass
class Track:
    id: int
    name: str
    events: list[NoteEvent]
