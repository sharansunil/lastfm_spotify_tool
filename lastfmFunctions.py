##############LASTFM
import pandas as pd
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
	df = pd.DataFrame(trackArtist, columns=['track', 'artist', 'album', 'date', 'time'])
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
	df1 = pd.DataFrame(ArtistPlays, columns=["artist", "plays"])
	df1.to_csv('exports/TopArtist.csv',index=False)
	for obj in topAlbums:
		sx = obj.item
		sx = sx.get_name()
		plays = obj.weight
		AlbumPlays.append([sx, plays])
	df2 = pd.DataFrame(AlbumPlays, columns=["album", "plays"])
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
	df = pd.DataFrame(df.groupby(["track", "artist"])["key"].nunique().to_frame(
	).reset_index().sort_values(by="key", ascending=False).reset_index().drop("index", axis=1))
	df.columns=["track","artist","plays"]
	df = df.assign(uid=df["track"]+df["artist"])
	df.to_csv("exports/AllTracksPlayed.csv",index=False)
	return df


def generateMasterTrackDatabase():
	tracksDB = pd.read_csv("exports/savedDB.csv", index_col=0).reset_index()
	df = tracksDB.assign(uid=tracksDB["track"]+tracksDB["artist"])
	trackPlaysDB = pd.read_csv("exports/AllTracksPlayed.csv")
	trackPlaysDB.uid = trackPlaysDB.uid.str.lower()
	trackPlaysDB.uid = trackPlaysDB.uid.str.strip()
	df.uid = df.uid.str.lower()
	df.uid = df.uid.str.strip()
	df = pd.merge(df, trackPlaysDB, how="left", on="uid", suffixes=('', '_y'))
	df = df.drop(columns=['track_y', 'artist_y'])
	df["plays"] = df["plays"].fillna(0)
	df.loc[:, "plays"] = df.loc[:, "plays"].astype(int)
	df = df.loc[:, ["track", "artist", "album", "date_added", "plays", "popularity", "acousticness", "danceability", "speechiness","tempo", "time_signature", "valence", "energy", "liveness", "instrumentalness"]].sort_values(by="date_added", ascending=False)
	df.iloc[:, [0, 1, 2, 3]] = df.iloc[:, [0, 1, 2, 3]].apply(lambda x: x.str.strip())
	df.iloc[:, [6, 7, 8, 9, 11, 12, 13, 14]] = df.iloc[:, [6, 7, 8, 9, 11, 12, 13, 14]].apply(lambda x: x.round(2))
	df.tempo = df.tempo.apply(lambda x: int(x))
	df = df.sort_values(by="plays", ascending=False).reset_index(drop=True)
	df.to_csv("exports/MasterTrackDatabase.csv",index=False)


def generatePlaylistDb():
	""""fixdf"""
	df = pd.read_csv("exports/playlistDB.csv", index_col=0).reset_index()
	df = df.assign(uid=df["trackname"]+df["artist"])
	df.uid = df.uid.str.lower()
	df.uid = df.uid.str.strip()

	"""fixtracks"""
	trackPlaysDB = pd.read_csv("exports/AllTracksPlayed.csv")
	trackPlaysDB.uid = trackPlaysDB.uid.str.lower()
	trackPlaysDB.uid = trackPlaysDB.uid.str.strip()

	"""merge and clean"""

	df = pd.merge(df, trackPlaysDB, how="left", on="uid", suffixes=('', '_y'))
	df = df.loc[:, ["playlist", "track", "artist", "album", "plays","date_added" ,"acousticness", "liveness",
                 "instrumentalness", "valence", "energy", "tempo", "time_signature", "danceability", "speechiness"]]
	df.iloc[:, 0:3] = df.iloc[:, 0:3].apply(lambda x: x.str.strip())
	df.plays = df.plays.fillna(0).astype(int)
	df.loc[:, ["acousticness", "liveness", "instrumentalness", "valence", "energy", "danceability", "speechiness"]] = df.loc[:, [
		"acousticness", "liveness", "instrumentalness", "valence", "energy", "danceability", "speechiness"]].apply(lambda x: x.round(2))
	df.tempo = df.tempo.astype(int)
	df.loc[:, "date_added"] = df.loc[:, "date_added"].apply(lambda x: x[:10])
	df.to_csv('exports/MasterPlaylistDatabase.csv', index=False)

def generateCombinedDatabases(network,lastfm_username,refresh=0):

	if refresh==0:
		
		try:
			generateMasterTrackDatabase()
			generatePlaylistDb()
			print("both datasets generated")
		
		except Exception as e:
			print("An error occurred: \n" + e )
	
	elif refresh ==1:
		try:
			topAlbumsArtists(network,lastfm_username)
			topTracksDB(network,lastfm_username)
			generateMasterTrackDatabase()
			generatePlaylistDb()
			print("LastFM data refreshed and datasets generated")
		except Exception as e:
			print("An error occurred: \n" + e )

	else:
		print("Wrong refresh key: 1 for yes, 0 for no. Its pretty straightforward.")
