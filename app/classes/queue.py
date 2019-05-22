#!/usr/bin/env python3.5

from .spotify import SpotifyPlayer
from .song_request import SongRequest
from .song_types import SongType

import threading
import time

class Queue:
    NO_SONG = 'No current song'
    NO_SONGS_IN_QUEUE = 'No songs in the queue. Add one with !sr'
    BOTIFY_ERROR = 'Spotify couldn\'t'

    def __init__(self):
        self.botify = SpotifyPlayer()
        self.queue = []
        self.skippers = set()
        self.playback_info = {}
        threading.Thread(target=self._check_current_song_to_play_next).start()

    def request_song(self, song, requester):
        if self._is_youtube_link(song):
            return "YouTube is currently not supported"
            #self.yt.search(song)

        success, response = self.botify.search(song)
        if not success:
            return response['error']

        # just add it to streamiest playlist for now
        self.botify.request_song(song)

        songRequest = SongRequest(SongType.Spotify, response['title'],
                response['song_uri'], requester)
        response = self._add_to_queue(songRequest)
        self._check_and_start_playing()
        return response

    def remove_song(self, requester):
        for i, song in reversed(list(enumerate(self.queue))):
            print(i, song, requester, song.requester)
            if i == 0:
                return 'Can\'t remove the currently playing song'
            if song.requester == requester:
                removed = self.queue.pop(i)
                return 'Removed: {}'.format(removed.song.title)
        return self.NO_SONGS_IN_QUEUE

    def playlist(self):
        if len(self.queue) == 0:
            return self.NO_SONGS_IN_QUEUE

        num_to_show = 3
        playlist_msg = 'The next songs are: '
        for i, song in enumerate(self.queue[:num_to_show]):
            playlist_msg += '#{}: {} requested by {} '.format(i+1,
                    song.song.title, song.requester)

        return playlist_msg

    def next_song(self, requester):
        if not self._should_skip(requester):
            return 'Not enough votes to skip: {}. Need 3 total. Vote with !nextsong'.format(len(self.skippers))

        return self._next_song()

    def _next_song(self):
        self._clear_playback_info()
        if len(self.queue) == 0:
            print('next_song with no next songs')
            return 'No next songs'

        response = None
        if len(self.queue) == 1:
            self.queue = []
            self.stop_playing()
            return self.NO_SONGS_IN_QUEUE

        self.start_playing(self.queue[1])
        self.queue = self.queue[1:]
        self.skippers = set()
        return self.current_song()

    def current_song(self):
        if len(self.queue) == 0:
            return self.NO_SONG
        return 'Currently playing: {} requested by {}'.format(
                    self.queue[0].song.title, self.queue[0].requester)

    def volume(self, volume):
        return self.botify.volume(volume)

    def get_volume(self):
        return self.botify.get_volume()

    def stop_playing(self):
        if len(self.queue) == 0:
            return self.NO_SONGS_IN_QUEUE

        if self.queue[0].song.type == SongType.Spotify:
            self.botify.pause_track()
        elif self.queue[0].song.type == SongType.Youtube:
            pass
        return 'Stopped the music :('

    def start_playing(self, sr=None):
        if len(self.queue) == 0:
            return self.NO_SONGS_IN_QUEUE

        if not sr:
            sr = self.queue[0]
# TODO: fix !play playing song while it's already playing
#        success, info = self._request_playback_info()
#        if not success:
#            return self.BOTIFY_ERROR
#
#        if info and info['is_playing']:
#            return 'Already playing chunes'

        if sr.song.type == SongType.Spotify:
            ms = 0
            if self.playback_info and self.playback_info['progress_ms']:
                ms = self.playback_info['progress_ms']
            self.botify.play_track(sr, position_ms=ms)
        elif sr.song.type == SongType.Youtube:
            pass
        return 'Playing the thicc beatz'

    def _clear_playback_info(self):
        self.playback_info = None

    def _should_skip(self, requester):
        if requester == 'stroopc' or requester == 'joker6878':
            return True

        self.skippers.add(requester)
        if len(self.skippers) >= 3:
            return True
        return False

    def _check_current_song_to_play_next(self):
        while True:
            time.sleep(5)
            if len(self.queue) == 0:
                continue

            success, self.playback_info = self._request_playback_info()
            if not success or not self.playback_info:
                continue

            title = "{} by {}".format(self.playback_info['name'],
                        self.playback_info['artist'])
            if self.playback_info['progress_ms'] == 0 \
                and not self.playback_info['is_playing'] \
                and title == self.queue[0].song.title:
                print("Playing next song")
                self._next_song()

    def _request_playback_info(self):
        if len(self.queue) == 0:
            return False, {}

        if self.queue[0].song.type == SongType.Spotify:
            return self.botify.request_playback_info()
        elif self.queue[0].song.type == SongType.Youtube:
            pass

    def _check_and_start_playing(self):
        if len(self.queue) != 1:
            return

        self.start_playing(self.queue[0])

    def _add_to_queue(self, songRequest):
        self.queue.append(songRequest)
        return "Added {} to the queue in position number #{}".format(
                songRequest.song.title, len(self.queue))

    def _remove_from_queue(self, requester):
        pass

    def _is_youtube_link(self, link):
        return 'youtube' in link or 'youtu.be' in link

