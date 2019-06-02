import time

from app.decorators.singleton import Singleton
from app.sockets.youtube import YouTubeSockets
from flask_socketio import Namespace, emit

@Singleton
class YouTubePlayer(YouTubeSockets):

    def __init__(self):
        super().__init__('/youtube')
        self.current_song_done = False
        self.callback = None
        self.volume = 25

    def play(self, link):
        print("Emitting play")
        emit("play", {"data": link}, broadcast=True, namespace='/youtube')
        return 'Playing video!'

    def pause(self):
        print("emitting pause")
        emit("pause", {}, broadcast=True, namespace='/youtube')
        return 'Pausing video!'

    def set_volume(self, vol):
        self.volume = vol
        print("setting volume", self.volume)
        emit("set_volume", {'volume': self.volume}, broadcast=True, namespace='/youtube')
        return "Set volume to {}".format(self.volume)

    def get_volume(self):
        print("Getting volume")
        print("before volume", self.volume)
        emit("get_volume", {}, broadcast=True, namespace='/youtube')
        time.sleep(.5)
        print("After volume: ", self.volume)
        return "Volume is: {}".format(self.volume)

    def get_int_volume(self):
        return self.volume

    def set_callback(self, callback):
        self.callback = callback

    def done(self):
        print("Emitting done")
        emit("done", {}, broadcast=True, namespace='/youtube')

    ######### websocket handlers #############
    def on_volume(self, data):
        print("Got volume handler", data)
        self.volume = data['volume']

    def on_next_song(self, data):
        print('got next song', data)
        self.callback()
