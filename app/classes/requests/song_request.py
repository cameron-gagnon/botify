from app.classes.song import Song

class SongRequest:

    def __init__(self, requester, player, *args):
        self.requester = requester
        self.player = player
        self.song_done = False
        self.song = Song(*args)

    def play(self):
        pass

    def pause(self):
        pass

    def set_volume(self):
        pass

    def get_volume(self):
        pass

    def done(self):
        self.song_done = True

    def _info(self):
        return '{} by {}'.format(self.song.name, self.song.artist)
