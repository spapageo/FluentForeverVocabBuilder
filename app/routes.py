import os
import re
import json

from flask import render_template, request, jsonify, send_from_directory

from app import app, forms
from app.service import forvo, wiktionary, images, anki_connect, linguee, reverso

ac = anki_connect.AnkiConnect()
save_path_pat = r".*(temp.*)"


@app.route('/')
def index():
    decks = ac.get_deck_names()
    form = forms.SearchForm()
    form.decks.choices = [(i, i) for i in decks]
    form.language.choices = [(l, l) for l in app.config["AVAILABLE_LANGUAGES"]]
    return render_template("index.html", decks=decks, form=form)


@app.route("/search")
def search():
    req = request.args
    word = req.get("word_query")
    deck_name = req.get("deck_name")
    language = req.get("language")
    search_result = wiktionary.search(word, language)
    form = forms.AnkiForm()
    form.ipa.data = search_result.get("ipa") or ""
    combo_choices = ["{}: {}".format(c[0], c[1]) for c in search_result.get("definitions")]
    form.word_usage.choices = [(i, i) for i in combo_choices]
    audio_filename = search_result.get("audio_filename")
    audio_relative_filename = ""
    if audio_filename:
        audio_relative_filename = re.findall(save_path_pat, audio_filename)[0].replace(os.sep, '/')
    else:
        audio_filename = forvo.download_audio(word, language)
        if audio_filename:
            audio_relative_filename = re.findall(save_path_pat, audio_filename)[0].replace(os.sep, '/')
        else:
            audio_relative_filename = ""

    form.image_query.data = word
    form.sentence_query.data = word
    form.test_spelling.data = True

    return render_template("search-results.html", word=word, deck=deck_name, form=form,
                           audio_filename=audio_relative_filename)


@app.route("/search-images")
def search_images():
    req = request.args
    word = req.get("word_query")
    language = req.get("language")
    image_paths = images.download_images(word, language)
    return jsonify(image_paths)


@app.route("/add", methods=["POST"])
def add():
    args = request.values
    word = args.get("word")
    deck = args.get("decks")
    ipa = args.get("ipa")
    word_usage = args.get("word_usage")
    audio_arg = args.get("audio_filename")
    sentence = args.get("sentence")
    sentence_blanked = args.get("sentence_blanked")
    if audio_arg:
        audio_filename = os.path.join(app.root_path, audio_arg)
    else:
        audio_filename = None
    json_image_paths = args.get("image_paths")
    parsed_json_image_paths = json.loads(json_image_paths)
    image_paths = list(map(images.format_json_image_path, parsed_json_image_paths))
    thumbnail_image_paths = list(map(images.generate_thumbnail, image_paths))
    notes = args.get("notes")
    test_spelling = args.get("test_spelling") or ""
    ac.add_sentence_note(deck_name=deck,
                word=word,
                image_paths=thumbnail_image_paths,
                word_usage=word_usage,
                notes=notes,
                recording_file_path=audio_filename,
                ipa_text=ipa,
                test_spelling=test_spelling,
                sentence=sentence,
                sentence_blanked=sentence_blanked)
    ac.sync()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/temp/<path:path>")
def get_temp_file(path):
    return send_from_directory("temp", path)

@app.route("/search-sentences")
def search_sentences():
    req = request.args
    word = req.get("word_query")
    language = req.get("language")
    sentence_data = linguee.get_sentences(word, language) + reverso.get_sentences(word, language)
    return jsonify(sentence_data)


@app.before_first_request
def init():
    app.config["web_driver"].init_driver()
    forvo.login()