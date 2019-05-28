from app.classes.requests.spotify_request import SpotifyRequest
from app.classes.requests.youtube_request import YouTubeRequest
from app.classes.players.youtube_player import YouTubePlayer
from app.classes.players.spotify_player import SpotifyPlayer
from app.classes.song_types import SongType

def song_request_factory(song_type, requester, *args, callback=None):
    if song_type == SongType.Spotify:
        return SpotifyRequest(requester, SpotifyPlayer.instance(), *args,
                callback=callback)
    elif song_type == SongType.YouTube:
        return YouTubeRequest(requester, YouTubePlayer.instance(), *args)
    else:
        raise 'Invalid SongRequest type'
