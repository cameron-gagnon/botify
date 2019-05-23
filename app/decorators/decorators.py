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

