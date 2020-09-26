import spotipy
import spotipy.util as util

from app.helpers.configs.config import Config
from main import app

class SpotifyBase(Config):
    RANGER_DEVICE_ID = '8a3c4ae699cdd7775c263a6993a5ddf78e20cc10'
    DEFAULT_PLAYLIST_TRACK = 'spotify:playlist:7ekRyn6gOaqR6P0GS24uZ5'

    def __init__(self):
        super().__init__('spotify')
        self._refresh()

    def _refresh(self):
        self.token = util.prompt_for_user_token(self.config['username'],
                self.config['scope'],
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                redirect_uri=self.config['redirect_uri'])
        if not self.token:
            app.logger.error('Unable to get Spotify auth token!')
            raise Exception('Unable to get auth token!')
        self.sp = spotipy.Spotify(auth=self.token)
        self.sp.trace = False

    def _song_info_from_search(self, result):
        track = result['tracks']['items'][0]
        return self._song_info_from_track(track)

    def _song_info_from_spotify_response(self, response):
        if not response:
            return {}

        res = self._song_info_from_track(response['item'])
        res['is_playing'] = response['is_playing']
        res['progress_ms'] = response['progress_ms']
        return res

    def _song_info_from_track(self, track):
        if not track:
            app.logger.error('Asked for track info, but got no track!')
            raise Exception('No track info provided when formatting info from track')

        response = {}
        response['song_uri'] = track['external_urls']['spotify']
        response['artist'] = track['artists'][0]['name']
        response['name'] = track['name']
        return response
