import spotipy
import spotipy.util as util



class SpotifyCredentials():

    def __init__(self, client_id, client_secret, redirect_uri, username, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.username = username
        self.scope = scope

    def setClientId(self, client_id):
        self.client_id = client_id

    def setClientSecret(self, client_secret):
        self.client_secret = client_secret

    def setRedirect(self, redirect_uri):
        self.redirect_uri = redirect_uri

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
