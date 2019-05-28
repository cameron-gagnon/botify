from flask_socketio import Namespace, emit

class YouTubeSockets(Namespace):

    def on_connect(self):
        print("Connected")

    def on_disconnect(self):
        print("Got disconnect")

    def on_my_event(self, data):
        print('my data', data)
