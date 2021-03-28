import os
from time import sleep
from selenium.common import exceptions
from pathlib import Path
from app import app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

cfg = app.config

def login():
    try:
        cfg["web_driver"].get_driver().get("https://forvo.com/login/")
        cfg["web_driver"].get_driver().find_element_by_id("login").send_keys(cfg["FORVO_USERNAME"])
        cfg["web_driver"].get_driver().find_element_by_id("password").send_keys(cfg["FORVO_PASSWORD"])
        cfg["web_driver"].get_driver().find_element_by_xpath("//*[@id='displayer']/div/section/form/div[2]/label").click()
        cfg["web_driver"].get_driver().find_element_by_id("password").send_keys(Keys.ENTER)
        print("Successfully logged in to forvo")
        return True
    except exceptions.NoSuchElementException:
        print("Failed to login to forvo")

language_to_code = {
    "french": "fr"
}


def get_latest_file_in_download_folder() -> Path:
    paths = [f for f in sorted(Path(cfg["web_driver"].download_path).iterdir(), key=os.path.getmtime, reverse=True) if f.is_file()]
    if len(paths) == 0:
        return None
    
    return paths[0].absolute().resolve()

def download_audio(word:str, language:str):
    code = language_to_code[language.lower()]
    word_with_underscores = word.replace(' ', '_')
    if (code == None):
        return ""
    url = "https://{}.forvo.com/word/{}/".format(code, word_with_underscores)
    print("Searching on: " + url)
    cfg["web_driver"].get_driver().get(url)

    try:
        element = cfg["web_driver"].get_driver().find_element_by_xpath("//*[@id=\"language-container-{}\"]/article[1]/ul/li[1]/div/div/p[3]".format(code))
        actions = ActionChains(cfg["web_driver"].get_driver())
        try:
            actions.move_to_element(element).perform()
        except:
            print("Failed to scroll to element")

        element.click()
        
        for i in range(3):
            latest_file = get_latest_file_in_download_folder()
            latest_file_string = str(latest_file)
            print("Found path: " + latest_file_string)
            if latest_file != None and latest_file_string.endswith('.mp3') and latest_file_string.find(word_with_underscores) != -1:
                print("Found mp3: " + latest_file_string)
                return latest_file_string
            else:
                print("File did not match criteria will wait")
                sleep(0.5)

        return ""
    except exceptions.NoSuchElementException:
        print("Failed to find the download using the audio button")
        return ""
    


