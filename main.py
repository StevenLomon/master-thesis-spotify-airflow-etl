import requests, rich
import pandas as pd
from dotenv import dotenv_values

config = dotenv_values(".env")
client_ID = config['CLIENT_ID']
print(client_ID)