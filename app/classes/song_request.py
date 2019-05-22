from .song import Song

class SongRequest:

    def __init__(self, song_type, title, link, requester):
        self.song = Song(song_type, title, link)
        self.requester = requester
