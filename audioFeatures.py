import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi  
import getPlaylists as gp
import spotifyInit as spi

#import token
token = spi.token

df = gp.generateMaster()
writeDf = df.to_csv('playlistDB.csv')

playlistAnalysis = df.groupby(["Playlist"])['valence', 'energy', 'acousticness', 'speechiness','danceability', 'instrumentalness', 'liveness', 'mode'].mean().round(3)


def make_spider(df, row, title, color):

        # number of variable
    categories = list(df)[1:]
    N = len(categories)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    ax = plt.subplot(5, 6, row+1, polar=True, )

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='grey', size=8)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.2,0.4,0.6,0.8], ["0.2","0.4","0.6","0.8"], color="grey", size=7)
    plt.ylim(0, 1)

    # Ind1
    values = df.loc[row].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)

    # Add a title
    plt.title(title, size=11, color=color, y=1.1)

my_dpi = 96

plt.figure(figsize=(1000/my_dpi, 1000/my_dpi), dpi=my_dpi)

# Create a color palette:
my_palette = plt.cm.get_cmap("Set2", len(playlistAnalysis.index))

# Loop to plot
for row in range(0, len(playlistAnalysis.index)):
    make_spider(df=playlistAnalysis,row=row, title=playlistAnalysis.index[row], color=my_palette(row))

plt.show()
