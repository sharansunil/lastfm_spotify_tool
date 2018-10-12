import spotipy
import spotipy.util as util
import pylast
import LastFmFunctions as last_func
import SpotifyFunctions as spot_func
import warnings
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gd
import sys
import os
import unidecode
import lyricsgenius as genius
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
from bs4 import BeautifulSoup as bs
import itertools
from time import sleep
from os import listdir

class LastFmCredentials:

	def __init__(self, lastfm_username):
		self.lastfm_username = lastfm_username

	def setPassword(self,password):
		self.password = pylast.md5(password)

	API_KEY = 'f2790f6bacdee1a1be45db1b542bd7fb'
	API_SECRET = '481449b2f6f3c95ee57eabe0cfe25258'

	def gen_network(self):
		net = pylast.LastFMNetwork(
			api_key=self.API_KEY, 
			api_secret=self.API_SECRET,
			username=self.lastfm_username, 
			password_hash=self.password)
		return net

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
				spot_func.generateAllDatasets(	
					self.sp, 
					self.sp_username, 
					refresh=refresh_spotify,
					playlists=refresh_playlist_viz,
					artist=refresh_artist_viz )
				last_func.generateCombinedDatabases(
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