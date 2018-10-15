from bs4 import BeautifulSoup as bs
from fuzzywuzzy import fuzz
from math import pi
from matplotlib.colors import ListedColormap
from oauth2client.service_account import ServiceAccountCredentials
from os import listdir
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv
import datetime
import gspread
import gspread_dataframe as gd
import itertools
import lyricsgenius as genius
import matplotlib.pyplot as plt
import numpy as np
import os
import os.path
import pandas as pd
import pylast
import seaborn as sns
import spotipy
import spotipy.util as util
import sys
import unidecode
import warnings


"""LastFM class details"""
class LastFmCredentials:

	def __init__(self, lastfm_username):
		self.lastfm_username = lastfm_username

	def setPassword(self, password):
		self.password = pylast.md5(password)

	API_KEY = 'f2790f6bacdee1a1be45db1b542bd7fb'
	API_SECRET = '481449b2f6f3c95ee57eabe0cfe25258'
	TRACK_SEPARATOR = u" - "

	def gen_network(self):
		net = pylast.LastFMNetwork(
			api_key=self.API_KEY,
			api_secret=self.API_SECRET,
			username=self.lastfm_username,
			password_hash=self.password)
		return net

	#global var dont touch
	"""helper functions - reader can ignore"""

	def unicode_track_and_timestamp(self, track):
		unicode_track = str(track.track)
		return track.playback_date + "\t" + unicode_track

	def split_artist_track(self, artist_track):
		artist_track = artist_track.replace(u" – ", " - ")
		artist_track = artist_track.replace(u"“", "\"")
		artist_track = artist_track.replace(u"”", "\"")
		(artist, track) = artist_track.split(self.TRACK_SEPARATOR)
		artist = artist.strip()
		track = track.strip()
		return (artist, track)

	def fixTime(self, test):
		test = datetime.datetime.strptime(test, '%H:%M')
		t = datetime.timedelta(hours=8)
		test = t+test
		test = test.strftime('%H:%M')
		return test

	"""dataset generators, do not customise unless you know what youre doing"""

	def topAlbumsArtists(self, network, username):
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
		df1.to_csv('exports/TopArtist.csv', index=False)
		for obj in topAlbums:
			sx = obj.item
			sx = sx.get_name()
			plays = obj.weight
			AlbumPlays.append([sx, plays])
		df2 = pd.DataFrame(AlbumPlays, columns=["album", "plays"])
		df2.to_csv("exports/TopAlbums.csv", index=False)
		return df1, df2

	def topTracksDB(self, network, username):
		df = list(network.get_user(username).get_recent_tracks(limit=1000))
		df = pd.DataFrame(
			df, columns=['trackartist', 'album', 'datetime', 'timestamp'])
		lastplayed = df.iloc[-1, -1]
		starttime = int(lastplayed)
		maxtime = 1514764800
		limit = 500
		while maxtime < starttime:
			df1 = network.get_user(username).get_recent_tracks(
				limit=limit, time_to=str(starttime))
			df1 = pd.DataFrame(
				df1, columns=['trackartist', 'album', 'datetime', 'timestamp'])
			starttime = int(df1.iloc[-1, -1])
			df = pd.concat([df, df1])
		# fix datetime
		dates = df.iloc[:, 2].str.split(",", expand=True)
		dates.columns = ['date', 'time']
		dates.time = dates.time.str.strip()
		dates.time = dates.time.apply(lambda x: self.fixTime(x))

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
		df = pd.DataFrame(trackArtist, columns=[
		                  'track', 'artist', 'album', 'date', 'time'])
		df = df.assign(key=pd.Series(np.random.randn(len(df.index))).values)
		df = pd.DataFrame(df.groupby(["track", "artist"])["key"].nunique().to_frame(
		).reset_index().sort_values(by="key", ascending=False).reset_index().drop("index", axis=1))
		df.columns = ["track", "artist", "plays"]
		df = df.assign(uid=df["track"]+df["artist"])
		df.uid = df.uid.str.lower()
		df.uid = df.uid.str.strip()
		df.artist = df.artist.str.replace("$", "s")
		df.uid = df.uid.str.replace("$", "s")
		df.to_csv("exports/AllTracksPlayed.csv", index=False)
		return df

	def generateMasterTrackDatabase(self):
		tracksDB = pd.read_csv("exports/savedDB.csv", index_col=0).reset_index()
		df = tracksDB.assign(uid=tracksDB["track"]+tracksDB["artist"])
		trackPlaysDB = pd.read_csv("exports/AllTracksPlayed.csv")
		df.uid = df.uid.str.lower()
		df.uid = df.uid.str.strip()
		df.uid = df.uid.str.replace("$", "s")
		df = pd.merge(df, trackPlaysDB, how="left", on="uid", suffixes=('', '_y'))
		df = df.drop(columns=['track_y', 'artist_y'])
		df["plays"] = df["plays"].fillna(0)
		df.loc[:, "plays"] = df.loc[:, "plays"].astype(int)
		df = df.loc[:, ["track", "artist", "album", "date_added", "plays", "popularity", "acousticness", "danceability", "speechiness",
                  "tempo", "time_signature", "valence", "energy", "liveness", "instrumentalness"]].sort_values(by="date_added", ascending=False)
		df.iloc[:, [0, 1, 2, 3]] = df.iloc[:, [
			0, 1, 2, 3]].apply(lambda x: x.str.strip())
		df.iloc[:, [6, 7, 8, 9, 11, 12, 13, 14]] = df.iloc[:, [
			6, 7, 8, 9, 11, 12, 13, 14]].apply(lambda x: x.round(2))
		df.tempo = df.tempo.apply(lambda x: int(x))
		df = df.sort_values(by="plays", ascending=False).reset_index(drop=True)
		df.to_csv("exports/MasterTrackDatabase.csv", index=False)

	def generatePlaylistDb(self):
		""""fixdf"""
		df = pd.read_csv("exports/playlistDB.csv", index_col=0).reset_index()
		df = df.assign(uid=df["trackname"]+df["artist"])
		df.uid = df.uid.str.lower()
		df.uid = df.uid.str.strip()
		df.uid = df.uid.str.replace("$", "s")
		"""fixtracks"""
		trackPlaysDB = pd.read_csv("exports/AllTracksPlayed.csv")

		"""merge and clean"""

		df = pd.merge(df, trackPlaysDB, how="left", on="uid", suffixes=('', '_y'))
		df = df.loc[:, ["playlist", "track", "artist", "album", "plays", "date_added", "acousticness", "liveness",
                  "instrumentalness", "valence", "energy", "tempo", "time_signature", "danceability", "speechiness"]]
		df.iloc[:, 0:3] = df.iloc[:, 0:3].apply(lambda x: x.str.strip())
		df.plays = df.plays.fillna(0).astype(int)
		df.loc[:, ["acousticness", "liveness", "instrumentalness", "valence", "energy", "danceability", "speechiness"]] = df.loc[:, [
			"acousticness", "liveness", "instrumentalness", "valence", "energy", "danceability", "speechiness"]].apply(lambda x: x.round(2))
		df.tempo = df.tempo.astype(int)
		df.loc[:, "date_added"] = df.loc[:, "date_added"].apply(lambda x: x[:10])
		df.to_csv('exports/MasterPlaylistDatabase.csv', index=False)

	"""master output file, do not modify. shit might break"""

	def generateCombinedDatabases(self, network, lastfm_username, tracks_playlists=0, top_albums_artists=0):

		try:
			retstr = ""
			if top_albums_artists == 1 and tracks_playlists == 1:
				self.topAlbumsArtists(network, lastfm_username)
				self.topTracksDB(network, lastfm_username)
				self.generateMasterTrackDatabase()
				self.generatePlaylistDb()
				retstr = "Top Albums,Artists datasets updated. Track and Playlist datasets updated."

			elif top_albums_artists == 1 and tracks_playlists == 0:
				self.topAlbumsArtists(network, lastfm_username)
				retstr = "Top Albums,Artists datasets updated. Track and Playlist not updated"

			elif top_albums_artists == 0 and tracks_playlists == 1:
				self.topTracksDB(network, lastfm_username)
				self.generateMasterTrackDatabase()
				self.generatePlaylistDb()
				retstr = "Tracks and Playlist dataset updated. Top Albums/Artists not updated."
			else:
				retstr = "LastFm not updated proceeding to Gsheets. Datasets can be found at MasterTrackDatabase.csv and MasterPlaylistDatabase.csv"

			print(retstr)

		except Exception as e:
			print("f to pay respects")
			print(e)

"""Spotify Class Details"""
class SpotifyCredentials:

	def __init__(self, sp_username, scope='user-library-read'):
		self.sp_username = sp_username
		self.scope = scope

	client_id = 'fe3712517e674d46b0dad0f1e83149cd'
	client_secret = '4adc68cc4f874edc9a7a2b655d8ccaf0'
	redirect_uri = 'https://facebook.com'

	def setScope(self, scope):
		self.scope = scope

	def setUsername(self, sp_username):
		self.sp_username = sp_username

	def getUsername(self):
		return self.sp_username

	def getScope(self):
		return self.scope

	def genAuth(self):
		token = util.prompt_for_user_token(
			username=self.sp_username,
			scope=self.scope,
			client_id=self.client_id,
			client_secret=self.client_secret,
			redirect_uri=self.redirect_uri)
		sp = spotipy.Spotify(auth=token)
		return sp

	"""extracts data from Track object"""

	def show_tracks(self, playname, playid, tracks):
		retdic = []
		for item in tracks['items']:
			track = item['track']
			artist = track['artists'][0]['name']
			trackname = track['name']
			album = track['album']['name']
			trackid = track['id']
			albumid = track['album']['id']
			artistid = track['artists'][0]['id']
			dateadded = item['added_at']
			retarray = [playname, playid, artist, artistid,
                            album, albumid, trackname, dateadded, trackid]
			retdic.append(retarray)
		return retdic

	"""playlist set generation"""

	def generatePlaylistSet(self, sp, username):
		playlists = sp.user_playlists(username)
		playlistarray = []
		for playlist in playlists['items']:
			playname = playlist['name']
			playid = playlist['id']
			results = sp.user_playlist(
				username, playlist['id'], fields="tracks,next")
			tracks = results['tracks']
			x = self.show_tracks(playname, playid, tracks)
			playlistarray.append(x)
		plArray = list(itertools.chain(*playlistarray))
		df = pd.DataFrame(
			data=plArray,
			columns=['playlist', 'playlistID', 'artist', 'artistID', 'album', 'albumID', 'trackname', 'date_added', 'trackID'])
		df.index.name = 'ID'
		trackColumns = ['trackname', 'trackID']
		df2 = df[[trackColumns[0], trackColumns[1]]]
		df2 = df2.assign(Features=df.iloc[:, -1])
		features = df2.iloc[:, -1].apply(sp.audio_features)
		chain = list(itertools.chain(*features))
		featdf = pd.DataFrame(chain)
		trackSet2 = pd.concat([df2.iloc[:, 0:2], featdf], axis=1, join='outer')
		totalSet = pd.merge(df, trackSet2, on=["trackname", "trackID"])
		totalSet = totalSet.drop_duplicates()
		totalSet = totalSet.sort_values(by=['playlist'])
		return totalSet

	"""saved tracks set generation"""

	def savedTracksSpDf(self, sp):
		offset = 0
		ret = []
		while offset < 2000:
			results = sp.current_user_saved_tracks(limit=50, offset=offset)
			for item in results['items']:
				track = item['track']
				date_added = item['added_at']
				date_added = date_added[:10]
				tup = [track['name'], track['artists'][0]['name'],
                                    track['album']['name'], date_added, track['popularity'], track['id']]
				ret.append(tup)
			offset += 50
		df = pd.DataFrame(ret, columns=('track', 'artist', 'album',
                                  'date_added', 'popularity', 'trackID'))
		df['Features'] = df.iloc[:, -1]
		try:
			features = df.iloc[:, -1].apply(sp.audio_features)
		except Exception as e:
			print(e)
		chain = list(itertools.chain(*features))
		df2 = pd.DataFrame(chain)
		df = pd.concat([df.iloc[:, 0:5], df2], axis=1, join='outer')
		df = df.drop_duplicates()
		df = df.sort_values(by=['date_added'], ascending=False)
		return df

	"""update dataset controller"""

	def updatespDataset(self, sp, username, key="both"):
		curdir = os.getcwd()
		newdir = os.path.join(curdir, r'exports')
		os.makedirs(newdir, exist_ok=True)
		if key == "both":
			df1 = self.savedTracksSpDf(sp)
			df1.to_csv('exports/savedDB.csv', index=False)
			df = self.generatePlaylistSet(sp, username)
			df.to_csv('exports/playlistDB.csv', index=False)
		elif key == "playlist":
			df = self.generatePlaylistSet(sp, username)
			df.to_csv('exports/playlistDB.csv', index=False)
		elif key == "saved":
			df = self.savedTracksSpDf(sp)
			df.to_csv('exports/savedDB.csv', index=False)
		else:
			print("Wrong key")

	"""generate playlist profile plots"""

	def make_spider(self, df, row, title, color):
		# number of variable
		categories = list(df)
		N = len(categories)
		# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
		angles = [n / float(N) * 2 * pi for n in range(N)]
		angles += angles[:1]
		# Initialise the spider plot
		ax = plt.subplot(111, polar=True,)
		# If you want the first axis to be on top:
		ax.set_theta_offset(pi / 2)
		ax.set_theta_direction(-1)
		plt.xticks(angles[:-1], categories, color='gray', size=8)
		# Draw ylabels
		ax.set_rlabel_position(0)
		plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4",
                                    "0.6", "0.8"], color="grey", size=7)
		plt.ylim(0, 1)
		plt.rcParams["figure.dpi"] = 188
		# Ind1
		values = df.iloc[row].values.flatten().tolist()
		values += values[:1]
		ax.plot(angles, values, color=color, linewidth=1, linestyle='solid')
		ax.fill(angles, values, color=color, alpha=0.5)
		plt.title(title, size=14, color=color, y=1.08, weight='bold')
		plt.tight_layout()

	def generatePlaylistPlots(self, df):
		# extract usable data
		playlistAnalysis = df.groupby(["playlist"])['valence', 'energy', 'acousticness',
                                              'speechiness', 'danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)
		plNames = list(playlistAnalysis.index)
		# Create a color palette:
		sns.set_palette("pastel")
		cmap = ListedColormap(sns.color_palette(n_colors=256))
		sns.set()
		curdir = os.getcwd()
		newdir = os.path.join(curdir, r'playlistPlots')
		os.makedirs(newdir, exist_ok=True)
		# initialise average dataset
		playlistAnalysisMean = pd.DataFrame(playlistAnalysis.mean())
		playlistAnalysisMean = playlistAnalysisMean.transpose()

		# Loop to plot
		for row in range(0, len(playlistAnalysis.index)):
			plt.clf()
			self.make_spider(df=playlistAnalysisMean, row=0, title="", color='grey')
			self.make_spider(df=playlistAnalysis, row=row,
                            title=plNames[row], color=cmap(row))
			plt.savefig('playlistPlots/'+plNames[row]+'.svg')

	"""generate artist distribution plots"""

	def getartistDist(self, df, artist, features):
		artistSet = df[df.artist == artist]
		filename = "artistDistribution/"+artist+"/"
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		for feature in features:
			plt.clf()
			sns.kdeplot(artistSet.loc[:, feature], label=artist, shade=True)
			sns.kdeplot(df.loc[:, feature], label="Dataset", shade=True)
			plt.title(feature.capitalize() + " distribution of " + artist)
			plt.legend()
			plt.savefig(filename+artist+" "+feature+".png")

	def artistSegments(self):
		df = pd.read_csv('exports/savedDB.csv')
		df['duration_min'] = df['duration_ms'].apply(lambda x: x/(1000*60)).round(2)
		df.drop(['duration_ms'], axis=1)
		sns.set(color_codes=True)
		artistList = list(df.loc[:, 'artist'].unique())
		features = ['valence', 'acousticness', 'instrumentalness',
                    'energy', 'speechiness', 'popularity', 'liveness']
		for artist in artistList:
			self.getartistDist(df, artist, features)

	"""	main controller for all functions
		if playlist toggled to 0 no playlist graphs will be generated
		if artist is toggled to 0 no artist distribution folder and graphs will be created """

	def generateAllspDatasets(self, sp, username, refresh=1, playlists=1, artist=1):
		refpr = "done"
		plpr = "done"
		art = "done"
		retstr = ""
		if refresh == 1:
			self.updatespDataset(sp, username, key="both")
		else:
			refpr = "omitted"
		df = pd.read_csv('exports/playlistDB.csv')
		if playlists == 1:
			self.generatePlaylistPlots(df)
		else:
			plpr = "omitted"
		if artist == 1:
			self.artistSegments()
		else:
			art = "omitted"
		if refresh + playlists + artist == 0:
			retstr = "Spotify not updated, proceeding to lastfm. Datasets can be found in playlistDB.csv and savedDB.csv"
		else:
			retstr = "Spotify updated with refresh {}, playlists {} and artists {}".format(
				refpr, plpr, art)
		print(retstr)

"""Gsheet class details"""
class GoogleSheetLoader:

	def __init__(self):
		self.gscope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
		self.credentials = ServiceAccountCredentials.from_json_keyfile_name('spotfm_credentials.json', self.gscope)
	def top100_to_df(self,refresh_gsheet):
		self.trax = pd.read_csv("exports/MasterTrackDatabase.csv")
		if refresh_gsheet==1:
			gc = gspread.authorize(self.credentials)
			top100 = gc.open('best albums').worksheet("top100")
			no_rows = int(top100.acell('S2').value)
			no_col = int(top100.acell('S1').value)
			retval = []
			for row in range(1, no_rows):
					retval.append(top100.row_values(row))
			df = pd.DataFrame(retval[1:], columns=[x.lower() for x in retval[0]])
			df = df.iloc[:, range(0, no_col)].fillna(0)
			df= self.top100_plays(self.trax,df)
			df=df.drop("album_y",axis=1)
			df=df.drop("alt",axis=1)
			colf = list(df.select_dtypes(include="object").columns)
			df.loc[:,colf]=df.loc[:,colf].apply(lambda x: x.str.strip())
			df=df.fillna(0)
			df.to_csv("exports/Top100.csv",index=False)
			df.to_excel(excel_writer="exports/Top 100.xlsx",index=False)
			self.pushToGsheet(gc,"Top 100 Albums")
			print("top 100 albums extracted and updated locally on csv,excel and on gsheet")
		else:
			print("Gsheet Refresh not selected, dataset can be found in Top100.csv if generated previously")
	def frep(self,tracks,x,retseg):
		rv = tracks.loc[tracks.album.str.contains(x), retseg].tolist()
		if len(rv) != 0:
			rv = rv[0]
		else:
			rv = 0
		return rv
	def generateClient(self):
		return gspread.authorize(self.credentials)
	def top100_plays(self,tracks, top100):
		tracks.album = tracks.album.apply(lambda x: x.lower().strip())
		tracks2 = tracks.groupby("album")["plays"].sum().to_frame().reset_index()
		top100.album = top100.album.apply(lambda x: x.lower().strip())
		top100 = top100.assign(plays=top100.album.apply(lambda x: self.frep(tracks2,x,"plays")))
		top100=top100.fillna(0)
		cols = list(tracks.select_dtypes(include="float64").columns)
		albums = pd.DataFrame(tracks.groupby('album')[cols].mean()).reset_index()
		top100 = top100.assign(alt="")
		top100.alt = top100.album.apply(lambda x: self.frep(tracks, x,"album"))
		top100 = pd.merge(top100, albums, how="left", left_on="alt", right_on="album",suffixes=('','_y'))
		return top100
	def pushToGsheet(self,client,fname):
		try:
			ss = client.open(fname)
		except gspread.exceptions.SpreadsheetNotFound:
			ss = client.create(fname)
			ss.share('sharansnl@gmail.com', perm_type='user', role='writer')
		ss = ss.sheet1
		df = pd.read_csv("exports/Top100.csv")
		gd.set_with_dataframe(ss, df)

"""Combined loader details"""
class Spotify_LastFM_Builder(SpotifyCredentials, LastFmCredentials,GoogleSheetLoader):

	def __init__(self, lastfm_username, sp_username, scope="user-library-read"):
		SpotifyCredentials.__init__(self,sp_username, scope)
		LastFmCredentials.__init__(self,lastfm_username)
		GoogleSheetLoader.__init__(self)

	def create_credentials(self):
		sp = SpotifyCredentials.genAuth(self)
		network = LastFmCredentials.gen_network(self)
		self.sp = sp
		self.network = network

	"""updates dataset without loading datasets in memory,store as csv"""
	def update_datasets(self,refresh_spotify=0,refresh_artist_viz=0,refresh_playlist_viz=0,lastfm_tracks=1,lastfm_artistalbum=1,refresh_gsheet=0):
		self.create_credentials()
		with warnings.catch_warnings():
			warnings.filterwarnings("ignore", category=RuntimeWarning)
			try:
				self.generateAllspDatasets(	
					self.sp, 
					self.sp_username, 
					refresh=refresh_spotify,
					playlists=refresh_playlist_viz,
					artist=refresh_artist_viz )
				self.generateCombinedDatabases(
					self.network, 
					self.lastfm_username, 
					tracks_playlists=lastfm_tracks,
					top_albums_artists=lastfm_artistalbum)
				self.top100_to_df(refresh_gsheet)

			except Exception as e:
				print("f to pay resepects\n\n")
				print(e)
	
	"""loads dataset into memory. toggle playlist and tracks to see which df's to load. selecting both will return as dictionary with playlist and tracks as keys"""
	def load_datasets(self,playlist=1,tracks=1,gsheet=1):
		self.tr =pd.DataFrame()
		self.pl=pd.DataFrame()
		self.gs=pd.DataFrame()
		if playlist==1:
			self.pl=pd.read_csv("exports/MasterPlaylistDatabase.csv",index_col="playlist")
		if tracks ==1:
			self.tr=pd.read_csv("exports/MasterTrackDatabase.csv",index_col="date_added")
		if gsheet ==1:
			self.gs=pd.read_csv("exports/Top100.csv")
		if tracks==1 and playlist==1 and gsheet==1: #all
			return {"playlist":self.pl,"tracks":self.tr,"top100":self.gs}
		elif tracks==1 and playlist==0 and gsheet==0: #tracks
			return self.tr 
		elif tracks == 1 and playlist == 0 and gsheet == 1: #tracks + gs
			return {"tracks":self.tr,"top100":self.gs}
		elif tracks==0 and playlist==1 and gsheet==0: #pl 
			return self.pl
		elif tracks == 0 and playlist == 1 and gsheet == 1: #pl + gs
			return {"playlist":self.pl,"top100":self.gs}
		elif tracks==0 and playlist==0 and gsheet==1: #gs
			return self.gs
		else:
			print("invalid keys given, please only type 1 or 0")

"""Lyric Class Details"""
class LyricGenerator:

	def __init__(self):
		self.lyric_token = '77eKBrbm6RQj4Sg0rxnmH7sFZwDcRmcRsBzde9en1SPcboe8Ilm2p8bt-2Ndr2zN'

	def blockPrint(self):
		sys.stdout = open(os.devnull, 'w')

	def enablePrint(self):
		sys.stdout = sys.__stdout__

	def pullGeniusLyrics(self,df):
		api = genius.Genius(self.lyric_token, verbose=False)
		errors = []
		for item in df.itertuples():
			artist = item[1]
			track = item[2]
			track = unidecode.unidecode(track)
			retstr = 'exports/lyric files/'+artist+'/'
			track=track.replace("/"," ")
			track = track.split("|")[0] if "|" in track else track
			track=track.strip()
			track=track.replace(":"," ")
			artist = unidecode.unidecode(artist)
			self.blockPrint()
			try:
				song=api.search_song(track, artist)
				os.makedirs(os.path.dirname(retstr), exist_ok=True)
				song.save_lyrics(retstr+track, verbose=False, overwrite=False)
			except AttributeError:
				errors.append(track +' '+artist)
		self.enablePrint()
		len_err = len(errors)
		len_df = len(df.index)
		retstr = "{} lyrics attempted. {} successful. {} errors.".format(len_df, len_df-len_err, len_err)
		print(retstr)
		return errors


	def fuzzer(self,a,b):
		if fuzz.partial_ratio(a, b) > 95:
			return True
		else:
			False


	def splitbar(self,s, pattern):
		if pattern in s:
			return s.split(pattern)[0]
		else:
			return s


	def getTop100MissingLyrics(self,spotify_fm):
		retdict=spotify_fm.load_datasets()
		top100 = retdict["top100"]
		top100 = top100.loc[:, ["artist", "album"]]
		track = retdict["tracks"]
		top100.album = top100.album.str.lower()
		top100.album = top100.album.str.strip()
		track.album = track.album.str.lower()
		track.album = track.album.str.strip()
		top100 = top100.assign(f=top100.album.isin(track.album))
		top100f = top100[top100.f == False]
		trackbum = list(track.album.unique())
		matches = []
		for item in top100f.itertuples():
			album = item[2]
			rv = ""
			for alb in trackbum:
				if self.fuzzer(album, alb):
					rv = alb
			matches.append((album, rv))
		matched = pd.DataFrame(matches, columns=['album', 'ref'])
		top100 = pd.merge(top100, matched, how="left", on="album")
		top100.ref = top100.ref.fillna(top100.album)
		top100 = top100.drop('f', axis=1)
		track = track.assign(istop=track.album.isin(top100.ref))
		top100s = track[track.istop == True]
		lyr = pd.read_csv('exports/currentlyrics.csv')
		top100s.track = top100s.track.str.strip()
		top100s.track = top100s.track.str.lower()
		top100s.track = top100s.track.apply(lambda x: self.splitbar(x, '|'))
		top100s.track = top100s.track.apply(lambda x: self.splitbar(x, ':'))
		top100_t = top100s.loc[:, ["artist", "track"]]
		top100_t = top100_t.assign(isL=top100_t.artist.isin(lyr.artist))
		top100_t = top100_t[top100_t.isL == False]
		top100_t = top100_t.sort_index(ascending=False)
		top100_t.artist = top100_t.artist.apply(lambda x: unidecode.unidecode(x))
		top100_t.index = top100_t.artist
		top100_t = top100_t.drop(["harunemuri", "MOL"]).reset_index(drop=True).drop('isL', axis=1)
		return top100_t


	def loadFiles(self,fname):
		with open('fname', 'r') as f:
			reader = csv.reader(f)
			f = list(reader)
		f = list(itertools.chain(*f))
		os.chdir("exports/lyric files")
		return f


	def scrapeToPage(self,driver, item):
		driver.get("https://genius.com/")
		elem = driver.find_element_by_name("q")
		elem.clear()
		elem.send_keys(item)
		el_one = elem.send_keys(Keys.RETURN)
		sleep(20)
		el_one = driver.find_element_by_tag_name("search-result-item")
		el_one.click()
		el_two = driver.page_source
		return el_two


	def writeAll(self):
		driver = webdriver.Chrome()
		df = self.loadFiles('dog.csv')
		for item in df:
			try:
				ret = self.scrapeToPage(driver, item)
			except Exception as e:
				print(e)
			html = bs(ret, "html.parser")
			lyrics = html.find("div", class_="lyrics").get_text("\n")
			lyrics = lyrics.lstrip('\n')
			lyrics = lyrics.rstrip('\n')
			with open(item+".txt", "w") as text_file:
				text_file.write(lyrics)
		driver.delete_all_cookies()


	def getCurrLyr(self):
		path = 'exports/lyric files/'

		baselist = listdir(path)
		len(baselist)
		baselist.remove('.DS_Store')
		bl = [unidecode.unidecode(item)for item in baselist]
		x = []
		for item in bl:
			rv = [item, listdir(path+item+'/')]
			x.append(rv)
		f = []

		for item in x:
			artist = item[0]
			rv = [(artist, tr.replace('.txt', '')) for tr in item[1]]
			f.append(rv)
		f = itertools.chain(*f)
		f = list(f)

		df = pd.DataFrame(f, columns=['artist', 'track'])
		df = df.sort_values(by='artist').reset_index(drop=True)
		df.to_csv('exports/currentlyrics.csv', index=False)
		return df

	def lyricController(self,spotify_fm):
		df=self.getTop100MissingLyrics(spotify_fm)
		success=0
		if len(df)==0:
			success=1
			print("All lyrics retrieved previously, no changes.")
		else:
			errors=self.pullGeniusLyrics(df)
			if len(errors)==0:
				success=1
				print("{} lyrics retrieved. No errors".format(len(df)))
			else:
				try:
					self.writeAll()
					success=1
					print("{} lyrics retrieved despite errors")
				except Exception as e:
					print(e)
		if success==1:
			rdf=self.getCurrLyr()
			return rdf
		else:
			print("Not all prints successful")
			return errors
