# core/midi_loader.py
import mido
from typing import List
from core.models import NoteEvent, Track

class MidiLoader:
    @staticmethod
    def load(path: str, sample_rate: int = 44100) -> List[Track]:
        """
        Load a MIDI file and convert it into a list of Track objects,
        each containing its NoteEvent list with real-time values.

        Args:
            path: path to the .mid file
            sample_rate: used to convert MIDI ticks to seconds via tempo
        Returns:
            List of Track, one per MIDI track
        """
        mid = mido.MidiFile(path)
        # build tempo map (time in ticks -> seconds)
        tempo = 500000  # default microseconds per beat
        ticks_per_beat = mid.ticks_per_beat
        # accumulate per-track events
        tracks: List[Track] = []
        for i, mtrack in enumerate(mid.tracks):
            abs_time = 0  # in ticks
            note_on_dict = {}  # key=(channel,pitch) -> (start_time_seconds)
            events: List[NoteEvent] = []
            for msg in mtrack:
                abs_time += msg.time
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                elif msg.type == 'note_on' and msg.velocity > 0:
                    # note on
                    seconds = mido.tick2second(abs_time, ticks_per_beat, tempo)
                    note_on_dict[(msg.channel, msg.note)] = seconds
                elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                    key = (msg.channel, msg.note)
                    if key in note_on_dict:
                        start = note_on_dict.pop(key)
                        end = mido.tick2second(abs_time, ticks_per_beat, tempo)
                        events.append(
                            NoteEvent(
                                pitch=msg.note,
                                velocity=msg.velocity if msg.type=='note_on' else 0,
                                start_time=start,
                                duration=end - start,
                                channel=msg.channel,
                                track_id=i
                            )
                        )
            # optional: get track name
            name = ''
            for meta in mtrack:
                if meta.type == 'track_name':
                    name = meta.name
                    break
            tracks.append(Track(id=i, name=name, events=events))
        return tracks
