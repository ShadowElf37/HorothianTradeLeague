import requests as reqs
from bs4 import BeautifulSoup

def scrape(url):
    return BeautifulSoup(reqs.get(url).text)