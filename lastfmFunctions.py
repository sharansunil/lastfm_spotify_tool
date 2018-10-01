##############LASTFM
import json
import requests
import pandas as pd
import pylast
import sys
import itertools
import datetime

TRACK_SEPARATOR = u" - "


def get_recent_tracks(network ,username, number):
	recent_tracks = network.get_user(username).get_recent_tracks(limit=number)
	return recent_tracks


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


def generateRecentTrackSet(network,username,n=500):
	df = list(get_recent_tracks(network,username, n))
	df = pd.DataFrame(df, columns=['trackartist', 'album', 'datetime', 'rand'])
	# fix datetime
	dates = df.iloc[:, 2].str.split(",", expand=True)
	dates.columns = ['date', 'time']
	dates.time = dates.time.str.strip()
	dates.time = dates.time.apply(lambda x: fixTime(x))
	#fix track and artist
	trackList = df.iloc[:, 0].tolist()
	trackArtist = []
	for item in trackList:
		trackname = item.get_title()
		artistname = item.get_artist().get_name()
		trackArtist.append([trackname, artistname])
	trackArtist = pd.DataFrame(trackArtist, columns=['track', 'artist'])
	# albums
	albums = df.loc[:, 'album']
	trackArtist = trackArtist.assign(albums=albums)
	df = pd.concat([trackArtist, dates], axis=1)
	df.to_csv('exports/recentTracks.csv')
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
	df1.to_csv('exports/TopArtist.csv')
	for obj in topAlbums:
		sx = obj.item
		sx = sx.get_name()
		plays = obj.weight
		AlbumPlays.append([sx, plays])
	df2 = pd.DataFrame(AlbumPlays, columns=["Album", "Plays"])
	df2.to_csv("exports/TopAlbums.csv")
	return df1,df2

def makeAllLastFm(network,username):
	tup=topAlbumsArtists(network,username)
	recentTracks=generateRecentTrackSet(network,username,1000)
	topArtists=tup[0]
	topAlbums=tup[1]
	dataframes={
		"Recent Tracks":recentTracks,
		"Top Artists":topArtists,
		"Top Albums":topAlbums
	}
	return dataframes
