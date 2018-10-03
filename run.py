from BaseClasses import Data_Plot_Builder
import pandas as pd
from os import listdir 


"""user specified arguments"""

scope = 'user-library-read'
sp_username = '1177566421'
lastfm_username = "sharansunil"

"""import main builder class, toggle settings accordingly"""

main=Data_Plot_Builder(lastfm_username=lastfm_username,sp_username=sp_username,scope=scope,refresh_sp=0,refresh_last_top_albums_artists=1,refresh_last_tracks_pl=1,refresh_playlists=1,refresh_artist=1)


"""set sensitive info and run create"""
#main.setPassword(input("Key in password dumbass:    "))
main.setPassword("synystrax")
main.create_all()