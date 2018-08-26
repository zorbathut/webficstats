
import web
import disk

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import itertools
import threading
import re
import datetime
import dateutil.parser
import math
import statistics

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
    def __init__(self, name, url, color, contentclass, dateclass, validationclass, validationtext, validationinvert, nextlinkclass, nextlinktext, contentblockbegin, contentblockend, domains, zerolength, finished, overridestart):
        self.name = name
        self.url = url
        self.color = '#' + color
        self.contentclass = contentclass
        self.dateclass = dateclass
        self.validationclass = validationclass
        self.validationtext = validationtext
        self.validationinvert = validationinvert
        self.nextlinkclass = nextlinkclass
        self.nextlinktext = nextlinktext
        self.contentblockbegin = contentblockbegin
        self.contentblockend = contentblockend
        self.domains = domains
        self.zerolength = zerolength
        self.finished = finished
        self.overridestart = overridestart
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


    def statstart(self):
        return dateutil.parser.parse(self.overridestart) if self.overridestart is not None else self.data.pages[0].date

    def words_per_week(self, weeks_to_average):
        return self.smoothed_worker(weeks_to_average, sum, True)

    def words_per_post(self, weeks_to_average):
        return self.smoothed_worker(weeks_to_average, self.meanornull, False)

    def meanornull(self, input):
        data = list(input)
        if len(data) > 0:
            return statistics.mean(data)
        else:
            return 0 # this is wrong, for now

    def posts_per_week(self, weeks_to_average):
        return self.smoothed_worker(weeks_to_average, lambda data: sum(1 if words > 0 else 0 for words in data), True)

    def smoothed_worker(self, weeks_to_average, func, per_week):
        week_length = 7
        average_size = week_length * weeks_to_average
        start = self.statstart()
        results = []
        for center in [start + datetime.timedelta(days = x) for x in range(0, (self.data.pages[-1].date - start).days)]:
            rstart = center - datetime.timedelta(days = average_size / 2)
            rend = center + datetime.timedelta(days = average_size / 2)
            rstartweeks = math.floor((center - max(rstart, self.statstart())).days / 7)
            rendweeks = math.floor((min(rend, self.data.pages[-1].date) - center).days / 7)
            rstart = center - datetime.timedelta(days = rstartweeks * 7)
            rend = center + datetime.timedelta(days = rendweeks * 7)
            if per_week:
                divisor = (rend - rstart).days / 7
            else:
                divisor = 1
            results += [(center, func(page.words for page in self.data.pages if page.date > rstart and page.date <= rend) / divisor)]
        return results

class StoryData:
    def __init__(self):
        self.pages = []

def handle_page(url, story):
    page, err = web.simple_get(url)
    if page is None:
        raise RuntimeError(f'Page {url} failed to download: {err}')
    html = BeautifulSoup(page, 'html.parser')

    if story.dateclass is not None:
        date = dateutil.parser.parse(html.select_one(story.dateclass).get_text())
    else:
        date = None
    
    words = words_of_entries(story.contentblock_crop(html.select(story.contentclass)))

    if words <= 0 and url not in story.zerolength:
        raise RuntimeError(f'Zero words detected in chapter {url}; that is never right')

    for link in html.select(story.nextlinkclass):
        if re.match(story.nextlinktext, link.text.strip()) and urlparse(link['href']).netloc in story.domains:
            next = urljoin(url, link['href'])
            break
    else:
        next = None

    # it's weirdly common to just link "next" back to the epilogue, so let's catch that
    if next == url:
        next = None

    if story.validationclass != None:
        validated = False
        for element in html.select(story.validationclass):
            validated = validated or re.match(story.validationtext, element.get_text().strip())
        if story.validationinvert:
            validated = not validated
    else:
        validated = True

    print(f'{url}, {date}: {words}, {next}' + (" (SKIPPED)" if not validated else ""))

    return PageInfo(date, words, next), validated

def handle_story(story):
    # we can be passed a string, so let's just convert that to a story
    if isinstance(story, str):
        story = disk.db()[story]

    # get rid of the last page, just in case it's changed (we expect this)
    if len(story.data.pages) > 0:
        with disk.cache_lock():
            story.data.pages.pop()

    # either use the final next if available, or the base URL
    if len(story.data.pages) > 0:
        url = story.data.pages[-1].next
    else:
        url = story.url

    while url != None:
        page, validated = handle_page(url, story)
        url = page.next
        if validated:
            with disk.cache_lock():
                story.data.pages += [page]
            disk.save_cache(optional = True)

def handle_stories(allowthreads):
    if allowthreads:
        threads = []
        for id, story in disk.db().items():
            threads.append(threading.Thread(target = lambda: handle_story(story)))
            threads[-1].start()

        for thread in threads:
            thread.join()
    else:
        for id, story in disk.db().items():
            handle_story(story)

    disk.save_cache()
