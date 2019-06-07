from app.models.players.spotify_player import SpotifyPlayer
from app.models.players.youtube_player import YouTubePlayer
from app.models.requests.song_types import SongType
from app.models.requests.spotify_request import SpotifyRequest
from app.models.requests.youtube_request import YouTubeRequest

def song_request_factory(song_type, requester, *args, callback=None):
    if song_type == SongType.Spotify:
        return SpotifyRequest(requester, SpotifyPlayer.instance(), *args,
                callback=callback)
    elif song_type == SongType.YouTube:
        YouTubePlayer.instance().set_callback(callback)
        return YouTubeRequest(requester, YouTubePlayer.instance(), *args)
    else:
        raise 'Invalid SongRequest type'
