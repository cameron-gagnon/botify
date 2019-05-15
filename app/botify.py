#!/usr/bin/env python3.5

from pprint import pprint
import sys
import yaml
#import decorators

import spotipy
import spotipy.util as util

class SpotifyPlayer:
    CONFIG_FILENAME = 'config.yml'
    RANGER_DEVICE_ID = '97b75274a2b8596ba6eaedf3d7caa971921fcd9a'

    def __init__(self):
        self.queue = []
        self._load_config()
        self._refresh()

    def request_song(self, song):
        ''' Supports URL and search term queries NOT URI queries'''
        try:
            return self._request_song(song)
        except spotipy.client.SpotifyException:
            print("Refreshing auth token")
            self._refresh()
            return self._request_song(song)

    def _request_song(self, song):
        song_uri = song_title = artist = None

        if self._is_url(song):
            song_uri = self._uri_from_url(song)

        res = self.sp.search(song, limit=1, market='US')
        if res['tracks']['total'] == 0:
            return "Error: {} could not be added".format(song)

        song_uri = res['tracks']['items'][0]['uri']
        artist = res['tracks']['items'][0]['artists'][0]['name']
        song_title = res['tracks']['items'][0]['name']


        self._add_song_to_playlist(song_uri)
        return "{song_title} by {artist} was added to the playlist".format(
                song_title=song_title, artist=artist)

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
        return ':' in song

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

    def search(self, query):
        song = self.sp.search(query, limit=1)
        print(song)

    def get_volume(self):
        return self._parse_volume(self.sp.current_playback(market='US'))

    def volume(self, volume_percent):
        try:
            volume_percent = int(volume_percent)
        except ValueError:
            return "Please enter a valid number between 1 and 50"

        if volume_percent > 35 and volume_percent != 69:
            return "Please don't make me go deaf while I play games :("

        self.sp.volume(volume_percent, device_id=self.RANGER_DEVICE_ID)
        return "Volume set to {}".format(volume_percent)

    def current_playback(self):
        return self._currently_playing(self.sp.current_playback(market='US'))

    def next_track(self):
        self.sp.next_track(device_id=self.RANGER_DEVICE_ID)

    def pause_track(self):
        self.sp.pause_playback(device_id=self.RANGER_DEVICE_ID)

    def play_track(self):
        self.sp.start_playback(device_id=self.RANGER_DEVICE_ID)

    def devices(self):
        print(self.sp.devices())

    def _parse_volume(self, response):
        if response['device']['name'] == 'RANGER':
            return "Volume is: {}".format(response['device']['volume_percent'])
        return "Unable to get volume :("

    def _currently_playing(self, response):
        link = response['item']['external_urls']['spotify']
        artist_name = response['item']['artists'][0]['name']
        album_name = response['item']['album']['name']
        song_title = response['item']['name']
        return "Currently playing: {song_title} by {artist_name} off of "\
                "{album_name}. Here's the link! {link}".format(
                        song_title=song_title, artist_name=artist_name,
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
            spot.current_playback()
            spot.volume(40)
            spot.get_volume()
            #spot.next_track()
            #spot.pause_track()
            #spot.play_track()
            #spot.devices()
        #except Exception as e:
        #    print(e)
        #    print("Error occurred, probably spotify's fault")
