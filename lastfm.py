import pylast

class LastFmGenerator():

	def __init__(self,username,password):
		self.username=username
		self.password=pylast.md5(password)


	API_KEY = 'f2790f6bacdee1a1be45db1b542bd7fb'
	API_SECRET = '481449b2f6f3c95ee57eabe0cfe25258'

	def gen_network(self):
		net=pylast.LastFMNetwork(api_key=self.API_KEY, api_secret=self.API_SECRET,username=self.username, password_hash=self.password)
		return net
