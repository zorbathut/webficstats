
import story

import yaml
import strictyaml

def load_from_yaml():
    with open('stories.yaml', 'r') as f:
        raw = strictyaml.load(f.read())

    stories = {}
    for key, value in raw.items():
        stories[key.text] = story.StoryInfo(value['name'].text, value['url'].text, value['nextlink'].text)

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

def save_cache():
    with open('cache.yaml', 'w') as f:
        yaml.dump({k: v.data for (k, v) in db().items()}, f)

database_storage = None
def db():
    global database_storage
    if database_storage is None:
        database_storage = load_from_yaml()
    return database_storage
