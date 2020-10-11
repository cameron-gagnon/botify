import gevent
from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

import logging
logging.getLogger("spotipy").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from app.helpers.configs.database import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)

    logging.basicConfig(filename='debug.log', level=logging.DEBUG,
                        format=("%(asctime)s %(levelname)s %(name)s"
                                "%(threadName)s : %(message)s"))
    app.config.from_object(config_class)
    app.logger.debug('Starting application')

    db.init_app(app)
    migrate.init_app(app, db)

    # Queue needs the app context to be filled on __init__
    with app.app_context():
        db.create_all()
        from app.controllers import bp as queue_bp

    from app.helpers.errors import bp as errors_bp
    from app.models.players.youtube import YouTubePlayer

    app.register_blueprint(queue_bp)
    app.register_blueprint(errors_bp)

    socketio = SocketIO(app, async_mode='gevent', message_queue='redis://localhost:6379/0')
    socketio.on_namespace(YouTubePlayer.instance())

    return app, socketio
