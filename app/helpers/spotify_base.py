import spotipy
import spotipy.util as util

from app.helpers.config import Config

class SpotifyBase(Config):
    RANGER_DEVICE_ID = '97b75274a2b8596ba6eaedf3d7caa971921fcd9a'

    def __init__(self):
        super().__init__('botify')
        self._refresh()

    def _refresh(self):
        self.token = util.prompt_for_user_token(self.config['username'],
                self.config['scope'],
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                redirect_uri=self.config['redirect_uri'])
        if not self.token:
            raise Exception("Unable to get auth token!")
        self.sp = spotipy.Spotify(auth=self.token)
        self.sp.trace = False