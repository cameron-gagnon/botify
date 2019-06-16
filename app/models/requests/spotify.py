import threading
import time

from app.models.requests.song_request import SongRequest

class SpotifyRequest(SongRequest):

    def __init__(self, requester, player, *args, callback=None):
        super().__init__(requester, player, *args)
        self.playback_info = None
        self.thread_started = False
        self.callback = callback

    def play(self):
        if not self.thread_started:
            self.thread_started = True
            threading.Thread(target=self._song_done).start()

        ms = 0
        if self.playback_info and self.playback_info['progress_ms']:
            ms = self.playback_info['progress_ms']
        self.player.play_track(self.link, position_ms=ms)

    def pause(self):
        self.player.pause_track()

    def set_volume(self, volume):
        return self.player.set_volume(volume)

    def get_volume(self):
        return self.player.get_volume()

    def _song_done(self):
        while True:
            time.sleep(5)
            if self.song_done:
                return

            success, self.playback_info = self.player.request_playback_info()
            print("request_player info:", success, self.playback_info)
            if not success:
                continue

            if self.playback_info \
                and self.playback_info['progress_ms'] == 0 \
                and not self.playback_info['is_playing'] \
                and self.playback_info['name'] == self.name:
                self.callback()
                return
