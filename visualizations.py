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

###toggle between 1 and 0: 1 to refresh, 0 to skip
hf.generateAllDatasets(sp,username,refresh=1)
hf.artistSegments()