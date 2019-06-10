from flask import Flask
from flask_socketio import SocketIO

def create_app():
    app = Flask(__name__)

    from app.apis.queue import bp as queue_bp
    from app.errors import bp as errors_bp
    from app.players.youtube import YouTubePlayer

    app.register_blueprint(queue_bp)
    app.register_blueprint(errors_bp)

    socketio = SocketIO(app)
    socketio.on_namespace(YouTubePlayer.instance())

    return app, socketio
