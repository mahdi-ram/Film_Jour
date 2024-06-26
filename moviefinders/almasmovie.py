import json
import re
from os import link

import requests
from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString, Tag

proxies = {
    "http": "http://127.0.0.1:2081",
    "https": "http://127.0.0.1:2081",
}

aderess = "https://filmgirbot.site"


def find_links(linkpage, type_):
    request = requests.get(linkpage)
    soup = bs(request.content, 'html.parser')
    dl_link = {}
    series_info = {}
    if type_ == "series":
        # Find all <h2> elements with class 'fs-20 text-main my-1'
        seasons = soup.find_all(
            'h2', class_='text-center fs-20 text-main my-1')

        for season in seasons:
            # Extract season number
            season_number = season.text.strip().split()[-1]
            links = []

            # Find all <a> elements within the next sibling <p> tags
            next_sibling = season.find_next_sibling('p')
            while next_sibling and next_sibling.name == 'p':
                link = next_sibling.find('a')
                if link and 'جستجوی زیرنویس' not in link.text:  # Skip subtitle links
                    quality = link.text.strip()
                    url = link['href']
                    links.append((quality, url))
                next_sibling = next_sibling.find_next_sibling('p')

            series_info[season_number] = dict(links)
        dl_link["HardSob"] = series_info
        return len(series_info), dl_link
    else:
        all_p = soup.find_all('p', class_='text-left direction-ltr')
        links = []
        for p in all_p:

            link = p.find('a')
            if link and 'جستجوی زیرنویس' not in link.text:  # Skip subtitle links
                quality = link.text.strip()
                url = link['href']
                links.append((quality, url))
            series_info["HardSob"] = dict(links)
        return "movie", series_info


def find_movie(imdbid):
    data = aderess+"/?showitem="+imdbid
    request = requests.get(data)
    soup = bs(request.content, 'html.parser')
    type_ = 0
    if soup.find('div', class_='seriesLinks'):
        type_ = "series"
    elif soup.find('div', class_='movieLinks'):
        type_ = "movie"
    else:
        data,type_=None ,None
    return data, type_


# print(find_links("https://filmgirbot.site/?showitem=tt15398776","ss"))
#print(find_movie("tt998997"))
