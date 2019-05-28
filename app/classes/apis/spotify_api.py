#!/usr/bin/env python3.5

from pprint import pprint
import sys

from app.helpers.spotify_base import SpotifyBase
from app.decorators.decorators import handle_500, handle_refresh

class SpotifyAPI(SpotifyBase):

    def __init__(self):
        super().__init__()

    @handle_refresh
    def search(self, song):
        response = {}

        search_res = self.sp.search(song, limit=1, market='US')

        if search_res['tracks']['total'] == 0:
            response['error'] = "Error: {} could not be found".format(song)
            return False, response

        response['song_uri'] = search_res['tracks']['items'][0]['uri']
        response['artist'] = search_res['tracks']['items'][0]['artists'][0]['name']
        response['name'] = search_res['tracks']['items'][0]['name']
        return True, response

    @handle_refresh
    def request_song(self, song):
        ''' Supports URL and search term queries NOT URI queries'''
        song_uri = song_name = artist = None

        success, response = self.search(song)
        if not success:
            return response['error']

        self._add_song_to_playlist(response['song_uri'])
        return "{song_name} by {artist} was added to the playlist".format(
                song_name=response['song_name'], artist=response['artist'])

    @handle_refresh
    def remove_song(self, song_or_uri):
        message = "Removed {song_or_uri} from playlist".format(song_or_uri=song_or_uri)
        if not self._is_uri(song_or_uri):
            success, response = self.search(song_or_uri)
            if not success:
                return response['error']
            message = "Removed {song_name} by {artist} from the playlist".format(
                        song_name=response['song_name'],
                        artist=response['artist'])
            song_uri = response['song_uri']

        self.sp.user_playlist_remove_all_occurrences_of_tracks(self.config['username'],
                self.config['playlist'], [song_uri])
        return message


    def devices(self):
        print(self.sp.devices())


    def _is_uri(self, song):
        return 'spotify:track:' in song

    def _add_song_to_playlist(self, song_uri):
        res = self.sp.user_playlist_add_tracks(
                self.config['username'],
                self.config['playlist'],
                tracks=[song_uri])
        print("Song added!", res)

if __name__ == "__main__":
    spot = SpotifyAPI()
    if len(sys.argv) > 1:
        spot.request_song(sys.argv[1])
    else:
        spot.request_playback_info()
