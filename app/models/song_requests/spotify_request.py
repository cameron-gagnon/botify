import gevent
import time

from flask_socketio import emit

from app.models.song_requests.song_request import SongRequest

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

    def __init__(self, requester, player, song_type, *args, callback=None):
        super().__init__(requester, player, song_type, *args)
        self.playback_info = None
        self.thread_started = False
        self.callback = callback

    def play(self):
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
            self.play_tmp_playlist(at_ms)

    def resume_playback_at(self):
        ms = 0
        if self.playback_info and self.playback_info['progress_ms']:
            ms = self.playback_info['progress_ms']
        return ms

    def play_tmp_playlist(self, position_ms):
        print(f"Playing song: {self.link} starting at {position_ms}ms in.")
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
    def spotify_sucks_pp(self):
        return self.playback_info['name'] == self.name \
                  and self.playback_info['progress_ms'] == 0

    def _song_done(self):
        while True:
            gevent.sleep(0.5)
            if self.song_done:
                return

            self.playback_info = self.player.request_playback_info()
            print("request_player info:", self.playback_info)

            if self.playing_next_song() or self.spotify_sucks_pp():
                print("Executing callback")
                self.callback()
                return
