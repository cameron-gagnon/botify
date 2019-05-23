from ..classes.queue import Queue

from flask import Blueprint, request

queue = Blueprint('queue', __name__, template_folder='templates')
song_queue = Queue()

@queue.route('/request_song', methods=['POST'])
def request_song():
    query = request.form.get('query')
    user = request.form.get('user')
    if not query:
        return "Type '!sr DAMN. Kendrick Lamar' to search for DAMN. by Kendrick Lamar"

    response = song_queue.request_song(query, user)
    return response

@queue.route('/wrong_song', methods=['POST'])
def wrong_song():
    user = request.form.get('user')
    return song_queue.remove_song(user)

@queue.route('/volume', methods=['POST'])
def volume():
    volume = request.form.get('volume')
    if not volume:
        return song_queue.get_volume()
    return song_queue.volume(volume)

@queue.route('/current_song', methods=['GET'])
def current_song():
    return song_queue.current_song()

@queue.route('/next_song', methods=['POST'])
def next_song():
    user = request.form.get('user')
    return song_queue.next_song(user)

@queue.route('/playlist', methods=['GET'])
@queue.route('/playlist/<offset>', methods=['GET'])
def playlist(offset=1):
    return song_queue.playlist(offset)

@queue.route('/promote', methods=['GET'])
@queue.route('/promote/<offset>', methods=['GET'])
def promote(offset=0):
    return song_queue.promote(offset)

@queue.route('/pause', methods=['GET'])
def pause_song():
    return song_queue.stop_playing()

@queue.route('/play', methods=['GET'])
def play_song():
    return song_queue.start_playing()
