from flask import Flask
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.configs.database import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    # Queue needs the app context to be filled on __init__
    with app.app_context():
        from app.apis.queue import bp as queue_bp

    from app.errors import bp as errors_bp
    from app.players.youtube import YouTubePlayer

    app.register_blueprint(queue_bp)
    app.register_blueprint(errors_bp)

    socketio = SocketIO(app)
    socketio.on_namespace(YouTubePlayer.instance())

    return app, socketio
