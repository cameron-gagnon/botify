from ..models.botify import SpotifyPlayer

from flask import Blueprint, request

botify = Blueprint('botify', __name__, template_folder='templates')
spot = SpotifyPlayer()

@botify.route('/request_song', methods=['POST'])
def request_song():
    query = request.form.get('query')
    if not query:
        print("No query!")
        return 'No query'

    response = spot.request_song(query)
    return response

@botify.route('/volume', methods=['POST'])
def volume():
    volume = request.form.get('volume')
    if not volume:
        return spot.get_volume()
    return spot.volume(volume)
