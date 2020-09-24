import re
import random

from app.models.players.spotify_base import SpotifyBase
from app.helpers.decorators.decorators import handle_refresh
from app.helpers.decorators.singleton import Singleton
from main import app

@Singleton
class SpotifyPlayer(SpotifyBase):

    TMP_PLAYLIST = 'spotify:playlist:7IaqpuGOD8ypXoSRKnZ865'

    def __init__(self):
        super().__init__()
        self.volume_percent = 35
        playlist_info = self.sp.user_playlist_tracks(self.config['user_id'],
                                             self.DEFAULT_PLAYLIST_TRACK,
                                             offset=1, limit=1)
        self.default_playlist_length = playlist_info['total']

    @handle_refresh
    def play_default_playlist(self):
        self.sp.shuffle(True, self.RANGER_DEVICE_ID)
        self.play_track(context_uri=self.DEFAULT_PLAYLIST_TRACK)

    @handle_refresh
    def random_track_from_default_playlist(self):
        random_int = random.randint(0, self.default_playlist_length)
        track_info = self.sp.user_playlist_tracks(self.config['user_id'],
                                             self.DEFAULT_PLAYLIST_TRACK,
                                             offset=random_int, limit=1)
        track = track_info['items'][0]['track']
        return self._song_info_from_track(track)

    @handle_refresh
    def modify_playlist(self, playlist_id, song_uri):
        res = self.sp.playlist_replace_items(playlist_id, [song_uri])
        print(f"result from adding (or clearing) {playlist_id}: {res}")

    @handle_refresh
    def get_volume(self):
        return self._parse_volume(self.sp.current_playback(market='US'))

    @handle_refresh
    def get_int_volume(self):
        return self._parse_int_volume(self.sp.current_playback(market='US'))

    @handle_refresh
    def set_volume(self, volume_percent):
        self.sp.volume(volume_percent, device_id=self.RANGER_DEVICE_ID)
        self.volume_percent = volume_percent
        return "Volume set to {}".format(volume_percent)

    @handle_refresh
    def request_playback_info(self):
        return self._song_info_from_currently_playing(self.sp.current_playback(market='US'))

    @handle_refresh
    def next_track(self):
        self.sp.next_track(device_id=self.RANGER_DEVICE_ID)

    @handle_refresh
    def pause_track(self):
        response = self.request_playback_info()
        if not response:
            app.logger.error("pause_track's response is empty")
            return

        if response['is_playing']:
            self.sp.pause_playback(device_id=self.RANGER_DEVICE_ID)

    @handle_refresh
    def play_track(self, uri=None, position_ms=0, context_uri=None):
        if uri:
            uri = [uri]

        print("Playing track", uri, position_ms)
        self.sp.start_playback(device_id=self.RANGER_DEVICE_ID,
                position_ms= position_ms, uris=uri, context_uri=context_uri)

    @handle_refresh
    def seek_track(self, postition_ms):
        self.sp.seek_track(postition_ms,device_id=self.RANGER_DEVICE_ID)

    def _parse_volume(self, response):
        if response['device']['name'] != 'RANGER':
            return "Unable to get volume :("

        return "Volume is: {}".format(self._parse_int_volume(response))

    def _parse_int_volume(self, response):
        if response['device']['name'] != 'RANGER':
            return 0
        return response['device']['volume_percent']
