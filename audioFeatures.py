import pandas as pd
import numpy as np
import getPlaylists as gp
import spotifyInit as spi

#import token
token = spi.token

df = gp.generateMaster()
writeDf = df.to_csv('playlistDB.csv')
fields = list(df)

playlistAnalysis = df.groupby(["Playlist"])['valence', 'energy', 'acousticness', 'speechiness','tempo','danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)

fields

