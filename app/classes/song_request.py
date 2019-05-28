from .song_types import SongType

class SongRequestFactory:
    def __init__(self, song_type, *args, **kwargs):
        if song_type == SongType.Spotify:
            return SpotifyRequest(song_type, *args, **kwargs)
        elif song_type == SongType.YouTube:
            return YouTubeRequest(song_type, *args, **kwargs)
        else:
            raise 'Invalid SongRequest type'

class SongRequest:

    def __init__(self, song_type, title, link, requester):
        self.song = Song(song_type, title, link)
        self.requester = requester

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

def YouTubeRequest(SongRequest):
    def __init__(self, song_type, title, link, requester):
        super().__init__(song_type, title, link, requester)

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

def SpotifyRequest(SongRequest):
    def __init__(self,song_type, title, link, requester):
        super().__init__(song_type, title, link, requester)
        self.playback_info = None

    def play(self):
        ms = 0
        if self.playback_info and self.playback_info['progress_ms']:
            ms = self.playback_info['progress_ms']
        self.botify.play_track(sr, position_ms=ms)

    def pause(self):
        pass

    def volume(self):
        self.botify.volume(volume)

    def info(self):
        return '{} requested by {}'.format(self.song.title, self.requester)

