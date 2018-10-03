from BaseClasses import Spotify_LastFM_Builder
import pandas as pd
from os import listdir 


#set user specific variables as needed.prompt for lastfm password is later
sp_username = '1177566421'
lastfm_username = "sharansunil"


"""creates main object to generate datasets and plots. all binary variables default to 1. scope is already set to user-library-read.
set all variables to 1 if generating for the first time"""
main = Spotify_LastFM_Builder(	
	lastfm_username=lastfm_username, 
	sp_username=sp_username
)

"""set password by input instance or fix it in code, up to you"""
main.setPassword("synystrax")

"""update dataset"""
main.update_datasets(
	##spotify refreshers - recommended to set at 0
	refresh_spotify=0,
	refresh_artist_viz=1,
	refresh_playlist_viz=0,
	##lastfm refreshers - recommended to set at 1
	lastfm_artistalbum=1,
	lastfm_tracks=1
	)

"""	load datasets. if both options set to 1 will return as dictionary with playlist and tracks as keys
	default state: """
df=main.load_datasets(playlist=1,tracks=1)