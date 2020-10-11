import threading
import time

from app.models.song_requests.song_request import SongRequest
from app.models.song_requests.song_types import SongType

class YouTubeRequest(SongRequest):
    def __init__(self, requester, player, *args):
        super().__init__(requester, player, *args)
        self.MAX_VOLUME = 35
        self.song_type = SongType.YouTube

    def play(self):
        return self.player.play(self.link)

    def pause(self):
        return self.player.pause()

    def set_volume(self, vol):
        return self.player.set_volume(vol)

    def get_volume(self):
        return self.player.get_volume()

    def done(self):
        self.song_done = True
        self.player.done()
