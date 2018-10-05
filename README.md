# spotify+lastfm integration and visualization tool

This is a project/tool to integrate spotify and lastfm apis' to get a summary of your Spotify+LastFM libraries.
I have expanded the scope to include visualizing artist profiles, playlist feature distributions and dataset upload flexibility.
Please feel free to give feedback and advice about my code be it optimisation, cleaning or more features!

### TODO
- Build unit and integration tests
- Create website
- Create a more secure way of storing data

### What does each python file do?
- For readability, the files were split into functions and classes.
- BaseClasses contains information to generate the main builder classes for lastfm,spotify and google sheets.
- LastFmFunctions and SpotifyFunctions do what the names say. 
- Execution is handled only at run.py. 

### I found a bug?
Submit an issue

### I want to add something new!
Submit a pull request

### License
This project is licensed under The Unlicense

### Dependencies
- Python 3.6+ only
- pandas 0.23.4
- seaborn 0.9.0
- itertools
- pylast https://github.com/pylast/pylast
- spotipy https://spotipy.readthedocs.io/en/latest/# 
- gspread v3.0.1 https://gspread.readthedocs.io/en/latest/
- gspread_dataframe https://pythonhosted.org/gspread-dataframe/