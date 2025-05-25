# core/models.py
from dataclasses import dataclass
from typing import List

@dataclass
class NoteEvent:
    """
    Represents a single MIDI note event.
    Attributes:
      pitch: MIDI note number (0-127)
      velocity: attack velocity (0-127)
      start_time: time in seconds when note-on occurs
      duration: time in seconds until note-off
      channel: MIDI channel (0-15)
      track_id: origin track index
    """
    pitch: int
    velocity: int
    start_time: float
    duration: float
    channel: int
    track_id: int

@dataclass
class Track:
    """
    A sequence of NoteEvent objects belonging to one MIDI track.
    Attributes:
      id: the track index in the MIDI file
      name: optional track name or instrument name
      events: ordered list of NoteEvent
    """
    id: int
    name: str
    events: List[NoteEvent]