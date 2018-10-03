from BaseClasses import Data_Plot_Builder
import pandas as pd
from os import listdir 


"""user specified arguments"""
scope = 'user-library-read'
sp_username = '1177566421'
lastfm_username = "sharansunil"

"""import main builder class, toggle settings accordingly"""
main=Data_Plot_Builder(lastfm_username=lastfm_username,sp_username=sp_username,scope=scope,refresh_sp=0,refresh_last=0,refresh_playlists=1,refresh_artist=0)


"""set sensitive info and run create"""
#main.setPassword(input("Key in password dumbass:    "))
main.setPassword("synystrax")
main.create_all()

"""get names of all csv files in list"""
masterTracks=pd.read_csv("exports/MasterTrackDatabase.csv",index_col="date_added").sort_index(ascending=False)
masterPlaylist=pd.read_csv("exports/MasterPlaylistDatabase.csv",index_col="playlist")

