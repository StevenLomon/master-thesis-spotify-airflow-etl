import requests, re, aiohttp, asyncio, time, random, psycopg2
import pandas as pd
from dotenv import dotenv_values

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


df = pd.read_csv("spotify_tracks.csv")

# Enrich df with danceability and energy level
async def fetch_feature(session, track_id):
    async with session.get(BASE_URL + 'audio-features/' + track_id, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return {
                'id': track_id,
                'danceability': data.get('danceability'),
                'energy': data.get('energy')
            }
        else:
            return {
                'id': track_id,
                'danceability': None,
                'energy': None
            }
        time.sleep(random.randint(1,3))

async def main(track_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feature(session, track_id) for track_id in track_ids]
        results = await asyncio.gather(*tasks)
        return pd.DataFrame(results)

# Run the async event loop
features_df = asyncio.run(main(df['id'].tolist()))

# Merge results
df = df.merge(features_df, on='id', how='left')

# Fill NaN values for 'danceability' and 'energy level' by the mean value of the same track if available
df['danceability'] = df.groupby('id')['danceability'].transform(lambda x: x.fillna(x.mean()))
df['energy level'] = df.groupby('id')['energy level'].transform(lambda x: x.fillna(x.mean()))

# Group by the unique track ID
df_aggregated = df.groupby('id').agg({
    'name': 'first',  # We can safely use 'first' since 'id' guarantees uniqueness
    'artist': 'first',
    'artist id': 'first',
    'popularity': 'first',
    'danceability': 'mean',  # Average danceability if there's variation
    'energy level': 'mean',  # Average energy level if there's variation
    'playlist source name': lambda x:list(set(x))  # Compile all playlist names into a list
}).reset_index()

# Rename the column for clarity
df_aggregated.rename(columns={'playlist source name': 'playlist sources'}, inplace=True)

# Column with occurance count
df_aggregated['playlist occurrences'] = df_aggregated['playlist sources'].apply(len)

# Download as parquet file
df_aggregated.to_parquet('spotify_final.parquet')