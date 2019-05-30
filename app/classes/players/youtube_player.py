from app.decorators.singleton import Singleton
from app.sockets.youtube import YouTubeSockets
from flask_socketio import Namespace, emit

@Singleton
class YouTubePlayer(YouTubeSockets):

    def __init__(self):
        super().__init__('/youtube')
        self.current_song_done = False
        self.callback = None

    def play(self, link):
        print("Emitting play")
        emit("play", {"data": link}, broadcast=True, namespace='/youtube')

    def pause(self):
        print("emitting pause")
        emit("pause", {}, broadcast=True, namespace='/youtube')

    def set_volume(self, vol):
        pass

    def get_volume(self):
        pass

    def set_callback(self, callback):
        self.callback = callback

    def done(self):
        print("Emitting done")
        emit("done", {}, broadcast=True, namespace='/youtube')

    # websocket handler
    def on_next_song(self, data):
        print('got next song', data)
        self.callback()
