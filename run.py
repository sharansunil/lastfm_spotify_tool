from BaseClasses import Spotify_LastFM_Builder, LyricGenerator
#usernames

SP_USERNAME='1177566421'
LASTFM_USERNAME='sharansunil'

#spotify-lastfm-gsheet-load and refresh
spotify_fm = Spotify_LastFM_Builder(
	lastfm_username=LASTFM_USERNAME,
	sp_username=SP_USERNAME)
spotify_fm.update_datasets(
	# spotify refreshers - recommended to set at 0
	refresh_spotify=1,
	refresh_artist_viz=1,
	refresh_playlist_viz=1,
	# lastfm refreshers - recommended to set at 1
	lastfm_artistalbum=1,
	lastfm_tracks=1,
	refresh_gsheet=1
)


retdict = spotify_fm.load_datasets()
#genius lyric pull
lyr=LyricGenerator()
lyr.lyricController(retdict)