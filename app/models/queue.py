import re
import requests

from app.helpers.decorators.decorators import handle_infinite_loop, check_queue_length, mods
from app.helpers.searcher import Searcher
from app.helpers.song_request_factory import song_request_factory
from app.models.song_requests.song_request import SongRequest
from app.models.song_requests.song_types import SongType
from app import db
from main import app

class Queue:
    NO_SONG = 'No current song'
    NO_SONGS_IN_QUEUE = 'No songs in the queue. Add one with !sr'
    MAX_LEN = 20
    MAX_SONG_REQS_PER_PERSON = 3
    ONE_SONG = 1
    THOOM_VOLUME = '70'
    VOL_REGEX = '[\+|-]\d{1,3}'
    ERR_TOO_LOUD = "Please don't make me go deaf while I play games :( Give a value between 0 and {} inclusive"
    ERR_INVALID_VOL = "Please enter a valid number between 0 and {}, inclusive"
    ERR_FULL_QUEUE = "Sorry, the queue is full right now :( Please add a song after the next one has played!"
    ERR_SONG_ALREADY_EXISTS = "This song is already on the queue"

    def __init__(self, searcher, spotify_player):
        self.searcher = searcher
        self.spotify_player = spotify_player
        self.queue = []
        self.skippers = set()
        self.playback_info = {}

        self._fill_queue()
        app.logger.debug('Initialized queue: {}'.format(self.queue))

    def request_song(self, song, requester_info):
        app.logger.debug('in request_song and the queue looks like this: {} '.format(self.queue))
        if len(self.queue) >= self.MAX_LEN:
            return self.ERR_FULL_QUEUE

        too_many_requests, response = self.too_many_requests(requester_info)
        if too_many_requests:
            return response

        success, song_request = self.searcher.search(song, requester_info['username'],
                self._next_song)
        if not success:
            return song_request

        if self.song_already_on_queue(song_request):
            return self.ERR_SONG_ALREADY_EXISTS

        response = self._check_and_start_playing(song_request)
        return response

    def song_already_on_queue(self, song_request):
        for song in self.queue:
            if song.name == song_request.name and \
               song.artist == song_request.artist:
                   return True
        app.logger.debug('song: {} already on queue'.format(song_request))
        return False

    def too_many_requests(self, requester_info):
        num_requests = 0
        for song in self.queue:
            if song.requester == requester_info['username']:
                num_requests += 1

        app.logger.debug('Too many requests for: {}'.format(requester_info))

        perm_limits = [('is_broadcaster', 50), ('is_mod', 10), ('is_subscriber', 15), ('is_vip', 5), ('is_follower', 5)]
        for permission, song_limit in perm_limits:
            if requester_info['userstatuses'][permission]:
                return num_requests >= song_limit, "Too many songs on the queue for your permission level: {}.".format(permission[3:])

        return True, "Follow to be able to request songs!"

    def remove_song(self, requester):
        for i, song in reversed(list(enumerate(self.queue))):
            if song.requester == requester:
                if i == 0:
                    self._next_song()

                removed = self.queue.pop(i)
                self._rm_song_from_db(removed)
                return 'Removed: {}'.format(removed.name)
        return self.NO_SONGS_IN_QUEUE

    @mods
    def promote(self, pos, requester_info=None):
        success, pos = self._validate_int(pos)
        if not success:
            return pos

#        song_1 = self.queue[1]
#        song_to_promote = self.queue[pos-1]
#        song_1 = SongRequest.query.filter_by(link=song_1.link).first()
#        song_to_promote = SongRequest.query.filter_by(link=song_to_promote.link).first()
#        tmp_id = song_1.pos_in_queue
#        print('song_1 id:', song_1.pos_in_queue)
#        print('promote id:', song_to_promote.pos_in_queue)
#        song_1.pos_in_queue = song_to_promote.pos_in_queue
#        song_to_promote.pos_in_queue = tmp_id
#
#        print('song_1 id:', song_1.pos_in_queue)
#        print('promote id:', song_to_promote.pos_in_queue)
#        db.session.commit()
#
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

    def next_song(self, requester_info):
        if not self._should_skip(requester_info):
            return 'Not enough votes to skip: {}. Need 3 total. Vote with !nextsong'.format(len(self.skippers))

        return self._next_song()

    def add_song_from_track(self, track):
        song_request = song_request_factory(SongType.Spotify, 'stroopc',
                                            track['name'], track['artist'],
                                            track['song_uri'],
                                            callback=self._next_song)
        app.logger.debug('Adding track from default playlist: {}'.format(song_request))
        self._add_to_queue(song_request)

    @check_queue_length
    def current_song(self):
        return 'Currently Playing: ' + self.queue[0].info()

    @mods
    def set_volume(self, volume_percent, requester_info=None):
        volume_percent = self._fmt_thoom_msg(volume_percent)

        cur_song = self.spotify_player
        max_volume = 50
        if len(self.queue):
            cur_song = self.queue[0]
            max_volume = cur_song.max_volume()

        matched = re.match(self.VOL_REGEX, volume_percent)
        if matched:
            volume_percent = cur_song.get_int_volume() + int(matched.group(0))

        if self._is_broadcaster(requester_info):
            volume_percent = int(volume_percent)
        else:
            volume_percent = self._clamp(int(volume_percent), 0, max_volume)

        return cur_song.set_volume(volume_percent)

    @check_queue_length
    def get_volume(self):
        return self.queue[0].get_volume()

    @mods
    def stop_playing(self, requester_info=None):
        return self._stop_playing()

    @mods
    def start_playing(self, sr=None, requester_info=None):
        return self._start_playing(sr=sr, requester_info=requester_info)

    @check_queue_length
    def _stop_playing(self, song=None):
        if not song:
            song = self.queue[0]

        app.logger.debug('Stopping playing: {}'.format(song))
        song.pause()

        return 'Stopped the music :('

    @check_queue_length
    def _start_playing(self, sr=None, requester_info=None):
        if not sr:
            app.logger.debug('Initializing sr with: {}'.format(self.queue[0]))
            sr = self.queue[0]

        sr.play()
        return 'Playing the thicc beatz'

    @check_queue_length
    def _next_song(self):
        return self._song_done()

    def _fill_queue(self):
        songs = SongRequest.query.all()
        for song in songs:
            self.queue.append(song_request_factory(song.song_type, song.requester,
                song.name, song.artist, song.link, callback=self._next_song))
            app.logger.debug("Filling queue... Added: {}".format(song))

    def _rm_song_from_db(self, song_to_del):
        try:
            with app.app_context():
                app.logger.debug('Removing {} from queue'.format(song_to_del))
                # this is run from within a thread and won't have access to the app
                # context unless this is given
                song = SongRequest.query.filter_by(link=song_to_del.link).first()

                # # songs that are added from the default playlist aren't actually
                # # added to the db since they aren't added/_ad
                # if song:
                print("db: '", db, "' song: '", song, "'")
                db.session.delete(song)
                db.session.commit()
        except sqlalchemy.orm.exc.UnmappedInstanceError as e:
            print("ERROR:", e)

    def _song_done(self):
        ''' Should only be called once per SongRequest '''
        last_song = self.queue.pop(0)
        app.logger.debug('Song finishing: {}'.format(last_song.name))
        last_song.done()

        self._rm_song_from_db(last_song)
        app.logger.debug('Removing song: {} from the queue'.format(last_song))

        self.skippers = set()

        return self._play_next_song(last_song)

    def _play_next_song(self, last_song):
        if len(self.queue) == 0:
            self._start_autoplay(last_song)
            return f"No more songs from chat, we vibin' on similar songs to {last_song.name}"
        print(f"last song was: {last_song}")

        # spotify will autoplay, so we need to stop it
        self._stop_playing(last_song)
        self._start_playing()
        return self.queue[0].info()

    def _start_autoplay(self, last_song):
        self._prep_autoplay(last_song)
        self._start_playing()

    def _prep_autoplay(self, last_song):
        track = None
        if last_song.song_type == SongType.YouTube:
            track = self.spotify_player.random_track_from_playlist()
        else:
            track = self.spotify_player.request_playback_info()

        self.add_song_from_track(track)

    def _validate_int(self, num):
        if not self.queue:
            return False, self.NO_SONGS_IN_QUEUE
        try:
            num = int(num)
        except ValueError:
            return False, "Give a valid integer"

        if num < 1 or num > len(self.queue):
            return False, 'Please give a number between 1 and {}'.format(len(self.queue))
        return True, num

    def _clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)

    def _should_skip(self, requester_info):
        if self._is_dj(requester_info):
            return True

        self.skippers.add(requester_info['username'])
        if len(self.skippers) >= 3:
            return True
        return False

    def _is_dj(self, requester_info):
        return requester_info and (requester_info['userstatuses']['is_mod']
                or requester_info['username'] == 'stroopc'
                or requester_info['userstatuses']['is_vip'])

    def _is_broadcaster(self, requester_info):
        return requester_info and requester_info['userstatuses']['is_broadcaster']

    def _check_and_start_playing(self, song_request):
        response = self._add_to_queue(song_request)

        if not self.queue:
            app.logger.error('Checked to start playing and got no queue: {}'.format(self.queue))
            return 'No queue object. Tell Stroop!'

        if self._queue_has_one_song():
            self._stop_playing()
            self._start_playing()

        return response

    def _queue_has_one_song(self):
        return len(self.queue) == self.ONE_SONG

    def _add_to_queue(self, song_request):
        with app.app_context():
            app.logger.debug('_adding_to_queue: {}'.format(song_request))
            self.queue.append(song_request)

            db.session.add(song_request)
            db.session.commit()
            return 'Added {} to position number #{}'.format(
                    song_request.info(), len(self.queue))

    def _fmt_thoom_msg(self, volume_percent):
        return self.THOOM_VOLUME if volume_percent == 'thoom' else volume_percent
