import requests, psycopg2
import pandas as pd
from dotenv import dotenv_values
from rich import print, print_json

# https://colab.research.google.com/drive/1VNzOMly5cGOHLtu8g8HUzPFyuyhaikQ5#scrollTo=B_XtLnVJtcu0

config = dotenv_values(".env")
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = config['CLIENT_SECRET']
POSTGRE_PW = config['POSTGRE_PW']

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

# ADD ARTIST!
for playlist in refined_playlists:
    playlist_id = playlist['id']
    r1 = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks', 
                 headers=headers, 
                 params={'market': 'SE'})
    d = r1.json()
    for track in d['items']:
        track_info = track.get('track', None)
        if track_info:
            r2 = requests.get(BASE_URL + 'audio-features/' + track_info['id'], headers=headers)
            refined_tracks.append({'id': track_info['id'], 'name': track_info['name'], 'playlist source': playlist_id,
                                   'playlist source name': playlist['name'], 'popularity': track_info['popularity'],
                                   'danceability': r2.json().get('danceability'), 'energy level': r2.json().get('energy')})

df = pd.json_normalize(refined_tracks)

# Connect to database
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password=POSTGRE_PW, port=5432)
cur = conn.cursor()

conn.commit()

cur.close()
conn.close()