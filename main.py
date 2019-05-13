#!/usr/bin/env python3.5

from app.botify import SpotifyPlayer
from flask import Flask, request

app = Flask(__name__)

spot = SpotifyPlayer()
@app.route('/request_song', methods=['POST'])
def request_song():
    query = request.form.get('query')
    if not query:
        print("No query!")
        return 'No query'

    response = spot.request_song(query)
    return response

app.run(debug=False, host='127.0.0.1', port = 4242)
