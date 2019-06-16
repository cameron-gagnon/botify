from flask import request, render_template

from app.models.queue import Queue
from app.helpers.searcher import Searcher
from app.apis.queue import bp as queue_bp

song_queue = Queue(Searcher())

@queue_bp.route('/request_song', methods=['POST'])
def request_song():
    query = request.form.get('query')
    user = request.form.get('user')
    if not query:
        return "Type '!sr DAMN. Kendrick Lamar' to search for DAMN. by Kendrick Lamar"

    response = song_queue.request_song(query, user)
    return response

@queue_bp.route('/wrong_song', methods=['POST'])
def wrong_song():
    user = request.form.get('user')
    return song_queue.remove_song(user)

@queue_bp.route('/volume', methods=['POST'])
def volume():
    volume = request.form.get('volume')
    if not volume:
        return song_queue.get_volume()
    return song_queue.set_volume(volume)

@queue_bp.route('/current_song', methods=['GET'])
def current_song():
    return song_queue.current_song()

@queue_bp.route('/next_song', methods=['POST'])
def next_song():
    user = request.form.get('user')
    return song_queue.next_song(user)

@queue_bp.route('/playlist', methods=['GET'])
@queue_bp.route('/playlist/<offset>', methods=['GET'])
def playlist(offset=1):
    return song_queue.playlist(offset)

@queue_bp.route('/promote', methods=['POST'])
def promote():
    pos = request.form.get('pos')
    user = request.form.get('user')
    return song_queue.promote(user, pos)

@queue_bp.route('/pause', methods=['GET'])
def pause_song():
    return song_queue.stop_playing()

@queue_bp.route('/play', methods=['GET'])
def play_song():
    return song_queue.start_playing()

@queue_bp.route('/queue', methods=['GET'])
def yt_queue():
    return render_template('queue.html')
