from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

from .views.queue import queue
from .views.error_handlers import error_handlers
from .sockets.youtube import YouTubeSockets

app.register_blueprint(queue)
app.register_blueprint(error_handlers)

socketio = SocketIO(app)

socketio.on_namespace(YouTubeSockets('/youtube'))
