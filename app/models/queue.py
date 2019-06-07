import re

from app.models.apis.spotify_api import SpotifyAPI
from app.models.apis.youtube_api import YouTubeAPI
from app.models.requests.song_request_factory import song_request_factory
from app.models.requests.song_types import SongType
from app.decorators.decorators import handle_infinite_loop, check_queue_length

class Queue:
    NO_SONG = 'No current song'
    NO_SONGS_IN_QUEUE = 'No songs in the queue. Add one with !sr'
    MAX_LEN = 20
    MAX_SONG_REQS_PER_PERSON = 3
    VOL_REGEX = '[\+|-]\d{1,3}'
    ERR_TOO_LOUD = "Please don't make me go deaf while I play games :( Give a value between 0 and {} inclusive"
    ERR_INVALID_VOL = "Please enter a valid number between 0 and {}, inclusive"
    ERR_FULL_QUEUE = "Sorry, the queue is full right now :( Please add a song after the next one has played!"
    ERR_TOO_MANY_REQUESTS = "You can only put {} number of songs on the queue"
    ERR_SONG_ALREADY_EXISTS = "This song is already on the queue"

    def __init__(self):
        self.spotify_api = SpotifyAPI()
        self.youtube_api = YouTubeAPI()
        self.queue = []
        self.skippers = set()
        self.playback_info = {}

    def request_song(self, song, requester):
        if len(self.queue) >= self.MAX_LEN:
            return self.ERR_FULL_QUEUE

        if self.too_many_requests(requester):
            return self.ERR_TOO_MANY_REQUESTS.format(self.MAX_SONG_REQS_PER_PERSON)

        song_type = None
        if self._is_youtube_link(song):
            success, response = self.youtube_api.is_valid_link(song)
            if success:
                song_type = SongType.YouTube

        if not song_type:
            success, response = self.spotify_api.search(song)
            if success:
                song_type = SongType.Spotify

        if not song_type:
            success, response = self.youtube_api.search(song)
            if success:
                song_type = SongType.YouTube

        if not song_type:
            return 'Could not find {} :('.format(song)

        if self.song_already_on_queue(response):
            return self.ERR_SONG_ALREADY_EXISTS

        song_request = song_request_factory(song_type, requester,
                response['name'], response['artist'], response['song_uri'],
                callback=self._song_done)

        response = self._add_to_queue(song_request)
        self._check_and_start_playing()
        return response

    def song_already_on_queue(self, response):
        for song in self.queue:
            if song.song.name == response['name'] and \
               song.song.artist == response['artist']:
                   return True
        return False

    def too_many_requests(self, requester):
        num_requests = 0
        for song in self.queue:
            if song.requester == requester:
                num_requests += 1

        return num_requests >= self.MAX_SONG_REQS_PER_PERSON

    def remove_song(self, requester):
        for i, song in reversed(list(enumerate(self.queue))):
            print(i, song, requester, song.requester)
            if i == 0:
                return 'Can\'t remove the currently playing song'
            if song.requester == requester:
                removed = self.queue.pop(i)
                return 'Removed: {}'.format(removed.song.name)
        return self.NO_SONGS_IN_QUEUE

    def promote(self, requester, pos):
        if requester not in ['stroopc', 'joker6878']:
            return "Sorry, only the DJs can promote songs :/"

        success, pos = self._validate_int(pos)
        if not success:
            return pos

        self.queue[1], self.queue[pos-1] = self.queue[pos-1], self.queue[1]
        return 'Promoted {} to #2'.format(self.queue[1].info())

    def playlist(self, offset=0):
        success, offset = self._validate_int(offset)
        if not success:
            return offset

        num_to_show = 3
        playlist_msg = 'The next songs are: '
        for i, song in enumerate(self.queue[offset-1:offset-1+num_to_show]):
            playlist_msg += '#{}: {} '.format(i+offset, song.info())

        return playlist_msg

    def next_song(self, requester):
        if not self._should_skip(requester):
            return 'Not enough votes to skip: {}. Need 3 total. Vote with !nextsong'.format(len(self.skippers))

        return self._next_song()

    def _song_done(self):
        ''' Should only be called once per SongRequest '''
        self.queue[0].done()

        if len(self.queue) == 1:
            response = self.NO_SONGS_IN_QUEUE
        else:
            self.start_playing(self.queue[1])
            self.skippers = set()
            response = self.queue[1].info()

        del self.queue[0]
        return response

    @check_queue_length
    def current_song(self):
        return 'Currently Playing: ' + self.queue[0].info()

    @check_queue_length
    def set_volume(self, volume_percent):
        max_volume = self.queue[0].max_volume()
        matched = re.match(self.VOL_REGEX, volume_percent)
        if matched:
            volume_percent = self.queue[0].get_int_volume() + int(matched.group(0))

        try:
            volume_percent = self._clamp(int(volume_percent), 0, 100)
        except ValueError:
            return self.ERR_INVALID_VOL.format(max_volume)

        if volume_percent > max_volume:
            return self.ERR_TOO_LOUD.format(max_volume)

        return self.queue[0].set_volume(volume_percent)

    @check_queue_length
    def get_volume(self):
        return self.queue[0].get_volume()

    @check_queue_length
    def stop_playing(self):
        self.queue[0].pause()

        return 'Stopped the music :('

    @check_queue_length
    def start_playing(self, sr=None):
        if not sr: sr = self.queue[0]
        sr.play()
        return 'Playing the thicc beatz'

    @check_queue_length
    def _next_song(self):
        response = None
        self.stop_playing()
        return self._song_done()

    def _validate_int(self, num):
        if not self.queue:
            return False, self.NO_SONGS_IN_QUEUE
        try:
            num = int(num)
        except ValueError:
            return False, "Give a valid integer"

        if num < 1 or num > len(self.queue):
            return False, "Please give a number between 1 and {}".format(len(self.queue))
        return True, num

    def _clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)

    def _should_skip(self, requester):
        if requester == 'stroopc' or requester == 'joker6878':
            return True

        self.skippers.add(requester)
        if len(self.skippers) >= 3:
            return True
        return False

    def _check_and_start_playing(self):
        if len(self.queue) != 1 or not self.queue: return
        self.start_playing()

    def _add_to_queue(self, songRequest):
        self.queue.append(songRequest)
        return "Added {} to position number #{}".format(
                songRequest.info(), len(self.queue))

    def _is_youtube_link(self, link):
        return 'youtube' in link or 'youtu.be' in link
