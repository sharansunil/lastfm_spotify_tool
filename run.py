from BaseClasses import Spotify_LastFM_Builder,LyricGenerator
import pandas as pd

sp_username = '1177566421'
lastfm_username = "sharansunil"

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
