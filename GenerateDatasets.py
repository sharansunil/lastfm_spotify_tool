import pandas as pd
import HelperFunctions as hf
from CredentialClass import SpotifyCredentials
from time import sleep

client_id = 'fe3712517e674d46b0dad0f1e83149cd'
client_secret = '4adc68cc4f874edc9a7a2b655d8ccaf0'
redirect_uri = 'https://facebook.com'

scope = 'user-library-read'
username = '1177566421'

myCred = SpotifyCredentials(client_id=client_id, client_secret=client_secret,
                            redirect_uri=redirect_uri, username=username, scope=scope)


sp = myCred.genAuth()

######playlist db generation
hf.updateDataset("playlist",sp,username)
df=pd.read_csv('exports/playlistDB.csv')
hf.exportVisualizationDataset(df)
hf.generatePlaylistPlots(df)
hf.runRscript('playlistPlots.R')

print('playlist done, 1 minute break')
sleep(60)
print('starting on saved db')
#####saved songs db generation
hf.updateDataset("saved", sp, username)
df2=pd.read_csv('exports/savedDB.csv')
hf.exportArtistAlbumSegments(df2)
print('saved db done')