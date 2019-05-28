from .song_request import SongRequest

class YouTubeRequest(SongRequest):
    def __init__(self, requester, player, *args):
        super().__init__(requester, player, *args)

    def play(self):
        pass

    def pause(self):
        pass

    def volume(self):
        pass

    def info(self):
        pass

    def should_play_next_song(self):
        pass
