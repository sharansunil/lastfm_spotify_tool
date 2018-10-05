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
			df.to_csv("exports/Top100.csv",index=False)
			df.to_excel(excel_writer="exports/Top 100.xlsx")
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
		top100 = pd.merge(top100, albums, how="left", left_on="alt", right_on="album")
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
