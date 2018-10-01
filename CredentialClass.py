import spotipy
import spotipy.util as util

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
