import requests
import pandas as pd
from dotenv import dotenv_values
from rich import print, print_json

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

# get the 5 most popular playlists in Sweden right now
r = requests.get(BASE_URL + 'browse/featured-playlists', 
                 headers=headers, 
                 params={'locale': 'sv_SE', 'limit': 5})
d = r.json()

# print(d)

refined_playlists = []
for playlist in d['playlists']['items']:
    refined_playlists.append({'id': playlist['id'], 'name': playlist['name'], 
                              'description': playlist['description'], 'tracks': playlist['tracks']['total']})

print(refined_playlists)

# get the songs from the playlists
playlist_id = refined_playlists[1]['id']
print(playlist_id)

r = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks', 
                 headers=headers, 
                 params={'market': 'SE'})
d = r.json()

print(len(d['items']))
# print(d['items'])

refined_tracks = []
for track in d['items']:
    track_info = track.get('track', None)
    if track_info:
        refined_tracks.append({'id': track_info['id'], 'name': track_info['name'], 
                              'popularity': track_info['popularity']})

# print(refined_tracks)

# enrich every track with danceability and energy that we can get from the audio-features endpoint
for track in refined_tracks:
    r = requests.get(BASE_URL + 'audio-features/' + track['id'], headers=headers)
    track['danceability'] = r.json().get('danceability')
    track['energy level'] = r.json().get('energy')

print(refined_tracks)