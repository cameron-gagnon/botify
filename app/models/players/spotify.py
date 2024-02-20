import re
import random
from time import sleep

from app.models.players.spotify_base import SpotifyBase
from app.helpers.decorators.decorators import handle_refresh
from app.helpers.decorators.singleton import Singleton
from main import app

@Singleton
class SpotifyPlayer(SpotifyBase):

    TMP_PLAYLIST = 'spotify:playlist:7IaqpuGOD8ypXoSRKnZ865'
    MAX_RETRIES = 5

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
    def random_track_from_playlist(self, playlid_uid=SpotifyBase.DEFAULT_PLAYLIST_TRACK):
        random_int = random.randint(0, self.default_playlist_length)
        track_info = self.sp.user_playlist_tracks(self.config['user_id'],
                            playlid_uid, offset=random_int, limit=1)
        app.logger.debug(f"Random track info from playlist: {track_info}")
        track = track_info['items'][0]['track']
        return self._song_info_from_track(track)

    @handle_refresh
    def get_next_song(self, track):
        self.sp.next_track(self.RANGER_DEVICE_ID)
        return self.request_playback_info()

    @handle_refresh
    def modify_playlist(self, playlist_id, song_uri):
        res = self.sp.playlist_replace_items(playlist_id, [song_uri])
        app.logger.debug(f"Setting the playlist to {song_uri}")

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
        current_playback_info = None
        retries = 0
        while retries < self.MAX_RETRIES:
            current_playback_info = self.sp.current_playback(market='US')
            if current_playback_info:
                break
            app.logger.debug(f'Got no playback info, {retries} times in a row')
            retries += 1
            sleep(0.2)

        return self._song_info_from_spotify_response(current_playback_info)

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
    def play_track(self, position_ms=0, context_uri=None):
        self.sp.start_playback(device_id=self.RANGER_DEVICE_ID,
                position_ms=position_ms, uris=None, context_uri=context_uri)

    @handle_refresh
    def seek_track(self, postition_ms):
        self.sp.seek_track(postition_ms,device_id=self.RANGER_DEVICE_ID)

    @handle_refresh
    def _all_user_playlists(self, limit=50):
        """
        _all_user_playlists returns the complete list of playlists belonging to
        the currently authorized Spotify user.

        :param limit: (optional, default 50) number of results to return (must be between 0-50)

        :return: list of all user playlists
        """

        # offset used to paginate through results
        offset = 0
        results = []

        tmp_results = self.sp.current_user_playlists(limit=limit)['items']
        while tmp_results != []:
            offset += limit
            results += tmp_results
            tmp_results = self.sp.current_user_playlists(limit=limit, offset=offset)['items']

        return results

    @handle_refresh
    def add_song_to_user_playlist(self, username: str, song_link: str):
        """
        add_song_to_user_playlist adds a song to a playlist containing the
        complete list of songs a user has requested (re-requested songs are
        added). If this is the first song a user has requested, then the
        playlist is created first before the song is added to it. The
        playlist is created in the Spotify authorized user's library.

        :param username: username of twitch user requesting a song
        :param song_link: spotify https URL of the song requested
        """
        requester_playlist_name = self._requester_playlist_name(username)

        # find the requester's playlist, if it already exists
        playlists = self._all_user_playlists()
        playlist = None
        for pl in playlists:
            if pl['name'] == requester_playlist_name:
                playlist = pl
                break

        # playlist for this user doesn't already exist, so we'll create it
        if not playlist:
            playlist = self.sp.user_playlist_create(self.sp.current_user()['id'],
                requester_playlist_name,
                description=f"Songs {username} has requested in StroopC's chat! Request more songs at https://twitch.tv/stroopc")

        self.sp.playlist_add_items(playlist['id'], [song_link])

    def _requester_playlist_name(self, username: str) -> str:
        """
        :return: name of the Spotify playlist containing the complete list of
        songs the user has requested
        """

        return f"[Twitch] {username}'s song requests"

    def _parse_volume(self, response):
        if response['device']['name'] != 'RANGER':
            return "Unable to get volume :("

        return "Volume is: {}".format(self._parse_int_volume(response))

    def _parse_int_volume(self, response):
        if response['device']['name'] != 'RANGER':
            return 0
        return response['device']['volume_percent']
