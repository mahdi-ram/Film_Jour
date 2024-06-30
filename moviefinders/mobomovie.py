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

aderess = "https://mobomovies1.site"


def process_series_data(data):
    seasons = {}
    for season_key, season_data in data.items():
        season_num = int(season_key)
        if season_num not in seasons:
            seasons[season_num] = {}

        for key, value in season_data.items():
            info = value['info']
            urls = value['urls']

            type_key = info['type']
            resolution_quality_codec = f"{info['resolution']} {
                info['quality']} {info['codec']} {info['encode']}"

            if type_key not in seasons[season_num]:
                seasons[season_num][type_key] = {}

            if resolution_quality_codec not in seasons[season_num][type_key]:
                seasons[season_num][type_key][resolution_quality_codec] = {}

            for url in urls:
                episode_title = url['title']
                episode_url = url['file']
                seasons[season_num][type_key][resolution_quality_codec][episode_title] = episode_url

    season_count = len(seasons)
    return season_count, seasons


def process_movie_data(data):
    movie = {}
    for file_type, files in data.items():
        file_info = {}
        for file_details in files:
            resolution = file_details['url_resolution']
            quality = file_details['url_quality']
            codec_encode = f"{
                file_details['url_codec']}/{file_details['url_encode']}"
            file_url = file_details['url_file']
            file_info[resolution+" "+quality+" "+codec_encode] = file_url
        movie[file_type] = file_info
    return movie


def find_links(post_id, type):
    data = {"post_id": post_id}
    request = requests.post(aderess+"/api/get-urls",
                            data=data)
    if type == "series":
        season, links = process_series_data(request.json())
        return season, links
    else:
        links = process_movie_data(request.json())
        return "movie", links


def find_movie(name, imdbid):
    request = requests.get(f'{aderess}/s/{name}')
    soup = bs(request.content, 'html.parser')
    posts = soup.find_all('article', class_='post-item')
    pagelink = list()
    for post in posts:

        img_tags = post.find_all('img', class_='thumbnail')
        for img in img_tags:
            if imdbid in img['src']:
                pagelinks = post.find('a', class_='mdb')
                if pagelinks:
                    pagelink.append(aderess+pagelinks['href'])
    data = list()
    li_tag=None
    if pagelink:
        request = requests.get(pagelink[0])
        soup = bs(request.content, 'html.parser')
        li_tag = soup.find('li', class_='tab-item',attrs={"data-target": "dls"})
    else:
        return None
    if li_tag:
        onclick_content = re.search(
            r"loadUrls\((\d+),\s*'(\w+)'\)", li_tag['onclick'])
        if onclick_content:
            number, text = onclick_content.groups()
            data.append(number)
            data.append(text)
    return data


#print(find_movie("WALL·E", "tt0910970"))
#print(find_links("6243","series"))
