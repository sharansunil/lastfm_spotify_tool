import spotipy
import spotipy.util as util
import pylast
import LastFmFunctions as last_func
import SpotifyFunctions as spot_func
import warnings


class LastFmCredentials():

	def __init__(self, lastfm_username):
		self.lastfm_username = lastfm_username

	def setPassword(self,password):
		self.password = pylast.md5(password)

	API_KEY = 'f2790f6bacdee1a1be45db1b542bd7fb'
	API_SECRET = '481449b2f6f3c95ee57eabe0cfe25258'

	def gen_network(self):
		net = pylast.LastFMNetwork(api_key=self.API_KEY, api_secret=self.API_SECRET,
								   username=self.lastfm_username, password_hash=self.password)
		return net


class SpotifyCredentials():

	def __init__(self, sp_username, scope):
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
		token = util.prompt_for_user_token(username=self.sp_username, scope=self.scope,
										   client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
		sp = spotipy.Spotify(auth=token)
		return sp


class Spotify_LastFM_Builder(SpotifyCredentials, LastFmCredentials):

	def __init__(self, lastfm_username, sp_username, scope, refresh_spotify, refresh_last_tracks_pl,refresh_last_top_albums_artists,refresh_playlists,refresh_artist):
		SpotifyCredentials.__init__(self,sp_username, scope)
		LastFmCredentials.__init__(self,lastfm_username)
		self.refresh_spotify = refresh_spotify
		self.refresh_last_tracks_pl = refresh_last_tracks_pl
		self.refresh_last_top_albums_artists=refresh_last_top_albums_artists
		self.playlists=refresh_playlists
		self.artist=refresh_artist

	def create_credentials(self):
		sp = SpotifyCredentials.genAuth(self)
		network = LastFmCredentials.gen_network(self)
		self.sp = sp
		self.network = network

	def create_all(self):
		self.create_credentials()
		with warnings.catch_warnings():
			warnings.filterwarnings("ignore", category=RuntimeWarning)
			try:
				spot_func.generateAllDatasets(self.sp, self.sp_username, refresh=self.refresh_spotify,playlists=self.playlists,artist=self.artist)
				last_func.generateCombinedDatabases(self.network, self.lastfm_username, tracks_playlists=self.refresh_last_tracks_pl,top_albums_artists=self.refresh_last_top_albums_artists)
			except Exception as e:
				print("f to pay resepects\n\n")
				print(e)
