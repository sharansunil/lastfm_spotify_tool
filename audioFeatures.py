import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi  
import getPlaylists as gp
import spotifyInit as spi
from matplotlib.colors import ListedColormap
#import token
token = spi.token
#uncomment if want to refresh dataset
#x=gp.updateDataset()
df=pd.read_csv('playlistDB.csv')

playlistAnalysis = df.groupby(["Playlist"])['valence', 'energy', 'acousticness', 'speechiness','danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)
# Create a color palette:
sns.set_palette("pastel")
cmap = ListedColormap(sns.color_palette(n_colors=256))

plNames=list(playlistAnalysis.index)
playlistAnalysisMean = pd.DataFrame(playlistAnalysis.mean())
playlistAnalysisMean = playlistAnalysisMean.transpose()
playlistAnalysisMean.index.name = "Average Playlist"
# Loop to plot
for row in range(0, len(playlistAnalysis.index)):
    plt.clf()
    gp.make_spider(df=playlistAnalysisMean, row=0, title="", color='grey')
    gp.make_spider(df=playlistAnalysis,row=row, title=plNames[row], color=cmap(row))
    plt.savefig('plots/'+plNames[row])

print("done") 
