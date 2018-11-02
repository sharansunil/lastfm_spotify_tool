from BaseClasses import Spotify_LastFM_Builder, LyricGenerator
import pandas as pd
#usernames
sp_username = '1177566421'
lastfm_username = "sharansunil"

#spotify-lastfm-gsheet-load and refresh
spotify_fm = Spotify_LastFM_Builder(
	lastfm_username=lastfm_username,
	sp_username=sp_username)
spotify_fm.setPassword("synystrax")

spotify_fm.update_datasets(
	# spotify refreshers - recommended to set at 0
	refresh_spotify=0,
	refresh_artist_viz=0,
	refresh_playlist_viz=0,
	# lastfm refreshers - recommended to set at 1
	lastfm_artistalbum=0,
	lastfm_tracks=0,
	refresh_gsheet=1
)


retdict = spotify_fm.load_datasets()
#genius lyric pull
lyr=LyricGenerator()
lyr.lyricController(retdict)
lyr.getMissingAlbums(retdict)
import matplotlib.pyplot as plt 
import seaborn as sns 
top100=retdict["top100"]
top100.columns
sns.set()
top100.overall=pd.Categorical(top100.overall,["PERFECT 10",'STRONG 9','DECENT 9','LIGHT 9','STRONG 8','DECENT 8'])
features=list(top100.select_dtypes('float64'))
for feature in features:
	top100.boxplot(feature,by="overall")
plt.show()
	
