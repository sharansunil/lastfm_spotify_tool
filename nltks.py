import nltk.classify.util 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import pandas as pd 
from fuzzywuzzy import fuzz 
import itertools 
from os import listdir
import unidecode 
import re
import os


def clean_all_lyrics():
	currlyr = pd.read_csv('exports/currentlyrics.csv')
	artists = currlyr.artist.unique().tolist()
	artists=[unidecode.unidecode(artist) for artist in artists]
	artists
	for artist in artists:
		path= "exports/lyric files/" + artist 
		items=listdir(path)
		for item in items:
			f = open(path+'/'+item, 'rb')
			all_words = ''
			for sentence in f.readlines():
				all_words += sentence
			f.close()
			#remove identifiers like chorus, verse, etc
			all_words = re.sub(r'[\(\[].*?[\)\]]', '', all_words)
			#remove empty lines
			all_words = os.linesep.join([s for s in all_words.splitlines() if s])
			f = open(path+'/'+item, 'wb')
			f.write(all_words.encode('utf-8'))
			f.close()
	print("all songs cleaned")

clean_all_lyrics()