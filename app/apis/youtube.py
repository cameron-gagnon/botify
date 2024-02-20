from pprint import pprint
import isodate
import os
import re
import requests
import urllib.parse as urlparse
import yaml

import googleapiclient.discovery
import googleapiclient.errors

from app.helpers.configs.config import Config


class YouTubeAPI(Config):

    TEST_LINK_ENDPOINT = "http://www.youtube.com/oembed?format=json&url={}"
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
    LINK_REGEX = '\/([^\/]+)\?'

    def __init__(self):
        super().__init__('youtube')

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and create an API client
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.config['api_key'],
            cache_discovery=False)

    def is_valid_link(self, link):
        my_response = {}
        r = requests.get(self.TEST_LINK_ENDPOINT.format(link))
        if r.status_code == 200:
            response = r.json()
            my_response['artist'] = response['author_name']
            my_response['name'] = response['title']
            my_response['song_uri'] = self.clean_link(link)

            return True, my_response

        return False, my_response

    def clean_link(self, link):
        base_link = "https://youtube.com/watch?v={}"
        v_id = self._parse_v_id_from_link(link)
        if not v_id:
            matched = re.match(self.LINK_REGEX, link)
            if matched:
                v_id = matched.group(0)
                print('matched v_id is', v_id)

        # probably a shortened link with/without '?t=xx' on it
        if not v_id:
            print('no v_id', v_id)
            last_slash_idx = link.rfind('/')
            first_question_mark = link.find('?')
            if first_question_mark == -1:
                v_id = link[last_slash_idx+1:]
            else:
                v_id = link[last_slash_idx+1:first_question_mark]
            print('vid is')

        return base_link.format(v_id)

    def _parse_v_id_from_link(self, link):
        parsed = urlparse.urlparse(link)
        # default's to mt. joy sheep if an improperly formatted link was given
        return urlparse.parse_qs(parsed.query).get('v', [None])[0]

    def _is_short_link(self, link):
        return 'youtu.be' in link

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
            pprint(response)
            my_response['error'] = "Error: Not a youtube video"
            return False, my_response

        my_response['video_id'] = response['items'][0]['id']['videoId']
        my_response['name'] = response['items'][0]['snippet']['title']
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
            my_response['error'] = "Error: Song {} is too long".format(my_response['name'])
            return False, my_response

        my_response['song_uri'] += my_response['video_id']
        return True, my_response

    def _duration_valid(self, duration):
        return isodate.parse_duration(duration).total_seconds() < 600

if __name__ == "__main__":
    yt_api = YouTubeAPI()
    #yt_api.search('https://youtu.be/18JQUYgpOlw')
    yt_api.is_valid_link('https://youtu.be/18JQUYgpOlw')
