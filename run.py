from BaseClasses import Spotify_LastFM_Builder
import pandas as pd
#set user specific variables as needed.prompt for lastfm password is later
sp_username = '1177566421'
lastfm_username = "sharansunil"

"""initializes main builder class"""
spotify_fm = Spotify_LastFM_Builder(	
	lastfm_username=lastfm_username, 
	sp_username=sp_username)

"""set last fm password"""
spotify_fm.setPassword("synystrax")

"""updates spotify and lastfm datasets. toggle settings as needed"""
spotify_fm.update_datasets(
	##spotify refreshers - recommended to set at 0
	refresh_spotify=0,
	refresh_artist_viz=0,
	refresh_playlist_viz=0,
	##lastfm refreshers - recommended to set at 1
	lastfm_artistalbum=1,
	lastfm_tracks=1
	)

spotify_fm.top100_to_df()

retdict=spotify_fm.load_datasets()

retdict.keys()

top100=retdict["top100"]
tracks=retdict["tracks"]
playlist=retdict["playlist"]

top100.head()