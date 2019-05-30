from app.classes.players.spotify_player import SpotifyPlayer
from app.classes.players.youtube_player import YouTubePlayer
from app.classes.requests.song_types import SongType
from app.classes.requests.spotify_request import SpotifyRequest
from app.classes.requests.youtube_request import YouTubeRequest

def song_request_factory(song_type, requester, *args, callback=None):
    if song_type == SongType.Spotify:
        return SpotifyRequest(requester, SpotifyPlayer.instance(), *args,
                callback=callback)
    elif song_type == SongType.YouTube:
        YouTubePlayer.instance().set_callback(callback)
        return YouTubeRequest(requester, YouTubePlayer.instance(), *args)
    else:
        raise 'Invalid SongRequest type'
