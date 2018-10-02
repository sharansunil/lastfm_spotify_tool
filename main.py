import spotifyFunctions as spot_func
from CredentialClass import SpotifyCredentials
from lastfm import LastFmGenerator
import lastfmFunctions as last_func
import pandas as pd
import warnings 

spotify_scope = 'user-library-read'
spotify_username = '1177566421'
lastfm_username = "sharansunil"
lastfm_password = "synystrax"

myCred = SpotifyCredentials(username=spotify_username, scope=spotify_scope)
LastFm = LastFmGenerator(username=lastfm_username, password=lastfm_password)


def refreshSpotify(refresh=1):
	sp = myCred.genAuth()
	spot_func.generateAllDatasets(sp,spotify_username,refresh=refresh)
	spot_func.artistSegments()
def refreshLastFm():
	network = LastFm.gen_network()
	last_func.topAlbumsArtists(network,lastfm_username)
	last_func.topTracksDB(network,lastfm_username)
def masterRefresh(x):
	refreshSpotify(x)
	refreshLastFm()
	last_func.generateMasterTrackDatabase()
	print("\n\nSpotify and LastFm datasets refreshed. All files can be found in csv's located in exports folder. Use your choice of viz software or statistical analysis package. The hard work is done. Let the fun begin!\n\n")

def exportCredentials():
	return myCred,LastFm

with warnings.catch_warnings():
	warnings.filterwarnings("ignore", category=RuntimeWarning)
	masterRefresh(0)

