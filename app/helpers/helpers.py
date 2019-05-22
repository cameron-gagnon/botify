#!/usr/bin/env python3.5

def handle_refresh(func):
    def wrapper():
        try:
            func()
        except spotipy.client.SpotifyException:
            print("Refreshing auth token")
            self._refresh()
            func()

    return wrapper
