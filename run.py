from BaseClasses import Spotify_LastFM_Builder
import pandas as pd
from os import listdir 


"""user specified arguments"""

scope = 'user-library-read'
sp_username = '1177566421'
lastfm_username = "sharansunil"

"""import main builder class and toggle settings accordingly:
refresh_sp = 0/1 to refresh spotify data
refresh_playlists = 0/1 to generate spotify playlist svg
refresh_artist = 0/1 to generate artist profiles from spotify
refresh_last_top_albums_artists = 0/1 to refresh and generate top artist and albums from lastfm
refresh_last_tracks_pl =0/1 to refresh all lastfm track data and generate master databases """

main = Spotify_LastFM_Builder(lastfm_username=lastfm_username, sp_username=sp_username, scope=scope, refresh_spotify=0,
							  refresh_last_top_albums_artists=1, refresh_last_tracks_pl=1, refresh_playlists=1, refresh_artist=1)

"""set sensitive info and run create"""
#main.setPassword(input("Key in password dumbass:    "))
main.setPassword("synystrax")
main.create_all()
