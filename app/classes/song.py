from .song_types import SongType

class Song:

    def __init__(self, song_type, title, link):
        self.type = song_type
        self.title = title
        self.link = link
