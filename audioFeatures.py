import pandas as pd
import numpy as np
import itertools
import getPlaylists as gp
import spotifyInit as spi
import itertools

#import token
token=spi.token

#various slices
trackColumns = ['Trackname', 'TrackID']
albumColumns = ['Album', 'AlbumID']
artistColumns = ['Artist', 'ArtistID']
playlistColumns = ['Playlist', 'PlaylistID']

#generate token for playlist read
sp = gp.init()

#generate dataset with playlist,album,artist,track info
dfo= gp.generateRefSet(sp)

#slice set based on preference
trackSet=gp.sliceRefSet(dfo,trackColumns)

featureSet=gp.generateFeatureSet(trackSet)

print (featureSet)