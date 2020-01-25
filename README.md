Create a `config.yml` in the root of the project with these keys and add the
values to them:
```yaml
youtube:
  api_key:

# get some of these values from https://developer.spotify.com/dashboard/applications
spotify:
  username:
  playlist:
  scope:
  client_id:
  client_secret:
  redirect_uri:
```


# TODO (in no particular order)

* Check if youtube video has more likes than dislikes
* Check if user becomes banned and clear their songs from the queue
* Admin commands: !clear, !close, !open, !delete #{}
* Remove 'by' from user's searches
* !commands with sub-commands for each additional command
* !srs "a" "b" "c" (save playlist)
* make relative volume work right after restart (fetch current volume before   adjusting, if no current volume)
* Filter search by only videos (not channels or playlists)
* remove extra code from music_visualization
* refactor color command to be more in python instead of JS.
* write tests for botify
* write tests for chatbot
* refactor handler/strip.py in pixelated
* do more exciting things when people follow/subscribe

Done:
* back botify by a DB
* Pulse the lights to the music
* If volume is over or under the limit, cap it at the limit instead of erroring
* add init scripts for botify and chatbot on mote
* socket io error working outside of application context
* Check if a user is VIP or Mod and allow them to put more songs on the queue

## Notes on how to migrate the db
FLASK_APP=main.py flask db init # one time thing
FLASK_APP=main.py flask db migrate
FLASK_APP=main.py flask db upgrade
