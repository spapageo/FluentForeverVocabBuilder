from urllib.request import urlopen
from bs4 import BeautifulSoup
from app import app

cfg = app.config


base_url = "https://context.reverso.net/translation/{}-{}/{}?utm_source=reversoweb&utm_medium=contextresults&utm_campaign=resultpage"

def get_target_language(language: str):
    if language.lower() != 'french':
        return 'french'
    else:
        return 'english'


def get_sentences(word: str, language: str):
    url = base_url.format(language.lower(), get_target_language(
        language), word.replace(' ', '%20'))
    print("Searching on {}".format(url))
    cfg["web_driver"].get_driver().get(url)
    soup = BeautifulSoup(cfg["web_driver"].get_driver().page_source, 'html.parser')
    response = [' '.join(example.stripped_strings) for example in soup.find_all('div', "src ltr")]
    response = [example.strip() for example in response if example.strip() != ""]
    print("Found sentences: {}".format(response))
    return response
