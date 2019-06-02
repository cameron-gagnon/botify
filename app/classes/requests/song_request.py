from app.classes.requests.song import Song

class SongRequest:

    def __init__(self, requester, player, *args):
        self.requester = requester
        self.player = player
        self.song_done = False
        self.song = Song(*args)
        self.MAX_VOLUME = 50

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

    def info(self):
        return '{} by {}. Requested by: {}'.format(self.song.name,
                self.song.artist, self.requester)

    def get_int_volume(self):
        return self.player.get_int_volume()

    def max_volume(self):
        return self.MAX_VOLUME
