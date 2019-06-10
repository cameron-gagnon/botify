import unittest
from unittest import mock

from app.models.queue import Queue

@mock.patch('app.helpers.searcher', autospec=True)
class TestQueue(unittest.TestCase):

    def test_request_song_when_queue_full(self, searcher_mock):
        song_queue = Queue(searcher_mock)
        #song_queue.request_song('foo bar', 'stroopc')

#    def test_request_song_when_too_many_requests(self):
#        self.assertEqual(True, True)
#
#    def test_request_song_with_valid_youtube_link(self):
#        self.assertEqual(True, True)
#
#    def test_request_song_when_valid_spotify_song(self):
#        self.assertEqual(True, True)
#
#    def test_request_song_when_valid_youtube_song(self):
#        self.assertEqual(True, True)
#
#    def test_request_song_when_song_not_found(self):
#        self.assertEqual(True, True)
#
#    def test_request_song_when_song_already_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_request_song_when_song_not_already_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_song_already_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_song_not_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_too_many_requests(self):
#        self.assertEqual(True, True)
#
#    def test_not_too_many_requests(self):
#        self.assertEqual(True, True)
#
#    def test_remove_song(self):
#        self.assertEqual(True, True)
#
#    def test_remove_song_when_currently_playing(self):
#        self.assertEqual(True, True)
#
#    def test_remove_song_when_song_not_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_remove_song_when_no_songs_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_remove_song_when_no_songs_on_queue(self):
#        self.assertEqual(True, True)
#
#    def test_promote_song(self):
#        self.assertEqual(True, True)
#
#    def test_promote_song_when_no_songs(self):
#        self.assertEqual(True, True)
#
#    def test_promote_song_when_index_too_high(self):
#        self.assertEqual(True, True)
#
#    def test_promote_song_when_index_too_low(self):
#        self.assertEqual(True, True)
#
#    def test_promote_song_when_dj(self):
#        self.assertEqual(True, True)
#
#    def test_promote_song_when_not_dj(self):
#        self.assertEqual(True, True)
#
#    def test_playlist(self):
#        self.assertEqual(True, True)
#
#    def test_playlist_at_valid_offset(self):
#        self.assertEqual(True, True)
#
#    def test_playlist_at_invalid_offset(self):
#        self.assertEqual(True, True)
#
#    def test_next_song(self):
#        self.assertEqual(True, True)
#
#    def test_next_song_when_no_next_song(self):
#        self.assertEqual(True, True)
#
#    def test_next_song_when_dj(self):
#        self.assertEqual(True, True)
#
#    def test_next_song_when_not_dj(self):
#        self.assertEqual(True, True)
#
