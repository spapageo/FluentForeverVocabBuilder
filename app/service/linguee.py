from bs4 import BeautifulSoup
from app import app

cfg = app.config

base_url = "https://www.linguee.com/"

def get_target_language(language: str):
    if language.lower() != 'french':
        return 'french'
    else:
        return 'english'


def get_sentences(word: str, language: str):
    url = base_url + language.lower() + '-' + get_target_language(language) + \
        "/search?source=auto&source=" + language.lower() + "&query=" + word.replace(' ', '%20')
    print("Searching on {}".format(url))
    cfg["web_driver"].get_driver().get(url)
    soup = BeautifulSoup(cfg["web_driver"].get_driver().page_source, 'html.parser')
    response = []
    for section in soup.find_all('div', 'lemma featured'):
        response = response + [example.string
                               for example in section.find_all('span', 'tag_s')]
    
    response = [example.strip() for example in response if example != None and example.strip() != ""]
    print("Found sentences: {}".format(response))
    return response
