import json
import requests
import pandas as pd
import pylast
import sys
import itertools
import datetime 

API_KEY = 'f2790f6bacdee1a1be45db1b542bd7fb'
API_SECRET = '481449b2f6f3c95ee57eabe0cfe25258'
username = "sharansunil"
password = pylast.md5("synystrax")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password)

TRACK_SEPARATOR = u" - "


def get_recent_tracks(username, number):
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
print("A")
def generateRecentTrackSet(n=500):
	df = list(get_recent_tracks(username, n))
	df = pd.DataFrame(df, columns=['trackartist', 'album', 'datetime', 'rand'])
	# fix datetime
	dates = df.iloc[:, 2].str.split(",", expand=True)
	dates.columns = ['date', 'time']
	dates.time = dates.time.str.strip()
	dates.time=dates.time.apply(lambda x:fixTime(x))
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

