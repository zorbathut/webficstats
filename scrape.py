from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from dateutil.parser import parse as dateutilparse
from urllib.parse import urlparse
import yaml
import strictyaml

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def words_of_entries(entries):
    words = 0
    for p in entries:
        words += len(p.get_text().split())
    return words

class PageInfo:
    def __init__(self, date, words, next):
        self.date = date
        self.words = words
        self.next = next

class StoryInfo:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.data = None;

class StoryData:
    def __init__(self):
        self.pages = []

def handle_page(url, nextvalidator):
    page = simple_get(url)
    html = BeautifulSoup(page, 'html.parser')

    date = dateutilparse(html.select_one('.entry-date').get_text())
    words = words_of_entries(html.select('.entry-content p')[1:-1])
    next = html.select('.entry-content p')[-1].find_all('a')[-1]['href']

    if not nextvalidator(next):
        next = None

    print(f'{url}, {date}: {words}, {next}')

    return PageInfo(date, words, next)

def handle_story(story):
    domain = urlparse(story.url).netloc

    # get rid of the last page, just in case it's changed (we expect this)
    if len(story.data.pages) > 0:
        story.data.pages.pop()

    # either use the final next if available, or the base URL
    if len(story.data.pages) > 0:
        url = story.data.pages[-1].next
    else:
        url = story.url

    while url != None:
        page = handle_page(url, lambda next: domain in next)
        story.data.pages += [page]
        url = page.next

def handle_stories(stories):
    for id, story in stories.items():
        handle_story(story)

def load_from_yaml():
    with open('stories.yaml', 'r') as f:
        raw = strictyaml.load(f.read())

    stories = {}
    for key, value in raw.items():
        stories[key.text] = StoryInfo(value['name'].text, value['url'].text)

    with open('cache.yaml', 'r') as f:
        cache = yaml.load(f)

    for key, value in stories.items():
        if key in cache:
            value.data = cache[key]
        else:
            value.data = StoryData()

    return stories

stories = load_from_yaml()
handle_stories(stories)

with open('cache.yaml', 'w') as f:
    yaml.dump({k: v.data for (k, v) in stories.items()}, f)
