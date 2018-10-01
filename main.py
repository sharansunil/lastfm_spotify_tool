import spotifyFunctions as spot_func
from CredentialClass import SpotifyCredentials
from lastfm import LastFmGenerator
import lastfmFunctions as last_func
import pandas as pd

spotify_scope = 'user-library-read'
spotify_username = '1177566421'
lastfm_username = "sharansunil"
lastfm_password = "synystrax"

myCred = SpotifyCredentials(username=spotify_username, scope=spotify_scope)
LastFm = LastFmGenerator(username=lastfm_username, password=lastfm_password)


###toggle between 1 and 0: 1 to refresh, 0 to skip
def refreshSpotify(refresh=0):
	sp = myCred.genAuth()
	spot_func.generateAllDatasets(sp,spotify_username,refresh=refresh)
	spot_func.artistSegments()

def refreshLastFm():
	network = LastFm.gen_network()
	last_func.topAlbumsArtists(network,lastfm_username)
	last_func.topTracksDB(network,lastfm_username)

#refreshSpotify()
#refreshLastFm()

df=last_func.generateMasterTrackDatabase()
df.head()