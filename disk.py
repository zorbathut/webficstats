
import story

import yaml
import strictyaml
import re
import time
import threading

from urllib.parse import urlparse, urljoin
from atomicwrites import atomic_write

def load_from_yaml():
    with open('stories.yaml', 'r') as f:
        raw = strictyaml.load(f.read())

    stories = {}
    for key, value in raw.items():
        stories[key.text] = story.StoryInfo(
            value['name'].text,
            value['url'].text,
            value['color'].text,
            value['contentclass'].text,
            value['validationclass'].text if 'validationclass' in value else None,
            value['validationtext'].text if 'validationtext' in value else None,
            value['nextlinkclass'].text,
            value['nextlinktext'].text,
            int(value['contentblockbegin'].text) if ('contentblockbegin' in value) else 0,
            int(value['contentblockend'].text) if ('contentblockend' in value) else 0,
            value['domains'] if 'domains' in value else urlparse(value['url'].text).netloc,
            value['zerolength'] if 'zerolength' in value else [],
            bool(value['finished'].text) if 'finished' in value else False,
            value['overridestart'].text if 'overridestart' in value else None,
        )

    try:
        with open('cache.yaml', 'r') as f:
            cache = yaml.load(f)
    except IOError:
        cache = None

    if cache == None:
        cache = {}

    for key, value in stories.items():
        if key in cache:
            value.data = cache[key]
        else:
            value.data = story.StoryData()

    return stories

cache_lock_inst = threading.Lock()
def cache_lock():
    global cache_lock_inst
    return cache_lock_inst

last_save = 0
def save_cache(optional = False):
    global last_save

    with cache_lock():
        if optional and last_save + 15 > time.time():
            return  # not yet

        with atomic_write('cache.yaml', overwrite=True) as f:
            yaml.dump({k: v.data for (k, v) in db().items()}, f)
            last_save = time.time()

database_storage = None
def db():
    global database_storage
    if database_storage is None:
        database_storage = load_from_yaml()
    return database_storage
