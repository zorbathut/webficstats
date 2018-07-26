
from web import *
from disk import *

from bs4 import BeautifulSoup
from dateutil.parser import parse as dateutilparse
from urllib.parse import urlparse, urljoin
import itertools

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
    def __init__(self, name, url, nextlink):
        self.name = name
        self.url = url
        self.nextlink = nextlink
        self.data = None;

    def words_total(self):
        return sum(page.words for page in self.data.pages)

class StoryData:
    def __init__(self):
        self.pages = []

def handle_page(url, nextvalidator):
    page = simple_get(url)
    html = BeautifulSoup(page, 'html.parser')

    date = dateutilparse(html.select_one('.entry-date').get_text())
    words = words_of_entries(html.select('.entry-content p')[1:-1])

    next = None
    for link in html.select('.entry-content p a'):
        if nextvalidator(link):
            next = urljoin(url, link['href'])

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
        page = handle_page(url, lambda next: story.nextlink == next.text.strip() and domain in next['href'])
        story.data.pages += [page]
        url = page.next
        save_cache()

def handle_stories():
    for id, story in db().items():
        handle_story(story)
