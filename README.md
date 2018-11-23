# music analysis integration (spotify, lastfm, genius, gdrive)

This is a personal project to analyze my listening habits and the features of my music library via Spotify and LastFm. A Gsheet integration is built to keep track of a dynamic labelled dataset I created for my favourite albums. A lyrics extraction feature using Genius has been completed and will be used for phase 2 which is sentiment analysis of lyrics and deploying a live website for the visualizations. I intend to expand on the scope of this project over the next year and welcome any interesting suggestions. 

### TODO
- Sentiment Analysis for lyrics
- Create plotly based website for interactive visualizations


### What does each python file do?
- BaseClasses contains all builder classes for spotify,lastfm, gsheet and genius.
- run is the execution/testing ground

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
- unidecode

*Take note that you will need api tokens for spotify,lastfm,google developer and genius if you plan to fork parts of the code for yourself

