#!/usr/bin/env python3.5

from app import app, socketio

socketio.run(app, debug=True, host='0.0.0.0', port=4242)
#app.run(debug=True, host='0.0.0.0', port=4242)
