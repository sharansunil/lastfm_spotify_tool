import pandas as pd
import numpy as np
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
from math import pi
from matplotlib.colors import ListedColormap
import os
import os.path

"""extracts data from Track object"""
def show_tracks(playname, playid, tracks):
	retdic = []
	for item in tracks['items']:
		track = item['track']
		artist = track['artists'][0]['name']
		trackname = track['name']
		album = track['album']['name']
		trackid = track['id']
		albumid = track['album']['id']
		artistid = track['artists'][0]['id']
		dateadded = item['added_at']
		retarray = [playname, playid, artist, artistid,
					album, albumid, trackname, dateadded, trackid]
		retdic.append(retarray)
	return retdic


"""playlist set generation"""
def generatePlaylistSet(sp, username):
	playlists = sp.user_playlists(username)
	playlistarray = []
	for playlist in playlists['items']:
		playname = playlist['name']
		playid = playlist['id']
		results = sp.user_playlist(
			username, playlist['id'], fields="tracks,next")
		tracks = results['tracks']
		x = show_tracks(playname, playid, tracks)
		playlistarray.append(x)
	plArray = list(itertools.chain(*playlistarray))
	df = pd.DataFrame(
		data=plArray, 
		columns=['playlist', 'playlistID', 'artist', 'artistID', 'album', 'albumID', 'trackname', 'date_added', 'trackID'])
	df.index.name = 'ID'
	trackColumns = ['trackname', 'trackID']
	df2 = df[[trackColumns[0], trackColumns[1]]]
	df2 = df2.assign(Features=df.iloc[:, -1])
	features = df2.iloc[:, -1].apply(sp.audio_features)
	chain = list(itertools.chain(*features))
	featdf = pd.DataFrame(chain)
	trackSet2 = pd.concat([df2.iloc[:, 0:2], featdf], axis=1, join='outer')
	totalSet = pd.merge(df, trackSet2, on=["trackname", "trackID"])
	totalSet = totalSet.drop_duplicates()
	totalSet = totalSet.sort_values(by=['playlist'])
	return totalSet

"""saved tracks set generation"""
def savedTracksDf(sp):
	offset = 0
	ret = []
	while offset < 2000:
		results = sp.current_user_saved_tracks(limit=50, offset=offset)
		for item in results['items']:
			track = item['track']
			date_added = item['added_at']
			date_added = date_added[:10]
			tup = [track['name'], track['artists'][0]['name'],
				   track['album']['name'], date_added, track['popularity'], track['id']]
			ret.append(tup)
		offset += 50
	df = pd.DataFrame(ret, columns=('track', 'artist','album', 'date_added', 'popularity', 'trackID'))
	df['Features'] = df.iloc[:, -1]
	try:
		features = df.iloc[:, -1].apply(sp.audio_features)
	except Exception as e:
		print(e)
	chain = list(itertools.chain(*features))
	df2 = pd.DataFrame(chain)
	df = pd.concat([df.iloc[:, 0:5], df2], axis=1, join='outer')
	df = df.drop_duplicates()
	df = df.sort_values(by=['date_added'], ascending=False)
	return df

"""update dataset controller"""
def updateDataset(sp, username,key="both"):
	curdir = os.getcwd()
	newdir = os.path.join(curdir, r'exports')
	os.makedirs(newdir, exist_ok=True)
	if  key == "both":
		df1 =savedTracksDf(sp)
		df1.to_csv('exports/savedDB.csv', index=False)
		df = generatePlaylistSet(sp, username)
		df.to_csv('exports/playlistDB.csv', index=False)
	elif key == "playlist":
		df = generatePlaylistSet(sp, username)
		df.to_csv('exports/playlistDB.csv', index=False)
	elif key == "saved":
		df = savedTracksDf(sp)
		df.to_csv('exports/savedDB.csv', index=False)
	else:
		print("Wrong key")


"""generate playlist profile plots"""
def make_spider(df, row, title, color):
	# number of variable
	categories = list(df)
	N = len(categories)
	# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
	angles = [n / float(N) * 2 * pi for n in range(N)]
	angles += angles[:1]
	# Initialise the spider plot
	ax = plt.subplot(111, polar=True,)
	# If you want the first axis to be on top:
	ax.set_theta_offset(pi / 2)
	ax.set_theta_direction(-1)
	plt.xticks(angles[:-1], categories, color='gray', size=8)
	# Draw ylabels
	ax.set_rlabel_position(0)
	plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4",
									  "0.6", "0.8"], color="grey", size=7)
	plt.ylim(0, 1)
	plt.rcParams["figure.dpi"] = 188
	# Ind1
	values = df.iloc[row].values.flatten().tolist()
	values += values[:1]
	ax.plot(angles, values, color=color, linewidth=1, linestyle='solid')
	ax.fill(angles, values, color=color, alpha=0.5)
	plt.title(title, size=14, color=color, y=1.08, weight='bold')
	plt.tight_layout()

def generatePlaylistPlots(df):
	# extract usable data
	playlistAnalysis = df.groupby(["playlist"])['valence', 'energy', 'acousticness',
												'speechiness', 'danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)
	plNames = list(playlistAnalysis.index)
	# Create a color palette:
	sns.set_palette("pastel")
	cmap = ListedColormap(sns.color_palette(n_colors=256))
	sns.set()
	curdir = os.getcwd()
	newdir = os.path.join(curdir, r'playlistPlots')
	os.makedirs(newdir, exist_ok=True)
	# initialise average dataset
	playlistAnalysisMean = pd.DataFrame(playlistAnalysis.mean())
	playlistAnalysisMean = playlistAnalysisMean.transpose()

	# Loop to plot
	for row in range(0, len(playlistAnalysis.index)):
		plt.clf()
		make_spider(df=playlistAnalysisMean, row=0, title="", color='grey')
		make_spider(df=playlistAnalysis, row=row,
					title=plNames[row], color=cmap(row))
		plt.savefig('playlistPlots/'+plNames[row]+'.svg')


"""generate artist distribution plots"""
def prepareArtistDf():
	df = pd.read_csv('exports/savedDB.csv')
	df['duration_min'] = df['duration_ms'].apply(lambda x: x/(1000*60)).round(2)
	df.drop(['duration_ms'], axis=1)
	return df

def getartistDist(df, artist, features):
	artistSet = df[df.artist == artist]
	filename = "artistDistribution/"+artist+"/"
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	for feature in features:
		plt.clf()
		sns.kdeplot(artistSet.loc[:, feature], label=artist, shade=True)
		sns.kdeplot(df.loc[:, feature], label="Dataset", shade=True)
		plt.title(feature.capitalize() + " distribution of " + artist)
		plt.legend()
		plt.savefig(filename+artist+" "+feature+".png")

def artistSegments():
	df = prepareArtistDf()
	sns.set(color_codes=True)
	artistList = list(df.loc[:, 'artist'].unique())
	features = ['valence', 'acousticness', 'instrumentalness',
			 'energy', 'speechiness', 'popularity', 'liveness']
	for artist in artistList:
		getartistDist(df, artist, features)


"""	main controller for all functions
	if playlist toggled to 0 no playlist graphs will be generated
	if artist is toggled to 0 no artist distribution folder and graphs will be created """
def generateAllDatasets(sp, username, refresh=1, playlists=1, artist=1):
	refpr = "done"
	plpr = "done"
	art = "done"
	retstr = ""
	if refresh == 1:
		updateDataset(sp,username,key="both")
	else:
		refpr = "omitted"
	df = pd.read_csv('exports/playlistDB.csv')
	if playlists == 1:
		generatePlaylistPlots(df)
	else:
		plpr = "omitted"
	if artist == 1:
		artistSegments()
	else:
		art = "omitted"
	if refresh + playlists + artist == 0:
		retstr = "Spotify not updated, proceeding to lastfm. Datasets can be found in playlistDB.csv and savedDB.csv"
	else:
		retstr = "Spotify updated with refresh {}, playlists {} and artists {}".format(
			refpr, plpr, art)
	print(retstr)
