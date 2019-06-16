#!/usr/bin/env python

from app import create_app, db
from app.models.requests.song_request import SongRequest

app, socketio = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'SongRequest': SongRequest}

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)
