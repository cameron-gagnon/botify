#!/usr/bin/env python3.5

from pprint import pprint
import sys
import yaml

import spotipy
import spotipy.util as util

def handle_refresh(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except spotipy.client.SpotifyException:
            print("Refreshing auth token")
            args[0]._refresh()
            return fn(*args, **kwargs)
    return wrapper

def handle_500(fn):
    def wrapper(*args, **kwargs):
        try:
            return True, fn(*args, **kwargs)
        except spotipy.client.SpotifyException:
            return False, None
    return wrapper


class SpotifyPlayer:
    CONFIG_FILENAME = 'config.yml'
    RANGER_DEVICE_ID = '97b75274a2b8596ba6eaedf3d7caa971921fcd9a'

    def __init__(self):
        self.queue = []
        self._load_config()
        self._refresh()

    @handle_refresh
    def search(self, song):
        response = {}

        search_res = self.sp.search(song, limit=1, market='US')

        if search_res['tracks']['total'] == 0:
            response['error'] = "Error: {} could not be found".format(song)
            return False, response

        response['song_uri'] = search_res['tracks']['items'][0]['uri']
        response['artist'] = search_res['tracks']['items'][0]['artists'][0]['name']
        response['song_name'] = search_res['tracks']['items'][0]['name']
        response['title'] = "{} by {}".format(response['song_name'],
                                response['artist'])
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

    @handle_refresh
    def get_volume(self):
        return self._parse_volume(self.sp.current_playback(market='US'))

    @handle_refresh
    def volume(self, volume_percent):
        try:
            volume_percent = int(volume_percent)
        except ValueError:
            return "Please enter a valid number between 1 and 50"

        if volume_percent > 50 and volume_percent != 69:
            return "Please don't make me go deaf while I play games :("

        self.sp.volume(volume_percent, device_id=self.RANGER_DEVICE_ID)

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
    def play_track(self, song_request, position_ms = 0):
        self.sp.start_playback(device_id=self.RANGER_DEVICE_ID,
                position_ms = position_ms, uris=[song_request.song.link])

    @handle_refresh
    def seek_track(self, postition_ms):
        self.sp.seek_track(postition_ms,device_id=self.RANGER_DEVICE_ID)

    def devices(self):
        print(self.sp.devices())

    def alert_on_song_change(self):
        ''' Should always be run in a thread '''
        pass
        #while currently_playing !=

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

    def _is_uri(self, song):
        return 'spotify:track:' in song

    def _is_url(self, song):
        return 'https://' in song

    def _uri_from_url(self, url):
        slash_idx = url.rfind('/')
        question_idx = url.rfind('?')
        song_id = url[slash_idx+1:question_idx]
        return 'spotify:track:' + song_id

    def _add_song_to_playlist(self, song_uri):
        res = self.sp.user_playlist_add_tracks(
                self.config['username'],
                self.config['playlist'],
                tracks=[song_uri])
        print("Song added!", res)


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

    def _load_config(self):
      with open(self.CONFIG_FILENAME) as stream:
          try:
              self.config = yaml.safe_load(stream)['botify']
          except yaml.YAMLError as e:
              print(e)

if __name__ == "__main__":
    spot = SpotifyPlayer()
    if (len(sys.argv) > 1):
        spot.request_song(sys.argv[1])
    else:
        #try:
            #spot.current_playback()
            spot.request_playback_info()
            #spot.volume(40)
            #spot.get_volume()
            #spot.next_track()
            #spot.pause_track()
            #spot.play_track()
            #spot.devices()
        #except Exception as e:
        #    print(e)
        #    print("Error occurred, probably spotify's fault")
