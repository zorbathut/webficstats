
from core import *

from requests import get
from requests.exceptions import RequestException
from contextlib import closing

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})) as resp:
            if is_good_response(resp):
                return resp.content, None
            else:
                return None, resp

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None, str(e)


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)
