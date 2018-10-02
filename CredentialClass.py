import spotipy
import spotipy.util as util
import pylast


class LastFmCredentials():

	def __init__(self, username, password):
		self.username = username
		self.password = pylast.md5(password)

	API_KEY = 'f2790f6bacdee1a1be45db1b542bd7fb'
	API_SECRET = '481449b2f6f3c95ee57eabe0cfe25258'

	def gen_network(self):
		net = pylast.LastFMNetwork(api_key=self.API_KEY, api_secret=self.API_SECRET,
		                           username=self.username, password_hash=self.password)
		return net

class SpotifyCredentials():


    def __init__(self,username, scope):
        self.username = username
        self.scope = scope
    
    client_id = 'fe3712517e674d46b0dad0f1e83149cd'
    client_secret = '4adc68cc4f874edc9a7a2b655d8ccaf0'
    redirect_uri = 'https://facebook.com'


    def setScope(self, scope):
        self.scope = scope

    def setUsername(self, username):
        self.username = username

    def getUsername(self):
        return self.username

    def getScope(self):
        return self.scope

    def genAuth(self):
        token = util.prompt_for_user_token(username=self.username, scope=self.scope, client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)
        sp = spotipy.Spotify(auth=token)
        return sp
