from typing import List

from note import Note

# Tracks of midi + notes
class NoteTrack:
    def __init__(self, notes: List[Note]):
        self.notes: List[Note] = notes

# TODO:
class StrudelTrack:
    def __init__(self):
        pass