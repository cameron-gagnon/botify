from app.apis.spotify import SpotifyAPI
from app.apis.youtube import YouTubeAPI
from app.models.song_requests.song_request_factory import song_request_factory
from app.models.song_requests.song_types import SongType

class Searcher:

    def __init__(self):
        self.spotify_api = SpotifyAPI()
        self.youtube_api = YouTubeAPI()

    def search(self, song, requester, callback):
        song_type = None
        if self._is_youtube_link(song):
            success, response = self.youtube_api.is_valid_link(song)
            if success:
                song_type = SongType.YouTube

        if not song_type:
            success, response = self.spotify_api.search(song)
            if success:
                song_type = SongType.Spotify

        if not song_type:
            success, response = self.youtube_api.search(song)
            if success:
                song_type = SongType.YouTube

        if not song_type:
            return False, 'Could not find {} :('.format(song)

        song_request = song_request_factory(song_type, requester,
                response['name'], response['artist'], response['song_uri'],
                callback=callback)
        return True, song_request

    def _is_youtube_link(self, link):
        return 'youtube' in link or 'youtu.be' in link
