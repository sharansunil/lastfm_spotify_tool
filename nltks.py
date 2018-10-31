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
	artists=[artist for artist in artists]
	for artist in artists:
		path= "exports/lyric files/" + artist 
		items=listdir(path)
		if len(items)>0:
			try:
				for item in items:
					if item != '.DS_Store':
						data=''
						with open(path+'/'+item, 'r') as myfile:
							data=myfile.read()
							data = re.sub(r'[\(\[].*?[\)\]]', '', data)
						#remove empty lines
							data = os.linesep.join([s for s in data.splitlines() if s])
						with open(path+'/'+item,'w') as myfile:
							myfile.write(data)
			except Exception as e:
				print ("error occurred at {}\n with error {}".format(artist+' '+ item,e))
	print("all songs cleaned")


artists=["Radiohead"]
for artist in artists:
	path = "exports/lyric files/" + artist 	
	num_words = 0
	all_words=[]
	all_filtered_words=[]
	
	items=listdir(path)
	for item in items:
		if item != '.DS_Store':
			data = ''
			with open(path+'/'+item, 'r') as myfile:
				data = myfile.read()
			words=data.split(" ")
			filtered_words = [word for word in words if word not in stopwords.words('english') and len(word) > 1 and word not in ['na', 'la']]


	df.loc[i] = (artist, num_words)
	i += 1

df.plot.bar(x='artist', y='words', title='Number of Words for each Artist')
plt.show()
