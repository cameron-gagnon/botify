#!/usr/bin/env python3.5

from flask import Flask, request
from app.views.queue import queue
from app.views.error_handlers import error_handlers

app = Flask(__name__)
app.register_blueprint(queue)
app.register_blueprint(error_handlers)

app.run(debug=True, host='127.0.0.1', port=4242)
