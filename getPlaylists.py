import spotifyInit as spi 
import pandas as pd
import numpy as np
import itertools

sp= spi.genAuth()


spo = sp[0]
username = sp[1]
playlists = spo.user_playlists(username)

trackColumns=['Trackname','TrackID']
albumColumns=['Album','AlbumID']
artistColumns =['Artist','ArtistID']
playlistColumns=['Playlist','PlaylistID']

def generateRefSet():
	playlistarray=[]
	for playlist in playlists['items']:
		playname=playlist['name']
		playid=playlist['id']
		results = spo.user_playlist(username,playlist['id'],fields="tracks,next")
		tracks=results['tracks']
		x=spi.show_tracks(playname,playid,tracks)
		playlistarray.append(x)
	plArray=list(itertools.chain(*playlistarray))

	referenceDataset=pd.DataFrame(data=plArray,columns=['Playlist','PlaylistID','Artist','ArtistID','Album','AlbumID','Trackname','TrackID'])
	referenceDataset.index.name = 'ID'
	return referenceDataset

df=generateRefSet()

