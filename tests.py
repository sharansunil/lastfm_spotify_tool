import pandas as pd 
from BaseClasses import Spotify_LastFM_Builder,LyricGenerator
from fuzzywuzzy import fuzz
import unidecode
import re
sp_username = '1177566421'
lastfm_username = "sharansunil"

#spotify-lastfm-gsheet-load and refresh
spotify_fm = Spotify_LastFM_Builder(
	lastfm_username=lastfm_username,
	sp_username=sp_username)
retdict = spotify_fm.load_datasets()

def cleanString(s):
	s = s.strip()
	s = s.lower()
	markers = ["|", "-"]
	indices = [(i, x) for i, x in enumerate(s) if x in markers]
	if indices != []:
		mins = indices[0]
		s= s.split(mins[1])[0].strip()
	dirt=["/",":",".","(",")"]
	for x in dirt:
		s=s.replace(x,'')
	s=re.sub(' +',' ',s)
	return s


def getMissingAlbums(retdict):
	curr=pd.read_csv("exports/currentlyrics.csv")
	top100=retdict["top100"].loc[:,["artist","album","best song"]]
	tracks=retdict["tracks"].loc[:,["artist","album","track"]]
	top100=top100.applymap(cleanString)
	tracks=tracks.applymap(cleanString).reset_index(drop=True)
	curr=curr.applymap(cleanString)
	top100=top100.assign(inCurr=top100.iloc[:,-1].isin(curr.track))
	errs=top100[top100.inCurr==False]
	errs.index = errs.album
	errs = errs.drop('album', axis=1)
	errs=errs.drop(["harutosyura","jord"])
	currerrs=curr[curr.artist.isin(errs.artist)]
	for item in errs.itertuples():
		errtrack=item[2]
		errart=item[1]
		for trx in currerrs.itertuples():
			basetrx=trx[2]
			baseart=trx[1]
			if errtrack in basetrx:
				errs=errs.drop(item[0])
				break
	return errs