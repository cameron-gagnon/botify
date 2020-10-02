from app import db

class SongRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.String(128), index=True)
    song_type = db.Column(db.String(128))
    name = db.Column(db.String(128), index=True)
    artist = db.Column(db.String(128), index=True)
    link = db.Column(db.String(256), index=True, unique=True)

    MAX_VOLUME = 50

    def __init__(self, requester, player, song_type, *args):
        self.requester = requester
        self.player = player
        self.song_type = song_type
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

    def __str__(self):
        return '%(name)s by %(artist)s %(link)s requested by %(requester)s' % {
            'name': self.name,
            'artist': self.artist,
            'link': self.link,
            'requester': self.requester,
        }
