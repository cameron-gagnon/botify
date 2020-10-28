import gevent
import time
from collections import deque
from flask_socketio import emit

from app.models.song_requests.song_request import SongRequest
from app.models.song_requests.song_types import SongType
from main import app

class Decorators:
    @classmethod
    def has_playback_info(cls, decorated):
        def wrapper(*args, **kwargs):
            if args[0].playback_info:
                return decorated(*args, **kwargs)
            else:
                return False
        return wrapper

class SpotifyRequest(SongRequest):

    SLEEP_TIME = 0.50
    MAX_DEQUE_LENGTH = 10

    def __init__(self, requester, player, *args, callback=None):
        super().__init__(requester, player, *args)
        self.playback_info = None
        self.thread_started = False
        self.callback = callback
        self.song_type = SongType.Spotify
        self._prev_pos_ms = deque(maxlen=self.MAX_DEQUE_LENGTH)

    def play(self):
        self.update_playback_info_if_already_playing()
        self.start_tracking_playback()
        self.start_playback()

    def start_tracking_playback(self):
        if not self.thread_started:
            self.thread_started = True
            gevent.spawn(self._song_done)

    def start_playback(self):
        at_ms = self.resume_playback_at()
        if not self.is_playing():
            self.player.modify_playlist(self.player.TMP_PLAYLIST, self.link)
            self.play_stream_playlist(at_ms)

    def resume_playback_at(self):
        ms = 0
        if self.playback_info and self.playback_info['progress_ms']:
            ms = self.playback_info['progress_ms']
        return ms

    def play_stream_playlist(self, position_ms):
        app.logger.debug(f"Playing song: {self.link} starting at {position_ms}ms in.")
        self.player.play_track(context_uri=self.player.TMP_PLAYLIST,
                               position_ms=position_ms)

    def pause(self):
        self.player.pause_track()

    def set_volume(self, volume):
        return self.player.set_volume(volume)

    def get_volume(self):
        return self.player.get_volume()

    @Decorators.has_playback_info
    def is_playing(self):
        return self.playback_info['is_playing']

    @Decorators.has_playback_info
    def playing_next_song(self):
        return self.playback_info['name'] != self.name

    @Decorators.has_playback_info
    def song_stuck_or_paused(self):
        return self.playback_info['name'] == self.name \
                  and self._has_not_progressed()

    def update_playback_info_if_already_playing(self):
        potential_playback_info = self.player.request_playback_info()
        if potential_playback_info.get('name', '') == self.name:
            self.update_playback_info()

    # @returns True if still playing current song
    # @returns False if playing next song or song is "paused"/stuck at 0ms
    def update_playback_info(self):
        app.logger.debug(f"Updating playback info for: {self.name}")

        self.playback_info = self.player.request_playback_info()
        self._update_playback_history()

        app.logger.debug(f"Updated playback info: {self.playback_info['name']} playing at {self.playback_info['progress_ms']}")
        return not (self.playing_next_song() or self.song_stuck_or_paused())

    @Decorators.has_playback_info
    def _update_playback_history(self):
        self._prev_pos_ms.append(self.playback_info['progress_ms'])

    def _has_not_progressed(self):
        num_times_at_0 = 0
        for pos_ms in self._prev_pos_ms:
            if pos_ms == 0:
                num_times_at_0 += 1
        return num_times_at_0 == self.MAX_DEQUE_LENGTH

    def _song_done(self):
        while True:
            gevent.sleep(self.SLEEP_TIME)
            if self.song_done:
                return

            playing_this_song = self.update_playback_info()
            if not playing_this_song:
                app.logger.debug(f"Executing callback for spotify song: {self.name}")
                self.callback()
                return
