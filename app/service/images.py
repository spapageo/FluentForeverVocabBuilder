import os
import re
from urllib.parse import unquote
from tempfile import NamedTemporaryFile
from mimetypes import guess_extension
import base64
from typing import List
from time import time as timer
from multiprocessing.pool import ThreadPool

from PIL import Image
from bing_images import bing
from app import app
import requests
import shutil

cfg = app.config

cwd = os.getcwd()
save_path_pat = r".*(temp.*)"



def download_image(url, path):
    try:
        r = requests.get(url, stream=True, timeout=(1, 1))
        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    except:
        return

def download_image_with_thread(entry):
    url, path, index = entry
    print("Downloading image #{} from {}".format(index, url))
    download_image(url, path)
    return index


def download_images_from_bing(
    query: str,
    limit: int,
    output_dir: str,
    pool_size: int = 20,
    adult: bool = True,
    file_type: str = '',
    filters: str = '',
    force_replace=False
):
    urls = bing.fetch_image_urls(query, limit, adult, file_type, filters)
    index = 1
    entries = []
    for url in urls:
        name = bing.file_name(url, index, query)
        path = os.path.join(output_dir, name)
        entries.append((url, path, index))
        index += 1

    start = timer()

    ps = pool_size
    if limit < pool_size:
        ps = limit
    results = ThreadPool(ps).imap_unordered(
        download_image_with_thread, entries)

    print("Done")
    elapsed = timer() - start
    print("Elapsed Time: %.2fs" % elapsed)
    return [entries[index - 1][1] for index in results]

def download_images(query: str, language=None) -> List[str]:
    paths = download_images_from_bing(query, limit=cfg["NUM_IMAGES"], output_dir=cfg["TEMP_DIR"])
    print(paths)
    relative_paths = [re.findall(save_path_pat, p)[0].replace(os.sep, '/') for p in paths if p]
    return relative_paths


def generate_thumbnail(path: str) -> str:
    filename = os.path.splitext(path)[0]
    ext = os.path.splitext(path)[1]

    thumb_filename = filename + ".thumb" + ext
    thumbnail_img = Image.open(path)
    thumbnail_img.thumbnail(cfg["MAX_IMAGE_SIZE"], Image.ANTIALIAS)
    thumbnail_img.save(thumb_filename, format=thumbnail_img.format)
    return thumb_filename


def format_json_image_path(json_path: str) -> str:
    if json_path.startswith("data:image"):
        absolute_image_path = save_base64_image_data(json_path)
    else:
        image_path_relative_to_temp_dir = re.findall(save_path_pat, json_path)[0]
        unquoted_image_path = unquote(image_path_relative_to_temp_dir)
        absolute_image_path = os.path.join(app.root_path, unquoted_image_path)
    return absolute_image_path


def save_base64_image_data(data_string: str) -> str:
    data_pat = r"data:(image\/.*);base64,(.*)"
    match = re.search(data_pat, data_string)
    if len(match.groups()) > 1:
        ext = guess_extension(match[1])
        data = match[2].encode()
        with NamedTemporaryFile(mode='wb', dir=os.path.join(app.root_path, "temp"), suffix=ext, delete=False) as f:
            f.write(base64.decodebytes(data))
            return f.name
