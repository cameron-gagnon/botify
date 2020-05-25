import json

from flask import request, render_template

from app.models.queue import Queue
from app.helpers.searcher import Searcher
from app.models.players.spotify import SpotifyPlayer
from app.controllers import bp as queue_bp

song_queue = Queue(Searcher(), SpotifyPlayer.instance())

@queue_bp.route('/request_song', methods=['POST'])
def request_song():
    query = request.form.get('query')
    userinfo = json.loads(request.form.get('userinfo'))

    print(userinfo)
    if not query:
        return "Type '!sr DAMN. Kendrick Lamar' to search for DAMN. by Kendrick Lamar"

    response = song_queue.request_song(query, userinfo)
    return response

@queue_bp.route('/wrong_song', methods=['POST'])
def wrong_song():
    user = request.form.get('user')
    return song_queue.remove_song(user)

@queue_bp.route('/volume', methods=['POST'])
def volume():
    volume = request.form.get('volume')
    userinfo = json.loads(request.form.get('userinfo'))
    if not volume:
        return song_queue.get_volume()

    return song_queue.set_volume(volume, requester_info=userinfo)

@queue_bp.route('/current_song', methods=['GET'])
def current_song():
    return song_queue.current_song()

@queue_bp.route('/next_song', methods=['POST'])
def next_song():
    userinfo = json.loads(request.form.get('userinfo'))
    return song_queue.next_song(userinfo)

@queue_bp.route('/playlist', methods=['GET'])
@queue_bp.route('/playlist/<offset>', methods=['GET'])
def playlist(offset=1):
    return song_queue.playlist(offset)

@queue_bp.route('/promote', methods=['POST'])
def promote():
    pos = request.form.get('pos')
    userinfo = json.loads(request.form.get('userinfo'))
    return song_queue.promote(pos, requester_info=userinfo)

@queue_bp.route('/pause', methods=['POST'])
def pause_song():
    userinfo = json.loads(request.form.get('userinfo'))
    return song_queue.stop_playing(requester_info=userinfo)

@queue_bp.route('/play', methods=['POST'])
def play_song():
    userinfo = json.loads(request.form.get('userinfo'))
    return song_queue.start_playing(requester_info=userinfo)

@queue_bp.route('/queue', methods=['GET'])
def yt_queue():
    return render_template('queue.html')
