#!/usr/bin/env python3.5
import os
import yaml
import isodate

from app.helpers.config import Config

from pprint import pprint

import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

class YouTubeAPI(Config):

    def __init__(self):
        super().__init__('youtube')

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and create an API client
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.config['api_key'])

    def search(self, query):
        my_response = {}

        request = self.youtube.search().list(
            part="snippet",
            maxResults=1,
            q=query,
            topicId="/m/04rlf"
        )
        response = request.execute()
        if len(response['items']) == 0:
            my_response['error'] = "Error: Could not find {}".format(query)
            return False, my_response

        # TODO: Check error condition when network errors?

        if response['items'][0]['id']['kind'] != 'youtube#video':
            return False, "Error: Not a youtube video"

        my_response['video_id'] = response['items'][0]['id']['videoId']
        my_response['title'] = response['items'][0]['snippet']['title']
        my_response['artist'] = response['items'][0]['snippet']['channelTitle']
        my_response['error'] = ''
        my_response['song_uri'] = 'https://youtube.com/watch?v='

        request = self.youtube.videos().list(
            part="contentDetails",
            id=my_response['video_id']
        )
        response = request.execute()

        # TODO: Check error condition when network errors?

        if len(response['items']) == 0:
            my_response['error'] = "Error: Could not find the details for {}".format(query)
            return False, my_response

        duration = response['items'][0]['contentDetails']['duration']

        # Check duration if it's too long
        if not self._duration_valid(duration):
            my_response['error'] = "Error: Song {} is too long".format(my_response['title'])
            return False, my_response

        my_response['song_uri'] += my_response['video_id']
        return True, my_response

    def _duration_valid(self, duration):
        return isodate.parse_duration(duration).total_seconds() < 600

if __name__ == "__main__":
    yt_api = YouTubeAPI()
    yt_api.search('https://youtu.be/18JQUYgpOlw')
