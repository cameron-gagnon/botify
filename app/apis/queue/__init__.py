from flask import Blueprint, request, render_template

bp = Blueprint('queue', __name__, template_folder='templates')

from app.apis.queue import queue
