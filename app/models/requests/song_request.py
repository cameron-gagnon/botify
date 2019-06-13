class SongRequest:

    MAX_VOLUME = 50

    def __init__(self, requester, player, *args):
        self.requester = requester
        self.player = player
        self.name = args[0]
        self.artist = args[1]
        self.link = args[2]

        self.song_done = False

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
        return '{} by {}. Requested by: {}. {}'.format(self.name,
                self.artist, self.requester, self.link)

    def get_int_volume(self):
        return self.player.get_int_volume()

    def max_volume(self):
        return self.MAX_VOLUME
