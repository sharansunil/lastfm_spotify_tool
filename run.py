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
	sp_username=sp_username, 
	refresh_last_top_albums_artists=1, #refresh top artists and albums dataset from lastfm: no recommendation, up to user 
	refresh_last_tracks_pl=1,#refresh last fm tracks and generates master dataset: recommended at 1
	refresh_spotify=1, #refresh spotify database. time and data intensive. recommended at 0 adhoc refresh
	refresh_playlists=1, #refresh playlist plots. recommended at 0 adhoc refresh
	refresh_artist=1#refresh artist distribution plots recommended at 0 adhoc refresh
)

"""set password by input instance or fix it in code, up to you"""
#main.setPassword(input("Key in password dumbass:    "))
main.setPassword("synystrax")

"""run file"""
main.create_all()
