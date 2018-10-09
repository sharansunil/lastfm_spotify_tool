from lyrics import LyricsGenerator
import pandas as pd
import requests
import json
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re

l=LyricsGenerator()
df=l.getLyricsUrl()


