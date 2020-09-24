import gevent
import time

from flask_socketio import emit

from app.models.song_requests.song_request import SongRequest

class SpotifyRequest(SongRequest):

    def __init__(self, requester, player, song_type, *args, callback=None):
        super().__init__(requester, player, song_type, *args)
        self.playback_info = None
        self.thread_started = False
        self.callback = callback

    def play(self):
        if not self.thread_started:
            self.thread_started = True
            gevent.spawn(self._song_done)

        self.start_playback()

    def start_playback(self):
        at_ms = self.resume_playback_at()
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

    def _song_done(self):
        while True:
            gevent.sleep(5)
            if self.song_done:
                return

            self.playback_info = self.player.request_playback_info()
            print("request_player info:", self.playback_info)

            # sometimes it seems when spotify finishes playing a song, if it
            # isn't on autoplay and isn't told to play a new song it will
            # immediately start returning no information for current playback
            # we assume we're not erroring out and instead spotify is just done
            # playing
            # if not self.playback_info:
            #     self.callback()
            #     return

            # and self.playback_info['progress_ms'] == 0 \
            # and not self.playback_info['is_playing'] \
            if self.playback_info \
                and self.playback_info['name'] != self.name:
                print("Executing callback")
                self.callback()
                return
