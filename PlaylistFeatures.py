import pandas as pd
import HelperFunctions as hf
from CredentialClass import SpotifyCredentials

client_id = 'fe3712517e674d46b0dad0f1e83149cd'
client_secret = '4adc68cc4f874edc9a7a2b655d8ccaf0'
redirect_uri = 'https://facebook.com'

scope = 'user-library-read'
username = '1177566421'

myCred = SpotifyCredentials(client_id=client_id, client_secret=client_secret,
                            redirect_uri=redirect_uri, username=username, scope=scope)

sp = myCred.genAuth()
hf.updateDataset("saved",sp,username)
df=pd.read_csv('savedDB.csv')
# hf.exportVisualizationDataset(df)
# hf.generatePlaylistPlots(df)
# hf.runRscript('playlistPlots.R')

df.head()

artistProfile=df.groupby(['Artist']).mean().loc[:,['Popularity','acousticness','danceability','energy','instrumentalness','liveness','speechiness','tempo','valence']]
albumProfile=df.groupby(['Album']).mean().loc[:,['Popularity','acousticness','danceability','energy','instrumentalness','liveness','speechiness','tempo','valence']]
artistProfile= artistProfile.assign(no_albums=df.groupby(['Artist'])['Album'].nunique())

artistProfile