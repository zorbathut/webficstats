from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from dateutil.parser import parse as dateutilparse

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

def handle_page(url):
    page = simple_get(url)
    html = BeautifulSoup(page, 'html.parser')

    date = dateutilparse(html.select_one('.entry-date').get_text())
    words = words_of_entries(html.select('.entry-content p')[1:-1])
    next = html.select('.entry-content p')[-1].find_all('a')[-1]['href']

    print(f'{url}, {date}: {words}, {next}')

    return PageInfo(date, words, next)

handle_page('https://pactwebserial.wordpress.com/2013/12/17/bonds-1-1/')
