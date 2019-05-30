import threading
import time

from app.classes.requests.song_request import SongRequest

class YouTubeRequest(SongRequest):
    def __init__(self, requester, player, *args):
        super().__init__(requester, player, *args)

    def play(self):
        self.player.play(self.song.link)

    def pause(self):
        self.player.pause()

    def set_volume(self, vol):
        return self.player.set_volume(vol)

    def get_volume(self):
        return self.player.get_volume()

    def done(self):
        self.done = True
        self.player.done()
