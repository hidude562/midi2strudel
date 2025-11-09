class Note:
    def __init__(self, note: int, length: float, channel: int):
        self.note: int = note
        self.length: float = length
        self.channel: int = channel

    def __str__(self) -> str:
        return f'Note: {self.note}, {self.length}'

class IncompleteNote:
    def __init__(self, note: int, start: float, channel: int, end=None):
        self.note: int = note
        self.start: float = start
        self.channel: int = channel
        self.end: float | None = end

    def generate_complete_note(self):
        if self.end == None:
            raise Exception("Incomplete note tried to generate")
        return Note(self.note, self.end - self.start, self.channel)

    def __str__(self) -> str:
        return f'IncompleteNote: {self.note}, {self.start}, {self.end}'
