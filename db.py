import psycopg2
import pandas as pd
from dotenv import dotenv_values

config = dotenv_values(".env")
POSTGRE_PW = config['POSTGRE_PW']

df = pd.read_csv("spotify_tracks_final.csv")

# Connect to database
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password=POSTGRE_PW, port=5432)
cur = conn.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS track (
            trackID VARCHAR(22),
            artistID VARCHAR(22),
            popularity INT,
            danceability FLOAT(3),
            energyLevel FLOAT(3),
            playlistSources VARCHAR(255) ARRAY,
            playlistOccurances INT
            )
            """)

conn.commit()

cur.close()
conn.close()