from .song_types import SongType

class Song:

    def __init__(self, name, artist, link):
        self.name = name
        self.artist = artist
        self.link = link
