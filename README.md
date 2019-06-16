# TODO (in no particular order)

* Check if youtube video has more likes than dislikes
* Check if user becomes banned and clear their songs from the queue
* Remove 'by' from user's searches
* Check if a user is VIP or Mod and allow them to put more songs on the queue
* !commands with sub-commands for each additional command
* !srs "a" "b" "c" (save playlist)
* make relative volume work right after restart (fetch current volume before   adjusting, if no current volume)
* Filter search by only videos (not channels or playlists)
* add init scripts for botify and chatbot on mote
* remove extra code from music_visualization
* refactor color command to be more in python instead of JS.
* write tests for botify
* write tests for chatbot
* refactor handler/strip.py in pixelated
* do more exciting things when people follow/subscribe
* socket io error working outside of application context
** means we needed to interface with the current application object in some way. solve this, set up the application context with app.app_context(). see docs for more info

Done:
* back botify by a DB
* cap volume instead of erroring out
* Pulse the lights to the music
