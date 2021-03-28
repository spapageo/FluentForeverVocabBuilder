import os
from pathlib import Path

from selenium import webdriver


class WebDriver(object):
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        self.driver = None

    def init_driver(self):
        self.download_path = os.path.join(
            os.getcwd(), self.temp_dir, "download")
        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        options = webdriver.ChromeOptions()
        options.set_headless()
        profile = {"download.prompt_for_download": False,
                   "download.directory_upgrade": True,
                   "download.default_directory": str(self.download_path)}
        options.add_experimental_option("prefs", profile)
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(chrome_options=options)

    def driver_cleanup(self):
        if self.driver != None:
            print("Requesting from the browser to quit")
            self.driver.quit()

    def get_driver(self):
        return self.driver
