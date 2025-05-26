import mido
from core.models import NoteEvent, Track

class MidiLoader:
    @staticmethod
    def load(path: str, sample_rate: int) -> list[Track]:
        mid = mido.MidiFile(path)
        tracks = []
        # Build absolute time in seconds:
        for ti, mtrack in enumerate(mid.tracks):
            events = []
            abs_time = 0.0
            tempo = 500000  # default µs per beat
            ticks_per_beat = mid.ticks_per_beat
            for msg in mtrack:
                abs_time += mido.tick2second(msg.time, ticks_per_beat, tempo)
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                elif msg.type == 'note_on' and msg.velocity>0:
                    # store pending note_on; you'll need a dict to match note_off
                    # for brevity, you can accumulate and then match pairs
                    events.append(NoteEvent(
                        pitch=msg.note,
                        velocity=msg.velocity,
                        start_time=abs_time,
                        duration=0.0,   # fill in later
                        channel=msg.channel,
                        track_id=ti
                    ))
                elif (msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0)):
                    # find matching note_on in events and set its duration
                    for e in reversed(events):
                        if e.pitch==msg.note and e.duration==0.0 and e.channel==msg.channel:
                            e.duration = abs_time - e.start_time
                            break
            tracks.append(Track(id=ti,
                                name=mtrack.name or "",
                                events=[e for e in events if e.duration>0]))
        return tracks