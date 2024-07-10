import json
import re
from os import link

import requests
from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString, Tag

aderess = "https://filmgirbot.site"

def find_movie_and_links(imdbid):
    data = aderess + "/?showitem=" + imdbid
    request = requests.get(data)
    soup = bs(request.content, 'html.parser')
    type_ = None
    
    if soup.find('div', class_='seriesLinks'):
        type_ = "series"
    elif soup.find('div', class_='movieLinks'):
        type_ = "movie"
    
    if not type_:
        return None
    
    series_info = {}
    
    if type_ == "series":
        seasons = soup.find_all('h2', class_='text-center fs-20 text-main my-1')

        for season in seasons:
            season_number = season.text.strip().split()[-1]
            links = []
            ader = {}
            next_sibling = season.find_next_sibling('p')
            while next_sibling and next_sibling.name == 'p':
                link = next_sibling.find('a')
                if link and 'زیرنویس' not in link.text:
                    quality = link.text.strip()
                    url = link['href']
                    links.append((quality, url))
                next_sibling = next_sibling.find_next_sibling('p')
            ader["HardSub"] = links
            series_info[season_number] = ader
        
        mobo = {}
        for season, qualities in series_info.items():
            mobo[int(season)] = {'HardSub': {}}
            for quality, episodes in qualities.items():
                for episode in episodes:
                    por = {}
                    quality_name = episode[0]
                    por["تمامی قسمت ها"] = episode[1]
                    mobo[int(season)]['HardSub'][quality_name] = por
        return len(series_info), mobo
    
    else:
        all_p = soup.find_all('p', class_='text-left direction-ltr')
        links = []
        for p in all_p:
            link = p.find('a')
            if link and 'زیرنویس' not in link.text:
                quality = link.text.strip()
                url = link['href']
                links.append((quality, url))
            series_info["HardSob"] = dict(links)
        return "movie", series_info


#print(find_movie_and_links("tt19231492"))
