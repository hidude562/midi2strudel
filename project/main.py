from typing import List

import mido
from note import IncompleteNote, Note
from track import NoteTrack

mid = mido.MidiFile('test.mid')

# Adjusted by the ticks multiplier
absolute_time = 0

ticks_multiplier = 1.0 / mid.ticks_per_beat

tracks: List[NoteTrack] = []

for track in mid.tracks:
    active_notes = []
    complete_notes = []

    # TODO: Implement space in music by when there are no complete notes, represent emptyness with a note value of -1 and said duration

    for msg in track:
        # Increment the time
        if msg.type == "track_name":
            absolute_time = msg.time * ticks_multiplier
        elif msg.type == "end_of_track":
            absolute_time = 0
        else:
            absolute_time += msg.time * ticks_multiplier

        # Check events
        if msg.type == 'note_on':
            active_notes.append(IncompleteNote(msg.note, absolute_time, msg.channel))
        elif msg.type == 'note_off':
            # Find the target note
            for incomplete_note in active_notes:
                if incomplete_note.channel == msg.channel:
                    if incomplete_note.note == msg.note:
                        incomplete_note.end = absolute_time
                        complete_notes.append(incomplete_note.generate_complete_note())
                        active_notes.remove(incomplete_note)

    tracks.append(NoteTrack(complete_notes))
    print([note.__str__() for note in complete_notes])