import spotifyFunctions as spot_func
from CredentialClass import SpotifyCredentials,LastFmCredentials
import lastfmFunctions as last_func
import pandas as pd
import warnings


spotify_scope = 'user-library-read'
spotify_username = '1177566421'
lastfm_username = "sharansunil"
lastfm_password = "synystrax"

Spotify = SpotifyCredentials(username=spotify_username, scope=spotify_scope)
LastFm = LastFmCredentials(username=lastfm_username, password=lastfm_password)

sp = Spotify.genAuth()
network=LastFm.gen_network()


with warnings.catch_warnings():
	warnings.filterwarnings("ignore", category=RuntimeWarning)
	try:
		spot_func.generateAllDatasets(sp, spotify_username, refresh=1)
		last_func.generateCombinedDatabases(network, lastfm_username, refresh=1)
		print("success")
	except Exception as e:
		print("failed because of \n" + e)

print("OH HI MARK")

