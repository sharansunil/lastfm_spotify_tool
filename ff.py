import pandas as pd
import lyricsgenius as genius
import os
import unidecode
import sys

class LyricGenerator:

	def __init__(self):
		self.lyric_token = '77eKBrbm6RQj4Sg0rxnmH7sFZwDcRmcRsBzde9en1SPcboe8Ilm2p8bt-2Ndr2zN'

	def blockPrint(self):
		sys.stdout = open(os.devnull, 'w')

	def enablePrint(self):
		sys.stdout = sys.__stdout__

	def pullLyrics(self,df):
		api= genius.Genius(self.lyric_token,verbose=False)
		errors=[]
		for item in df.itertuples():
			artist=item[1]
			track=item[2]
			retstr='exports/lyric files/'+artist+'/'
			track=unidecode.unidecode(track)
			artist=unidecode.unidecode(artist)
			os.makedirs(os.path.dirname(retstr), exist_ok=True)
			self.blockPrint()
			try:
				song = api.search_song(track, artist)
				song.save_lyrics(retstr+track,verbose=False,overwrite=True)
			except Exception as e:
				errors.append([artist,track,e])
		self.enablePrint()
		len_err=len(errors)
		len_df=len(df.index)
		retstr= "{} lyrics attempted. {} successful. {} errors.".format(len_df,len_df-len_err,len_err)
		print(retstr)
		return errors