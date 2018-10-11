import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
from bs4 import BeautifulSoup as bs
import os
import itertools
from string import punctuation
from time import time
from time import sleep
driver = webdriver.Chrome()
def loadFiles():
	with open('exports/errors.csv', 'r') as f:
		reader = csv.reader(f)
		f = list(reader)
	f = list(itertools.chain(*f))
	os.chdir("exports/lyric files")
	return f

def scrapeToPage(driver, item):
	driver.get("https://genius.com/")
	elem = driver.find_element_by_name("q")
	elem.clear()
	elem.send_keys(item)
	el_one = elem.send_keys(Keys.RETURN)
	sleep(20)
	el_one = driver.find_element_by_tag_name("search-result-item")
	el_one.click()
	el_two = driver.page_source
	return el_two


def writeAll(driver):
	df = loadFiles()
	for item in df:
		try:
			ret = scrapeToPage(driver, item)
		except Exception as e:
			print(e)
		html = bs(ret, "html.parser")
		lyrics = html.find("div", class_="lyrics").get_text("\n")
		lyrics = lyrics.lstrip('\n')
		lyrics = lyrics.rstrip('\n')
		with open(item+".txt", "w") as text_file:
			text_file.write(lyrics)
	driver.delete_all_cookies()
writeAll(driver)
