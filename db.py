import psycopg2
from psycopg2 import extras
import pandas as pd
from dotenv import dotenv_values

config = dotenv_values(".env")
POSTGRE_PW = config['POSTGRE_PW']

df = pd.read_parquet("spotify_final.parquet")

# Connect to database
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password=POSTGRE_PW, port=5432)
cur = conn.cursor()

# First, ensure the artist table is defined:
cur.execute("""
CREATE TABLE IF NOT EXISTS artist (
    artistID VARCHAR(22) PRIMARY KEY,
    name VARCHAR(255)
)
""")

# Then, define the track table with a foreign key reference:
cur.execute("""
CREATE TABLE IF NOT EXISTS track (
    trackID VARCHAR(22) PRIMARY KEY,
    artistID VARCHAR(22),
    name VARCHAR(255),
    popularity INT,
    danceability FLOAT,
    energyLevel FLOAT,
    playlistSources TEXT[],
    playlistOccurrences INT,
    FOREIGN KEY (artistID) REFERENCES artist(artistID) -- Adding foreign key relationship; maintaining referential integrity within the database
)
""")

# for index, row in df.iterrows():
#     cur.execuse("""
#                 INSERT INTO track (trackID, artistID, popularity, danceability, 
#                 energyLevel, playylistSources, playlistOccurances) VALUES
#                 (row['id'], row['artist id'], row['popularity'], row['danceability'],
#                 row['energy level'], row['playlist sources'], row['playlist occurances'])
#                 """)

# Insert data into the artist table first
artist_data_to_insert = df[['artist id', 'artist']].drop_duplicates().values.tolist()
extras.execute_batch(cur, """
                     INSERT INTO artist (artistID, name) VALUES
                     (%s, %s)
                     ON CONFLICT (artistID) DO NOTHING
                     """, artist_data_to_insert)
conn.commit()  # Commit after inserting into artist

# Prepare and insert data into the track table
track_data_to_insert = [
    (
        row['id'],
        row['artist id'],
        row['name'],
        int(row['popularity']),
        float(row['danceability']),
        float(row['energy level']),
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