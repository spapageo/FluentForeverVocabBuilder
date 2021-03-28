import os


class Config(object):
    SECRET_KEY = "fluent-forever"
    WIKTIONARY_LANGUAGE = "french"
    NUM_IMAGES = 20 
    TEMP_DIR = os.path.join(os.getcwd(), "app", "temp")
    MAX_IMAGE_SIZE = (400, 400)
    SIMPLE_WORDS_NOTE_TYPE = "2. Picture Words"
    SENTENCE_NOTE_TYPE = "2. French Vocabulary Card Type"
    FORVO_USERNAME = ""
    FORVO_PASSWORD = ""
    AVAILABLE_LANGUAGES = [
        "Arabic",
        "Chinese",
        "Czech",
        "Danish",
        "Dutch",
        "English",
        "Estonian",
        "Finnish",
        "French",
        "German",
        "Greek",
        "Hebrew",
        "Hungarian",
        "Icelandic",
        "Italian",
        "Japanese",
        "Korean",
        "Latvian",
        "Lithuanian",
        "Norwegian",
        "Portuguese",
        "Polish",
        "Romanian",
        "Russian",
        "Spanish",
        "Swedish",
        "Turkish"
    ]
