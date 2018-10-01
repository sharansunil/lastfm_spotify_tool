import SpotifyFunctions as spot_func
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


sp = myCred.genAuth()
network=LastFm.gen_network()
###toggle between 1 and 0: 1 to refresh, 0 to skip
spot_func.generateAllDatasets(sp,spotify_username,refresh=0)
spot_func.artistSegments()

lastfm_dic=last_func.makeAllLastFm(network,lastfm_username)










