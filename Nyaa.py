from bs4 import BeautifulSoup
import re
import requests
import sys
import time

delay = 0


def _retry_on_fail(req, *args, **kwargs):
    global delay
    try:
        r = req(*args, **kwargs)
        if r.status_code not in range(100, 399):
            delay = delay * 2 + 5
            print('Connection error, retrying in {} seconds... '
                  '(HTTP {})'.format(delay, r.status_code), file=sys.stderr)
            if delay > 1800:
                print('Too many retry attempts.')
                exit(code=1)
            time.sleep(delay)
            return _retry_on_fail(req, *args, **kwargs)
        else:
            delay = 0
            return r
    except requests.exceptions.RequestException as e:
        delay = delay * 2 + 5
        print('Connection error, retrying in {} seconds... '
              '({})'.format(delay, e.args[0].args[0]), file=sys.stderr)
        if delay > 1800:
            print('Too many retry attempts.')
            exit(code=1)
        time.sleep(delay)
        return _retry_on_fail(req, *args, **kwargs)
    except requests.packages.urllib3.exceptions.ProtocolError as e:
        delay = delay * 2 + 5
        print('Connection error, retrying in {} seconds... '
              '({})'.format(delay, e.args[1]), file=sys.stderr)
        if delay > 1800:
            print('Too many retry attempts.')
            exit(code=1)
        time.sleep(delay)
        return _retry_on_fail(req, *args, **kwargs)


class Nyaa(object):
    def __init__(self, url):
        self.url = url
        self.info_url = url + '?page=view&tid='
        self.dl_url = url + '?page=download&tid='

    @property
    def last_entry(self):
        r = _retry_on_fail(requests.get, self.url)
        soup = BeautifulSoup(r.text)
        link = soup.find('tr', class_='tlistrow') \
                   .find('td', class_='tlistname').a['href']
        return int(re.search('tid=([0-9]*)', link).group(1))


class NyaaEntry(object):
    def __init__(self, nyaa, nyaa_id):
        self.info_url = '{}{}'.format(nyaa.info_url, nyaa_id)
        self.download_url = '{}{}&magnet=1'.format(nyaa.dl_url, nyaa_id)

        r = _retry_on_fail(requests.get, self.info_url)
        setattr(r, 'encoding', 'utf-8')
        self.page = BeautifulSoup(r.text)
        content = self.page.find('div', class_='content').text
        if 'The torrent you are looking for does not appear ' \
           'to be in the database' in content:
            self.exists = False
        elif 'The torrent you are looking for has been deleted' in content:
            self.exists = False
        else:
            self.exists = True

    @property
    def category(self):
        return (
            self.page.find('td', class_='viewcategory').find_all('a')[0].text
        )

    @property
    def sub_category(self):
        return (
            self.page.find('td', class_='viewcategory').find_all('a')[1].text
        )

    @property
    def name(self):
        return self.page.find('td', class_='viewtorrentname').text

    @property
    def time(self):
        return self.page.find('td', class_='vtop').text.split(', ')

    @property
    def status(self):
        _status = self.page.find('div', class_=re.compile('content'))['class']
        if 'trusted' in _status:
            return 'trusted'
        elif 'remake' in _status:
            return 'remake'
        elif 'aplus' in _status:
            return 'a+'
        else:
            return 'normal'

    @property
    def hash(self):
        r = _retry_on_fail(requests.head, self.download_url)
        if 'Location' in r.headers:
            return re.search(r'magnet:\?xt=urn:btih:(.*)&tr=',
                             r.headers['Location']).group(1).upper()
        else:
            return None
