import spotipy
import spotipy.util as util

client_id='fe3712517e674d46b0dad0f1e83149cd'
client_secret= '4adc68cc4f874edc9a7a2b655d8ccaf0'
redirect_uri='https://facebook.com'

scope = 'user-library-read'
username='1177566421'
token = util.prompt_for_user_token(username=username,scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)



def genAuth():
    sp = spotipy.Spotify(auth=token)
    return sp,username 

def show_tracks(playname,playid,tracks):
    retdic=[]
    for i,item in enumerate(tracks['items']):
        track = item['track']
        artist=track['artists'][0]['name']
        trackname=track['name']
        album=track['album']['name']
        trackid=track['id']
        albumid=track['album']['id']
        artistid=track['artists'][0]['id']
        retarray=[playname,playid,artist,artistid,album,albumid,trackname,trackid]
        retdic.append(retarray)
    return retdic 