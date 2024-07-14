import requests
from bs4 import BeautifulSoup as bs
import re
search_link="https://empirebesttv29.cfd/?s="
def find_movie_and_links(imdbid:str):
    request = requests.get(search_link+imdbid)
    
    soup = bs(request.content, 'html.parser')
    post = soup.find('article', class_='post-item')
    link =post.find('a', class_='item')["href"]
    
    return link
print(find_movie_and_links("tt14452776")) 