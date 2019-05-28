import re

from app.helpers.spotify_base import SpotifyBase
from app.decorators.decorators import handle_refresh, handle_500
from app.decorators.singleton import Singleton

@Singleton
class SpotifyPlayer(SpotifyBase):
    VOL_REGEX = '[\+|-]\d{1,3}'

    def __init__(self):
        super().__init__()
        self.volume_percent = 35

    @handle_refresh
    def get_volume(self):
        return self._parse_volume(self.sp.current_playback(market='US'))

    @handle_refresh
    def set_volume(self, volume_percent):
        matched = re.match(self.VOL_REGEX, volume_percent)
        if matched:
            volume_percent = self.volume_percent + int(matched.group(0))

        try:
            volume_percent = self._clamp(int(volume_percent), 0, 100)
        except ValueError:
            return "Please enter a valid number between 1 and 50, inclusive"

        if volume_percent > 50 and volume_percent != 69:
            return "Please don't make me go deaf while I play games :( Give a value between 0 and 50, inclusive"

        self.sp.volume(volume_percent, device_id=self.RANGER_DEVICE_ID)
        self.volume_percent = volume_percent

        return "Volume set to {}".format(volume_percent)

    @handle_refresh
    def current_playback(self):
        return self._currently_playing(self.sp.current_playback(market='US'))

    @handle_500
    def request_playback_info(self):
        return self._current_song_name(self.sp.current_playback(market='US'))

    @handle_refresh
    def next_track(self):
        self.sp.next_track(device_id=self.RANGER_DEVICE_ID)

    @handle_refresh
    def pause_track(self):
        self.sp.pause_playback(device_id=self.RANGER_DEVICE_ID)

    @handle_refresh
    def play_track(self, uri, position_ms = 0):
        self.sp.start_playback(device_id=self.RANGER_DEVICE_ID,
                position_ms = position_ms, uris=[uri])

    @handle_refresh
    def seek_track(self, postition_ms):
        self.sp.seek_track(postition_ms,device_id=self.RANGER_DEVICE_ID)

    def _parse_volume(self, response):
        if response['device']['name'] == 'RANGER':
            return "Volume is: {}".format(response['device']['volume_percent'])
        return "Unable to get volume :("

    def _current_song_name(self, response):
        #pprint(response)
        res = {}
        if not response:
            return res

        res['name'] = response['item']['name']
        res['artist'] = response['item']['artists'][0]['name']
        res['is_playing'] = response['is_playing']
        res['progress_ms'] = response['progress_ms']
        return res

    def _currently_playing(self, response):
        link = response['item']['external_urls']['spotify']
        artist_name = response['item']['artists'][0]['name']
        album_name = response['item']['album']['name']
        song_name = response['item']['name']
        return "Currently playing: {song_name} by {artist_name} off of "\
                "{album_name}. Here's the link! {link}".format(
                        song_name=song_name, artist_name=artist_name,
                        album_name=album_name, link=link)

    def _clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)
