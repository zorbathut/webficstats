
from web import *
from disk import *

from bs4 import BeautifulSoup
from dateutil.parser import parse as dateutilparse
from urllib.parse import urlparse, urljoin
import itertools
import threading

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
    def __init__(self, name, url, nextlinkclass, nextlinktext, contentblockbegin, contentblockend, domains, zerolength):
        self.name = name
        self.url = url
        self.nextlinkclass = nextlinkclass
        self.nextlinktext = nextlinktext
        self.contentblockbegin = contentblockbegin
        self.contentblockend = contentblockend
        self.domains = domains
        self.zerolength = zerolength
        self.data = None;

    def words_total(self):
        return sum(page.words for page in self.data.pages)

    def contentblock_crop(self, blocks):
        if self.contentblockend != 0:
            return blocks[self.contentblockbegin:-self.contentblockend]
        elif self.contentblockbegin != 0:
            return blocks[self.contentblockbegin:]
        else:
            return blocks

class StoryData:
    def __init__(self):
        self.pages = []

def handle_page(url, story):
    page = simple_get(url)
    html = BeautifulSoup(page, 'html.parser')

    date = dateutilparse(html.select_one('.entry-date').get_text())
    words = words_of_entries(story.contentblock_crop(html.select('.entry-content p')))

    if words <= 0 and url not in story.zerolength:
        raise RuntimeError(f'Zero words detected in chapter {url}; that is never right')

    for link in html.select(story.nextlinkclass):
        if re.match(story.nextlinktext, link.text.strip()) and urlparse(link['href']).netloc in story.domains:
            next = urljoin(url, link['href'])
            break
    else:
        next = None

    print(f'{url}, {date}: {words}, {next}')

    return PageInfo(date, words, next)

def handle_story(story):
    # get rid of the last page, just in case it's changed (we expect this)
    if len(story.data.pages) > 0:
        with cache_lock():
            story.data.pages.pop()

    # either use the final next if available, or the base URL
    if len(story.data.pages) > 0:
        url = story.data.pages[-1].next
    else:
        url = story.url

    while url != None:
        page = handle_page(url, story)
        with cache_lock():
            story.data.pages += [page]
        url = page.next
        save_cache(optional = True)

def handle_stories():
    threads = []
    for id, story in db().items():
        threads.append(threading.Thread(target = lambda: handle_story(story)))
        threads[-1].start()

    for thread in threads:
        thread.join()

    save_cache()
