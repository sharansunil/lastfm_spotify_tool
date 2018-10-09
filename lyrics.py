import pandas as pd
import requests
import json
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re


class LyricsGenerator:
	def __init__(self):
		self.token = '77eKBrbm6RQj4Sg0rxnmH7sFZwDcRmcRsBzde9en1SPcboe8Ilm2p8bt-2Ndr2zN'
		self.base_url = "http://api.genius.com"

	def prepareDf(self):
		df = pd.read_csv('exports/MasterTrackDatabase.csv')
		df = df.loc[:, ["track", "artist", "album"]].reset_index(drop=True)
		df.album = df.album.str.lower()
		df_top = pd.read_csv('exports/Top100.csv')
		x = list(df.album.unique())
		y = list(df_top.album.unique())
		f = []
		for item in y:
			rv = ()
			for sub in x:
				if sub == item:
					rv = (sub, item, True)
					break
				elif item in sub:
					rv = (sub, item, True)
					break
				elif sub in item:
					rv = (item, sub, True)
					break
				elif fuzz.partial_ratio(item, sub) > 95:
					rv = (sub, item, True)
			f.append(rv)
		f = set(f)
		f = list(f)
		f = pd.DataFrame(f, columns=['album', 'album_ref', 'truth']).dropna()
		df = pd.merge(df, f, how="left", on="album")
		df = df[df.truth == True]
		df.track = df.track.str.lower()
		df.track = df.track.apply(lambda x: x.replace('(remastered)', ''))
		df = df.reset_index(drop=True)
		dfs = df
		dfs = dfs.loc[:, ['track', 'artist']]
		search_track = []
		search_params = ['(', 'remastered', '- remastered','- remix', '- live', '- 1998', ' - ', '(2009']
		for track in dfs.track:
			rv = ()
			for param in search_params:
				if param in track:
					rv = (track, track.split(param)[0].strip())
				else:
					rv = (track, track)
			search_track.append(rv)
		search_track = pd.DataFrame(search_track, columns=['track', 'search_track'])
		dfs = pd.merge(dfs, search_track, how="left", on="track")
		dfs = dfs.sort_values(by="artist")
		dfs = dfs.loc[:, ["artist", "search_track"]]
		dfs = dfs.drop_duplicates().reset_index(drop=True)
		return dfs

	def request_song_info(self, song_title, artist_name):
		headers = {'Authorization': 'Bearer ' + self.token}
		search_url = self.base_url + '/search'
		data = {'q': artist_name + ' ' + song_title}
		response = requests.get(search_url, params=data, headers=headers)
		json = response.json()
		remote_song_info = None
		for hit in json['response']['hits']:
			if song_title.lower() in hit['result']['title'].lower():
				remote_song_info = hit['result']['url']
		return remote_song_info
	def getLyricsUrl(self,df):
		f = []
		for item in df.itertuples():
			track = item[2]
			artist = item[1]
			rv = [track, self.request_song_info(track, artist)]
			f.append(rv)
		f = pd.DataFrame(f, columns=['search_track', 'lyrics'])
		df = pd.merge(df, f, how="left", on="search_track", suffixes=('', '_'))
		return df
