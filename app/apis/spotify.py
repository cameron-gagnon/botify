from app.models.players.spotify_base import SpotifyBase
from app.helpers.decorators.decorators import handle_refresh

class SpotifyAPI(SpotifyBase):

    def __init__(self):
        super().__init__()

    @handle_refresh
    def search(self, song):
        response = {}

        # probably a spotify link or URI
        if 'spotify' in song:
            search_res = self.sp.track(song)
            response = self._song_info_from_track(search_res)
        else:
            search_res = self.sp.search(song, limit=1, market='US')

            if search_res['tracks']['total'] == 0:
                response['error'] = "Error: {} could not be found".format(song)
                return False, response

            response = self._song_info_from_search(search_res)
        return True, response
