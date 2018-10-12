# music analysis integration (spotify, lastfm, genius, gdrive)

This is a repo for my personal project to analyze my listening habits and music library. It currently encompasses an integration between spotify and lastfm to get listening and music data. A Gsheet integration is built to keep track of a labelled dataset I created for my favourite albums. A lyrics extraction feature has also been added and will be used for phase 2 which is sentiment analysis of lyrics and deploying a live website for the visualizations.

### TODO
- Sentiment Analysis for lyrics
- Create website for visualizations
- Create a more secure way of storing data

### What does each python file do?
- BaseClasses contains all builder classes for spotify,lastfm, gsheet and genius.
- Spotify and LastFm functions are built to be helper functions (built earlier, will integrate with BaseClasses soon)
- run is the main runner tool 

### License
This project is licensed under The Unlicense

### Dependencies
- Python 3.6+ only
- pandas 0.23.4
- seaborn 0.9.0
- itertools
- pylast 3.0 https://github.com/pylast/pylast
- spotipy 2.0 https://spotipy.readthedocs.io/en/latest/# 
- gspread v3.0.1 https://gspread.readthedocs.io/en/latest/
- gspread_dataframe https://pythonhosted.org/gspread-dataframe/
- fuzzywuzzy
- Selenium https://selenium-python.readthedocs.io/getting-started.html
- lyricsgenius https://github.com/johnwmillr/LyricsGenius#usage
- BeautifulSoup4

*Take note that you will need api tokens for spotify,lastfm,google developer and genius

