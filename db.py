import psycopg2
from psycopg2 import extras
import pandas as pd
from dotenv import dotenv_values

config = dotenv_values(".env")
POSTGRE_PW = config['POSTGRE_PW']

df = pd.read_parquet("spotify_final.parquet")

# Connect to database
try:
    conn = psycopg2.connect(
        host="192.168.1.225",
        dbname="postgres",
        user="postgres",
        password=POSTGRE_PW,
        port=5432
    )
    print("Connection successful")
except Exception as e:
    print(f"Error: {e}")
cur = conn.cursor()

# First, ensure all the dimension tables are defined:
cur.execute("""
CREATE TABLE IF NOT EXISTS artist (
    artistID VARCHAR(22) PRIMARY KEY,
    name VARCHAR(255),
    popularity INT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS album (
    albumID VARCHAR(22) PRIMARY KEY,
    name VARCHAR(255),
    releaseDate TIMESTAMP,
    popularity INT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS trackFeatures (
    trackID VARCHAR(22) PRIMARY KEY,
    danceability FLOAT,
    energyLevel FLOAT,
    instrumentalness FLOAT, 
    liveness FLOAT, 
    loudness FLOAT, 
    speechiness FLOAT, 
    tempo FLOAT, 
    duration_ms FLOAT, 
    time_signature FLOAT
)
""")

# Then, define the track table with a foreign key reference:
cur.execute("""
CREATE TABLE IF NOT EXISTS track (
    trackID VARCHAR(22) PRIMARY KEY,
    artistID VARCHAR(22),
    albumID VARCHAR(22),
    name VARCHAR(255),
    popularity INT,
    genres TEXT[],
    playlistSources TEXT[],
    playlistOccurences INT,
    FOREIGN KEY (artistID) REFERENCES artist(artistID), # Adding foreign key relationship; maintaining referential integrity within the database
    FOREIGN KEY (albumID) REFERENCES album(albumID),
    FOREIGN KEY (trackID) REFERENCES trackFeatures(trackID)
)
""")

# Insert data into the dimension tables first
artist_data_to_insert = df[['artist id', 'artist', 'artist popularity']].drop_duplicates().values.tolist()
extras.execute_batch(cur, """
                     INSERT INTO artist (artistID, name, popularity) VALUES
                     (%s, %s, %s)
                     ON CONFLICT (artistID) DO NOTHING
                     """, artist_data_to_insert)

album_data_to_insert = df[['album id', 'album', 'album release date', 'album popularity']].drop_duplicates().values.tolist()
extras.execute_batch(cur, """
                     INSERT INTO album (albumID, name, releaseDate, popularity) VALUES
                     (%s, %s, %s, %s)
                     ON CONFLICT (albumID) DO NOTHING
                     """, album_data_to_insert)

track_features_data_to_insert = df[['id', 'danceability', 'energy level', 'instrumentalness',
                                    'liveness', 'loudness', 'speechiness', 'tempo',
                                    'tempo_ms', 'time signature']].drop_duplicates().values.tolist()
extras.execute_batch(cur, """
                     INSERT INTO trackFeatures (trackID, danceability, energyLevel, instrumentalness,
                                                liveness, loudness, speechiness, tempo, 
                                                tempo_ms, timeSignature) VALUES
                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON CONFLICT (trackID) DO NOTHING
                     """, track_features_data_to_insert)
conn.commit()  # Commit after inserting into dimension tables

# Prepare and insert data into the track table
track_data_to_insert = [
    (
        row['id'],
        row['artist id'],
        row['album id'],
        row['name'],
        int(row['popularity']),
        row['genres'],  
        row['playlist sources'],  
        int(row['playlist occurrences'])
    )
    for index, row in df.iterrows()
]

extras.execute_batch(cur, """
                     INSERT INTO track (trackID, artistID, name, popularity, danceability,
                     energyLevel, playlistSources, playlistOccurrences) VALUES
                     (%s, %s, %s, %s, %s, %s, %s, %s)
                     """, track_data_to_insert)
conn.commit()  # Commit after inserting into track

# Clean up
cur.close()
conn.close()