import pandas as pd
import numpy as np
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
from math import pi
from matplotlib.colors import ListedColormap
import subprocess
from time import sleep
import os

def show_tracks(playname, playid, tracks):
    retdic = []
    for  item in tracks['items']:
        track = item['track']
        artist = track['artists'][0]['name']
        trackname = track['name']
        album = track['album']['name']
        trackid = track['id']
        albumid = track['album']['id']
        artistid = track['artists'][0]['id']
        retarray = [playname, playid, artist, artistid,
                    album, albumid, trackname, trackid]
        retdic.append(retarray)
    return retdic

######PLAYLIST SET GENERATION############
def generateRefSet(sp,username):
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

    referenceDataset = pd.DataFrame(data=plArray, columns=[
                                    'Playlist', 'PlaylistID', 'Artist', 'ArtistID', 'Album', 'AlbumID', 'Trackname', 'TrackID'])
    referenceDataset.index.name = 'ID'
    return referenceDataset

def generateFeatureSet(df,sp,segment):
    df = df[[segment[0], segment[1]]]
    df = df.assign(Features=df.iloc[:, -1])
    features = df.iloc[:, -1].apply(sp.audio_features)
    chain = list(itertools.chain(*features))
    featdf = pd.DataFrame(chain)
    trackSet2 = pd.concat([df.iloc[:, 0:2], featdf], axis=1, join='outer')
    return trackSet2
def generatePlaylistSet(sp,username):
    trackColumns = ['Trackname', 'TrackID']
    df = generateRefSet(sp,username)
    featureSet = generateFeatureSet(df,sp,trackColumns)
    totalSet = pd.merge(df, featureSet, on=["Trackname", "TrackID"])
    keyMap = pd.DataFrame({'key': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 'music_key': [
                          "C", "C#", "D", "D#", "E", "E#", "F", "F#", "G", "G#", "A", "A#", "B", "B#"]})
    modalMap = pd.DataFrame({'mode': [0, 1], 'modality': ['Major', 'Minor']})
    totalSet = totalSet.merge(modalMap, on="mode")
    totalSet = totalSet.merge(keyMap, on="key")
    totalSet["modalityKey"] = totalSet["music_key"] + \
        " " + totalSet["modality"]
    totalSet = totalSet.drop_duplicates()
    totalSet = totalSet.sort_values(by=['Playlist'])
    return totalSet

#########SAVED TRACKS SET GENERATION###############
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

    df = pd.DataFrame(ret, columns=('Track', 'Artist',
                                    'Album', 'Date Added', 'Popularity', 'TrackID'))

    return df
def generateSavedTracksSet(sp):
    df = savedTracksDf(sp)
    df['Features'] = df.iloc[:, -1]
    sleep(30)
    print("wait over, getting features")
    try:
        features = df.iloc[:, -1].apply(sp.audio_features)
    except Exception as e:
        print(e)
    chain = list(itertools.chain(*features))
    df2 = pd.DataFrame(chain)
    df = pd.concat([df.iloc[:, 0:5], df2], axis=1, join='outer')
    keyMap = pd.DataFrame({'key': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 'music_key': [
                          "C", "C#", "D", "D#", "E", "E#", "F", "F#", "G", "G#", "A", "A#", "B", "B#"]})
    modalMap = pd.DataFrame({'mode': [0, 1], 'modality': ['Major', 'Minor']})
    df = df.merge(modalMap, on="mode")
    df = df.merge(keyMap, on="key")
    df["modalityKey"] = df["music_key"] + " " + df["modality"]
    df = df.drop_duplicates()
    df = df.sort_values(by=['Date Added'],ascending=False)
    df=df.iloc[:,1:-1]
    return df


#########CHOOSE BETWEEN PLAYLIST AND SAVED DATASET TO GENERATE#########
def updateDataset(key,sp,username):
    if key=="playlist":
        df = generatePlaylistSet(sp,username)
        df.to_csv('exports/playlistDB.csv')
    elif key=="saved":
        df=generateSavedTracksSet(sp)
        df.to_csv('exports/savedDB.csv')
    else:
        print("Wrong key")

###########CREATE VIZ#################
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
    plt.rcParams["figure.dpi"]=188
    # Ind1
    values = df.iloc[row].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=1, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.5)
    plt.title(title, size=14, color=color, y=1.08, weight='bold')
    plt.tight_layout()
def generatePlaylistPlots(df):
    # extract usable data
    playlistAnalysis = df.groupby(["Playlist"])['valence', 'energy', 'acousticness',
                                                'speechiness', 'danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)
    plNames = list(playlistAnalysis.index)
    # Create a color palette:
    sns.set_palette("pastel")
    cmap = ListedColormap(sns.color_palette(n_colors=256))
    sns.set()
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
    print("images generated")
def exportVisualizationDataset(df):
    playlistAnalysis = df.groupby(["Playlist"])['valence', 'energy', 'acousticness',
                                                'speechiness', 'danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)
    playlistAnalysis.to_csv('exports/playlistViz.csv')
def runRscript(filename):
    command = 'Rscript'
    path2script = filename
    cmd = [command, path2script]
    subprocess.check_output(cmd)
def exportArtistAlbumSegments(df):
    artistProfile = df.groupby(['Artist']).mean().loc[:, ['Popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness','liveness', 'speechiness', 'tempo', 'valence']].assign(no_albums=df.groupby(['Artist'])['Album'].nunique())
    albumProfile = df.groupby(['Album']).mean().loc[:, ['Popularity', 'acousticness', 'danceability','energy', 'instrumentalness', 'liveness', 'speechiness', 'tempo', 'valence']]
    artistProfile.to_csv('exports/artistProfile.csv')
    albumProfile.to_csv('exports/albumProfile.csv')

###########CREATE ARTIST DISTRIBUTIONS##############
def prepareArtistDf():
	df = pd.read_csv('exports/savedDB.csv')

	df['duration_min'] = df['duration_ms'].apply(lambda x: x/(1000*60)).round(2)
	df.drop(['duration_ms'], axis=1)
	return df
def getartistDist(df, artist, features):
	artistSet = df[df.Artist == artist]
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
	artistList = list(df.loc[:, 'Artist'].unique())
	features = ['valence', 'acousticness', 'instrumentalness',
             'energy', 'speechiness', 'Popularity', 'liveness']
	for artist in artistList:
		getartistDist(df, artist, features)


def generateAllDatasets(sp, username,refresh):
        ######playlist db generation
    if refresh==1:
        updateDataset("playlist", sp, username)
    df = pd.read_csv('exports/playlistDB.csv')
    exportVisualizationDataset(df)
    generatePlaylistPlots(df)
    runRscript('playlistPlots.R')
    #####break
    print('playlist done, 1 minute break')
    sleep(60)
    print('starting on saved db')
    #####saved songs db generation
    if refresh==1:
        updateDataset("saved", sp, username)
    df2 = pd.read_csv('exports/savedDB.csv')
    exportArtistAlbumSegments(df2)
    runRscript('savedPlots.R')
