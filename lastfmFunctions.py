##############LASTFM
import pandas as pd
import pylast
import sys
import itertools
import datetime
import numpy as np

TRACK_SEPARATOR = u" - "

def unicode_track_and_timestamp(track):
	unicode_track = str(track.track)
	return track.playback_date + "\t" + unicode_track


def split_artist_track(artist_track):
	artist_track = artist_track.replace(u" – ", " - ")
	artist_track = artist_track.replace(u"“", "\"")
	artist_track = artist_track.replace(u"”", "\"")
	(artist, track) = artist_track.split(TRACK_SEPARATOR)
	artist = artist.strip()
	track = track.strip()
	return (artist, track)


def fixTime(test):
	test = datetime.datetime.strptime(test, '%H:%M')
	t = datetime.timedelta(hours=8)
	test = t+test
	test = test.strftime('%H:%M')
	return test


def generateTrackSet(network,username):
	df = list(network.get_user(username).get_recent_tracks(limit=1000))
	df = pd.DataFrame(df, columns=['trackartist', 'album', 'datetime', 'timestamp'])
	lastplayed = df.iloc[-1, -1]
	starttime = int(lastplayed)
	maxtime =1514764800
	limit=500
	while maxtime<starttime:
		df1 = network.get_user(username).get_recent_tracks(limit=limit, time_to=str(starttime))
		df1 = pd.DataFrame(df1, columns=['trackartist', 'album', 'datetime', 'timestamp'])
		starttime = int(df1.iloc[-1, -1])
		df = pd.concat([df, df1])
	# fix datetime
	dates = df.iloc[:, 2].str.split(",", expand=True)
	dates.columns = ['date', 'time']
	dates.time = dates.time.str.strip()
	dates.time = dates.time.apply(lambda x: fixTime(x))

	#fix track and artist
	trackList = df.iloc[:, 0].tolist()
	trackArtist = []
	album = df.loc[:, ['album']].iloc[:, -1].tolist()
	dates = dates.values.tolist()
	counter = 0
	for item in trackList:
		trackname = item.get_title()
		artistname = item.get_artist().get_name()
		albname = album[counter]
		date = dates[counter][0]
		time = dates[counter][1]
		trackArtist.append([trackname, artistname, albname, date, time])
		counter += 1
	df = pd.DataFrame(trackArtist, columns=['Track', 'Artist', 'Album', 'Date', 'Time'])
	return df


def topAlbumsArtists(network,username):
	user = network.get_user(username)
	topArtists = user.get_top_artists(limit=100)
	topAlbums = user.get_top_albums(limit=100)
	ArtistPlays = []
	AlbumPlays = []

	for obj in topArtists:
		sx = obj.item
		sx = sx.get_name()
		plays = obj.weight
		ArtistPlays.append([sx, plays])
	df1 = pd.DataFrame(ArtistPlays, columns=["Artist", "Plays"])
	df1.to_csv('exports/TopArtist.csv',index=False)
	for obj in topAlbums:
		sx = obj.item
		sx = sx.get_name()
		plays = obj.weight
		AlbumPlays.append([sx, plays])
	df2 = pd.DataFrame(AlbumPlays, columns=["Album", "Plays"])
	df2.to_csv("exports/TopAlbums.csv",index=False)
	return df1,df2

def makeAllLastFm(network,username):
	tup=topAlbumsArtists(network,username)
	recentTracks=generateTrackSet(network,username)
	topArtists=tup[0]
	topAlbums=tup[1]
	dataframes={
		"Recent Tracks":recentTracks,
		"Top Artists":topArtists,
		"Top Albums":topAlbums
	}
	return dataframes

def topTracksDB(network, username):
	df = generateTrackSet(network, username)
	df = df.assign(key=pd.Series(np.random.randn(len(df.index))).values)
	playFreq = pd.DataFrame(df.groupby(["Track", "Artist"])["key"].nunique().to_frame(
	).reset_index().sort_values(by="key", ascending=False).reset_index().drop("index", axis=1))
	playFreq.columns=["Track","Artist","Plays"]
	playFreq.to_csv("exports/AllTracksPlayed.csv",index=False)
	return playFreq


def generateMasterTrackDatabase():
	tracksDB = pd.read_csv("exports/savedDB.csv", index_col=0).reset_index()
	trackPlaysDB = pd.read_csv("exports/AllTracksPlayed.csv")
	trackPlaysDB.columns = ["Track", "Artist", "Plays"]
	df = pd.merge(tracksDB, trackPlaysDB, how="left", on=["Track", "Artist"])

	df_usable = df.loc[:, ["Track", "Artist", "Album", "Date Added", "Plays", "Popularity", "acousticness", "danceability", "speechiness", "tempo", "time_signature", "valence", "energy", "liveness", "instrumentalness"]].sort_values(by="Date Added", ascending=False)
	df_usable = df_usable.fillna(0).reset_index(drop=True)
	df_usable.loc[:, "Plays"] = df_usable.loc[:, "Plays"].astype(int)
	df_usable.to_csv("exports/MasterTrackDatabase.csv")
	return df_usable
