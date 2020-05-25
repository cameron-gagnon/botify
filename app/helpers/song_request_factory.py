from app.models.players.spotify import SpotifyPlayer
from app.models.players.youtube import YouTubePlayer
from app.models.song_requests.song_types import SongType
from app.models.song_requests.spotify import SpotifyRequest
from app.models.song_requests.youtube import YouTubeRequest

def song_request_factory(song_type, requester, *args, callback=None):
    if song_type == SongType.Spotify:
        return SpotifyRequest(requester, SpotifyPlayer.instance(), *args,
                callback=callback)
    elif song_type == SongType.YouTube:
        YouTubePlayer.instance().set_callback(callback)
        return YouTubeRequest(requester, YouTubePlayer.instance(), *args)
    else:
        raise 'Invalid SongRequest type Specified. Please give either YouTube or Spotify song request types'
