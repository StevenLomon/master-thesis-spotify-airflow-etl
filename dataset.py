import requests
import pandas as pd
from dotenv import dotenv_values
from rich import print, print_json

# https://colab.research.google.com/drive/1VNzOMly5cGOHLtu8g8HUzPFyuyhaikQ5#scrollTo=B_XtLnVJtcu0

config = dotenv_values(".env")
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = config['CLIENT_SECRET']

AUTH_URL = 'https://accounts.spotify.com/api/token'
redirect_uri = 'http://localhost:8888/callback'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

artist_id = '36QJpDe2go2KgaRleHCDTp'

# get the 50 most popular featured playlists in Sweden right now
r = requests.get(BASE_URL + 'browse/featured-playlists',
                 headers=headers,
                 params={'q': 'top%20%20tracks', 'type': 'playlist', 
                         'market': 'SE', 'limit': 50})
d = r.json()

refined_playlists = []
for playlist in d['playlists']['items']:
    refined_playlists.append({'id': playlist['id'], 'name': playlist['name'],
                              'description': playlist['description'], 'tracks': playlist['tracks']['total']})

# collect all tracks from all the playlists and enrich with audio features danceability and energy level
refined_tracks = []

for playlist in refined_playlists:
    playlist_id = playlist['id']
    r1 = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks',
                 headers=headers,
                 params={'market': 'SE'})
    d = r1.json()
    try:
        for track in d['items']:
            track_info = track.get('track', None)
            if track_info:
                r2 = requests.get(BASE_URL + 'audio-features/' + track_info['id'], headers=headers)
                refined_tracks.append({'id': track_info['id'], 'name': track_info['name'], 'artist': track_info['artists'][0]['name'],
                                      'artist id': track_info['artists'][0]['id'], 'playlist source name': playlist['name'],
                                      'playlist id': playlist_id, 'popularity': track_info['popularity'],
                                      'danceability': r2.json().get('danceability'), 'energy level': r2.json().get('energy')})
    except:
        pass

df = pd.json_normalize(refined_tracks)