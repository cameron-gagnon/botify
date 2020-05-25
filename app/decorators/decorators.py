from spotipy.client import SpotifyException
from requests.exceptions import ConnectionError

def handle_infinite_loop(fn):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return fn(*args, **kwargs)
            except ConnectionError as e:
                print("Connection Error", e)

    return wrapper

def handle_refresh(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except SpotifyException:
            print("Refreshing auth token")
            args[0]._refresh()
            return fn(*args, **kwargs)
    return wrapper

def handle_500(fn):
    def wrapper(*args, **kwargs):
        try:
            return True, fn(*args, **kwargs)
        except SpotifyException:
            return False, None
    return wrapper


def check_queue_length(fn):
    def wrapper(*args, **kwargs):
        if len(args[0].queue) == 0:
            return args[0].NO_SONGS_IN_QUEUE

        return fn(*args, **kwargs)
    return wrapper

def mods(fn):
    def wrapper(*args, **kwargs):
        if not args[0]._is_dj(kwargs['requester_info']):
            return "Sorry, only DJs can perform this action"

        return fn(*args, **kwargs)
    return wrapper
